---
name: ch-research
description: >-
  Stage P1: turns the video brief into 01_research.md + sources.json with primary-first sourcing and
  verified claims, then stops for Gate 1 human approval before any scripting. Trigger: ch-run reaches
  "P1 Research" for a video id, or the user asks to research / re-research a video.
---

Research one brief into verified, citable facts - then stop for Gate 1.

Read videos/<id>/state.json first; update it last. Full spec: docs/MASTER_PLAN.pdf. Config: config/pipeline.json.

## Inputs
- videos/<id>/00_brief.md (title, angle, audience, target length)
- brand/brand.md (tone, do-not list)

## Outputs
- videos/<id>/01_research.md
- videos/<id>/sources.json (array: {id, url, publisher, date, claimsSupported[]})

## Done when
- Every key claim has >=2 independent sources; every number carries its date; the "Uncertain" list
  exists; 01_research.md ends with a one-sentence unique angle; P1 marked done in state.json.

## Stop and ask when
- A key claim cannot reach 2 independent sources.
- Sources contradict each other on a load-bearing fact.
- The angle would lean on a real-person claim the sources do not fully document.

## Rules
- Primary sources first (official stats, filings, company pages, peer-reviewed papers); secondary only
  when no primary exists.
- >=2 independent sources per key claim; note contradictions between sources instead of averaging them.
- Put dates on every number ("as of ...").
- Keep an explicit "Uncertain" list - claims that could not be pinned down (feeds ch-script).
- One-sentence unique angle at the end: the single claim the whole video hangs on.
- No accusations about real people beyond documented facts.

## How
1. Spawn the `researcher` subagent (see agents\researcher.md) with the brief path, the brand do-nots,
   and the rules above; it writes both files.
2. Spot-check 2-3 of its URLs yourself (WebFetch): publisher, date, and supported claims all real.
3. Enforce the sources.json shape (id / url / publisher / date / claimsSupported).
4. Weak spots: re-brief the subagent once. Still weak -> put it on the Gate 1 question list.
5. Mark P1 done in state.json. ch-run holds Gate 1: P2 waits for the user's "approved gate1 <id>".
