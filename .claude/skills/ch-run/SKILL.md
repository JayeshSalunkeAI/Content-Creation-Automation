---
name: ch-run
description: >-
  Orchestrator for the C:\channel shorts pipeline: walks one video through stages P0-P14 in order,
  updating videos/<id>/state.json and stopping for human approval at every gate (1-4). Trigger: the
  user says "run <id>", "continue <id>", "resume the pipeline", or wants a video driven end to end;
  also the reconnect point after an interruption or usage cutoff.
---

Drive one video through every stage - gates included, gates enforced.

Read videos/<id>/state.json first; update it last. Full spec: docs/MASTER_PLAN.pdf. Config: config/pipeline.json.

## Inputs
- videos/<id>/state.json, config/pipeline.json (stage list, workers/concurrency)
- brand/brand.md, brand/voice.json, brand/palette.json (frozen channel choices)

## Outputs
- state.json updates (stage status + gate approvals), git tags `gate<n>-<id>`
- logs/<id>.md entries, one per stage

## Done when
- All stages P0-P14 done, or parked at a gate waiting for the user; state + logs + tags consistent.

## Stop and ask when
- Any gate is reached - always stop, never merge, skip, or pre-approve a gate.
- A stage fails its fix loop 3 times; hand the report back instead of looping further.
- Meaning changes, segment swaps, palette/voice/captions/brand touches, unclear licenses, real-person
  depictions, alignment <95%, or any taste call (the master plan's "always ask" list).

## Stage map
| Stage | Owner | Notes |
|---|---|---|
| P0 Intake | ch-new | skeleton + brief |
| P1 Research | ch-research | Gate 1 after |
| P2 Script | ch-script | factcheck loop |
| P3+P4 Voice + timing | ch-voice | Gate 2 after; narration FROZEN |
| P5 Storyboard | ch-storyboard | Gate 3 after; segment mix frozen |
| P6 Assets | ch-assets | validate_assets.py must pass |
| P7 2D shots | ch-2d-shots | QC-1 sheet per batch |
| P8 Plugin render | direct command | full render |
| P9 Mix | ch-audio | audio/mix.wav |
| P10 Remotion build | ch-remotion-build | draft_vN.mp4 |
| P11 QA | ch-qa | Gate 4 after (watch draft with sound on a phone) |
| P12 Revise | ch-revise | loops back per routing |
| P13+P14 Publish + log | ch-publish | exports + experiments.csv row |

- P8 command: `& C:\channel\.venv\Scripts\python.exe pipeline\render_plugin.py --video <id>`
- Run pipeline\validate.py before every render (P8 and P10).

## How
1. Read state.json; pick the first stage not done (or the stage the user named). One stage per session
   is preferred - tell the user to /clear between stages when the usage budget matters.
2. Invoke that stage's skill (or run the P8 command). Stop on the first hard error.
3. Update state.json and append to logs/<id>.md after the stage; then continue or stop at a gate.

## Gate protocol (5 lines, exact shape)
```
GATE <n> | <id>
Review: <files to open>
Check: <what to verify - e.g. watch draft with sound on a phone>
Reply "approved gate<n> <id>" to continue, or list changes.
Reference: docs/MASTER_PLAN.pdf.
```
- On approval: record {gate, approvedOn, by} in state.json, `git tag gate<n>-<id>` (skip silently if
  git tags are unavailable), log it, continue.

## Hard rules
- Python: always `& C:\channel\.venv\Scripts\python.exe ...` by absolute path - never bare python / py -3.
- ffmpeg + ffprobe live at C:\channel\tools\ffmpeg\bin.
- Never hand-edit timeline/words.json or timeline/words.frames.json (generated only).
- Never invoke the plugin's own skills (make-2d-video, new-video, video-styles, render-video, video-sound).
- Renderers run sequentially (8 GB laptop): plugin --workers 2, Remotion concurrency 2.
- Resume = re-read state.json, trust frozen stages (narration after Gate 2, segments after Gate 3), and
  continue from the first stage not done. Never re-render what is already approved.
