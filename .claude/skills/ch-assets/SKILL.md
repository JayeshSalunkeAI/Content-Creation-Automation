---
name: ch-assets
description: >-
  Stage P6: collects the images/footage/maps/logos/music/SFX named in 03_assets_needed.md into library\
  under verified licenses, records them in library/licenses.json, refreshes the catalog, and stages
  copies for Remotion and the plugin. Trigger: ch-run after Gate 3, or "fetch the missing assets" when
  P6 reopens after a Gate 3 change.
---

Fill the library requests from 03_assets_needed.md - license first, download second.

Read videos/<id>/state.json first; update it last. Full spec: docs/MASTER_PLAN.pdf. Config: config/pipeline.json.

## Inputs
- videos/<id>/03_assets_needed.md (Gate 3 approved)
- library\licenses.json + library\catalog.json (existing holdings)

## Outputs
- library\<kind>\ assets - kind = sfx | music | logos | footage | images | maps
- library\licenses.json rows: {assetId, file, sha256, sourceUrl, author, license, licenseUrl,
  attributionRequired, retrievedOn}
- Refreshed library\catalog.json
- Staged copies: remotion\public\staged\<id>\ (build_props.py --stage) and plugin input\ where needed

## Done when
- pipeline/validate_assets.py passes for this video; every asset in use has a licenses.json row;
  staged copies exist; P6 done.

## Stop and ask when
- A license is unclear, missing, or "custom" without written terms - do NOT use it, list it instead.
- An asset would come from an AI generator (blocked by spec) or needs a paid license.

## Rules
- Check the license on the asset's OWN page, never from an aggregator snippet.
- Preferences in order: Wikimedia Commons; NASA; Natural Earth; Pexels/Pixabay (still verify per item);
  official press kits for logos.
- NO AI-generated images. NO commercial music. Logos only from official press kits.
- Footage is not usable until transcoded to H.264 CFR 30 (ffmpeg at C:\channel\tools\ffmpeg\bin).
- Attribution required? Record it - ch-publish auto-writes attributions into publish.md.
- licenses.json is append-only: never remove or rewrite existing rows.
- Music also needs a SOURCES.txt-style provenance note (see library\SOURCES.txt).

## How
1. Work item by item through 03_assets_needed.md; for each: fetch, hash, verify license on own page,
   write the licenses.json row BEFORE the next item.
2. Refresh the catalog and stage copies:
   `& C:\channel\.venv\Scripts\python.exe pipeline\catalog_assets.py`
   `& C:\channel\.venv\Scripts\python.exe pipeline\build_props.py --video <id> --stage`
3. Transcode footage to H.264 CFR 30, e.g.
   `& C:\channel\tools\ffmpeg\bin\ffmpeg.exe -i in.mp4 -vf -r 30 ... out_h264_cfr30.mp4`
4. Gate the stage:
   `& C:\channel\.venv\Scripts\python.exe pipeline\validate_assets.py --video <id>`
   MUST pass - it blocks the build on unlicensed files.
