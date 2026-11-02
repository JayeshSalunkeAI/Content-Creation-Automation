"""pipeline/build_props.py — build the Remotion input-props file (stage P10) + staging.

Usage:
  .venv/Scripts/python.exe pipeline/build_props.py --video <id> [--stage]

--stage additionally copies (Mode A):
  studio/projects/<id>/build/video_silent.mp4 -> remotion/public/staged/<id>/plugin_full.mp4
  videos/<id>/audio/mix.wav                  -> remotion/public/staged/<id>/mix.wav

Writes remotion/public/props/<id>.json = { master, words, debug:false } with paths
rewritten relative to remotion/public/ so staticFile() resolves them.
"""

import argparse
import os
import shutil

from _common import (load_json, save_json, video_dir, studio_project, REMOTION)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--stage", action="store_true")
    a = ap.parse_args()

    vdir = video_dir(a.video)
    master_path = os.path.join(vdir, "master.json")
    if not os.path.exists(master_path):
        raise SystemExit(f"missing {master_path} (Stage P5 writes it)")
    master = load_json(master_path)

    frames_path = os.path.join(vdir, "timeline", "words.frames.json")
    if not os.path.exists(frames_path):
        raise SystemExit(f"missing {frames_path} — run make_plugin_files.py after Gate 3 master.json")

    # ---- staging
    if a.stage:
        pdir = studio_project(a.video)
        staged = os.path.join(REMOTION, "public", "staged", a.video)
        os.makedirs(staged, exist_ok=True)
        silent = os.path.join(pdir, "build", "video_silent.mp4")
        if not os.path.exists(silent):
            raise SystemExit(f"missing {silent} — run render_plugin.py --video {a.video} first (Mode A)")
        clip = shutil.copy2(silent, os.path.join(staged, "plugin_full.mp4"))
        mix_src = os.path.join(vdir, "audio", "mix.wav")
        if os.path.exists(mix_src):
            shutil.copy2(mix_src, os.path.join(staged, "mix.wav"))
        else:
            print("NOTE: audio/mix.wav missing yet — Stage P9 runs before final render (audio-only remux possible later)")
        master["segments"] = [
            {**seg, "plugin": {**seg["plugin"], "clip": f"staged/{a.video}/plugin_full.mp4"}}
            if seg["type"] == "plugin" else seg
            for seg in master["segments"]
        ]
        master["audio"] = {**master["audio"], "mixFile": f"staged/{a.video}/mix.wav"}

    props = {"master": master, "words": load_json(frames_path), "debug": False,
             "brandTheme": master.get("brand", "utility")}
    out_dir = os.path.join(REMOTION, "public", "props")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{a.video}.props.json")
    save_json(out, props)
    print(f"props written: {out}")
    print("render:")
    print(f'  cd remotion && npx remotion render ShortVideo ../../videos/{a.video}/renders/draft.mp4 --props=public/props/{a.video}.props.json --scale 0.5')
    print("  (final: omit --scale, write renders/final.mp4; QC path follows qa_check.py)")


if __name__ == "__main__":
    main()
