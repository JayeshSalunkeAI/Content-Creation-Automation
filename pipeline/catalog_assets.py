"""pipeline/catalog_assets.py — scan library/{sfx,music,...} into catalog.json + todo list.

Usage:
  .venv/Scripts/python.exe pipeline/catalog_assets.py [--rescan]

Writes:
  library/catalog.json  { "<assetId>": {file, kind, durationSec, sampleRate, peakDb, tags[]} }
  library/catalog_todo.md  files with no useful description — write a tag line for each

MVP measures duration/rate via ffprobe; tags come from folder names + filename tokens.
(BPM/energy/beat grid via librosa arrive in a later phase; Phase-2 semantic layer >>300 files.)
"""

import argparse
import os
import re
import subprocess

from _common import LIBRARY, ROOT, ffmpeg_exe, save_json

KINDS = ("sfx", "music", "logos", "footage", "images", "maps")


def probe(path):
    out = subprocess.run([ffmpeg_exe("ffprobe.exe"), "-v", "error", "-show_entries",
                          "format=duration", "-show_entries", "sample_rate", "-of", "json", path],
                         capture_output=True, text=True).stdout
    import json
    try:
        j = json.loads(out)
        dur = float(j["format"]["duration"])
        rate = int(j["format"].get("sample_rate", 0) or (j["streams"][0].get("sample_rate", 0) if j.get("streams") else 0))
        return round(dur, 3), rate
    except Exception:
        return None, 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rescan", action="store_true")
    a = ap.parse_args()

    cat_path = os.path.join(LIBRARY, "catalog.json")
    catalog = {}
    if os.path.exists(cat_path) and not a.rescan:
        import json
        catalog = json.load(open(cat_path, encoding="utf-8"))

    todo = []
    for kind in KINDS:
        d = os.path.join(LIBRARY, kind)
        if not os.path.isdir(d):
            continue
        for base_d, _dirs, files in os.walk(d):
            for f in sorted(files):
                if not re.search(r"\.(wav|mp3|ogg|flac|m4a|png|jpg|jpeg|mp4|mov)$", f, re.I):
                    continue
                full = os.path.join(base_d, f)
                rel = os.path.relpath(full, LIBRARY).replace("\\", "/")
                token = os.path.splitext(f)[0].lower() + "_" + kind
                aid = re.sub(r"[^a-z0-9_]", "_", token)
                if aid in catalog:
                    continue
                dur, rate = probe(full) if kind in ("sfx", "music", "footage") else (None, 0)
                tags = [t for t in re.split(r"[-_\s]+", os.path.splitext(f)[0].lower()) if t]
                core = "sfx" in rel and "core" in rel.lower()
                catalog[aid] = {"assetId": aid, "file": rel, "kind": kind,
                                "durationSec": dur, "sampleRate": rate,
                                "tags": tags, "core": core}
                if that_needs_todo(tags, kind):
                    todo.append(f"{aid} ({rel})")

    save_json(cat_path, catalog)
    if todo:
        with open(os.path.join(LIBRARY, "catalog_todo.md"), "w", encoding="utf-8") as fo:
            fo.write("# Assets needing a one-line description (you listen, write a tag line)\n\n")
            for t in todo:
                fo.write(f"- {t}\n")
    print(f"catalog: {len(catalog)} entries -> {cat_path}; {len(todo)} need descriptions")


def that_needs_todo(tags, kind):
    return kind in ("sfx", "music") and len(tags) <= 1


if __name__ == "__main__":
    main()
