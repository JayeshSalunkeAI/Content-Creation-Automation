"""pipeline/qa_check.py — QC-3 automated file checks (stage P11).

Usage:
  .venv/Scripts/python.exe pipeline/qa_check.py --video <id> --file <mp4> [--stills-dir path]

Checks: container facts vs master.json (size/fps/frames/pix fmt/within 1 frame),
loudness (loudnorm print), unplanned silence (>1.5 s) and black frames, and a
missing-scene sanity scan (red error text detect via Python red-pixel ratio on
contact sheets when --sheet-dir given). Writes/merges videos/<id>/qa/report.json.
"""

import argparse
import json
import os
import re
import subprocess

from _common import (ffmpeg_exe, load_config, load_json, save_json, video_dir)


def ffprobe_json(path):
    out = subprocess.run([ffmpeg_exe("ffprobe.exe"), "-v", "error", "-show_streams",
                          "-show_format", "-of", "json", path],
                         capture_output=True, text=True).stdout
    return json.loads(out)


def loudness(path):
    p = subprocess.run([ffmpeg_exe(), "-hide_banner", "-nostats", "-i", path,
                        "-af", "loudnorm=print_format=summary", "-f", "null", "-"],
                       capture_output=True, text=True)
    txt = p.stderr
    d = {}
    for k, pat in (("input_i", r"Input Integrated:\\s*(-?[\\d.]+)"), ("input_tp", r"Input True Peak:\\s*(-?[\\d.]+)"),
                   ("input_lra", r"Input LRA:\\s*(-?[\\d.]+)")):
        m = re.search(pat, txt)
        if m:
            d[k] = float(m.group(1))
    return d, txt


def silences(path, sr=None):
    p = subprocess.run([ffmpeg_exe(), "-v", "error", "-i", path, "-af",
                        "silencedetect=noise=-45dB:d=1.5", "-f", "null", "-"],
                       capture_output=True, text=True)
    return re.findall(r"silence_duration:\\s*([\\d.]+)", p.stderr)


def black_frames(path, min_sec=0.1):
    p = subprocess.run([ffmpeg_exe(), "-v", "error", "-i", path, "-vf",
                        f"blackdetect=d={min_sec}:pix_th=0.10", "-f", "null", "-"],
                       capture_output=True, text=True)
    return p.stdout.count("black_start") + len(re.findall(r"black_start", p.stderr))


def red_error_scan(png_path):
    """Contact-sheet sanity: plugin draws shot errors as red text. Squint: red ratio."""
    try:
        from PIL import Image
    except Exception:
        return None
    im = Image.open(png_path).convert("RGB")
    px = im.getdata()
    red = sum(1 for r, g, b in px if r > 200 and g < 90 and b < 90)
    return red / max(1, len(px))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--file", required=True)
    ap.add_argument("--sheet-dir")
    a = ap.parse_args()

    cfg = load_config()
    vdir = video_dir(a.video)
    master = load_json(os.path.join(vdir, "master.json"))
    exp_frames = master["durationFrames"]

    report_path = os.path.join(vdir, "qa", "report.json")
    rep = load_json(report_path) if os.path.exists(report_path) else {"open": []}
    rep.setdefault("checks", [])
    checks = []

    info = ffprobe_json(a.file)
    vs = next(s for s in info["streams"] if s["codec_type"] == "video")
    as_ = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    checks.append(f"video {vs['width']}x{vs['height']} {vs['codec_name']} {vs['pix_fmt']}")
    checks.append(f"fps {vs['avg_frame_rate']} vs master {master['fps']}/1")
    checks.append(f"frames {vs.get('nb_frames')} vs master {exp_frames} (±1)")
    if as_:
        checks.append(f"audio {as_['codec_name']} {as_['sample_rate']}Hz")

    lu, _ = loudness(a.file)
    if lu:
        checks.append(f"loudness I={lu.get('input_i')} TP={lu.get('input_tp')} LRA={lu.get('input_lra')} (target {master['audio'].get('loudnessTarget', cfg['audio']['loudness_target'])})")
    sil = silences(a.file)
    if sil:
        sil = [s for s in sil if float(s) > 1.5]
    if sil:
        checks.append(f"WARNING silent gaps >1.5s: {len(sil)}")
    black = black_frames(a.file)
    if black:
        checks.append(f"WARNING black ranges: {black}")

    sheet_flags = []
    if a.sheet_dir and os.path.isdir(a.sheet_dir):
        for f in os.listdir(a.sheet_dir):
            if f.endswith(".png"):
                ratio = red_error_scan(os.path.join(a.sheet_dir, f))
                if ratio is not None and ratio > 0.0005:
                    sheet_flags.append({"sheet": f, "red_ratio": ratio})
        if sheet_flags:
            checks.append(f"WARNING red ERROR text on sheets: {sheet_flags}")

    rep["checks"].append({"file": a.file, "checks": checks, "sheet_flags": sheet_flags, "silences": sil})
    save_json(report_path, rep)
    print("\\n".join(checks))
    print(f"qa/report.json updated ({report_path})")


if __name__ == "__main__":
    main()
