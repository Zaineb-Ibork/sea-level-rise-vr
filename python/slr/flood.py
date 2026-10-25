"""Connected "bathtub" flood model.

A cell floods when its elevation is below the water level AND it is
hydraulically connected to the sea. Low inland basins that are not connected
stay dry, which is the main correction over a naive threshold.

This is a static first-order model: no dynamics, defences, tides or surge
unless you add them to `water_level`. State this limit in the app.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

_STRUCT = {4: ndimage.generate_binary_structure(2, 1), 8: ndimage.generate_binary_structure(2, 2)}


def border_seeds(dem: np.ndarray, sides=("north", "south", "east", "west")) -> np.ndarray:
    """Seed mask on the chosen raster edges (use the edge(s) facing the sea)."""
    seed = np.zeros(dem.shape, bool)
    if "north" in sides:
        seed[0, :] = True
    if "south" in sides:
        seed[-1, :] = True
    if "west" in sides:
        seed[:, 0] = True
    if "east" in sides:
        seed[:, -1] = True
    return seed


def bathtub_flood(dem: np.ndarray, water_level: float, sea_mask: np.ndarray | None = None,
                  connectivity: int = 8) -> np.ndarray:
    """Boolean flood mask for a given water level (same vertical datum as dem).

    sea_mask: cells known to be sea (e.g. class 9 water points or a coastline
    polygon). Defaults to all raster edges.
    """
    below = dem < water_level
    seeds = (sea_mask if sea_mask is not None else border_seeds(dem)) & below
    labels, _ = ndimage.label(below, structure=_STRUCT[connectivity])
    connected = np.unique(labels[seeds])
    connected = connected[connected > 0]
    return np.isin(labels, connected)


def flood_depth(dem: np.ndarray, water_level: float, **kw) -> np.ndarray:
    """Water depth in metres (0 where dry)."""
    mask = bathtub_flood(dem, water_level, **kw)
    return np.where(mask, water_level - dem, 0.0)


def flooded_area_m2(mask: np.ndarray, res: float) -> float:
    return float(mask.sum()) * res * res
