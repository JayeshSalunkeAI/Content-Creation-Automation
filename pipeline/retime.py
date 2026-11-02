"""pipeline/retime.py — voice swap re-time (director structure preserved).

Usage:
  .venv/Scripts/python.exe pipeline/retime.py --video <id>

When brand/voice.json freezes a NEW voice, narration timing shifts. This tool re-times the
whole film WITHOUT re-directing: it builds a piecewise-linear warp from the old narration
timing (timeline/backup/words_frames_old.json) onto the new whisper timing
(timeline/words.json, seconds), then warps:

  story/shots.json shot boundaries (all kit shots + the Remotion takeover hold)
  master.json segment boundaries, durationFrames, StatCounter tween, endCard window

Everything is derived from real data; the film keeps its shot count, style and narrative
exactly — only the clock stretches to fit the new voice. Backups of the originals are
written to timeline/backup/ once (prev_* files), so re-running retime twice is safe-ish:
run --restore first if you need the pristine liam master back.
"""
import argparse
import json
import os
import re

from _common import ROOT, load_json, save_json, video_dir, studio_project

PAD_ENDCARD = 46   # frames between last word end and endCard start (matches original 1130 = lastend + 46)
ENDCARD = 44       # endCard length (o_endcard 1130->1174)


def norm(w):
    return re.sub(r"[^\w']", "", w.lower())


def script_paras(vdir):
    txt = open(os.path.join(vdir, "script.txt"), encoding="utf-8-sig").read()
    return [[norm(x) for x in p.split()] for p in re.split(r"\n\s*\n", txt.strip()) if p.strip()]


def para_spans(words, paras, frame_scale):
    """Sequential cursor: consume `words` matching each paragraph's token count.
    words: list of dicts with a word+timing key; returns spans [(first_i_frame, last_i_frame)]."""
    spans, cursor = [], 0
    for tokens in paras:
        take = words[cursor:cursor + len(tokens)]
        if len(take) < len(tokens):
            raise SystemExit(f"words list too short at cursor {cursor} for paragraph ({len(tokens)} tokens)")
        starts = [t["startFrame"] if frame_scale else t["start"] for t in take]
        ends = [t["endFrame"] if frame_scale else t["end"] for t in take]
        spans.append((float(min(starts)), float(max(ends))))
        cursor += len(tokens)
    if cursor != len(words):
        raise SystemExit(f"token count mismatch: script has {cursor} words, whisper gave {len(words)}")
    return spans


def build_warp(old_spans, new_spans):
    """old frame-time -> new frame-time. Para k interior affine; gaps stretched proportionally; tails preserved."""
    a0, a1 = old_spans[0][0], old_spans[-1][1]
    b0, b1 = new_spans[0][0], new_spans[-1][1]

    def warp(x):
        # head lead-in stretches to keep the new head proportion of the old head
        if x <= a0:
            return x * (b0 / a0) if a0 else x
        if x >= a1:
            return b1 + (x - a1)
        for k, ((oa0, oa1), (na0, na1)) in enumerate(zip(old_spans, new_spans)):
            if x < oa0:  # in gap before para k (after para k-1's end)
                po0, po1 = old_spans[k - 1]
                pn0, pn1 = new_spans[k - 1]
                gap_o = oa0 - po1
                gap_n = na0 - pn1
                t = (x - po1) / gap_o if gap_o else 0
                return pn1 + t * gap_n
            if x <= oa1:
                t = (x - oa0) / (oa1 - oa0)
                return na0 + t * (na1 - na0)
        return x
    return warp, (a0, a1), (b0, b1)


