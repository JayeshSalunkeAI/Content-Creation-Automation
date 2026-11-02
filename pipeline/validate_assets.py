"""pipeline/validate_assets.py — QC-0 asset gate: license records + catalog references.

Usage:
  .venv/Scripts/python.exe pipeline/validate_assets.py --video <id>
  (or --all to validate the whole library)

Rules: every asset referenced by master.json (sfxId/trackId/remotion assets) must
exist on disk and have a record in library/licenses.json (assetId match). Fails hard
otherwise — this is what keeps unlicensed files out of videos.
"""

import argparse
import os

from _common import LIBRARY, load_json, video_dir, studio_project


def load_records():
    p = os.path.join(LIBRARY, "licenses.json")
    if not os.path.exists(p):
        return {}
    doc = load_json(p)
    items = doc.get("records", doc) if isinstance(doc, dict) else doc
    return {r.get("assetId"): r for r in items if isinstance(r.get("assetId"), str)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", help="validate assets referenced by master.json")
    ap.add_argument("--all", action="store_true", help="validate every library file")
    a = ap.parse_args()
    if not (a.video or a.all):
        raise SystemExit("need --video <id> or --all")

    records = load_records()
    catalog = {}
    cat_path = os.path.join(LIBRARY, "catalog.json")
    if os.path.exists(cat_path):
        catalog = load_json(cat_path)

    refs = []  # (assetId, kind)
    if a.video:
        vdir = video_dir(a.video)
        master = load_json(os.path.join(vdir, "master.json"))
        audio = master.get("audio", {})
        refs += [(t["trackId"], "music") for t in audio.get("music", [])]
        refs += [(c["sfxId"], "sfx") for c in audio.get("cues", [])]
        for seg in master.get("segments", []):
            if seg["type"] == "remotion":
                refs += [(aid, "asset") for aid in seg.get("remotion", {}).get("assets", [])]
    if a.all:
        for aid in catalog:
            refs.append((aid, "catalog"))

    errors = []
    for aid, kind in refs:
        entry = catalog.get(aid, {})
        fpath = entry.get("file")
        if not fpath:
            errors.append(f"{kind} {aid}: no catalog entry/file")
            continue
        if kind != "sfx" or True:
            if not os.path.exists(fpath if os.path.isabs(fpath) else os.path.join(LIBRARY, fpath)) and not os.path.exists(fpath):
                errors.append(f"{kind} {aid}: file missing on disk ({fpath})")
        if aid not in records:
            errors.append(f"{kind} {aid}: no license record in licenses.json")
        elif kind == "music" and not _ok_music(records[aid]):
            errors.append(f"{kind} {aid}: license not clearly usable ({records[aid].get('license')})")

    if refs:
        print(f"checked {len(refs)} asset reference(s)")
    if a.all:
        print(f"library catalog has {len(catalog)} entries, {len(records)} license records")
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print("assets PASS")


def _ok_music(rec):
    lic = (rec.get("license") or "").lower()
    bad = ("commercial?", "non-commercial", "nc", "unknown", "=", "tbd")
    if lic in bad or not lic:
        return False
    return True


if __name__ == "__main__":
    main()
