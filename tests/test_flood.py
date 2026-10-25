import json

import numpy as np

from slr.flood import bathtub_flood, border_seeds, flood_depth
from slr.lidar import GROUND, BUILDING, PointCloud, build_dtm, fill_nan_nearest, rasterize_min
from slr.scenarios import load_scenarios, water_level


def coastal_dem():
    """Slope rising from the sea (south, row -1) to the north, with an inland basin."""
    rows, cols = 50, 40
    dem = np.tile(np.linspace(5.0, 0.0, rows)[:, None], (1, cols))
    dem[10:15, 10:15] = -1.0          # isolated inland depression, below sea level
    return dem


def test_disconnected_basin_stays_dry():
    dem = coastal_dem()
    mask = bathtub_flood(dem, 1.0, sea_mask=border_seeds(dem, ["south"]))
    assert mask[-1].all()                 # coast floods
    assert not mask[10:15, 10:15].any()   # basin is not connected
    assert not mask[0].any()              # high ground dry


def test_flood_grows_with_level():
    dem = coastal_dem()
    seeds = border_seeds(dem, ["south"])
    areas = [bathtub_flood(dem, h, sea_mask=seeds).sum() for h in (0.5, 1.0, 2.0, 3.0)]
    assert areas == sorted(areas) and areas[0] < areas[-1]


def test_depth_positive_only_where_flooded():
    dem = coastal_dem()
    d = flood_depth(dem, 1.0, sea_mask=border_seeds(dem, ["south"]))
    assert (d >= 0).all() and d.max() <= 1.0 + 1e-9


def test_rasterize_and_fill():
    xyz = np.array([[0.2, 0.2, 5.0], [0.3, 0.3, 3.0], [2.5, 2.5, 7.0], [2.6, 0.1, 1.0]])
    r = rasterize_min(PointCloud(xyz, np.full(4, GROUND, np.uint8)), res=1.0)
    assert r.data.shape == (3, 3)
    assert r.data[2, 0] == 3.0           # min z kept, south-west cell
    assert np.isnan(r.data).any()
    filled = fill_nan_nearest(r.data)
    assert not np.isnan(filled).any()


def test_build_dtm_ignores_buildings():
    rng = np.random.default_rng(0)
    g = np.column_stack([rng.uniform(0, 20, 2000), rng.uniform(0, 20, 2000), np.zeros(2000)])
    b = np.column_stack([rng.uniform(5, 10, 300), rng.uniform(5, 10, 300), np.full(300, 12.0)])
    pc = PointCloud(np.vstack([g, b]), np.r_[np.full(2000, GROUND), np.full(300, BUILDING)].astype(np.uint8))
    dtm = build_dtm(pc, 1.0)
    assert np.nanmax(dtm.data) < 1.0


def test_scenarios_example(tmp_path):
    from pathlib import Path
    src = Path(__file__).resolve().parents[1] / "data" / "scenarios.example.json"
    base, scen = load_scenarios(str(src))
    assert len(scen) >= 2
    assert water_level(base, scen[1]) > base
