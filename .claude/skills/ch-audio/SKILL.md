---
name: ch-audio
description: >-
  Stage P9: mixes voice, SFX and music from master.json audio cues into audio/mix.wav via
  pipeline/mix_audio.py (ducked, loudnorm -14 LUFS, TP -1.5 dBTP) with per-cue frame checks. Trigger:
  ch-run after P8, or whenever a mix is missing/outdated - and later for audio-only fixes that only
  need a remux.
---

Mix the soundtrack; keep the cue timing honest.

Read videos/<id>/state.json first; update it last. Full spec: docs/MASTER_PLAN.pdf. Config: config/pipeline.json.

## Inputs
- videos/<id>/audio/voice.wav
- videos/<id>/master.json audio.cues (only timing source)
- library\music + library\sfx rows with licenses in library\licenses.json

## Outputs
- videos/<id>/audio/mix.wav (the single Audio element for the Remotion render)
- Mix/cues report (per-cue placement checks)
- state.json P9 done; logs/<id>.md entry

## Done when
- mix.wav exists; every cue verified inside the total duration AND inside its own segment (>=3 frames
  from neighbors); loudness normalized to -14 LUFS / TP -1.5 dBTP; music ducked under narration.

## Stop and ask when
- A cue cannot be honored inside its segment - that is a routing problem (ch-revise), not a local hack.
- Any music/SFX choice lacks a licenses.json row.

## How
1. `& C:\channel\.venv\Scripts\python.exe pipeline\mix_audio.py --video <id>`
   Voice + master.json cues + library music; ducked; loudnorm to -14 LUFS, TP -1.5 -> audio/mix.wav
   plus the cues report.
2. Check the report: cue frame within duration and inside its segment; no unplanned silence gaps.
3. Spot-listen (or ask the user) if the report shows clipped or ducked regions.

## Remux-only rule (audio-only late fixes)
Rebuild mix.wav, then stream-copy remux with ffmpeg - NO re-render of video:
```
& C:\channel\tools\ffmpeg\bin\ffmpeg.exe -i renders\final.mp4 -i audio\mix.wav `
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k renders\final_remux.mp4
```
Then replace renders\final.mp4 with final_remux.mp4 and note it in logs/<id>.md.
