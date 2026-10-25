"""Build a 1 m terrain model from one or more IGN LiDAR HD tiles.

    python python/scripts/build_dtm.py data/raw/*.laz --res 1.0 --out data/processed/dtm.npz
"""
import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from slr.lidar import PointCloud, build_dtm, load_las  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tiles", nargs="+")
    ap.add_argument("--res", type=float, default=1.0)
    ap.add_argument("--out", default="data/processed/dtm.npz")
    a = ap.parse_args()

    clouds = [load_las(t) for t in a.tiles]
    pc = PointCloud(np.vstack([c.xyz for c in clouds]), np.concatenate([c.classification for c in clouds]))
    print(f"{len(pc.xyz):,} points, classes: {sorted(set(pc.classification.tolist()))}")
    dtm = build_dtm(pc, a.res)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, dem=dtm.data, x0=dtm.x0, y0=dtm.y0, res=dtm.res)
    print(f"DTM {dtm.data.shape} saved to {a.out}  (z {np.nanmin(dtm.data):.2f}..{np.nanmax(dtm.data):.2f} m)")


if __name__ == "__main__":
    main()
