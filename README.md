# Sea-Level Rise VR

Visualize sea-level rise in a real Mediterranean or Normandy town, in a VR headset (Meta Quest) and in a web browser, from IGN LiDAR HD data and IPCC AR6 scenarios.

> **Coming soon.** Starter code and tests are here; demo, results and video are on the way. Project page: [zaineb-ibork.github.io/sea-level-rise-vr/](https://zaineb-ibork.github.io/sea-level-rise-vr/)

<!-- Replace with a GIF of the app once you have one: docs/media/demo.gif -->

## What it does

1. Turns IGN LiDAR HD point clouds into a terrain model and a lightweight 3D mesh of the town.
2. Computes, for each IPCC scenario, which streets flood using a **connected bathtub model** (inland basins not connected to the sea stay dry).
3. Lets the user stand in the street in VR, or explore in the browser, and raise the water scenario by scenario.

## Repository layout

```
python/slr/          library: LiDAR loading, terrain model, flood model, scenarios
python/scripts/      command-line steps of the pipeline
unity/               Unity scripts + setup guide (VR app for Quest)
web/                 three.js + WebXR viewer (no build step)
data/                scenarios file; raw/processed data are NOT committed
docs/                user guide and technical documentation
tests/               pytest tests on synthetic data
```

## Quick start

```bash
conda env create -f environment.yml
conda activate slr-vr
pytest                                   # all tests should pass

# 1. Download 1-4 LiDAR HD tiles of your town into data/raw/ (see data/README.md)
python python/scripts/build_dtm.py data/raw/*.laz --res 1.0
cp data/scenarios.example.json data/scenarios.json   # then put real NASA values in it
python python/scripts/flood_maps.py data/processed/dtm.npz data/scenarios.json --sea-side south
python python/scripts/pointcloud_to_mesh.py data/raw/<tile>.laz --out data/processed/town.glb

# 2. Web viewer
cp data/processed/town.glb* data/scenarios.json web/
python -m http.server -d web 8000         # open http://localhost:8000
```

Then follow `unity/README.md` for the VR app.

## Roadmap

- [ ] **VR basics:** Unity + XR Interaction Toolkit; scene where you walk and raise a water plane
- [ ] **Geodata:** LiDAR tile → clean terrain + town mesh in Unity (`build_dtm.py`, `pointcloud_to_mesh.py`)
- [ ] **Flood + realism:** connected flood masks per scenario (`flood_maps.py`), water shader, real IPCC values
- [ ] **Multi-platform:** web viewer with WebXR, one 360° street scene
- [ ] **Alongside:** user guide (`docs/user-guide.md`), technical doc (`docs/technical.md`), test with non-specialists

## Skills demonstrated

Unity · C# · XR Interaction Toolkit · OpenXR · Meta Quest · LiDAR (PDAL, laspy, Open3D) · GIS (Lambert-93, terrain models) · flood modelling · three.js / WebXR · scientific outreach

## Data and credits

- LiDAR: IGN LiDAR HD, Licence Ouverte Etalab 2.0
- Sea-level projections: IPCC AR6 via the NASA Sea Level Projection Tool

## Limitations

Static flood model: no tides, waves, storm dynamics or coastal defences unless added to the water level. Results are illustrative, for awareness, not for planning decisions.

## Author

Zaineb Ibork, PhD in Computer Science (3D vision and AI). License: MIT.
