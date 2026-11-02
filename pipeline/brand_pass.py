"""pipeline/brand_pass.py — ch-brand stage 2: the "receipts" pass.

Usage:
  .venv/Scripts/python.exe pipeline/brand_pass.py --video <id>

Runs ONCE over a director-final master.json (after P5, before renders) and injects the
brand's structural signature WITHOUT touching picture timing:

  telemetry overlays ("the video shows its own receipts")
    receiptTicker  0..end     live frame counter, mono, top-left (useCurrentFrame = real number)
    takeStamp      seg start  "SHOT i/N · TAKE 1" clack-in per segment (seg ids = real data)
    qcSeal         endcard    "QC PASS · <durationFrames>F" yellow seal near the endcard

  brand audio cues (written to master.audio.cues[]; mixed by mix_audio.py via library/catalog.json)
    stg_entry_riser @ 0, stg_tick_clack @ every segment start, stg_qc_triplet @ qcSeal frame

Also stamps master.brand = brand theme id and updates master.voice to the frozen brand voice so
the manifest stays truthful. Idempotent: re-running replaces previous *_brand ids/cues.
"""
import argparse
import json
import os

from _common import ROOT, load_json, save_json, video_dir

ENDCARD_FRAMES = 44          # endcard tail length (o_endcard previously 1130->1174 = 44)
TAKE_STAMP_FRAMES = 54       # how long a take stamp shows at a segment start
QC_SEAL_FRAMES = 30


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    a = ap.parse_args()

    vdir = video_dir(a.video)
    master_path = os.path.join(vdir, "master.json")
    master = load_json(master_path)
    fps = master["fps"]
    brand = load_json(os.path.join(ROOT, "brand", "brand.json"))
    theme_id = brand["theme"]

    # ---- truthful voice stamp (frozen brand voice)
    voice = load_json(os.path.join(ROOT, "brand", "voice.json"))
    master["voice"] = {**master["voice"], "voiceId": voice["voiceId"], "speed": voice["speed"]}
    master["brand"] = theme_id

    segs = master["segments"]
    n = len(segs)
    dur = master["durationFrames"]

    # ---- overlays (idempotent: drop anything added by an earlier pass)
    kept = [o for o in master.get("overlays", []) if not o["id"].startswith("rs_")]
    overlays = list(kept)

    def add(kind, start, end, props):
        overlays.append({"id": f"rs_{kind}_{start}", "kind": kind,
                         "startFrame": int(start), "endFrame": int(min(end, dur)),
                         "props": props})

    # 1) always-on receipt ticker (the frame counter top-left)
    add("receiptTicker", 0, dur, {"totalFrames": dur, "fps": fps})

    # 2) take stamps at every segment start (real shot boundaries from the director master)
    for i, seg in enumerate(segs, start=1):
        add("takeStamp", seg["startFrame"], seg["startFrame"] + TAKE_STAMP_FRAMES,
            {"text": f"SHOT {i}/{n}", "take": 1})

    # 3) QC seal in the endcard window
    endcard = next((o for o in master.get("overlays", []) if o["kind"] == "endCard"), None)
    qc_start = int(endcard["startFrame"] + (endcard["endFrame"] - endcard["startFrame"]) * 0.55) if endcard \
        else dur - (ENDCARD_FRAMES + QC_SEAL_FRAMES)
    add("qcSeal", qc_start, dur, {"label": "QC PASS"})

    master["overlays"] = sorted(overlays, key=lambda o: (o["startFrame"], o["id"]))

    # ---- audio cues (brand stingers)
    cues = [c for c in master.get("audio", {}).get("cues", []) if not c["id"].startswith("rs_")]
    cues.append({"id": "rs_entry", "frame": 0, "sfxId": "stg_entry_riser", "gainDb": -7})
    for i, seg in enumerate(segs, start=1):
        cues.append({"id": f"rs_clack_{i}", "frame": int(seg["startFrame"]),
                     "sfxId": "stg_tick_clack", "gainDb": -11})
    cues.append({"id": "rs_qc", "frame": qc_start, "sfxId": "stg_qc_triplet", "gainDb": -8})
    master.setdefault("audio", {})["cues"] = sorted(cues, key=lambda c: c["frame"])

    save_json(master_path, master)
    bcue = lambda c: f"  frame {c['frame']:>5}  {c['sfxId']:<17} {c['gainDb']} dB"
    print(f"brand pass ok: brand={theme_id} voice={voice['voiceId']}@{voice['speed']}")
    print(f"  overlays: {len(master['overlays'])}  cues:")
    print("\n".join(bcue(c) for c in master["audio"]["cues"]))


if __name__ == "__main__":
    main()
