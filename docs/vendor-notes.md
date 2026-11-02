# docs/vendor-notes.md — provenance + change log for the vendored aiTrends kit

## Provenance
- Source archive: `docs/vendor/aitrends-2d-studio.plugin` (copied unmodified from
  the download `aitrends-2d-studio.plugin`).
- **Archive sha256:** `bd20af711f947f7f2da1d1738cc4429e436915b39b755cb8fc5b7dbb8623c1bd`
- Package version: `.claude-plugin/plugin.json` says **0.1.0**; internal
  `kit/package.json` says **1.0.0** (mismatch pinned at vendoring time).
- **No LICENSE file and no license field anywhere in the archive.** Commercial use
  rights must be confirmed in writing with the author before monetising. Until then,
  treat outputs as test material.
- Extracted 2026-11-01: 30 kit files → `studio/`, 6 reference docs → `docs/vendor/references/`.
  Plugin's own skills (7 SKILL.md files: make-2d-video, new-video, video-styles,
  render-video, video-sound) deliberately NOT installed — no name clashes with ch-* skills.

## Rules
1. Never edit kit files except `studio/engine/styles.js` (brand style entry).
2. Any allowed local change goes below, dated, with reason. Re-run
   `pipeline/doctor.py --smoke` and the T2 checks after adopting an updated kit pin.
3. Never auto-update the kit: vendor a new archive, re-hash, re-bench.

## Local changes log
| Date | File | Change | Why |
|---|---|---|---|
| (none yet) | | | |
