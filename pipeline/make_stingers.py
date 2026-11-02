"""pipeline/make_stingers.py — ch-brand stage 1: procedural brand stingers + micro-sfx.

Usage:
  .venv/Scripts/python.exe pipeline/make_stingers.py

Synthesizes the channel's signature sound entirely in numpy/scipy (license-clean by
construction: the audio exists nowhere else — it is generated, not sampled). Deterministic
(seed fixed) so re-runs reproduce the exact same bytes.

Writes:
  brand/audio/stingers/entry_riser.wav   ~2.3s opening stinger (riser -> thump + tick)
  brand/audio/stingers/tick_clack.wav    clapper/slate clack for cut-ins
  brand/audio/stingers/whoosh.wav        soft 0.8s transition whoosh
  brand/audio/stingers/qc_triplet.wav    "QC pass" tick-tick-tick + confirm tone (telemetry motif)
  brand/audio/stingers/stinger_preview.wav   all of the above, gapped, master-normalized

Stage 2 wires these into the mix (voice stays foreground; stingers sit ~10 dB under voice).
"""
import os
import numpy as np
import soundfile as sf
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "brand", "audio", "stingers")
SR = 48000
SEED = 20261101
rng = np.random.default_rng(SEED)


def t_axis(dur):
    return np.arange(int(SR * dur)) / SR


def lowpass(x, cutoff, order=2):
    sos = signal.butter(order, cutoff, btype="low", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def highpass(x, cutoff, order=2):
    sos = signal.butter(order, cutoff, btype="high", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def bandpass(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def stereo(l, r):
    st = np.stack([l, r], axis=1)
    peak = np.max(np.abs(st)) or 1.0
    return st / peak


def entry_riser():
    """Signature opener: 1.6s paper-ish noise + rising sweep, ending in a cork thump + tick."""
    dur = 2.3
    n = int(SR * dur)
    t = np.arange(n) / SR
    # swelling filtered noise bed
    noise = highpass(lowpass(rng.standard_normal(n), 3200), 180)
    swell = np.clip(t / 1.6, 0, 1) ** 2
    bed = noise * swell
    # rising sweep (monotonic chirp), fades right before impact
    sweep = signal.chirp(t_axis(dur), 180, dur, 1450) * np.interp(t, [0.15, 1.45, 1.62, dur], [0.02, 0.5, 0.05, 0.0])
    # cork thump: fast-decaying low sine + click tick
    thump_t = np.arange(int(SR * 0.35)) / SR
    thump = np.sin(2 * np.pi * 92 * thump_t * np.exp(-thump_t * 1.5)) * np.exp(-thump_t * 16)
    out = np.zeros(n)
    at = int(1.78 * SR)
    out += bed * 0.5 + sweep * 0.45
    out[at:at + len(thump)] += thump * 0.9
    # final brand tick (short 2.2kHz blip) right on the thump
    tick = np.sin(2 * np.pi * 2200 * thump_t) * np.exp(-thump_t * 70)
    out[at + int(0.02 * SR):at + int(0.02 * SR) + len(tick)] += tick * 0.35
    return stereo(out, out)


def tick_clack():
    """Clapper: two damped noise bursts (dry, forward) + wooden knock."""
    dur = 0.5
    n = int(SR * dur)
    out = np.zeros(n)
    bun = int(SR * 0.045)
    for start, g in ((int(0.005 * SR), 1.0), (int(0.105 * SR), 0.75)):
        burst = highpass(rng.standard_normal(bun), 1200) * np.exp(-np.arange(bun) / SR * 90)
        out[start:start + bun] += burst * g
        knock = np.sin(2 * np.pi * 190 * np.arange(bun) / SR) * np.exp(-np.arange(bun) / SR * 60)
        out[start:start + bun] += knock * g * 0.4
    return stereo(out, out * 0.96)


def whoosh():
    """0.8s air pass: two decorrelated noise streams, band-shaped, volume up-down, slight doppler tilt."""
    dur = 0.8
    n = int(SR * dur)
    t = np.arange(n) / SR
    env = np.sin(np.pi * t / dur) ** 1.6
    # doppler-ish tilt: left highpassed heavily, right progressively lower -> airiness
    l = bandpass(rng.standard_normal(n), 700, 5200) * env
    r = bandpass(rng.standard_normal(n), 380, 3400) * env * 0.92
    # soft attack/decay edges to kill clicks
    edge = np.minimum(1, np.minimum(t, dur - t) / 0.06)
    return stereo(l * edge, r * edge)


def qc_triplet():
    """Telemetry motif: tick-tick-tick (QC meter) then a two-note confirm. Used at video end."""
    dur = 1.1
    n = int(SR * dur)
    out = np.zeros(n)
    tap = np.arange(int(SR * 0.03)) / SR
    tk = np.sin(2 * np.pi * 2350 * tap) * np.exp(-tap * 160)

    for i, at in enumerate((0.02, 0.16, 0.30)):
        a = int(at * SR)
        out[a:a + len(tk)] += tk * 0.5

    # confirm: 880 -> 1318 (E -> rising) soft plucks
    pluck = np.arange(int(SR * 0.24)) / SR
    for i, at in enumerate((0.5, 0.66)):
        a = int(at * SR)
        f = 880 if i == 0 else 1318.5
        note = np.sin(2 * np.pi * f * pluck) * np.exp(-pluck * 12)
        out[a:a + len(note)] += note * 0.3
    return stereo(out, out)


def main():
    os.makedirs(OUT, exist_ok=True)
    files = {
        "entry_riser.wav": entry_riser(),
        "tick_clack.wav": tick_clack(),
        "whoosh.wav": whoosh(),
        "qc_triplet.wav": qc_triplet(),
    }
    for name, data in files.items():
        path = os.path.join(OUT, name)
        sf.write(path, data, SR)
        print(f"  {name}  {len(data) / SR:.2f}s")

    # preview reel: riser / clack / whoosh / qc with one-second gaps
    ch = files["entry_riser.wav"].shape[1]
    gap = np.zeros((int(SR * 1.0), ch), dtype="float32")
    parts = []
    for i, name in enumerate(files):
        parts.append(files[name])
        if i < len(files) - 1:
            parts.append(gap)
    reel = np.concatenate(parts).astype("float32")
    sf.write(os.path.join(OUT, "stinger_preview_raw.wav"), reel, SR)
    print(f"  stinger_preview_raw.wav  {len(reel) / SR:.2f}s")


if __name__ == "__main__":
    main()
