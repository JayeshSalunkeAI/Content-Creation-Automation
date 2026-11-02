---
name: ch-remotion-build
description: >-
  Stage P10: builds Remotion props from master.json, renders the ShortVideo composition draft at scale
  0.5, pulls boundary and stress-frame stills with SafeZones on (QC-2), fixes at most 3 loops, and
  publishes draft_vN.mp4 into renders\. Trigger: ch-run after P9, or "rebuild the remotion draft" when
  only Remotion layers changed.
---

Assemble and draft-render the Remotion master composition.

Read videos/<id>/state.json first; update it last. Full spec: docs/MASTER_PLAN.pdf. Config: config/pipeline.json.

## Inputs
- videos\<id>\master.json (frozen), audio\mix.wav, videos\<id>\build\video_silent.mp4 (plugin layers,
  muted), staged assets in remotion\public\staged\<id>\, timeline\words.frames.json
- remotion\src\components\registry.tsx (available segment components), config\pipeline.json (concurrency 2)

## Outputs
- remotion\public\props\<id>.props.json + remotion\public\staged\<id>\ (built by build_props.py --stage)
- QC-2 stills (SafeZones on) + renders\draft_vN.mp4
- state.json P10 done

## Done when
- Draft renders clean at the boundaries; QC-2 stills pass SafeZones; <=3 fix loops; draft in renders\.

## Stop and ask when
- A component needs a new visual behavior (meaning change / taste call - always the user).
- Any issue survives 3 fix loops.

## Invariants (check every build)
- Video elements are ALWAYS muted; plugin clips via OffthreadVideo with startFrom offsets.
- Exactly ONE Audio element (audio\mix.wav).
- GradeOverlay owns vignette + grain (never double from a plugin style).
- Captions = brand Captions: 3-word phrases from timeline\words.frames.json, script spelling.
- Overlays per master.json: hookText / lowerThird / logoBug / sourceTag / progressBar / endCard.

## How
1. Before render: `& C:\channel\.venv\Scripts\python.exe pipeline\validate.py --video <id>`
2. Props + staging (copies plugin_full.mp4 + mix.wav into remotion\public\staged\<id>\):
   `& C:\channel\.venv\Scripts\python.exe pipeline\build_props.py --video <id> --stage`
   -> remotion\public\props\<id>.props.json
3. Draft render (concurrency 2 - the 8 GB laptop limit; scale 0.5):
   ```
   cd C:\channel\remotion
   npx remotion render ShortVideo ..\videos\<id>\renders\draft_vN.mp4 `
     --props="public/props/<id>.props.json" --concurrency=2 --scale=0.5
   ```
4. QC-2 stills with SafeZones on (first frame - both sides of EVERY segment boundary - mid-stress
   frames - end card): `& C:\channel\.venv\Scripts\python.exe pipeline\qa_stills.py --video <id> --debug`
   -> videos\<id>\qa\stills\f<frame>_safe.png (one still at a time; --frames 0,450,901 to override).
5. QC-2 review: overflow / wrap / safe-zone / caption-wrap / staging issues; cue markers within <=3
   frames tolerance boundaries; red frames; native size; fps.
6. Fix loop: max 3 - fix classes listed above are automatic; anything else goes to the user.
7. Escalate draft_v1.mp4 -> draft_v2.mp4 ... in renders\ (never overwrite a reviewed draft).
