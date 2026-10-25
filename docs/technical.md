# Technical documentation (template)

## Pipeline

```
LiDAR HD .laz ──build_dtm.py──▶ dtm.npz ──flood_maps.py──▶ floods/*.png + summary.json ─┐
      │                                                                                 ├─▶ Unity / web
      └──pointcloud_to_mesh.py──▶ town.glb (+ offset.json) ─────────────────────────────┘
```

## Choices to document

- Site, tiles used (names and dates), area covered
- Terrain resolution and hole-filling method
- Baseline water level and its source; vertical datum
- Scenario values and the NASA tool location used
- Mesh: Poisson depth, decimation target, triangle count, measured quality
- Performance on Quest: frame rate, draw calls

## Validation

- Compare flooded areas with an official map (e.g. Géorisques flood zones) where available
- Known limits of the connected bathtub model

## Reproducing

Commands from the README, plus versions (`conda env export > docs/env-lock.yml`).
