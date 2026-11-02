# 001_paper_fold — Storyboard v3 (Gate 3 redo, LOCKED to voice)

Brand: **Utility Class** (graphite + safety yellow) · 9:16 1080×1920 · 30 fps · **47.4 s (1421 frames, voice-locked)**
Voice: am_fenrir@1.0 · 9 shots in 3 segments · no end card (echo ending + black tail)
**Script v3 contract: the voice speaks SCALES (almost no numbers); the FOLDS counter, stamps
and cards carry every number.** Numbers all from `../research/fold_table.json` (machine-verified).
Timings below are LOCKED to the real fenrir recording (43.93 s speech + 8 × 0.28 s pauses
= 46.17 s voice + 1.2 s black tail); word-level ±0.2 s polish happens after whisper align.

## Board at a glance (voice-locked)

| # | Shot | Time | Beat | Set | Key event |
|---|------|------|------|-----|-----------|
| 1 | s001 | 0.00–3.98 | HOOK QUESTION | desk | sheet slam + "WHAT IF... 1000 FOLDS?" + counter 0000→1000→0001 |
| 2 | s002 | 3.98–6.16 | BREATHER | desk | 7 self-folds; cards `7 MAX ✗ → RECORD 12 ✓ → 13 unofficial` |
| 3 | s003 | 6.16–10.92 | LADDER 1 | void skyline | 0023 Burj ✓ 828 m · 0027 Everest ✓ 8,848 m (silent receipt) |
| 4 | s004 | 10.92–16.00 | LADDER 2 | void orbit | 0030 SPACE ✓ 100 km · 0042 Moon ✓ 384,400 km |
| 5 | s005 | 16.00–22.20 | LADDER 3 | void deep space | 0051 Sun ✓ 149.6 Mkm · 0058 Voyager glyph |
| 6 | s006 | 22.20–27.96 | UNIVERSE JUMP | void cosmos | 0103 — universe shrinks to a dot, "897 FOLDS REMAIN", dead air |
| 7 | s007 | 27.96–33.46 | REALITY | desk | voice answers THE question: twelve folds · Gallivan 1,219 m · ×4-law curve |
| 8 | s008 | 33.46–41.34 | PAYOFF | void black | 10^281 types in; universe line shrinks to a tick; 10^270× bar |
| 9 | s009 | 41.34–47.37 | ECHO | desk | exact frame-1 replica, FOLDS 001 flash, black tail (voice ends 46.17) |

Master pattern: frames are the single timing source (`master.json`), kit shots draw the
picture (`studio/projects/001_paper_fold/story/shots.json`), Remotion owns captions,
`brand_pass.py` injects the receipt ticker / take stamps / QC seal.

## Shot cards

### s001 — HOOK QUESTION (0.00–3.98, desk, cut)
- Picture: top-down graphite desk; 80 gsm sheet reaches frame-coast with a spring (crack snaps
  frame 7); title card **'WHAT IF... 1000 FOLDS?'** typewriter-in in 96px safety yellow; mono
  tag `PAPER: 80 GSM · 0.1 mm` bottom (auditability); the FOLDS counter spins 0000→1000 in a
  blur then snaps back to **0001** — the open loop. No claim, no answer: the video OWES the payoff.
- sfx: `sfx_ice_crack_snap` (f7) + brand entry riser under (brand_pass).

### s002 — BREATHER (3.98–6.16, desk, whip 0.2 s)
- Macro: the sheet folds ITSELF ×7 in quick ticks (counter holds 0001).
- Card strip stamps across: `7 MAX ✗` (deny sound) → `OFFICIAL RECORD: 12 ✓` (accept sound)
  → `13 unofficial`. NO spoken facts — the voice just says the trust line.
- sfx: 3 fast brand clacks (f124/128/133 −16), `sfx_ui_deny_low` (f146 −10), `sfx_ui_accept_glassy` (f160 −10).
- Ends in dead silence → the skyline reset is the hardest early pattern break.

### s003 — LADDER 1 (6.16–10.92, void, cut) — *"taller than the tallest building we've ever built"*
- FOLDS counter **0023** → ruler passes the Burj Khalifa silhouette → stamp `PAST BURJ KHALIFA ✓ 828 m`
  pops exactly on the voice's "tallest building" (f273).
- Counter **0027** → Everest line → stamp `PAST EVEREST ✓ 8,848 m` = the SILENT receipt,landing
  inside the narration gap (f323) — the viewer reads it themselves.
- `FOLDS LEFT: 977` ticker under the counter = the second motion plane.
- sfx: brand clack at f185 (seg2 start) + f273/f323 (stamps).

### s004 — LADDER 2 (10.92–16.00, void, whip 0.3 s) — *"climbs into space... and soon passes the Moon"*
- **0030**: ruler punches through the horizontal `SPACE · 100 KM` boundary line; stamp
  `PAST SPACE ✓ 100 km` on "climbs into space" (f416) (white-negative-space contrast pop).
- **0042**: stamp `PAST THE MOON ✓ 384,400 km` + sub-bass landing on "passes the Moon" (f460).
- sfx: clacks at f416/f460.

### s005 — LADDER 3 (16.00–22.20, void, cut) — *"clears the Sun... and passes Voyager One"*
- **0051**: stamp `PAST THE SUN ✓ 149.6 Mkm` (f539).
- **0058**: tiny gray probe glyph `VOYAGER 1 · 25 BILLION KM · FARTHEST THING HUMANS EVER
  BUILT` gets passed — the human-note beat (f569) before everything scales to infinity.
