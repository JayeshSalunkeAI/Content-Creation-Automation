# channel

Faceless, quality-first explainer short-videos for YouTube Shorts / IG Reels / FB Reels -
9:16, 1080x1920, 30 fps, 30-45 s, one narrated picture-story per video.

Pipeline v2 couples two renderers on one master timeline (`master.json`, integer frames):

- `studio\` - the vendored aiTrends 2D Studio kit: every frame of the "cinematic stick-figure"
  scenes drawn by code (canvas + Three.js) in headless Chromium (Playwright), piped to ffmpeg.
  It renders PICTURES ONLY in our flow (captions false, fades 0, no plugin audio).
- `remotion\` - the Remotion master editor: plugin clips (muted OffthreadVideo with startFrom),
  Remotion segment components, GradeOverlay (vignette + grain), overlays (hookText / lowerThird /
  logoBug / sourceTag / progressBar / endCard), brand Captions (3-word phrases, Whisper-timed from a
  script-as-truth alignment), and ONE Audio element (`audio\mix.wav`).

## Folder map
```
.claude\         ch-* skills (skills\<name>\SKILL.md) + subagents (agents\*.md)
analytics\       experiments.csv (one row per published video, early metrics blank until real data)
brand\           brand.md (TEMPLATE), palette.json, voice.json, pronunciations.json, components.md
cache\           TTS + model caches (cache\tts paragraph waves, cache\hf huggingface models)
config\          pipeline configuration (workers, concurrency) - do not hand-edit casually
docs\            MASTER_PLAN.pdf (authoritative spec), vendor\ (kit + vendored references), vendor-notes.md
library\         sfx, music, logos, footage, images, maps + licenses.json + catalog.json + SOURCES.txt
logs\            logs\<id>.md per-video stage log
pipeline\        the machinery (doctor, tts, align, beats, storyboard validators, mix, builds, QA)
remotion\        the Remotion master project
schemas\         master.json (ch.master/1) and other stage schemas
studio\          vendored aiTrends 2D kit (engine + render.mjs + styles.js + shared\)
tests\           fixtures + smoke tests
tools\           portable ffmpeg + ffprobe
videos\          one folder per video id: yyyy-mm-dd_slug\ with state.json keyed by stage
```
Per-video lifecycle: state.json (status + input hashes per stage) makes every stage resumable.
Gates where work STOPS for the human: Gate 1 after research, Gate 2 after script + voice (narration
frozen), Gate 3 after storyboard (segment mix frozen), Gate 4 after the draft render (watch with sound
on a phone).

## Quickstart
1. Check the environment: `& C:\channel\.venv\Scripts\python.exe pipeline\doctor.py`
2. New video: `/ch-new` (creates videos\<yyyy-mm-dd_slug>\ + brief + pending state.json)
3. Run it: `/ch-run <id>` - approve gates when asked. One stage per session; /clear between stages.

## Notes
- Python: ALWAYS `& C:\channel\.venv\Scripts\python.exe` by absolute path (never bare `python` / `py -3`).
- Authoritative spec: `docs\MASTER_PLAN.pdf` (Parts 18-27 describe this exact design).
- Kit provenance + local assumptions: `docs\vendor-notes.md`.
- Platform specs (max length, size, captions, disclosure): `docs\PLATFORM_NOTES.md` - verify before upload.

## LICENSE WARNING
The vendored aiTrends plugin archive ships with NO LICENSE file. Commercial use rights must be
confirmed with the author before monetising anything built with it (archive sha256 begins `bd20af71`;
the archive id can be cited when asking). Independently of that: every asset used in a video must have
a license row in `library\licenses.json`, and videos must not include AI-generated images or
commercial music.
