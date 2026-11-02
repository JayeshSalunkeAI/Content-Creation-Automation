"""001_paper_fold deep research: fold -> height ladder, computationally verified.

Assumption: standard office copy paper, 80 gsm, thickness ~0.1 mm = 100 microns.
Sources: SciAm 2026 (0.1 mm; ladder), BachelorPrint/industry calipers (100 um typical).
Each fold doubles thickness: h(n) = t * 2^n.

Outputs:
  - console verification report
  - fold_table.json (milestones, selected folds, Gallivan law, final 1000-fold number)
"""
import json
import math
from pathlib import Path

T = 0.0001  # m, 80 gsm copy paper (~100 um)
LY = 9.4607e15  # m / light-year
OUT = Path(__file__).with_name("fold_table.json")

def h(n: float) -> float:
    """Stack height after n folds, meters (float ok; safe to 1.79e308)."""
    return T * 2.0 ** n

def layers(n: float) -> float:
    return 2.0 ** n

def crossing_fold(meters: float) -> int:
    """Smallest n with t*2^n >= meters, verified exactly."""
    n = math.ceil(math.log2(meters / T))
    # verify with exact ints (t Trev: use integer microns)
    microns_target = meters * 1e6
    while 2 ** n * 100 < microns_target:
        n += 1
    while n > 0 and 2 ** (n - 1) * 100 >= microns_target:
        n -= 1
    return n

MILESTONES = [
    ("Credit card thickness",            0.0008,             "t*8 -> fold 3 stack"),
    ("Human height",                     1.70,               "taller than the folder"),
    ("Statue of Liberty (w/ pedestal)",  93.0,               ""),
    ("Eiffel Tower",                     330.0,              ""),
    ("Burj Khalifa",                     828.0,              "tallest building on Earth"),
    ("Everest",                          8848.86,            "highest mountain"),
    ("Kármán line (space boundary)",     100000.0,           "internationally agreed 100 km"),
    ("ISS orbit",                        408000.0,           "average ISS altitude"),
    ("Geostationary orbit",              35786000.0,         "GPS 20180 km crosses fold 38"),
    ("The Moon (mean distance)",         384400000.0,        "Earth-Moon"),
    ("Mars (closest approach)",          5.46e10,            "min Earth-Mars distance"),
    ("The Sun (1 AU)",                   1.495978707e11,     "Earth-Sun mean"),
    ("Jupiter (closest)",                5.896e11,           ""),
    ("Neptune (closest)",                4.298e12,           ""),
    ("Voyager 1 (Nov 2026 ~168 AU)",     168 * 1.495978707e11, "farthest human-made object"),
    ("1 light-year",                     LY,                 ""),
    ("Proxima Centauri",                 4.246 * LY,         "nearest star: 6.24 ly at fold 69"),
    ("Distance to Andromeda",            2.51e6 * LY,        "nearest big galaxy"),
    ("Milky Way diameter",               9.4607e20,          "= 100,000 ly (SciAm ladder -> fold 83); a 1.0e21 m round-up crosses fold 84"),
    ("Laniakea supercluster span",       520e6 * LY,         "largest known structure ~520 Mly"),
    ("Observable universe diameter",     8.79e26,            "93 billion ly"),
]

print("=" * 96)
print("FOLD -> HEIGHT LADDER (t = 0.1 mm). 'fold n' = first fold whose stack PASSES the object.")
print("=" * 96)

rows = []
for name, meters, note in MILESTONES:
    n = crossing_fold(meters)
    hit = h(n)
    prev = h(n - 1)
    pretty_hit = f"{hit:,.3g} m"
    rows.append({"object": name, "meters": meters, "fold": n,
                 "height_at_fold_m": hit, "height_next_below_m": prev, "note": note})
    cross_v = "" if hit >= meters else "  <-- FAIL exact check"
    print(f"fold {n:>3} | {name:<34} (>={meters:>13.6g} m)  hit {pretty_hit:>12}  "
          f"(below: {prev:,.3g} m){cross_v}")

sel = [1, 5, 7, 10, 12, 14, 17, 20, 23, 26, 27, 30, 32, 38, 39, 41, 42, 49, 51, 58, 67, 69, 83, 88, 96, 103]
print("\nSELECTED FOLDS:")
selected = []
for n in sel:
    meters = 2 ** n * 100 / 1e6  # exact int math: microns -> m
    selected.append({"fold": n, "height_m": meters})
    print(f"  fold {n:>3}: {meters:42e} m  = {meters / 1000:38,.4g} km   = {meters / LY:36,.10g} ly")

print("\nGALLIVAN'S LAW: min paper length L = (pi*t/6) * (2^n + 4) * (2^n - 1)  [single-direction folds]")
gallivan = []
for n in (12, 13, 14, 17, 20, 27):
    L = math.pi * T / 6 * (2 ** n + 4) * (2 ** n - 1)
    gallivan.append({"fold": n, "min_length_m": L})
    print(f"  n={n:>2}: L = {L:28,.0f} m   ({L/1000:12,.4g} km)")

print("\nWIDTH SHRINK (alternating-direction halving, W0 = 297 mm A4):")
PI_planck = 1.616e-35
PROTON = 8.4e-16
W0 = 0.297
width_rows = []
for label, target in (("bacterium (1 um)", 1e-6), ("proton radius", PROTON), ("Planck length", PI_planck)):
    half_folds = math.log2(W0 / target)
    n = math.ceil(2 * half_folds)
    w = W0 / 2 ** (n / 2)
    width_rows.append({"target": label, "fold": n, "width_m": w})
    print(f"  width < {label:<22} at fold {n:>3}  (w = {w:.3g} m)")

print("\nFINAL: 1000 FOLDS")
layers1000 = 2 ** 1000             # exact big int
height1000_m = layers1000 * 100 / 1e6
height1000_ly = height1000_m / LY
universe_diam = 8.79e26
ratio = height1000_m / universe_diam
atoms = 1e80
print(f"  layers            = 2^1000 = {layers1000}")
print(f"  height            = {height1000_m:.6e} m")
print(f"  in light-years    = {height1000_ly:.6e} ly")
print(f"  / universe diam   = {ratio:.6e} x")
print(f"  layers vs atoms   = {layers1000 / atoms:.4e} x (layer-count >= 1e80 universe atoms when 2^n >= 1e80)")
n_atoms = math.ceil(math.log2(atoms))
while 2 ** n_atoms < atoms:
    n_atoms += 1
print(f"  exact: layer count exceeds 1e80 (atoms in universe) at fold {n_atoms}")

data = {
    "assumptions": {
        "thickness_m": T,
        "thickness_source": "80 gsm standard copy paper ~= 100 um (Science American 2026; paper industry caliper)",
        "light_year_m": LY,
        "observable_universe_diameter_m": universe_diam,
        "formula": "h(n) = t * 2^n",
    },
    "milestones": rows,
    "selected_folds": selected,
    "gallivan_min_length_law": gallivan,
    "width_shrink": width_rows,
    "final_1000": {
        "layers": str(layers1000),
        "height_m": str(height1000_m),
        "height_light_years": str(height1000_ly),
        "ratio_times_observable_universe_diameter": str(ratio),
        "atoms_crossing_fold": n_atoms,
    },
}
OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False))
print(f"\nwritten: {OUT}")
