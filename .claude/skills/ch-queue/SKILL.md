---
name: ch-queue
description: >-
  BETA overnight batch runner: pushes queue-approved videos through P8-P13 sequentially on the shared
  laptop, one video at a time, stopping at the first error, and leaves a short morning report.
  NOT enabled by default - run only on an explicit user request ("run the queue tonight"); it never
  passes gates by itself.
---

Overnight queue: one video at a time, stop on first error, morning report.

Read videos/<id>/state.json first; update it last. Full spec: docs/MASTER_PLAN.pdf. Config: config/pipeline.json.

## Inputs
- The set of videos the user names (or all videos whose state.json shows enough approvals)
- config\pipeline.json (workers/concurrency caps)

## Outputs
- Advanced state.json per video (P8-P13 progressed only as far as approvals allow)
- logs\queue\<yyyy-mm-dd>.md morning report

## Done when
- Every queued video either completed its allowed span, parked at a gate, or stopped on first error -
  and the morning report lists all three outcomes.

## Hard limits (8 GB shared laptop)
- ONE video at a time; plugin --workers 2; Remotion concurrency 2.
- Gates are NEVER passed overnight: stop BEFORE anything that needs the human (Gate 4) and park that
  video; a video with Gate 4 already approved may finish P13 publish.
- First error anywhere = stop the whole queue (do not skip to the next video); leave that video's
  state.json exactly at the failure point.
- Defender exclusions for the project folder: optional, ask the user ONCE, never add silently.

## Allowed overnight span per video
- P8 full plugin render -> P9 mix -> P10 remotion draft -> (stop at Gate 4), or through P13 if Gate 4
  was already approved. P11/QA is fine to run (it does not render); Gate 4 stop is mandatory.

## How
1. Collect the queue from state.json (order: oldest first; skip parked-at-gate videos).
2. For each video: run the stage owner as ch-run would (skills or direct commands), updating state.json
   and logs\<id>.md after each stage; stop at gates or the first error.
3. Before every render: validate.py must pass.
4. Morning report in logs\queue\<yyyy-mm-dd>.md, per video: stages done, gate reached, first error +
   log tail, suggested next action (one line each).
