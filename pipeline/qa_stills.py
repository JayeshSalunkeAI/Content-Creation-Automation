"""pipeline/qa_stills.py — QC-2: still frames from the Remotion composition.

Usage:
  .venv/Scripts/python.exe pipeline/qa_stills.py --video <id> [--frames 0,450,901] [--debug] [--overwrite]

Default frames (Master plan QC-2):
  0 (hook start), total-1 (final frame), every segment boundary b: b-1 (before cut)
  and b (first frame of next segment), the middle of every remotion segment
  (stress mid), and the first frame of any endCard overlay.

Requires (run first):
  pipeline/make_plugin_files.py --video <id>     (writes timeline/words.frames.json)
  pipeline/build_props.py --video <id> --stage   (writes remotion/public/props/<id>.props.json)

Writes:  videos/<id>/qa/stills/f<frame>.png  (+ "(_safe)" suffix when --debug, SafeZones on)
One still at a time (shared laptop: never run two renderers at once).
"""

import argparse
import os
import shutil

from _common import (REMOTION, ROOT, ensure_env, load_config, load_json,
                     run, save_json, video_dir)


def pick_frames(master):
    total = master["durationFrames"]
    frames = {0, total - 1}
    for seg in master["segments"][1:]:
        b = seg["startFrame"]
        if 0 < b < total:
            frames.add(b - 1)   # frame BEFORE the cut
            frames.add(b)       # first frame of the new segment
    for seg in master["segments"]:
        if seg["type"] == "remotion":
            frames.add((seg["startFrame"] + seg["endFrame"]) // 2)
    for o in master.get("overlays", []):
        if o.get("kind") == "endCard":
            frames.add(min(total - 1, o["startFrame"]))
    return sorted(f for f in frames if 0 <= f < total)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--frames", help="override: comma-separated frame numbers")
    ap.add_argument("--debug", action="store_true", help="SafeZones debug overlay on")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()

    vdir = video_dir(a.video)
    master = load_json(os.path.join(vdir, "master.json"))
    props_rel = f"public/props/{a.video}.props.json"
    props_path = os.path.join(REMOTION, props_rel.replace("/", os.sep))
    if not os.path.exists(props_path):
        raise SystemExit(
            f"missing {props_path}\n"
            f"run first:  pipeline/build_props.py --video {a.video} --stage")

    # --debug needs a props copy with debug:true (SafeZones guides rendered)
    if a.debug:
        props = load_json(props_path)
        props["debug"] = True
        dbg_rel = f"public/props/{a.video}.props.debug.json"
        save_json(os.path.join(REMOTION, dbg_rel.replace("/", os.sep)), props)
        props_rel = dbg_rel

    user = sorted({int(x) for x in a.frames.split(",")}) if a.frames else pick_frames(master)
    out_dir = os.path.join(vdir, "qa", "stills")
    os.makedirs(out_dir, exist_ok=True)

    which_npx = shutil.which("npx") or shutil.which("npx.cmd")
    if not which_npx:
        raise SystemExit("npx not found on PATH (install Node first)")
    print(f"rendering {len(user)} still(s) to {out_dir}")
    for f in user:
        tail = "_safe" if a.debug else ""
        target = os.path.join(out_dir, f"f{f:06d}{tail}.png")
        if os.path.exists(target) and not a.overwrite:
            print(f"  skip (exists) f{f:06d} — use --overwrite to re-render")
            continue
        cmd = [which_npx, "remotion", "still", "ShortVideo", os.path.abspath(target),
               "--frame", str(f), f"--props={props_rel.replace(os.sep, '/')}",
               f"--cwd={ROOT}"]
        print("  " + " ".join(cmd))
        p = run(cmd, cwd=REMOTION, check=False)
        if p.returncode != 0 or not os.path.exists(target):
            print((p.stderr or p.stdout or "")[-1500:])
            raise SystemExit(f"still failed at frame {f}")
    print(f"stills ok: {out_dir}")


if __name__ == "__main__":
    main()
