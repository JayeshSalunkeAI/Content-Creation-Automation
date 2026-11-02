# 001_paper_fold — Deep Research (Gate 1)

Topic: **"HOW MUCH WILL BE THE HEIGHT OF PAPER FOLD IF WE FOLD IT 1000 TIMES"**

Every number below was re-derived from scratch in `compute_ladder.py` (exact big-integer
math, not copied from any article) and written to `fold_table.json`. Assumption shown on
screen in the video: a standard **80 gsm office paper sheet, thickness t = 0.1 mm**.

## TL;DR (the answer)

- Each fold doubles the stack: **h(n) = 0.1 mm × 2^n**.
- By **fold 23** the stack is past the tallest building on Earth; **42** past the Moon;
  **51** past the Sun; **103** past the observable universe.
- **1000 folds: 0.1 mm × 2^1000 = 1.0715 × 10^297 meters = 1.1326 × 10^281 light-years**
  ≈ **10^270 times wider than the observable universe is** (93 Gly = 8.79e26 m).
- Real paper physically dies at **12 official / 13 unofficial folds** — everything beyond
  is honest math, and the video says so explicitly.

## Sources (external, web-verified today)

| # | Source | Supports |
|---|--------|----------|
| 1 | Scientific American — "How many paper folds would get you to the moon?" (2026-08) https://www.scientificamerican.com/article/how-many-paper-folds-would-get-you-to-the-moon/ | 0.1 mm standard thickness; fold 42 = Moon (fold 41 = 220,000 km ✓ matches our 219,900 km); 51 = Sun (225 Mkm ✓); 69 = Proxima (6 ly ✓); 83 = Milky Way; 88 = Andromeda; 103 = observable universe; width shrinks to a bump at ~42 folds ("smaller than a bacterium"); "half as thick adds only one fold" (thickness robustness) |
| 2 | Gizmodo (2014) "If you fold a paper in half 103 times it'll get as thick as the Universe" https://gizmodo.com/if-you-fold-a-paper-in-half-103-times-it-will-be-as-thi-1607632639 | 103 folds = 93 Gly universe; 23 folds ≈ 1 km; 30 folds = 100 km space; record = 12 (Gallivan) |
| 3 | MathsIsFun — "Doubling Paper" https://www.mathsisfun.com/measure/doubling-paper.html | Full 0–102 fold table for t = 0.1 mm (agrees with ours cell-by-cell); "it is very hard to go beyond the 6th fold, just try it!" — the send trigger |
| 4 | NPR (2011-12-05) "Record Folders: 54,000 Feet Of Paper; 13 Folds" https://www.npr.org/sections/thetwo-way/2011/12/05/143150449/record-folders-54000-feet-of-paper-13-folds-one-new-standard | St. Mark's School 13 folds, 54,000 ft toilet paper, MIT Infinite Corridor (825 ft); MythBusters 11 folds with football-field paper |
| 5 | Gallivan's own page — Pomona Valley Historical Society (archived) https://web.archive.org/web/20051102085038/http://pomonahistorical.org/12times.htm | Britney Gallivan (17 y/o, 2002) folded 1,219 m of tissue 12 times (official record); gold foil 12 first; derived the folding-limit law L = (πt/6)(2^n+4)(2^n−1); the radius/creep section is the real reason folding stops |
| 6 | ZME Science (2015) "If you fold an A4 sheet of paper 103 times..." https://www.zmescience.com/feature-post/natural-sciences/mathematics/folding-a4-paper-103-times-5345/ | Gallivan bio, "each extra fold needs ~4x more paper", energy ramps |
| 7 | Paper thickness x4: BachelorPrint (80 gsm ≈ 100 µm) https://www.bachelorprint.com/printing-guide/printer-paper/paper-weight/paper-thickness/ ; ToolzPlus (Copy 80 GSM = 0.10 mm) https://www.toolzplus.com/everyday-life/paper-thickness-calculator/ ; SF Paper (~100 µm for 20 lb bond) https://www.sfpaper.com/what-is-regular-copy-paper-weight-a-practical-guide-to-gsm-lb-thickness | t = 0.1 mm is the industry-standard copy paper caliper |
| 8 | Earlier research batch (checkpoint notes) | Guinness treats Gallivan's 12 as the official record; St. Mark's 13 is unofficial (taped strips — Gallivan disputed); MythBusters episode 2007 (11 folds) |

## The verified ladder (from `fold_table.json`)

