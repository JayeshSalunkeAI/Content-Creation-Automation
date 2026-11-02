"""pipeline/voice_audition.py — ch-brand stage 1: same 3 lines, several candidate voices.

Usage:
  .venv/Scripts/python.exe pipeline/voice_audition.py            # all candidates
  .venv/Scripts/python.exe pipeline/voice_audition.py --only am_puck,am_fenrir

Writes:
  brand/auditions/voice_<n>_<id>.wav    individual cut (48 kHz)
  brand/auditions/voice_audition_all.wav  all cuts concatenated with breathing gaps
  brand/auditions/voice_audition.json     meta (what was synthesized)

Lines are taken from the shipped demo script (hook / mid / close) so the user judges
tone on real narration material. Kokoro pipeline; cache via tts cache when unchanged.
"""

import argparse
import os
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import ROOT, ffmpeg_exe, run  # noqa: E402
import tts  # noqa: E402  (pipeline/tts.py — shares kokoro pipeline + synth)

LINES = [
    "This video built itself. Watch the machine that made it.",
    "Step three, the voice. A local model speaks it, right now.",
    "That is the factory. One folder, zero cameras, every week.",
]

CANDIDATES = [
    (1, "am_liam", 1.05),   # current demo voice (reference)
    (2, "am_puck", 1.05),   # brighter, punchy
    (3, "am_fenrir", 1.00), # deeper baritone
    (4, "am_michael", 1.05),# neutral broadcaster
]

OUT_DIR = os.path.join(ROOT, "brand", "auditions")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma-separated voice ids to limit the audition")
    args = ap.parse_args()
    only = set(s.strip() for s in args.only.split(",")) if args.only else None

    os.makedirs(OUT_DIR, exist_ok=True)
    pipe = tts.kokoro_pipeline()

    cuts = []
    for n, voice, speed in CANDIDATES:
        if only and voice not in only:
            continue
        segs = []
        for line in LINES:
            audio = tts.synth_paragraph(pipe, line, voice, speed)
            if hasattr(audio, 'detach'):  # torch tensor -> numpy for soundfile
                audio = audio.detach().cpu().numpy()
            audio = np.asarray(audio, dtype=np.float32)
            if audio.ndim > 1:
                audio = audio[:, 0]
            segs.append(audio)
            segs.append(np.zeros(int(0.45 * 24000), dtype=np.float32))
        segs = segs[:-1]  # trailing pause off
        cut = np.concatenate(segs)
        cut = tts.resample_poly(cut, 2, 1)  # 24k -> 48k
        path = os.path.join(OUT_DIR, f"voice_{n}_{voice.replace('_', '')}.wav")
        sf.write(path, cut, 48000)
        cuts.append({"n": n, "voice": voice, "speed": speed, "wav": os.path.relpath(path, ROOT), "secs": round(len(cut) / 48000, 2)})
        print(f"  cut {n}: {voice} @ {speed}  ->  {path}  ({len(cut) / 48000:.1f}s)")

    # combined preview: fade-in seam of 0.7 s between cuts
    gap = np.zeros(int(0.7 * 48000), dtype=np.float32)
    parts = []
    for i, c in enumerate(cuts):
        wav, _ = sf.read(os.path.join(ROOT, c["wav"]), dtype="float32")
        parts.append(wav if i == 0 else np.concatenate([gap, wav]))
    all_path = os.path.join(OUT_DIR, "voice_audition_all.wav")
    sf.write(all_path, np.concatenate(parts), 48000)
    print(f"audition ok -> {all_path}")


if __name__ == "__main__":
    main()
