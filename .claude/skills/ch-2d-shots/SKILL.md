---
name: ch-2d-shots
description: >-
  Stage P7: the shot-builder subagent writes the stick-figure scene code (sets + shots) in batches of
  8-12 against the vendored style bible, with a mandatory plugin contact-sheet review (QC-1) after each
  batch and at most 3 fix loops. Trigger: ch-run after P6, or "rebuild shots" / "fix the sheet" when
  plugin shots are reopened.
---

Turn storyboard scenes into code-drawn shots, batch by batch, sheet-checked.

Read videos/<id>/state.json first; update it last. Full spec: docs/MASTER_PLAN.pdf. Config: config/pipeline.json.

## Inputs
- videos/<id>/story/bible.md + master.json segment ids (frozen at Gate 3) + scenes\cast.js
- studio\shared\ (reuse FIRST), docs\vendor\references\ (style bible)

## Required reading (once per session)
- docs\vendor\references\style-bible.md
- docs\vendor\references\engine-api.md
- docs\vendor\references\story-breakdown.md
- docs\vendor\references\render-qc.md

## Outputs
- scene files: sets\*.js + shots\*.js (one per master.json plugin segment)
- contact sheets per batch: videos\<id>\build\sheets\*.png (QC-1)
- Promoted sets in studio\shared\sets\ + a dated note appended to docs\vendor-notes.md

## Done when
- Every plugin segment has a shot; every batch passed a QC-1 sheet review (or its open issues are on
  your report to the user); P7 done.

## Stop and ask when
- A batch still fails QC-1 after 3 fix loops - stop and report, never loop past 3.
- "Picture matches line" is a taste call you cannot settle (show two candidates).
- A set change would alter the look beyond this scene (brand-adjacent - always the human).

## Hard rules inside shots
- PICTURES ONLY: no captions, no plugin bars/text (Remotion owns all text), no fade in/out.
- No Math.random(), no Date.now() - use rng(seed) from the engine. V() for aspect-dependent values.
- 30 fps; timing via window.renderFrame(f) with t = f / fps.
- 9:16 framing: ground line at ~65-70% of height; foreground prop rows may use the bottom quarter only
  when narration-safe.
- Picture matches the line: key action on the key word, camera motion, moody value structure, rim light.

## How
1. Read the four vendored references ONCE. Inventory reusable sets in studio\shared\sets\ before writing.
2. Spawn the `shot-builder` subagent (agents\shot-builder.md) for batches of 8-12 shots, in segment
   order from master.json.
3. After EVERY batch (never ship without it):
   `& C:\channel\.venv\Scripts\python.exe pipeline\render_plugin.py --video <id> --sheet`
4. QC-1 review of build\sheets\*.png: no MISSING labels, no red ERROR frames, picture matches the line,
   key action on the key word, rim light present, no double captions, on-screen text kept short.
5. Fix loops: max 3 per batch; then stop and report what still fails.
6. Promote good new sets to studio\shared\sets\ - record it by APPENDING a dated note to
   docs\vendor-notes.md. Never edit kit engine code from this skill (styles.js belongs to ch-brand).

## Never
- Never invoke the plugin's own skills (make-2d-video, new-video, video-styles, render-video, video-sound).
- Never render without validate.py first: `& C:\channel\.venv\Scripts\python.exe pipeline\validate.py --video <id>`.
