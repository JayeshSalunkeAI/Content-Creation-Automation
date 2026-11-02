"""pipeline/make_plugin_files.py — generate the vendored-kit project files (P4 → P8).

Usage:
  C:\\channel\\.venv\\Scripts\\python.exe pipeline\\make_plugin_files.py --video <id>

Creates/refreshes (idempotent):
  studio/projects/<id>/                     kit project layout
  studio/projects/<id>/config.json          pictures-only config: captions off, fades 0, no music/sfx
  studio/projects/<id>/input/voiceover.wav  copied from videos/<id>/audio/voice.wav
  studio/projects/<id>/timeline/words.json  exact copy of the canonical words.json
  studio/projects/<id>/story/shots.json     skeleton ONLY if the file does not exist yet:
      plugin shots = slots for the director/shot-builder (start/end 0 until authored),
      remotion segments = 'hold_<segid>' placeholder shots with correct bounds
  studio/projects/<id>/scenes/shots/hold_<segid>.js   placeholder scene per remotion segment
  videos/<id>/timeline/words.frames.json    Remotion copy of words (needs master.json for segmentIds)

Rules:
- config.style = "brand" only if studio/engine/styles.js defines it (ch-brand), else fallback.
- This script NEVER overwrites an existing story/shots.json (creative truth lives there).
- shots.json scenes must keep plugin sfx[]/amb empty: all audio lives in master.json cues.
"""

import argparse
import math
import os
import re
import shutil

from _common import (ROOT, STUDIO, load_config, load_json, probe_duration,
                     save_json, video_dir, studio_project)

HOLD_TEMPLATE = """// hold_<id>.js — generated placeholder covering a Remotion-owned time range.
// The player must cover every frame; Remotion overlays this segment, but semi
// transparent transitions can briefly reveal the picture underneath, hence a
// plain brand-dark hold instead of MISSING frames.
import {{ E, registerShot }} from '/engine/core.js';

registerShot('{id}', {{
  draw(g, t, info) {{
    g.fillStyle = '#0b0e1a'; g.fillRect(0, 0, E.W, E.H);
    g.fillStyle = 'rgba(255,255,255,0.03)';
    const r = E.W * 0.02;
    g.beginPath();
    g.arc((0.5 + 0.02 * Math.sin(t * 0.5)) * E.W, E.H * 0.5, r, 0, 7);
    g.fill();
  }},
}});
"""


