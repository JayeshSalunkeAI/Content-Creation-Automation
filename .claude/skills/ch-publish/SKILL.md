---
name: ch-publish
description: >-
  Stages P13+P14: after Gate 4, renders the full-resolution final into renders/final.mp4, writes
  publish.md (titles, description, hashtags, attributions, synthetic-content disclosure, upload
  checklist), copies the pack to exports/<id>/, and appends the analytics/experiments.csv row.
  Trigger: ch-run after a passed Gate 4, or the user says "finalize <id>" / "publish <id>".
---

Ship it: final render, publish pack, log the experiment.

Read videos/<id>/state.json first; update it last. Full spec: docs/MASTER_PLAN.pdf. Config: config/pipeline.json.

## Inputs
- Approved draft (Gate 4 approved) + its props/build inputs
- videos\<id>\master.json (attributions), brand\brand.md, docs\PLATFORM_NOTES.md, library\licenses.json

## Outputs
- videos\<id>\renders\final.mp4 (full res 1080x1920)
- videos\<id>\publish.md
- exports\<id>\final.mp4 + exports\<id>\publish.md (copy)
- One new row in analytics\experiments.csv; state.json P13+P14 done; logs/<id>.md entry

## Done when
- final.mp4 rendered and spot-checked; publish.md complete (attributions + disclosure decision);
  exports copy exists; experiments row appended.

## Stop and ask when
- Gate 4 is not approved - never publish from an unapproved draft.
- An attribution line is missing or a license row is absent (validate_assets would also block).
- The synthetic-content disclosure decision is unclear for any platform.

## How (P13)
1. Confirm inputs unchanged since the approved draft (input hashes in state.json); re-run
   `& C:\channel\.venv\Scripts\python.exe pipeline\validate.py --video <id>`
2. Full-res render:
   ```
   cd C:\channel\remotion
   npx remotion render ShortVideo ..\videos\<id>\renders\final.mp4 `
     --props="..\videos\<id>\remotion_props.json" --concurrency=2
   ```
3. Spot-check: ffprobe specs; first/middle/last frame stills; loudness matches the P9 report.
4. publish.md:
   - 3 title options (front-load the value; respect platform length/caption limits)
   - description + hashtags
   - attribution lines from master.json attributions (auto-written from licenses.json rows)
   - synthetic-content disclosure decision (yes/no + which platform setting)
   - upload checklist per docs\PLATFORM_NOTES.md: max length, file size, caption limits - each with the
     date it was verified
5. Copy renders\final.mp4 + publish.md to exports\<id>\.

## How (P14)
- Append ONE row to analytics\experiments.csv (header order exact):
  video_id, date, platform, style_variant, hook_type, length_s, topic_type, then SWIPE-AWAY / % VIEWED /
  shares / saves / follows_gained until data exists (leave blank, note the upload date), notes.
- Log the upload pack path + tag `publish-<id>` in git if tags are in use.
