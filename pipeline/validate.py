"""pipeline/validate.py — QC-0 gate: run before EVERY slow render.

Usage:
  .venv/Scripts/python.exe pipeline/validate.py --video <id>

Checks master.json against schemas/master.schema.json + the extra rules the schema
cannot express (contiguous segments, shots exist/cut rule, catalog/licence refs,
registry components, words match report). Exit 0 = pass; prints failures as list.
"""

import argparse
import json
import os
import re

from _common import (REMOTION, ROOT, load_config, load_json, video_dir, studio_project)

try:
    import jsonschema
except Exception as e:  # pragma: no cover
    raise SystemExit(f"jsonschema missing (install_venv.ps1): {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    a = ap.parse_args()

    cfg = load_config()
    fps = int(cfg["fps"])
    vdir = video_dir(a.video)
    pdir = studio_project(a.video)
    errors, warnings = [], []

    master_path = os.path.join(vdir, "master.json")
    if not os.path.exists(master_path):
        raise SystemExit(f"missing {master_path}")
    master = load_json(master_path)
    story_path = os.path.join(pdir, "story", "shots.json")
    story = load_json(story_path) if os.path.exists(story_path) else None

    # 1. schema
    schema = load_json(os.path.join(ROOT, "schemas", "master.schema.json"))
    try:
        jsonschema.validate(master, schema)
    except jsonschema.ValidationError as e:
        errors.append(f"schema: {e.message} @ {list(e.path)}")

    # 2. segment contiguity + frame grid
    segs = master.get("segments", [])
    if segs:
        exp = 0
        for s in segs:
            if s["startFrame"] != exp:
                errors.append(f"{s['id']}: startFrame {s['startFrame']} != expected {exp} (gaps/overlaps forbidden)")
            exp = s["endFrame"]
        if exp != master["durationFrames"]:
            errors.append(f"segments end at {exp}, master says durationFrames {master['durationFrames']}")

    # 3. shots exist + in:cut rule + timing agreement
    if story and segs:
        by_id = {s["id"]: s for s in story["shots"]}
        for seg in segs:
            if seg["type"] == "plugin":
                for sid in seg["plugin"]["shotIds"]:
                    sh = by_id.get(sid)
                    if sh is None:
                        errors.append(f"shot {sid} missing in story/shots.json")
                        continue
                    if abs(sh["end"] - sh["start"]) < 0.01 and sid.startswith("s"):
                        errors.append(f"shot {sid} has no start/end yet (skeleton) — shot-builder must set them")
                # boundary shots must cut in (transitions belong to Remotion)
                first_shot_id = seg["plugin"]["shotIds"][0] if seg["plugin"]["shotIds"] else None
                if first_shot_id and first_shot_id in by_id:
                    it = by_id[first_shot_id].get("in", {"type": "cut"}).get("type")
                    if it and it != "cut" and seg["startFrame"] > 0:
                        errors.append(f"shot {first_shot_id} starts a plugin segment @frame {seg['startFrame']} with in={it}; must be cut")
            else:
                hold = by_id.get(f"hold_{seg['id']}")
                if hold is None:
                    errors.append(f"placeholder hold_{seg['id']} missing in shots.json")
            # per-shot timing vs frames (plugin shots owned by shot-builder; ±1 frame)
            if seg["type"] == "plugin":
                rng = [(by_id[i].get("start"), by_id[i].get("end")) for i in seg["plugin"]["shotIds"] if i in by_id and (by_id[i].get("end") or 0) > 0]
                if rng:
                    if abs(rng[0][0] - seg["startFrame"] / fps) > 0.04:
                        warnings.append(f"seg {seg['id']}: first shot start {rng[0][0]} vs frame {seg['startFrame']/fps:.3f}s")
                    if abs(rng[-1][1] - seg["endFrame"] / fps) > 0.04:
                        warnings.append(f"seg {seg['id']}: last shot end {rng[-1][1]} vs frame {seg['endFrame']/fps:.3f}s")

    # 4. catalog/licence refs
    lib = os.path.join(ROOT, "library")
    catalog = load_json(os.path.join(lib, "catalog.json")) if os.path.exists(os.path.join(lib, "catalog.json")) else {}
    audio = master.get("audio", {})
    for trk in audio.get("music", []):
        if trk["trackId"] not in catalog:
            errors.append(f"music trackId {trk['trackId']} not in library/catalog.json")
        if not _licensed(os.path.join(lib, "licenses.json"), trk["trackId"]):
            errors.append(f"music {trk['trackId']} has no license record")
    for cue in audio.get("cues", []):
        if cue["sfxId"] not in catalog:
            warnings.append(f"sfxId {cue['sfxId']} not in library/catalog.json (ok if Library not built yet)")

    # 5. remotion components exist in the registry
    reg_path = os.path.join(REMOTION, "src", "components", "registry.tsx")
    reg_names = set()
    if os.path.exists(reg_path):
        reg_src = open(reg_path, encoding="utf-8").read()
        reg_names = set(re.findall(r"^\s*(\w+|'[\w-]+'|\"[\w-]+\")\s*:\s*\{\s*component", reg_src, re.M))
        reg_names |= {n.strip("'\"") for n in reg_names}
    for seg in segs:
        if seg["type"] == "remotion":
            name = seg["remotion"]["component"]
            if reg_names and name not in reg_names:
                errors.append(f"component {name} not registered in remotion registry")

    # 6. words match report (alignment gate)
    rep_path = os.path.join(vdir, "timeline", "align_report.json")
    if not os.path.exists(rep_path):
        errors.append("timeline/align_report.json missing — run pipeline/align.py (P4)")
    else:
        rep = load_json(rep_path)
        if rep.get("match_pct", 0) < int(cfg["align"]["min_match_pct"]):
            errors.append(f"word match {rep.get('match_pct')}% below {cfg['align']['min_match_pct']}%")

    # 7. plugin config = pictures-only contract (kit config copy must match master)
    pdir_cfg = os.path.join(pdir, "config.json")
    if os.path.exists(pdir_cfg):
        pcfg = load_json(pdir_cfg)
        if pcfg.get("captions"):
            errors.append("plugin config has captions on — Remotion owns captions")
        if pcfg.get("fadeIn") or pcfg.get("fadeOut"):
            errors.append("plugin config has fades on — Remotion owns fades")
        if (pcfg.get("music") or {}).get("enabled"):
            errors.append("plugin config has music on — our mixer owns audio")
        if (pcfg.get("sfx") or {}).get("enabled"):
            errors.append("plugin config has sfx on — our mixer owns audio")

    print(json.dumps({"video": a.video, "ok": not errors, "errors": errors, "warnings": warnings},
                     indent=1, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


def _licensed(licenses_path, asset_id):
    if not os.path.exists(licenses_path):
        return False
    try:
        recs = load_json(licenses_path)
    except Exception:
        return False
    items = recs.get("records", recs) if isinstance(recs, dict) else recs
    for r in items:
        if isinstance(r, dict) and r.get("assetId") == asset_id:
            return True
    return False


if __name__ == "__main__":
    main()
