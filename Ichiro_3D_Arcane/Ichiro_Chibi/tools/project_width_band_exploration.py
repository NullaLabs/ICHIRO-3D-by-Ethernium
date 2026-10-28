"""Project an isolated, parameterized width-band hypothesis against all references.

The locked source is duplicated in memory, then compressed along world Y inside
a smooth Z band. The source .blend is never saved or modified.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import project_reference_silhouettes as projector

SOURCE_OBJECT = "ICH_CHIBI_HIGHDETAIL_SOURCE__READONLY"
EXPECTED_VERSION = (5, 2)


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--resolution", type=int, default=384)
    parser.add_argument("--frame-scale", type=float, default=1.12)
    parser.add_argument("--center-from-bottom", type=float, default=0.30,
                        help="vertical band center as a fraction of character height")
    parser.add_argument("--falloff", type=float, default=0.09,
                        help="half-width of the smooth band as a fraction of height")
    parser.add_argument("--strength", type=float, default=0.15,
                        help="maximum proportional squeeze along world Y, 0..0.5")
    args = parser.parse_args(argv)
    if not 64 <= args.resolution <= 2048:
        parser.error("--resolution must be between 64 and 2048")
    if args.frame_scale <= 1 or not math.isfinite(args.frame_scale):
        parser.error("--frame-scale must be finite and greater than 1")
    if not 0 <= args.center_from_bottom <= 1:
        parser.error("--center-from-bottom must be in [0, 1]")
    if not 0 < args.falloff <= 0.5:
        parser.error("--falloff must be in (0, 0.5]")
    if not 0 <= args.strength <= 0.5:
        parser.error("--strength must be in [0, 0.5]")
    return args


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def world_bounds(obj):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    minimum = Vector(tuple(min(v[i] for v in corners) for i in range(3)))
    maximum = Vector(tuple(max(v[i] for v in corners) for i in range(3)))
    return minimum, maximum


def make_candidate(source, minimum, maximum, center_from_bottom, falloff, strength):
    if source.data.shape_keys is not None:
        raise RuntimeError("Width-band exploration does not edit meshes with shape keys")
    candidate = source.copy()
    candidate.data = source.data.copy()
    candidate.name = "ICH_CHIBI_WIDTH_BAND_EXPLORATION__GENERATED"
    candidate.data.name = "ICH_CHIBI_WIDTH_BAND_EXPLORATION_MESH__GENERATED"
    bpy.context.scene.collection.objects.link(candidate)

    height = maximum.z - minimum.z
    band_center_z = minimum.z + height * center_from_bottom
    band_half_width = height * falloff
    center_y = (minimum.y + maximum.y) * 0.5
    inverse_world = candidate.matrix_world.inverted()
    moved_vertices = 0

    for vertex in candidate.data.vertices:
        world = candidate.matrix_world @ vertex.co
        normalized_distance = abs(world.z - band_center_z) / band_half_width
        if normalized_distance >= 1.0:
            continue
        weight = (1.0 - normalized_distance * normalized_distance) ** 2
        local_scale = 1.0 - strength * weight
        world.y = center_y + (world.y - center_y) * local_scale
        vertex.co = inverse_world @ world
        moved_vertices += 1

    candidate.data.update()
    bpy.context.view_layer.update()
    return candidate, band_center_z, band_half_width, moved_vertices


def main():
    if bpy.app.version[:2] != EXPECTED_VERSION:
        raise RuntimeError(f"Expected Blender 5.2.x, got {bpy.app.version_string}")
    if not bpy.data.filepath:
        raise RuntimeError("Open the locked source blend before running the exploration")
    source = bpy.data.objects.get(SOURCE_OBJECT)
    if source is None or source.type != "MESH":
        raise RuntimeError(f"Missing locked source mesh: {SOURCE_OBJECT}")

    args = parse_args()
    output_dir = args.out.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    minimum, maximum = world_bounds(source)
    height = maximum.z - minimum.z
    if height <= 0:
        raise RuntimeError("Source has invalid height")

    candidate, band_center_z, band_half_width, moved_vertices = make_candidate(
        source, minimum, maximum, args.center_from_bottom, args.falloff, args.strength
    )
    depsgraph = bpy.context.evaluated_depsgraph_get()
    tree = BVHTree.FromObject(candidate, depsgraph, epsilon=1e-6)
    if tree is None:
        raise RuntimeError("Could not build BVH for the exploration candidate")

    views = {}
    for name, azimuth_degrees in projector.VIEWS.items():
        angle = math.radians(azimuth_degrees)
        direction = Vector((math.cos(angle), math.sin(angle), 0.0))
        pixels, hits = projector.project_view(
            tree, (minimum + maximum) * 0.5, direction, height,
            args.resolution, args.frame_scale
        )
        if hits <= 0:
            raise RuntimeError(f"Candidate has no hits in {name} view")
        filename = f"candidate_{name}.pgm"
        projector.write_pgm(output_dir / filename, pixels, args.resolution, args.resolution)
        views[name] = {
            "image": filename,
            "camera_azimuth_degrees_about_z": azimuth_degrees,
            "hit_pixels": hits,
            "silhouette_sample_fraction": hits / (args.resolution ** 2),
        }
        print(f"PROJECTED {name}: {hits} hit pixels -> {output_dir / filename}")

    manifest = {
        "schema": "ethernium.width-band-exploration.v1",
        "blender_version": bpy.app.version_string,
        "source_file_name": Path(bpy.data.filepath).name,
        "source_file_sha256": sha256_file(bpy.data.filepath),
        "source_object": SOURCE_OBJECT,
        "candidate_object": candidate.name,
        "candidate_creation": "in-memory duplicate; no blend saved",
        "source_scene_saved": False,
        "source_dimensions_world_m": [float(v) for v in source.dimensions],
        "candidate_dimensions_world_m": [float(v) for v in candidate.dimensions],
        "axes": {"front": "+X", "width": "Y", "up": "+Z"},
        "transform": {
            "type": "smooth symmetric Y squeeze within a normalized height band",
            "center_from_bottom": args.center_from_bottom,
            "band_center_z_world_m": band_center_z,
            "falloff_half_width_fraction": args.falloff,
            "band_half_width_m": band_half_width,
            "maximum_squeeze_fraction": args.strength,
            "weight_curve": "(1 - d^2)^2 for |d| < 1; zero outside",
            "moved_vertex_count": moved_vertices,
        },
        "sample_size_px": [args.resolution, args.resolution],
        "projection": "orthographic CPU BVH ray cast",
        "views": views,
    }
    manifest_path = output_dir / "candidate_projection_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"CANDIDATE_MANIFEST={manifest_path}")
    print("SOURCE_SCENE_SAVED=False")


if __name__ == "__main__":
    main()
