"""pipeline/beats.py — thin wrapper around the vendored kit's beats.py (stage P4).

Usage:
  .venv/Scripts/python.exe pipeline/beats.py --video <id> [--force] [--target 3] [--max 6.5] ...

The kit tool consumes ONLY studio/projects/<id>/config.json + timeline/words.json and
writes a DRAFT story/shots.json (shot boundaries derived from narration gaps + the kit's
shot-length heuristics). It is a starting point only: the storyboard stage (P5, director)
owns the final master.json; without --force the kit refuses to overwrite shots.json.
"""

import argparse
import os
import sys

from _common import ROOT, run, studio_project


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--force", action="store_true", help="overwrite an existing story/shots.json")
    ap.add_argument("--target", type=float, help="ideal shot length, seconds")
    ap.add_argument("--max", type=float, help="max shot length, seconds")
    ap.add_argument("--min", type=float, help="min shot length, seconds")
    ap.add_argument("--lead", type=float, help="picture lead-in before first word, seconds")
    ap.add_argument("--tail", type=float, help="picture after last word, seconds")
    a = ap.parse_args()

    pdir = studio_project(a.video)
    for need in (os.path.join(pdir, "config.json"),
                 os.path.join(pdir, "timeline", "words.json")):
        if not os.path.exists(need):
            raise SystemExit(
                f"missing {need}\n"
                f"run first:\n"
                f"  pipeline/make_plugin_files.py --video {a.video}\n"
                f"  pipeline/align.py --video {a.video}")

    cmd = [sys.executable, os.path.join(ROOT, "studio", "tools", "beats.py"),
           "--project", pdir]
    if a.force:
        cmd.append("--force")
    for opt in ("target", "max", "min", "lead", "tail"):
        v = getattr(a, opt)
        if v is not None:
            cmd += [f"--{opt}", str(v)]

    print(" ".join(cmd))
    p = run(cmd, check=False)
    print((p.stdout or "")[-2000:])
    if p.returncode != 0:
        print((p.stderr or "")[-1500:])
        raise SystemExit(p.returncode)
    print(f"beats draft -> {os.path.join(pdir, 'story', 'shots.json')}")


if __name__ == "__main__":
    main()
