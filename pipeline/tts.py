"""pipeline/tts.py — local narration with Kokoro (stage P3).

Usage:
  .venv/Scripts/python.exe pipeline/tts.py --video <id>

Reads videos/<id>/script.txt (plain narration; blank lines split paragraphs) and
brand/voice.json (voiceId, speed; falls back to config/pipeline.json defaults).
Writes:
  videos/<id>/audio/voice.wav        48 kHz mono/stereo narration of the whole script
  videos/<id>/audio/voice_parts/     per-paragraph parts (restart-friendliness)
  videos/<id>/audio/voice_meta.json  {voiceId, speed, parts:[{i,text,wav,secs}], totalSecs}
Cache: cache/tts/<sha256(text|voice|speed)>.wav — re-running an unchanged script is instant.

Kokoro outputs 24 kHz; we resample to 48 kHz once (scipy), matching pipeline audio.
"""

import argparse
import hashlib
import os

from _common import (CACHE, ROOT, VIDEOS, load_config, load_json, probe_duration, run,
                     video_dir, ffmpeg_exe, load_json as _lj, save_json)

try:
    import numpy as np
    import soundfile as sf
    from scipy.signal import resample_poly
except Exception as e:  # pragma: no cover
    raise SystemExit(f"missing deps (run install_venv.ps1 first): {e}")


def kokoro_pipeline():
    import espeakng_loader
    try:
        espeakng_loader.get_library_path()  # pre-flight: library exists
        espeakng_loader.get_data_path()
    except Exception as e:
        raise SystemExit(f"espeakng-loader problem: {e}")
    from kokoro import KPipeline
    return KPipeline(lang_code="a")  # en-US; 'b' = en-GB


def synth_paragraph(pipe, text, voice, speed):
    chunks = []
    for _gs, _ps, audio in pipe(text, voice=voice, speed=speed):
        chunks.append(audio)
    if not chunks:
        raise SystemExit("kokoro returned no audio — check script text/voice id")
    return np.concatenate(chunks) if len(chunks) > 1 else chunks[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=False, help="videos/<id>; if omitted, synthesize + print preview only")
    ap.add_argument("--text")
    a = ap.parse_args()

    cfg = load_config()
    # voice: brand/voice.json wins over config defaults
    voice_path = os.path.join(ROOT, "brand", "voice.json")
    voice = load_json(voice_path) if os.path.exists(voice_path) else {}
    voice_id = voice.get("voiceId") or cfg["tts"]["default_voice_id"]
    speed = float(voice.get("speed", cfg["tts"]["speed"]))
    lang_code = voice.get("lang_code") or cfg["tts"]["lang_code"]

    if a.video and not a.text:
        vdir = video_dir(a.video)
        script_path = os.path.join(vdir, "script.txt")
        if not os.path.exists(script_path):
            raise SystemExit(f"missing narration source: {script_path} (Stage P2 writes it)")
        text_all = open(script_path, encoding="utf-8").read()
        text_all = "\n".join(line for line in text_all.splitlines() if not line.strip().startswith("#"))
        paras = [p.strip() for p in text_all.split("\n\n") if p.strip()]
    elif a.text:
        paras = [p.strip() for p in a.text.split("\n\n") if p.strip()]
    else:
        raise SystemExit("need --video <id> (uses script.txt) or --text '...'")

    pipe = kokoro_pipeline()

    parts = []
    out_dir = os.path.join(video_dir(a.video), "audio", "voice_parts") if a.video else os.path.join(CACHE, "tts")
    os.makedirs(out_dir, exist_ok=True)
    total = 0.0
    for i, para in enumerate(paras):
        key = hashlib.sha256(f"{lang_code}|{voice_id}|{speed}|{para}".encode("utf-8")).hexdigest()[:24]
        cache_wav = os.path.join(CACHE, "tts", f"{key}.wav")
        if os.path.exists(cache_wav):
            audio, sr = sf.read(cache_wav)
        else:
            audio = synth_paragraph(pipe, para, voice_id, speed)
            os.makedirs(os.path.join(CACHE, "tts"), exist_ok=True)
            sf.write(cache_wav, audio, 24000)
            audio, sr = sf.read(cache_wav)
        # cache stored at 24k; upsample to 48k for the pipeline
        if sr == 24000:
            audio = resample_poly(audio, 2, 1)
            sr = 48000
        stem = f"para_{i + 1:02d}.wav"
        sf.write(os.path.join(out_dir, stem), audio, sr)
        secs = len(audio) / sr
        parts.append({"i": i, "text": para, "wav": os.path.join("audio", "voice_parts", stem), "secs": round(secs, 3)})
        total += secs
        print(f"  para {i + 1}/{len(paras)}  {secs:6.2f}s  {para[:50]}…")

    if not a.video:
        print(f"preview synth ok: {len(paras)} part(s), {total:.1f}s")
        return

    # concat parts -> audio/voice.wav
    vdir = video_dir(a.video)
    voice_txt = "\n".join(p["text"] for p in parts)
    key = hashlib.sha256(f"v2|{lang_code}|{voice_id}|{speed}|{voice_txt}".encode("utf-8")).hexdigest()[:24]
    cache_wav = os.path.join(CACHE, "tts", f"full_{key}.wav")
    if os.path.exists(cache_wav):
        audio, sr = sf.read(cache_wav)
    else:
        segs = [sf.read(os.path.join(vdir, p["wav"]), dtype="float32")[0] for p in parts]
        # small pause between paragraphs so narration breathes (paragraphs = scene beats)
        pause = np.zeros(int(0.28 * 48000), dtype=np.float32)
        audio = np.concatenate([seg if i == 0 else np.concatenate([pause, seg])
                                for i, seg in enumerate(segs)])
        sf.write(cache_wav, audio, 48000)
    out = os.path.join(vdir, "audio", "voice.wav")
    sf.write(out, audio, 48000)
    meta = {"voiceId": voice_id, "speed": speed, "lang_code": lang_code,
            "parts": parts, "totalSecs": round(total, 3),
            "probeSecs": round(probe_duration(out), 3)}
    save_json(os.path.join(vdir, "audio", "voice_meta.json"), meta)
    print(f"voice.wav written: {meta['probeSecs']}s total, sample rate 48000, voice {voice_id} @ {speed}")


if __name__ == "__main__":
    main()