| Fold | Height (computed) | Passes |
|------|-------------------|--------|
| 1 | 0.2 mm | — |
| 5 | 3.2 mm | credit card ≈ fold 3 (0.8 mm) |
| 7 | 12.8 mm | the myth says "stop here" (a 128-page notebook) |
| 10 | 102.4 mm | width of a hand |
| 12 | **40.96 cm** | the official world record's stack height |
| 14 | 1.64 m | taller than the person folding (1.7 m crosses fold 15) |
| 17 | 13.1 m | 4-storey building |
| 20 | 104.9 m | Statue of Liberty with pedestal (93 m) |
| 22 | 419 m | Eiffel Tower (330 m) |
| **23** | **838.9 m** | **Burj Khalifa (828 m)** — tallest building ever built |
| 26 | 6.71 km | jet cruise altitude (~10 km at fold 27) |
| **27** | **13.42 km** | **Everest (8,848.86 m)** |
| **30** | **107.4 km** | **Kármán line (100 km)** — the space boundary |
| **32** | **429.5 km** | **ISS orbit (~408 km)** |
| 38 | 27,488 km | GPS constellation (20,180 km) |
| 39 | 54,976 km | geostationary orbit (35,786 km) |
| **42** | **439,805 km** | **the Moon (384,400 km)** — fold 41 = 219,902 km (SciAm's "220,000") |
| 49 | 56.3 M km | closest-record Earth–Mars distance (54.6 M km, 2003) |
| **51** | **225.2 M km** | **the Sun's distance (1 AU = 149.6 M km)** |
| 53 | 901 Gm | Jupiter (590 Gm at closest) |
| 56 | 7.21 Tm | Neptune (4.30 Tm at closest) |
| **58** | **28.82 B km (192 AU)** | **Voyager 1 (~168 AU ≈ 25.1 B km in 2026)** — farthest human-made object |
| **67** | **1.56 ly** | **1 light-year (9.46e15 m)** |
| **69** | **6.24 ly** | **Proxima Centauri (4.246 ly)** — nearest star |
| **83** | **102,227 ly** | **Milky Way diameter (100,000 ly)** |
| 88 | 3.27 Mly | distance to Andromeda (2.51 Mly) |
| 96 | 837 Mly | Laniakea supercluster span (~520 Mly) |
| **103** | **107.2 Gly (1.0141e27 m)** | **observable universe diameter (93 Gly = 8.79e26 m)** — fold 102 = 53.6 Gly is still inside |

## Reality limits (what actually happens — honesty baseline)

- **Official world record: 12 folds** — Britney Gallivan, 2002, 1,219 m (0.76 mi) of tissue
  paper; ~879 m of paper demanded by her own law at t = 0.1 mm, and she had margin.
- **Unofficial 13** — St. Mark's School (2011), 54,000 ft of taped-together toilet paper in
  MIT's 825-ft Infinite Corridor; disputed (tapes violate single-sheet rules), so the
  script always says "official record: 12".
- **Gallivan's law** — why folding stops: L(n) = (πt/6)(2^n+4)(2^n−1). The folded round
  "radius section" eats length ~4× per fold. Required original length: 879 m @12 folds,
  3.5 km @13, 900 km @17, 57,571 km @20, 943 million km @27 (≈ Jupiter's orbit).
- **Width collapse** — each 2 folds halve each side; at fold 42 width ≈ 0.14 µm (a
  bacterium), fold 37 < 1 µm, fold 97 < proton radius, Planck length at fold 228 (SciAm).
- **Atom bankruptcy** — fold 266 would need 2^266 ≈ 1.2e80 layers > all atoms in the
  observable universe (~1e80). Past fold 266 even imaginary paper can't exist.
- Physical folding difficulty (creases, book-midpoint creep) is the real wall, not strength.

## The 1000-fold answer (made for the payoff)

- Layers: 2^1000 = a **302-digit integer** (exact value in fold_table.json).
- Height: **1.0715 × 10^297 m**.
- In light-years: **1.1326 × 10^281 ly** — a **281-digit number**.
- vs the observable universe: **≈ 1.219 × 10^270 ×** its diameter.

## Send trigger + retell line

- Send trigger: the friend who will immediately try to fold paper at their desk
  (MathsIsFun literally challenges: "just try it!" — everyone can join, everyone fails
  by fold 7). The video physically shows the 7-fold desk attempt as the bridge.
- Retell line (the one sentence): *"Fold a paper 1000 times and it's 10^281 light-years
  tall — the universe itself is only 93 billion."*

## Honesty rules for the script (hard constraints)

1. Any claim past twelve folds is phrased as **math would** / **on paper** — no fake person
   "did" 1000 folds. The 1000-fold ladder is explicitly a thought experiment.
2. Record framing: **"official record: 12"** — never "13" without "unofficial/disputed".
3. t = 0.1 mm appears on screen (label), so the arithmetic is auditable.
4. All numbers in stamps/counter = fold_table.json values to the digit shown.
5. Gallivan gets credit in the receipt line (a girl the crowd's mythology forgot).
