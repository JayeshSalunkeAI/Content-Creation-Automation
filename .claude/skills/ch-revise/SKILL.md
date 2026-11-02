---
name: ch-revise
description: >-
  Stage P12: classifies the user's feedback in videos/<id>/feedback_vN.md and produces the minimal
  re-run plan EXACTLY per the routing table (which gates reopen, which stages re-run). Trigger: ch-run
  after Gate 4, or the user says "I have feedback on <id>" / "changes to <id>".
---

Feedback in - the smallest correct re-run out (no freelancing).

Read videos/<id>/state.json first; update it last. Full spec: docs/MASTER_PLAN.pdf. Config: config/pipeline.json.

## Inputs
- videos/<id>/feedback_vN.md (the user's notes from watching the draft)
- videos/<id>/qa/report.json, master.json, state.json (what is frozen where)

## Outputs
- ONE classification table: item -> class -> action -> stages re-run
- state.json P12 updated with the agreed plan; feedback logged to logs/<id>.md

## Done when
- Every feedback item classified; plan confirmed with the user; hand-off back to ch-run.

## Stop and ask when
- Feedback changes meaning, a segment type, or anything touching palette / voice / captions / brand -
  always the human first.
- Feedback contradicts qa/report.json or itself - re-read with the user before classifying.
- You cannot fit an item into the routing table - name it and ask.

## Routing table (EXACT - do not freelance)
| Feedback class | Action |
|---|---|
| wording / facts / voice | reopen Gate 2 (ch-script/ch-voice), then full downstream P5-P11 |
| segment type change | reopen Gate 3 (ch-storyboard), then P6-P11 as affected |
| plugin-shot visual (single scene) | edit that scene file, re-render that range with --from/--to and
        9-frame handles, then P9-P11 |
| remotion-only (overlays, captions, grade, components) | fix component/props, then P10-P11 |
| sfx / music / mix | adjust master.json audio cues or the library pick, run P9, then stream-copy remux
        of mix.wav (no video re-render) |
| timing move <6 frames | edit master.json frame numbers, then P9-P11 |
| timing beyond <6 frames / marker change | rising: reopen Gate 3 first (tell the user the cost) |

## Rules
- The minimal plan wins: never re-run a frozen stage unless its gate actually reopens.
- Opening Gate 2 invalidates everything downstream: tell the user the concrete cost (frames, re-renders)
  before touching anything.
- Scene edits stay within the one scene unless the change is a bible rule (that is Gate 3 territory).
- ch-revise itself renders NOTHING: it produces the plan; ch-run executes the re-run stages.

## Output shape
```
| # | Feedback (verbatim) | Class | Plan | Stages re-run | Gates reopened |
|---|---|---|---|---|---|
```
