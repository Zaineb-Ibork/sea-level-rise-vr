# Unity project

The Unity project itself is created on your machine (Unity Hub generates a lot of files),
then these scripts are dropped in. Only `Assets/`, `Packages/` and `ProjectSettings/`
are committed; `.gitignore` handles the rest.

## One-time setup

1. Install **Unity Hub** and a **Unity 6 LTS** editor with the **Android Build Support** module (for Quest).
2. In Unity Hub: *New project* → **VR** template (or *3D (URP)*), location = this `unity/` folder.
3. *Window → Package Manager*, install:
   - **XR Interaction Toolkit** (+ import the *Starter Assets* and *XR Device Simulator* samples)
   - **OpenXR Plugin** (Project Settings → XR Plug-in Management → enable OpenXR for PC and Android, add the *Meta Quest* feature group)
   - **TextMeshPro** (usually already there)
   - Optional: **Cesium for Unity** (follow Cesium's install guide; it uses a scoped registry)
4. Copy `data/scenarios.json` to `Assets/StreamingAssets/scenarios.json`.

## Scene recipe (milestone of Phase 1)

1. Add an *XR Origin (XR Rig)* from the Starter Assets; add *XR Device Simulator* to test without a headset.
2. Import `data/processed/town.glb` (drag into `Assets/Models/`). Glb import needs the **glTFast** package.
3. Add a large Plane named `Water`, give it a water material (URP: transparent blue to start; later HDRP Water or a shader).
4. Add `WaterLevelController` to `Water`. Set `verticalOffset` = the z value from `town.glb.offset.json`.
5. Create a world-space Canvas with a `TMP_Dropdown` and a text, add `ScenarioMenu`, wire the references.
6. Press Play: pick a scenario, the water rises.

## Build to Quest

File → Build Profiles → Android → Switch platform → enable *Development Build* → plug in the headset (developer mode on) → *Build And Run*.

## Git notes

Large binaries (`.glb`, `.fbx`, textures) go through **Git LFS** (see `.gitattributes`).
Run `git lfs install` once on your machine before the first commit.
