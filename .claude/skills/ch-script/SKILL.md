---
name: ch-script
description: >-
  Stage P2: writes 02_script.md (three hook options, scene-split narration, length math) and the plain
  script.txt that feeds TTS + captions verbatim, logs new proper names to brand/pronunciations.json,
  and runs the fact-checker subagent into factcheck.md. Trigger: ch-run reaching P2 after Gate 1, or
  "rewrite the script" while the narration is not yet frozen.
---

Write the narration the voice and captions will inherit - fact-checked, length-checked.

Read videos/<id>/state.json first; update it last. Full spec: docs/MASTER_PLAN.pdf. Config: config/pipeline.json.

## Inputs
- videos/<id>/01_research.md + sources.json (Gate 1 approved)
- brand/brand.md + brand/pronunciations.json

## Outputs
- videos/<id>/02_script.md (hook options + scene-split narration + length math)
- videos/<id>/script.txt (narration ONLY - the TTS / caption source of truth)
- videos/<id>/factcheck.md
- brand/pronunciations.json (appended entries)

## Done when
- Three hook options present with a recommendation; narration split by scene; word count lands inside
  140-160 wpm at the target length; factcheck.md has no silent unknowns; P2 done.

## Stop and ask when
- An unsupported claim is the only way to keep the story - offer the supported version instead.
- A line would accuse a real person beyond documented facts - rewrite, always.
- The target length is unreachable at 140-160 wpm - propose a cut, do not silently over/under-read.

## Rules
- Draft from research only; nothing "probably true".
- 02_script.md: THREE hook options (front-load the most surprising supported fact), then the narration
  split by scene with per-scene intent notes, then word-count math: words / (wpm / 60) vs target length
  at 140-160 wpm.
- New proper names: append {"<Name>": "<phonetic respelling>"} to brand/pronunciations.json, respelled
  readably for TTS.
- script.txt: narration only. No headings, no markdown, no stage directions, no URLs - it is read
  verbatim by TTS and aligned by Whisper. Write numbers the way the voice must say them.
- No accusations about real people beyond documented facts.

## How
1. Draft 02_script.md per the rules; check length math; trim/add before writing script.txt.
2. Spawn the `fact-checker` subagent (script.txt + sources.json -> factcheck.md: every factual sentence
   marked supported / unsupported / uncertain, plus a needs-sources list).
3. Fix every unsupported/uncertain line; re-run the checker once; finish when clean or user-approved.
4. Mark P2 done. No separate gate: script + voice are reviewed together at Gate 2 (after ch-voice)
   and the narration is FROZEN from there - wording/voice changes later reopen Gate 2 (ch-revise).
