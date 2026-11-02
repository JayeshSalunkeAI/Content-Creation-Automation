---
name: ch-storyboard
description: >-
  Stage P5: the director subagent turns the frozen narration and beats into master.json (segments,
  overlays, caption config, audio cues), story/bible.md, scenes/cast.js, 03_assets_needed.md and an SFX
  audition page; pipeline/validate.py must pass before Gate 3. Trigger: ch-run after Gate 2, or "redo
  the storyboard" when segment types are reopened via ch-revise.
---

Direct the video on paper before anything renders.

Read videos/<id>/state.json first; update it last. Full spec: docs/MASTER_PLAN.pdf. Config: config/pipeline.json.

## Inputs
- Frozen narration (02_script.md, script.txt), timeline/words.frames.json, beats draft
- brand/brand.md + brand/palette.json, library/catalog.json (existing SFX/music/logos)
- Vendored references (see Required reading)

## Outputs
- videos/<id>/master.json (schema ch.master/1 - validate against schemas\master.schema.json)
- videos/<id>/story/bible.md + scenes/cast.js
- videos/<id>/03_assets_needed.md
- videos/<id>/qa/sfx_audition.html

## Done when
- master.json passes pipeline/validate.py; every cue frame sits inside its segment with >=3 frames of
  separation; plugin carries 65-85% of duration; assets-needed list matches the plan; P5 done.

## Stop and ask when
- The mix cannot satisfy the standing rules (e.g. too many layer switches at this length).
- SFX desire has no licensed candidate in the library (list it for the user, do not improvise).
- A map/chart/footage idea exceeds what ch-assets can license cleanly.

## Required reading (once per session)
- docs\vendor\references\style-bible.md
- docs\vendor\references\engine-api.md
- docs\vendor\references\story-breakdown.md
- docs\vendor\references\render-qc.md
- docs\vendor\references\sound-design.md (SFX placement guidance)

## Standing rules for master.json
- master.json is the ONLY timing source: integer frames at the pipeline fps (matches config/pipeline.json
  and the plugin project config.json). Segments: "plugin" (stick-figure scenes) or "remotion" (components).
- Plugin carries ~65-85% of total duration. Remotion takes maps, charts, photos, footage, logos, end card.
- Max ~one layer switch per 5 s; hook picture lands in the first 3 s; end card occupies the last 1.5-2 s.
- Plugin shots keep sfx[]/amb EMPTY - all sound cues live in master.json audio.cues.
- Captions config: 3-word phrases built from timeline/words.frames.json; script spelling is truth.
- SFX only from the library core_set if one is defined; otherwise catalog items with licenses confirmed
  (ch-assets verifies on the page).
- Cues need >=3 frames of separation from neighbors; each cue inside its own segment bounds.

## How
1. Read the vendored references once; summarize what binds the shots.
2. Spawn the `director` subagent (agents\director.md) with the inputs + standing rules; it writes all
   five outputs and runs:
   `& C:\channel\.venv\Scripts\python.exe pipeline\validate.py --video <id>`
   It fixes schema/segment errors itself and re-validates until clean.
3. You review its return: print the segment mix (plugin % of duration, switch count), SFX list, asset list.
4. Confirm qa/sfx_audition.html: scene list + play buttons for the chosen SFX (paths from library/catalog.json).

## Gate 3
**STOP.** Segment mix, SFX picks and asset needs are frozen after the user approves. Anything changing
segment types later reopens Gate 3 (ch-revise). Never invoke the plugin's own skills (make-2d-video,
new-video, video-styles, render-video, video-sound).