- sfx: clacks at f539/f569.

### s006 — UNIVERSE JUMP (22.20–27.96, void, zoom 0.45 s) — *"grows bigger than the observable universe"*
- **0103**: the ruler bursts off the canvas (boom f779 on "bigger"); `OBSERVABLE UNIVERSE ·
  93,000,000,000 LY` circle collapses to a dot (arp f803); lower card **`...AND 897 FOLDS
  REMAIN`**; then ~1 s of natural narration-gap dead air = the beat drop.
- sfx: `sfx_boom_a` (f779 −7) + `mus_cosmic_drone` bed (f666–839, −20) + `sfx_arp_reveal_down` (f803 −16).

### s007 — REALITY CHECK (27.96–33.46, desk, hard cut) — *"Real paper stopped at twelve"*
- Hard cut back at f839 (debris woosh). Crumpled sheet + tissue roll unrolls with marker
  `GALLIVAN, 2002 · 1,219 M`; card `PHYSICS LIMIT: 12 FOLDS`; her ×4-law curve plots in
  yellow, marker flags at 12/13, tag `×4 PAPER EVERY FOLD`.
- The voice ANSWERS the title's actual question here — twelve folds is what reality allows.
  Quiet, honest, no lore — the trust beat that makes the payoff legal (user-mandated change).
- sfx: `sfx_debris_woosh` (f839 −12) + `mus_dark_amb` bed (f839–1004, −24).

### s008 — PAYOFF (33.46–41.34, void, dip 0.4 s) — *"ten to the power of 281 light-years"*
- Black; **`10^281`** types in yellow digit-by-digit (boom lands on "One thousand folds" f1038),
  waterfall of zeros behind, label `LIGHT-YEARS`; magic shimmer as "281" lands (f1152).
  `UNIVERSE: 93,000,000,000 LY` shrinks to a baseline tick on "nothing in the universe comes
  close"; bar fills `10^270× THE UNIVERSE`.
- The macro loop closes HERE — the hook's withheld answer finally lands.
- sfx: `sfx_boom_b` (f1038 −9) + `sfx_magic_astonish` (f1152 −14) — the loudest pair of the video.

### s009 — ECHO ENDING (41.34–47.37, desk, cut)
- Exact replica of s001 frame 1 — same sheet, same `WHAT IF` card position; counter flashes
  `FOLDS 001` once (double-click f1240); spoken *"One sheet of paper, one thousand folds...
  and the universe comes up short."*; at voice end (f1385 = 46.17 s) the canvas hard-cuts
  to black and holds ~1.2 s (brand QC seal prints there). No end card, no captions after
  the payoff — the replay hands the dare straight back.

## Sound plan (editorial cues — master.json audio; frames voice-locked)

Brand cues come from `brand_pass.py` (entry riser f0, take clacks at seg starts f0/185/839,
QC triplet f1347 on the tail). Editorial cues below are from the GDC Game Audio Bundle 2026
(channel-owned license; exact file picks are already in `library/catalog.json`):

| f | id | file | dB |
|---|----|------|----|
| 7 | sfx_ice_crack_snap | Kopeikin Designed Ice — ice crack snapping-001 | −8 |
| 124/128/133 | stg_tick_clack | brand procedural (7-fold ticks) | −16 |
| 146 | sfx_ui_deny_low | CSD System & UI Feedback — Deny Low Fat Dark | −10 |
| 160 | sfx_ui_accept_glassy | CSD Interface & Infographics — Accept Glassy Snap | −10 |
| 185 | stg_whoosh | brand procedural (desk→skyline reset) | −14 |
| 273/323/416/460/539/569 | stg_tick_clack | brand procedural (stamp falls) | −11 |
| 779 | sfx_boom_a | Federico Soler Trailer Booms 011 | −7 |
| 803 | sfx_arp_reveal_down | CSD System & UI Feedback — Arp Reveal Down Long | −16 |
| 839 | sfx_debris_woosh | CSD Colossal Impacts — Woosh Debris | −12 |
| 1038 | sfx_boom_b | Federico Soler Trailer Booms 075 | −9 |
| 1152 | sfx_magic_astonish | Kopeikin Emotion and Magic — energy flow astonishment | −14 |
| 1240 | sfx_ui_double_click | ESM Board Game — analog double click | −16 |

Music (ducked under voice by the mixer): `mus_cosmic_drone` (Kopeikin — spellbound drone,
f666–839 @ −20), `mus_dark_amb` (CSD Sci-Fi Drones — Dark Industrial Ambience, f839–1004 @ −24).

## Brand mechanics (auto-injected by brand_pass — listed for the board)

- receiptTicker: live frame counter top-left, 0→1421 (the receipts motif).
- takeStamps: 'SHOT 1/3' (f0), 'SHOT 2/3' (f185), 'SHOT 3/3' (f839), each 1.8 s.
- qcSeal: 'QC PASS' yellow seal at f1347 (≈44.9 s, printing through the black tail).
- No endCard by design (echo ending instead) — skill rule: payoff, then stop.

## Notes for Gate 4+ (flags, not blockers)

- Beat timings above are locked to the voice recording; whisper-align then moves them at
  word level (±0.2 s) — cards and cue TYPES don't move.
- The 7 self-folds in s002 run 0–0.5 s into the shot (tick rhythm, no slow-mo lore).
- Caption pass + word timing happen at align; captions are owned by Remotion.
- Width-collapse receipt ('smaller than a bacterium by fold 42') stays in research only —
  the ladder must all escalate upward in size.
