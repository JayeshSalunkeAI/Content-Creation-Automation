# pipeline/run_stage.py — thin dispatcher for the ch-* skills / orchestrator.
#
#   .venv/Scripts/python.exe pipeline/run_stage.py --stage tts --video <id>
#
# Wraps the per-stage scripts so every stage is one command; skills stay thin.

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = os.path.join(ROOT, ".venv", "Scripts", "python.exe")

SCRIPTS = {
    "tts":          ["pipeline/tts.py", "--video"],
    "align":        ["pipeline/align.py", "--video"],
    "pluginfiles":  ["pipeline/make_plugin_files.py", "--video"],
    "beats":        ["pipeline/beats.py", "--video"],
    "render":       ["pipeline/render_plugin.py", "--video"],
    "sheet":        ["pipeline/render_plugin.py", "--video", "--sheet"],
    "stills":       ["pipeline/render_plugin.py", "--video", "--stills"],
    "range":        ["pipeline/render_plugin.py", "--video"],
    "mix":          ["pipeline/mix_audio.py", "--video"],
    "props":        ["pipeline/build_props.py", "--video"],
    "validate":     ["pipeline/validate.py", "--video"],
    "qa":           ["pipeline/qa_check.py", "--video", "--file"],
    "qa_stills":    ["pipeline/qa_stills.py", "--video"],
    "doctor":       ["pipeline/doctor.py"],
    "doctor_smoke": ["pipeline/doctor.py", "--smoke"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(SCRIPTS))
    ap.add_argument("--video")
    ap.add_argument("--rest", nargs="*", default=[])
    a = ap.parse_args()

    cmd = [PY] + SCRIPTS[a.stage].copy()
    if a.video:
        cmd += [a.video]
    cmd += a.rest
    if a.stage in ("qa", "stills", "range"):
        pass  # --video then extra args as given
    print(" ".join(cmd))
    p = subprocess.run(cmd)
    sys.exit(p.returncode)


if __name__ == "__main__":
    main()
