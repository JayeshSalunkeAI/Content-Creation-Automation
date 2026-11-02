---
name: ch-qa
description: >-
  Stage P11: runs pipeline/qa_check.py machine checks (ffprobe specs, duration, loudness, silence/black
  detection) and has the qa-reviewer subagent review stills and contact sheets into videos/<id>/qa/
  report.json; no rendering here. Ends by presenting Gate 4 to the human. Trigger: ch-run after P10 or
  P12, or "run QC on <id>".
---

Machine QC + a human-facing list - the human decides at Gate 4.

Read videos/<id>/state.json first; update it last. Full spec: docs/MASTER_PLAN.pdf. Config: config/pipeline.json.

## Inputs
- videos\<id>\renders\draft_vN.mp4 (latest), videos\<id>\build\sheets\*.png, remotion stills, master.json

## Outputs
- qa_check.py results (machine findings)
- videos\<id>\qa\report.json (severity blocker|major|minor, loops_used, what_was_tried) + qa\notes.md
- state.json P11 done (unless blockers open)

## Done when
- qa_check.py is clean (or findings triaged); report.json written; the remaining open list is presented.

## Stop and ask when
- Gate 4 is reached: ALWAYS present the open list and stop - the user watches draft_vN.mp4 with sound
  ON, on a phone, and approves with "approved gate4 <id>".
- qa_check is red on loudness or specs: fix belongs to P9/P10 re-runs, not local patching here.

## How
1. Machine checks - do NOT render anything:
   `& C:\channel\.venv\Scripts\python.exe pipeline\qa_check.py --video <id> --file videos\<id>\renders\draft_vN.mp4`
   It verifies: ffprobe specs = 1080x1920 CFR 30 fps, H.264, yuv420p, AAC 48 kHz; duration within 1
   frame of master.json; loudness -14 LUFS with TP <= -1 dBTP; silencedetect / blackdetect = no
   unplanned silence or black.
2. Spawn the `qa-reviewer` subagent (agents\qa-reviewer.md): read all sheets + stills; layer/caption/
   grade consistency; write ONLY inside videos\<id>\qa\ ; summarize <=20 lines.
3. Triage: fix only issue classes already approved for auto-fix (overflow/wrap/safe zones/caption wrap/
   staging/cue <3 frames/loudness/red frames/native size/fps - via P9/P10 re-runs). Everything else ->
   the human list.
4. Gate 4 presentation: open list + "watch with sound on a phone" instruction; ch-run records approval.
