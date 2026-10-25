"""Point cloud -> lightweight mesh for VR (Open3D Poisson + decimation).

    python python/scripts/pointcloud_to_mesh.py data/raw/tile.laz \
        --classes 2 6 --depth 10 --faces 200000 --out data/processed/town.glb

Tips (where your mesh-quality expertise pays off):
- Re-centre coordinates: Lambert-93 values (~10^6 m) break float32 precision
  in Unity. The script subtracts the centroid and writes it to <out>.offset.json.
- Crop low-density Poisson surfaces (--density-quantile) to remove "bubbles".
- Aim for < 500k triangles on Quest standalone; check with your quality metrics.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from slr.lidar import load_las  # noqa: E402


def main():
    import open3d as o3d

    ap = argparse.ArgumentParser()
    ap.add_argument("tile")
    ap.add_argument("--classes", type=int, nargs="+", default=[2, 6])
    ap.add_argument("--voxel", type=float, default=0.25)
    ap.add_argument("--depth", type=int, default=10)
    ap.add_argument("--density-quantile", type=float, default=0.02)
    ap.add_argument("--faces", type=int, default=200_000)
    ap.add_argument("--out", default="data/processed/town.glb")
    a = ap.parse_args()

    pc = load_las(a.tile).select(a.classes)
    offset = pc.xyz.mean(axis=0)
    pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(pc.xyz - offset))
    pcd = pcd.voxel_down_sample(a.voxel)
    pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
    pcd.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=1.0, max_nn=30))
    pcd.orient_normals_towards_camera_location(np.array([0, 0, 1000.0]))

    mesh, dens = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=a.depth)
    dens = np.asarray(dens)
    mesh.remove_vertices_by_mask(dens < np.quantile(dens, a.density_quantile))
    mesh = mesh.simplify_quadric_decimation(a.faces)
    mesh.remove_degenerate_triangles()
    mesh.remove_unreferenced_vertices()
    mesh.compute_vertex_normals()

    # glTF is Y-up and right-handed: (east, north, up) -> (x east, y up, z south).
    # A rotation, not an axis swap, so the town is not mirrored and normals stay outward;
    # three.js and Unity's glTF importers handle their own conversion from there.
    v = np.asarray(mesh.vertices)
    mesh.vertices = o3d.utility.Vector3dVector(np.column_stack([v[:, 0], v[:, 2], -v[:, 1]]))

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    o3d.io.write_triangle_mesh(a.out, mesh)
    Path(a.out + ".offset.json").write_text(json.dumps({"offset_l93": offset.tolist()}))
    print(f"{len(mesh.triangles):,} triangles -> {a.out}")


if __name__ == "__main__":
    main()
