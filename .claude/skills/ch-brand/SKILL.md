---
name: ch-brand
description: >-
  One-time (and on-change) channel brand setup: Part A auditions six Kokoro voices blind and locks
  brand\voice.json; Part B explores plugin styles and writes the custom "brand" entry into
  studio\engine\styles.js, syncing brand\palette.json with remotion\src\theme.ts and setting the caption
  style. Trigger: first-time setup, or the user asks to change voice / palette / caption style / brand
  look - every choice is its own mini-gate waiting on the user.
---

Choose the voice and the look once, deliberately - one mini-gate at a time.

Channel-level work (no per-video state.json): outputs land in brand\, the studio kit (styles.js
"brand" entry only), and remotion\src\theme.ts. Log decisions to logs\brand.md.
Full spec: docs\MASTER_PLAN.pdf. Config: config/pipeline.json.

## Inputs
- Studio kit presets (studio\engine\styles.js), Kokoro voices, remotion\src\theme.ts stub
- docs\vendor\references\style-bible.md (required reading once)

## Outputs
- brand\voice.json (+ seeded brand\pronunciations.json)
- brand\palette.json <-> remotion\src\theme.ts (kept in sync)
- studio\engine\styles.js "brand" entry only
- brand\brand.md filled section by section; brand\components.md refreshed
- audition pages under brand\auditions\ + logs\brand.md

## Done when
- Every existing section of brand.md is filled from an explicit user pick; voice.json + palette.json +
  theme.ts + styles.js agree.

## Always rule
- Every single choice (voice, palette, captions, anything brand-adjacent) gets its own MINI-GATE -
  present, wait, record the pick. Never finalize a brand touch without the user.

## Part A - narrator voice (Kokoro audition)
1. Write ONE neutral ~60-word paragraph (channel-tone average; no names, no jokes; a number with a date).
2. Render it in SIX Kokoro English voices - mixed US/UK, male/female - labeled A-F only, files under
   brand\auditions\voice\. Suggested set: af_heart, af_sky, am_michael (US) + bf_emma, bf_isabella,
   bm_george (UK).
3. Build brand\auditions\voice\review.html: play buttons per clip, NO voice names visible (blind).
4. MINI-GATE 1: user picks the top 2. Render both at three speeds (0.9 / 1.0 / 1.1) plus one harder
   sentence (names + numbers) -> new blind page. MINI-GATE 2: final pick.
5. Write brand\voice.json {voiceId, speed, lang_code} and seed brand\pronunciations.json
   ("script -> phonetic respelling" flow). Videos already past Gate 2 keep their frozen voice.

## Part B - visual style (studio kit)
1. Build a probe: one simple ~10 s scene as a studio project (per docs\vendor\references\engine-api.md,
   or reuse an existing simple shot). No captions/text in the probe.
2. Render the probe in the presets AND one custom candidate (from C:\channel\studio):
   `node .\render.mjs --project projects\<probe> --style <id> --stills <t1,t2,t3> --sheet`
   - preset style ids live in studio\engine\styles.js: dusk, midnight, golden, neon, storybook
3. Review stills together -> MINI-GATE 3 (user may mix: preset coloring + custom tweaks).
4. Write the custom look into studio\engine\styles.js as ONE new entry with id "brand". Styles are plain
   objects: palette per mood; grade {lift, gamma, gain, contrast, sat}; vignette: 0 and grain: 0 -
   Remotion's GradeOverlay always owns vignette + grain; keep grade.bloom. Never touch preset entries.
5. Sync brand\palette.json <-> remotion\src\theme.ts (edit both sides, same values).
6. MINI-GATE 4: caption style (size, vertical position, maxWords = 3-word phrases, script spelling) ->
   record in brand\brand.md, then refresh brand\components.md from remotion\src\components\registry.tsx.

## Never
- Never invoke the plugin's own skills (make-2d-video, new-video, video-styles, render-video, video-sound).
- Never edit anything under studio\ except the "brand" entry in engine\styles.js and (with vendor-notes
  documentation beyond this skill's scope) kit-owned provenance files.
- Brand changes never retro-apply: they take effect from the next video's Gates.
