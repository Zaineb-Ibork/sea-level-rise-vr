"""Compute flood masks for every scenario and export them for Unity / web.

    python python/scripts/flood_maps.py data/processed/dtm.npz data/scenarios.json \
        --sea-side south --out data/processed/floods

Outputs per scenario: <name>_<year>.png (RGBA water mask, usable as a texture)
and a summary.json with flooded area and level, read by the apps.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from slr.flood import bathtub_flood, border_seeds, flooded_area_m2  # noqa: E402
from slr.scenarios import load_scenarios, water_level  # noqa: E402


def save_mask_png(mask: np.ndarray, depth: np.ndarray, path: Path):
    from PIL import Image

    rgba = np.zeros((*mask.shape, 4), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = 30, 110, 200
    alpha = np.clip(80 + depth * 120, 0, 230)
    rgba[..., 3] = np.where(mask, alpha, 0).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dtm")
    ap.add_argument("scenarios")
    ap.add_argument("--sea-side", nargs="+", default=["south"], help="raster edge(s) facing the sea")
    ap.add_argument("--out", default="data/processed/floods")
    a = ap.parse_args()

    d = np.load(a.dtm)
    dem, res = d["dem"], float(d["res"])
    base, scen = load_scenarios(a.scenarios)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    seeds = border_seeds(dem, a.sea_side)

    summary = []
    for s in scen:
        lvl = water_level(base, s)
        mask = bathtub_flood(dem, lvl, sea_mask=seeds)
        depth = np.where(mask, lvl - dem, 0)
        name = f"{s.name.replace(' ', '_')}_{s.year}"
        save_mask_png(mask, depth, out / f"{name}.png")
        summary.append({"name": s.name, "year": s.year, "water_level_m": lvl,
                        "flooded_m2": flooded_area_m2(mask, res), "mask": f"{name}.png"})
        print(f"{name:30s} level {lvl:5.2f} m  flooded {summary[-1]['flooded_m2'] / 1e4:8.2f} ha")
    (out / "summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