def _video_title(vdir, fallback):
    brief = os.path.join(vdir, "00_brief.md")
    if os.path.exists(brief):
        for line in open(brief, encoding="utf-8"):
            m = re.match(r"^#\s+(.+)$", line.strip()) or re.match(r"^title:\s*(.+)$", line.strip(), re.I)
            if m:
                return m.group(1).strip()
    return fallback


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    a = ap.parse_args()

    cfg = load_config()
    vdir = video_dir(a.video)
    pdir = studio_project(a.video)
    if not os.path.isdir(vdir):
        raise SystemExit(f"missing videos/{a.video}")

    for d in ("input", "timeline", "story",
              os.path.join("scenes", "sets"), os.path.join("scenes", "shots"),
              "build", "out"):
        os.makedirs(os.path.join(pdir, d), exist_ok=True)

    # ---- voiceover
    voice_wav = os.path.join(vdir, "audio", "voice.wav")
    if not os.path.exists(voice_wav):
        raise SystemExit(f"missing {voice_wav}\nrun first:  .venv\\Scripts\\python.exe pipeline\\tts.py --video {a.video}")
    shutil.copy2(voice_wav, os.path.join(pdir, "input", "voiceover.wav"))
    dur = probe_duration(os.path.join(pdir, "input", "voiceover.wav"))

    fps = int(cfg["fps"])

    # master.json (Gate 3) may extend the runtime past the narration (end-card tail)
    master_path = os.path.join(vdir, "master.json")
    master = load_json(master_path) if os.path.exists(master_path) else None
    if master:
        dur = max(dur, round(master["durationFrames"] / fps, 3))

    # ---- style: master.brand wins when ch-brand registered it in the vendored styles.js
    sjs = open(os.path.join(STUDIO, "engine", "styles.js"), encoding="utf-8").read()
    defined = set(re.findall(r"^  ([A-Za-z_][A-Za-z0-9_]*)\s*:\s*\{", sjs, re.M))
    brand_id = master.get("brand") if master else None
    if brand_id in defined:
        style = brand_id
    elif "brand" in defined:
        style = "brand"
    else:
        style = cfg["plugin"].get("style_fallback", "dusk")

    pcfg = {
        "title": _video_title(vdir, a.video),
        "aspect": cfg["aspect"],
        "resolution": cfg["resolution_short_side"],
        "fps": fps,
        "style": style,
        "voiceover": "input/voiceover.wav",
        "script": None,   # timing already aligned once (canonical words.json); never re-align
        "duration": round(dur, 3),
        "captions": False,        # Remotion owns captions
        "captionStyle": {"y": 1500, "size": 64, "max": 3},
        "bars": None,             # Remotion owns letterbox/safe framing
        "fadeIn": 0,              # Remotion owns fades
        "fadeOut": 0,
        "music": {"enabled": False},   # our mixer owns music/SFX
        "sfx": {"enabled": False},
        "loudness": cfg["audio"]["loudness_target"],
    }
    save_json(os.path.join(pdir, "config.json"), pcfg)

    # ---- canonical words copy (first pass: align.py runs right AFTER make_plugin_files;
    # master pass: this rewrite refreshes the finished timeline inside the kit project)
    words_src = os.path.join(vdir, "timeline", "words.json")
    if os.path.exists(words_src):
        shutil.copy2(words_src, os.path.join(pdir, "timeline", "words.json"))
    else:
        print(f"NOTE: {words_src} missing — run pipeline/align.py --video {a.video} next (first pass)")

    # ---- story/shots.json skeleton (only if absent)
    story_path = os.path.join(pdir, "story", "shots.json")
    if master and not os.path.exists(story_path):
        shots = []
        for seg in master["segments"]:
            if seg["type"] == "plugin":
                for sid in seg["plugin"]["shotIds"]:
                    shots.append({"id": sid, "start": 0.0, "end": 0.0, "line": seg.get("line", ""),
                                  "scene": "TODO", "set": None, "bars": None, "in": {"type": "cut"},
                                  "sfx": [], "amb": None, "params": {}, "vignette": True,
                                  "notes": "skeleton slot — start/end/scene by shot-builder"})
            else:
                hold_id = f"hold_{seg['id']}"
                shots.append({"id": hold_id, "start": round(seg["startFrame"] / fps, 3),
                              "end": round(seg["endFrame"] / fps, 3),
                              "line": "", "scene": "Remotion takeover hold", "set": "void",
                              "bars": None, "in": {"type": "cut"}, "sfx": [], "amb": None,
                              "params": {}, "vignette": False, "notes": "generated placeholder"})
        save_json(story_path, {"title": pcfg["title"],
                               "duration": round(master["durationFrames"] / fps, 3),
                               "shots": shots, "music": []})

    # ---- placeholder scenes for remotion segments
    if master:
        for seg in master["segments"]:
            if seg["type"] == "remotion":
                fid = f"hold_{seg['id']}"
                dest = os.path.join(pdir, "scenes", "shots", f"{fid}.js")
                open(dest, "w", encoding="utf-8", newline="\n").write(HOLD_TEMPLATE.format(id=fid))

        # ---- words.frames.json (Remotion format)
        if os.path.exists(words_src):
            words = load_json(words_src)["words"]
            seg_ranges = [(s["startFrame"], s["endFrame"], s["id"]) for s in master["segments"]]

            def seg_of(frame):
                for st, en, sid in seg_ranges:
                    if st <= frame < en:
                        return sid
                return ""

            frames = {"fps": fps, "words": []}
            for i, w in enumerate(words):
                sf = int(w["start"] * fps + 0.5)
                ef = max(sf + 1, int(w["end"] * fps + 0.5))
                frames["words"].append({"i": i, "text": w["word"], "startFrame": sf,
                                        "endFrame": ef, "segmentId": seg_of(sf)})
            save_json(os.path.join(vdir, "timeline", "words.frames.json"), frames)
        else:
            print("NOTE: words.frames.json skipped — canonical words.json missing (run align.py first)")

    print(f"plugin files ready: {pdir}\n  style={style} fps={fps} duration={dur:.2f}s "
          f"(caption/fades/music/sfx all off — Remotion + our mixer own them)")


if __name__ == "__main__":
    main()
