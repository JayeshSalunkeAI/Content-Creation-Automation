---
name: ch-new
description: >-
  Creates the skeleton for a new video: videos/<yyyy-mm-dd_slug>/ with 00_brief.md, a pending
  state.json and the empty stage folders, and registers the id in config/pipeline.json. Trigger: the
  user says "new video", "start a video about ...", or hands over a brief/title for the queue.
---

Make the folder, the brief, the state - then hand off to ch-run.

state.json is created and filled here (nothing to read yet). Full spec: docs/MASTER_PLAN.pdf. Config: config/pipeline.json.

## Inputs
- From the user: working title, angle (one line), audience, target length (30-45 s), series (optional),
  style-variant (optional).

## Outputs
- videos/<yyyy-mm-dd_slug>/00_brief.md
- videos/<yyyy-mm-dd_slug>/state.json (all stages pending)
- Empty stage folders; the id appended to the videos list in config/pipeline.json

## Done when
- Skeleton exists, brief is filled (or marked TODO), id registered, user knows to run ch-run next.

## Stop and ask when
- The slug collides with an existing video id.
- Audience AND target length are both missing - ask instead of inventing defaults.

## How
1. Build the id: `yyyy-mm-dd_<slug>` - lowercase, hyphenated, short, unique under videos\.
2. Create videos\<id>\ plus subfolders: audio\, timeline\, story\, scenes\, qa\, renders\, build\,
   cache\tts\ (pipeline scripts create anything beyond these).
3. Write 00_brief.md from the user's brief; leave unknowns as TODO (template below).
4. Write state.json from the template below - every stage "pending", "gates": {} empty. Keep stage keys;
   pipeline scripts add their own hashes later.
5. Register the id: add ONLY the new id entry to the videos list in config/pipeline.json - touch
   nothing else there.
6. Point the user to ch-run (one stage per session from here on).

## 00_brief.md template
```
# <id>
- Title (working):
- Angle (one line):
- Audience:
- Target length (s): 35   # 30-45
- Series: none
- Style-variant: default
- Notes:   # extra context, links, embargo dates
```

## state.json template
```json
{
  "schema": "ch.state/1",
  "id": "<id>",
  "created": "<yyyy-mm-dd>",
  "stages": {
    "P0":  { "status": "pending" },
    "P1":  { "status": "pending" },
    "P2":  { "status": "pending" },
    "P3":  { "status": "pending" },
    "P4":  { "status": "pending" },
    "P5":  { "status": "pending" },
    "P6":  { "status": "pending" },
    "P7":  { "status": "pending" },
    "P8":  { "status": "pending" },
    "P9":  { "status": "pending" },
    "P10": { "status": "pending" },
    "P11": { "status": "pending" },
    "P12": { "status": "pending" },
    "P13": { "status": "pending" },
    "P14": { "status": "pending" }
  },
  "gates": {}
}
```
