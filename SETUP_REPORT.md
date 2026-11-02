# SETUP_REPORT — 2026-11-01

Filled with verified values from the setup session. Final doctor run: **ALL PASS** (incl. smoke),
log: `logs/doctor_2026-11-01_011229.txt`.

## Installed (every step re-runnable; scripts live in `pipeline\`)

- Python 3.11 venv at `C:\channel\.venv` — `pipeline\install_venv.ps1` (pinned stack frozen to `requirements.txt`).
- ffmpeg + ffprobe 9.0.2 **portable** at `C:\channel\tools\ffmpeg\bin`, registered on the user PATH;
  user-scope env: `PYTHONUTF8=1`, `HF_HOME=C:\channel\cache\hf` — `pipeline\bootstrap_ffmpeg.ps1`.
  No winget, no admin, no UAC anywhere.
- aiTrends 2D Studio kit vendored at `studio\` (30 files, sha256-pinned archive in `docs\vendor\`),
  npm deps + Playwright Chromium — `pipeline\install_studio.ps1`.
- Remotion master-edit project at `remotion\` (scaffold written, deps installed, headless Chrome registered).
- Models cached **project-local** in `C:\channel\cache\hf`: Kokoro-82M (TTS) + faster-whisper small.en (461 MB).

## Versions

| Component | Version |
|---|---|
| Python (venv) | 3.11.9 (pip 26.2.2) |
| Node.js / npm | v24.14.0 / 11.9.0 |
| git | 2.51.1.windows.1 |
| ffmpeg / ffprobe | 9.0.2-essentials (gyan.dev portable) |
| torch | 2.15.0+cpu (CUDA off — CPU-first by design) |
| kokoro / misaki / espeakng-loader | 0.9.4 / 0.9.4 / 0.2.4 |
| faster-whisper / ctranslate2 | 1.2.1 / 4.8.4 (model small.en) |
| numpy / scipy / soundfile | 2.4.6 / 1.17.1 / 0.14.0 |
| librosa / pyloudnorm / jsonschema / Pillow | 0.11.0 / 0.2.0 / 4.26.0 / 13.0.0 |
| remotion / @remotion/cli | 4.0.539 / 4.0.539 |
| Playwright Chromium | 141.0.7390.37 (Remotion headless shell 157.0.8080.0) |

## Doctor — ALL PASS

- 35 checks OK: venv python, portable ffmpeg on PATH, node ≥ 18, GPU driver present,
  all Python imports, studio three/playwright/fonts, Remotion node_modules, both headless
  browsers found, kit `render.mjs` + `engine/player.js`, `docs/MASTER_PLAN.pdf`.
- `--smoke` PASS: Kokoro rendered *“This is a pipeline smoke test. If you can hear this line,
  the voice works.”* and faster-whisper small.en transcribed it back word-perfect —
  the save→ASR round-trip the whole alignment stage depends on works end to end.
- First smoke failure (no wav) was a doctor bug: subprocess lacked `HF_HOME` and swallowed
  stderr with the misaki EspeakWrapper lines missing. Fixed in `pipeline/doctor.py`; cured.

## Assumptions / caveats (8 GB laptop)

- ~7.4 GB usable RAM: plugin `--workers 2`, Remotion `--concurrency 2`, drafts `--scale 0.5`,
  **never two renderers at once** (enforced by the ch-* skills).
- Whisper + Kokoro run CPU int8 (small.en); the kit's WebGL shots use Chromium `--gl auto`
  (RTX 3050 may accelerate later; nothing depends on it).
- Whisper model read-back earlier landed in the user home HF cache during smoke; moved to
  `C:\channel\cache\hf` so `pipeline/align.py` finds it without a re-download.
- User-scope env vars only reach **new** terminals; already-open shells need manual PATH.

## How to re-run doctor

```
& C:\channel\.venv\Scripts\python.exe pipeline\doctor.py --smoke
```
(`--smoke` adds the Kokoro→Whisper round-trip; models are cached, it takes ~1–2 min.)

## Open issues

1. **No LICENSE in the aiTrends archive** — confirm commercial-use rights with the author
   before monetising anything rendered with the kit (archive sha256 begins `bd20af71`).
   Non-commercial/test use meanwhile.
2. **npm audit: 10 high-severity advisories** (remotion dev dependencies; studio: 0).
   Dev-only, not shipped in renders — review after the first demo render rather than
   blanket `npm audit fix` mid-build.
3. **Nothing rendered yet** — installs + contracts + scripts verified; the first real
   end-to-end test is the planned demo video (`videos/000_pipeline_test`, next session).
4. Git history starts at `5b890c9` (scaffold) — no remote configured yet; add one before
   relying on it for backups.
