# Data

Raw and processed data are **not committed** (too large; see `.gitignore`). Each user downloads them.

## Where to get it

| Data | Source | Notes |
| --- | --- | --- |
| LiDAR point clouds | IGN LiDAR HD: https://geoservices.ign.fr/lidarhd | Classified .laz tiles, 1 km × 1 km, Lambert-93 (EPSG:2154) |
| Terrain model (alternative) | IGN RGE ALTI / LiDAR HD MNT on geoservices.ign.fr | Use if you only need the ground |
| Sea-level projections | NASA IPCC AR6 Sea Level Projection Tool: https://sealevel.nasa.gov/ipcc-ar6-sea-level-projection-tool | Pick the tide gauge nearest your site (e.g. Toulon for Hyères) |

## Folders

```
data/raw/         downloaded .laz tiles
data/processed/   dtm.npz, floods/, town.glb  (generated)
data/scenarios.json   your real scenario values (copy from scenarios.example.json)
```

## Vertical datum

LiDAR HD heights are in NGF-IGN69. NASA projections are *changes* in sea level, so add them to a baseline water level in the same datum (for example local mean high water from SHOM). Write down which baseline you used in `docs/technical.md`.
