"""pipeline/mix_audio.py — the ONE mixer (stage P9). Voice + master.json cues + library music.

Usage:
  .venv/Scripts/python.exe pipeline/mix_audio.py --video <id> [--no-music] [--no-cues]

Consumes:
  videos/<id>/audio/voice.wav             (stage P3)
  videos/<id>/master.json audio.cues[]/music[] (frames @ fps)
  library/catalog.json  { "<assetId>": {file, peakDb, leadingSilenceMs, ...} } (optional)

Produces:
  videos/<id>/audio/mix_raw.wav   pre-master
  videos/<id>/audio/mix.wav       ffmpeg loudnorm -> config loudness (-14 LUFS, TP -1.5, LRA 11)
  videos/<id>/audio/cues.json     placement report (cue frame/host segment/matched file)

Design facts used: music ducked under voice envelope; our SFX files placed at exact cue
frames (dc gain); plugin shots keep sfx empty — this is the single cue list.
MVP ducking: simple RMS envelope (upgrade path: pyloudnorm + true duck envelope).
"""

import argparse
import os

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

from _common import (LIBRARY, ROOT, ffmpeg_exe, load_config, load_json, run,
                     save_json, video_dir)


def rms_env(x, sr, hop_ms=10, floor_db=-50, span_db=30):
    mono = np.abs(x).mean(axis=1) if x.ndim == 2 else np.abs(x)
    hop = max(1, int(sr * hop_ms / 1000))
    n = len(mono)
    frames = np.sqrt(np.add.reduceat(mono ** 2, np.arange(0, n, hop))[: max(1, n // hop)] / hop)
    db = 20 * np.log10(frames + 1e-9)
    lv = np.clip((db - floor_db) / span_db, 0, 1)
    # light smoothing (attack-ish)
    k = 5
    kernel = np.ones(k) / k
    lv = np.convolve(lv, kernel, mode="same")
    return lv


def load_any(path, sr):
    audio, rate = sf.read(path, dtype="float32", always_2d=False)
    if audio.ndim == 1:
        audio = np.stack([audio, audio], axis=1)
    elif audio.shape[1] == 1:
        audio = np.repeat(audio, 2, axis=1)
    if rate != sr:
        g = _gcd(rate, sr)
        audio = resample_poly(audio, sr // g, rate // g, axis=0)
    return audio


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def place(dst, snd, start_sample, gain_db):
    i = max(0, int(start_sample))
    j = min(len(dst), i + len(snd))
    if j > i:
        dst[i:j] += snd[: j - i] * (10 ** (gain_db / 20))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--no-music", action="store_true")
    ap.add_argument("--no-cues", action="store_true")
    a = ap.parse_args()

    cfg = load_config()
    sr = int(cfg["audio"]["sample_rate"])
    vdir = video_dir(a.video)
    master_path = os.path.join(vdir, "master.json")
    if not os.path.exists(master_path):
        raise SystemExit(f"missing {master_path} (Stage P5 writes it)")
    master = load_json(master_path)
    audio_cfg = master.get("audio", {})

    total_frames = master["durationFrames"]
    n = int(total_frames * sr / master["fps"]) + 1

    voice_path = os.path.join(vdir, "audio", "voice.wav")
    if not os.path.exists(voice_path):
        raise SystemExit(f"missing {voice_path} — run pipeline/tts.py first")
    voice = load_any(voice_path, sr)[:n]
    if len(voice) < n:
        voice = np.concatenate([voice, np.zeros((n - len(voice), 2), np.float32)])
    env = rms_env(voice, sr)

    mix = voice.copy()
    report = {"cues": [], "music": [], "notes": []}

    # catalogs
    catalog = {}
    cat_path = os.path.join(LIBRARY, "catalog.json")
    if os.path.exists(cat_path):
        catalog = load_json(cat_path)

    # ---- music: ducked under voice (config gain per track)
    if not a.no_music:
        for trk in audio_cfg.get("music", []):
            entry = catalog.get(trk["trackId"], {})
            fpath = entry.get("file") or _resolve_library_file(trk["trackId"])
            if not fpath or not os.path.exists(fpath):
                report["notes"].append(f"music track missing: {trk['trackId']}")
                continue
            mus = load_any(fpath, sr)
            sf_, ef = trk["startFrame"], trk["endFrame"]
            seg = mus[: max(1, int((ef - sf_) * sr / master["fps"]))].copy()
            per = trk.get("gainDb", -18)
            # env is sampled at ~10 ms hops; interpolate onto the sample grid so
            # ducking follows the voice envelope at any sr/hop combination
            hop = max(1, int(sr * 10 / 1000))
            base = int(sf_ * sr / master["fps"])
            env_at = np.interp((base + np.arange(len(seg), dtype=np.float64)) / hop,
                               np.arange(len(env), dtype=np.float64), env)
            seg *= (10.0 ** ((per - 12.0 * env_at) / 20.0))[:, None]
            place(mix, seg, sf_ * sr / master["fps"], 0)
            report["music"].append({"trackId": trk["trackId"], "gainDb": per,
                                    "startFrame": sf_, "endFrame": ef})

    # ---- SFX cues at exact frames
    if not a.no_cues:
        for cue in audio_cfg.get("cues", []):
            entry = catalog.get(cue["sfxId"], {})
            fpath = entry.get("file") or _resolve_library_file(cue["sfxId"])
            if fpath and not os.path.isabs(fpath):
                fpath = os.path.join(ROOT, fpath)  # catalog stores ROOT-relative paths
            if not fpath or not os.path.exists(fpath):
                report["notes"].append(f"sfx missing: {cue['sfxId']} @ frame {cue['frame']}")
                continue
            snd = load_any(fpath, sr)
            snd = snd[: int(snd.shape[0])]  # keep original length
            place(mix, snd, cue["frame"] * sr / master["fps"], cue.get("gainDb", -6))
            report["cues"].append({"id": cue["id"], "frame": cue["frame"],
                                   "sfxId": cue["sfxId"], "file": fpath,
                                   "gainDb": cue.get("gainDb", -6),
                                   "segmentId": cue.get("segmentId", "")})

    # ---- gentle high-pass + soft clip, then loudnorm via ffmpeg (verified recipe)
    raw = os.path.join(vdir, "audio", "mix_raw.wav")
    sf.write(raw, np.tanh(mix) * 0.95, sr)
    out = os.path.join(vdir, "audio", "mix.wav")
    I = float(audio_cfg.get("loudnessTarget", cfg["audio"]["loudness_target"]))
    tp = float(cfg["audio"]["true_peak"])
    lra = int(cfg["audio"]["lra"])
    run([ffmpeg_exe(), "-y", "-v", "error", "-i", raw,
         "-af", f"loudnorm=I={I}:TP={tp}:LRA={lra}", "-ar", str(sr), out],
        check=True)
    save_json(os.path.join(vdir, "audio", "cues.json"), report)
    print(f"mix written: {out}  (target {I} LUFS, cues {len(report['cues'])}, music {len(report['music'])})")


def _resolve_library_file(asset_id):
    """Search common library folders by loose filename match on asset id."""
    hint = asset_id.replace("_", "")
    for root_d, _dirs, files in os.walk(LIBRARY):
        for f in files:
            if f.lower().replace("_", "").startswith(hint[:12]):
                return os.path.join(root_d, f)
    return None


if __name__ == "__main__":
    main()