def warp_dict(w, d):
    out = dict(d)
    out["startFrame"] = round(w(d["startFrame"]))
    out["endFrame"] = round(w(d["endFrame"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--restore", action="store_true", help="put prev master/shots back for a clean re-run")
    a = ap.parse_args()

    vdir = video_dir(a.video)
    pdir = studio_project(a.video)
    tdir = os.path.join(vdir, "timeline")
    bdir = os.path.join(tdir, "backup")
    fps = 30

    new_words = load_json(os.path.join(tdir, "words.json"))["words"]  # new voice (seconds)
    old_frames = load_json(os.path.join(bdir, "words_frames_old.json"))["words"]  # old voice (frames)
    paras = script_paras(vdir)

    old_spans = para_spans(old_frames, paras, frame_scale=True)
    new_spans = para_spans(new_words, paras, frame_scale=False)
    new_spans = [(s * fps, e * fps) for s, e in new_spans]
    w, old_span, new_span = build_warp(old_spans, new_spans)
    print(f"warp: old narration {old_span[0]:.0f}-{old_span[1]:.0f}f  ->  new {new_span[0]:.0f}-{new_span[1]:.0f}f")

    def backups():
        os.makedirs(bdir, exist_ok=True)
        for src, name in ((os.path.join(vdir, "master.json"), "prev_master.json"),
                          (os.path.join(pdir, "story", "shots.json"), "prev_shots.json")):
            dst = os.path.join(bdir, name)
            if not os.path.exists(dst):
                with open(src, "rb") as fi, open(dst, "wb") as fo:
                    fo.write(fi.read())

    if a.restore:
        for name, dst in (("prev_master.json", os.path.join(vdir, "master.json")),
                          ("prev_shots.json", os.path.join(pdir, "story", "shots.json"))):
            src = os.path.join(bdir, name)
            if os.path.exists(src):
                with open(src, "rb") as fi, open(dst, "wb") as fo:
                    fo.write(fi.read())
                print(f"restored {dst}")
        return

    backups()

    # ---- master.json: segments, statcounter tween, endcard window, duration
    master = load_json(os.path.join(vdir, "master.json"))
    new_seg_frames = [warp_dict(w, s) for s in master["segments"]]
    # duration: new last word end + the original lastword->endcard pad + endcard length
    last_end_new = new_spans[-1][1]
    old_master_end = master["durationFrames"]
    old_last_end = old_spans[-1][1]
    old_tail = old_master_end - old_last_end
    dur = int(round(last_end_new + old_tail))
    for s in new_seg_frames:
        s["endFrame"] = min(s["endFrame"], dur)
    if new_seg_frames[-1]["endFrame"] < dur:
        new_seg_frames[-1]["endFrame"] = dur  # final seg runs to the very end
    master["segments"] = new_seg_frames
    master["durationFrames"] = dur

    counter = next(s for s in new_seg_frames if s.get("remotion"))
    counter["remotion"]["props"]["tween"] = {"from": 0, "to": dur,
                                             "durFrames": counter["endFrame"] - counter["startFrame"]}
    brand = load_json(os.path.join(ROOT, "brand", "brand.json"))
    counter["remotion"]["props"]["tag"] = f"{fps} FPS · {brand['theme']}"

    ec = next((o for o in master.get("overlays", []) if o["kind"] == "endCard"), None)
    if ec:
        ec["startFrame"] = dur - ENDCARD
        ec["endFrame"] = dur

    save_json(os.path.join(vdir, "master.json"), master)
    print(f"master re-timed: cuts -> {[(s['startFrame'], s['endFrame']) for s in new_seg_frames]}")
    print(f"  durationFrames {old_master_end} -> {dur}; endcard @ {dur - ENDCARD}; counter tag '{counter['remotion']['props']['tag']}'")

    # ---- kit shots.json: warp every boundary, keep ids/structure
    spath = os.path.join(pdir, "story", "shots.json")
    data = load_json(spath) if os.path.exists(spath) else None
    if data:
        shots = data["shots"] if isinstance(data, dict) and "shots" in data else data
        for s in shots:
            s["start"] = round(max(0.0, w(round(s["start"] * fps)) / fps), 3)
            s["end"] = round(max(0.0, min(dur, round(w(round(s["end"] * fps)) / fps))), 3)
        # enforce monotonic + cover duration
        prev = 0.0
        for s in shots:
            s["start"] = max(prev, s["start"] if s.get("start") is not None else 0.0)
            if s["end"] <= s["start"]:
                s["end"] = s["start"] + 0.1
            prev = s["start"]
        prev_end = 0.0
        for s in shots:
            if s["start"] < prev_end:
                s["start"] = prev_end
            s["end"] = max(s["end"], s["start"] + 0.05)
            prev_end = s["end"]
        if shots and shots[-1]["end"] < dur / fps:
            shots[-1]["end"] = round(dur / fps, 3)
        save_json(spath, data)
        print(f"shots.json re-timed: {len(shots)} shots, ends at {shots[-1]['end']}s")


if __name__ == "__main__":
    main()
