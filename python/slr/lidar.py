"""LiDAR loading and DEM rasterization for IGN LiDAR HD tiles.

IGN LiDAR HD uses ASPRS classes: 1 unclassified, 2 ground, 3-5 vegetation,
6 building, 9 water, 17 bridge, 64+ IGN-specific. Coordinates are Lambert-93
(EPSG:2154) with NGF-IGN69 heights.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import ndimage

GROUND = 2
BUILDING = 6
WATER = 9


@dataclass
class PointCloud:
    xyz: np.ndarray            # (N, 3) float64
    classification: np.ndarray  # (N,) uint8

    def select(self, classes) -> "PointCloud":
        m = np.isin(self.classification, list(classes))
        return PointCloud(self.xyz[m], self.classification[m])


def load_las(path: str) -> PointCloud:
    """Read a .las/.laz file (laz needs `pip install laspy[lazrs]`)."""
    import laspy

    las = laspy.read(path)
    xyz = np.column_stack([las.x, las.y, las.z]).astype(np.float64)
    return PointCloud(xyz, np.asarray(las.classification, dtype=np.uint8))


@dataclass
class Raster:
    data: np.ndarray   # (rows, cols), row 0 = north
    x0: float          # west edge
    y0: float          # north edge
    res: float         # cell size in metres

    def cell_centers(self):
        rows, cols = self.data.shape
        xs = self.x0 + (np.arange(cols) + 0.5) * self.res
        ys = self.y0 - (np.arange(rows) + 0.5) * self.res
        return np.meshgrid(xs, ys)


def rasterize_min(pc: PointCloud, res: float = 1.0, bounds=None) -> Raster:
    """Grid points, keeping the lowest z per cell (NaN where empty)."""
    x, y, z = pc.xyz.T
    if bounds is None:
        bounds = (x.min(), y.min(), x.max(), y.max())
    xmin, ymin, xmax, ymax = bounds
    cols = int(np.ceil((xmax - xmin) / res)) or 1
    rows = int(np.ceil((ymax - ymin) / res)) or 1
    c = np.clip(((x - xmin) / res).astype(int), 0, cols - 1)
    r = np.clip(((ymax - y) / res).astype(int), 0, rows - 1)
    grid = np.full(rows * cols, np.inf)
    np.minimum.at(grid, r * cols + c, z)
    grid[np.isinf(grid)] = np.nan
    return Raster(grid.reshape(rows, cols), xmin, ymax, res)


def fill_nan_nearest(a: np.ndarray) -> np.ndarray:
    """Fill holes (under buildings, water) with the nearest valid value."""
    mask = np.isnan(a)
    if not mask.any():
        return a.copy()
    if mask.all():
        raise ValueError("raster has no valid cells")
    idx = ndimage.distance_transform_edt(mask, return_distances=False, return_indices=True)
    return a[tuple(idx)]


def build_dtm(pc: PointCloud, res: float = 1.0) -> Raster:
    """Digital terrain model from ground (+ water) points, holes filled."""
    ground = pc.select([GROUND, WATER])
    bounds = (pc.xyz[:, 0].min(), pc.xyz[:, 1].min(), pc.xyz[:, 0].max(), pc.xyz[:, 1].max())
    r = rasterize_min(ground, res, bounds)
    r.data = fill_nan_nearest(r.data)
    return r
