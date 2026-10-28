"""Project the locked source into eight CPU-only orthographic silhouette masks.

This avoids EEVEE/OpenGL and never edits or saves the source scene. Each image
pixel casts one ray against a BVH built from the source mesh; any hit marks that
pixel as character silhouette. A PGM mask is used so Blender needs no imaging
dependency.

Run Blender 5.2 in background with Ichiro_Chibi_HighDetail_Working.blend loaded.
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

EXPECTED_VERSION = (5, 2)
SOURCE_OBJECT = "ICH_CHIBI_HIGHDETAIL_SOURCE__READONLY"
VIEWS = {
    # Camera azimuth around +Z. Front is from +X; positive angles move toward +Y.
    "front": 0,
    "front_left": 45,
    "left": 90,
    "left_back": 135,
    "back": 180,
    "back_right": 225,
    "right": 270,
    "front_right": 315,
}


def options_from_argv():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--resolution", type=int, default=384)
    parser.add_argument("--views", nargs="+", choices=tuple(VIEWS), default=list(VIEWS))
    parser.add_argument("--frame-scale", type=float, default=1.12,
                        help="Orthographic view height as a multiple of source height")
    args = parser.parse_args(argv)
    if not 64 <= args.resolution <= 2048:
        parser.error("--resolution must be between 64 and 2048")
    if not math.isfinite(args.frame_scale) or args.frame_scale <= 1.0:
        parser.error("--frame-scale must be finite and greater than 1")
    return args


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_pgm(path, pixels, width, height):
    with Path(path).open("wb") as stream:
        stream.write(f"P5\n{width} {height}\n255\n".encode("ascii"))
        stream.write(pixels)


def project_view(tree, center, camera_direction, height, resolution, frame_scale):
    direction = camera_direction.normalized()
    ray_direction = -direction
    world_up = Vector((0, 0, 1))
    screen_right = ray_direction.cross(world_up).normalized()
    screen_up = screen_right.cross(ray_direction).normalized()
    field_height = height * frame_scale
    pixel_step = field_height / resolution
    camera_origin = center + direction * (height * 4.0)
    ray_length = height * 8.0
    pixels = bytearray(resolution * resolution)
    hits = 0

    # Pixel centers are sampled in image order (top row first).
    for py in range(resolution):
        dy = (resolution * 0.5 - py - 0.5) * pixel_step
        row = py * resolution
        for px in range(resolution):
            dx = (px + 0.5 - resolution * 0.5) * pixel_step
            origin = camera_origin + screen_right * dx + screen_up * dy
            location, _normal, _face_index, _distance = tree.ray_cast(
                origin, ray_direction, ray_length
            )
            if location is not None:
                pixels[row + px] = 255
                hits += 1
    return bytes(pixels), hits


def main():
    if bpy.app.version[:2] != EXPECTED_VERSION:
        raise RuntimeError(
            f"Expected Blender {EXPECTED_VERSION[0]}.{EXPECTED_VERSION[1]}.x; "
            f"found {bpy.app.version_string}"
        )
    source = bpy.data.objects.get(SOURCE_OBJECT)
    if source is None or source.type != "MESH":
        raise RuntimeError(f"Missing mesh object: {SOURCE_OBJECT}")
    if not bpy.data.filepath:
        raise RuntimeError("Open the locked .blend before running this script")
    args = options_from_argv()
    output_dir = args.out.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    bounds = [source.matrix_world @ Vector(corner) for corner in source.bound_box]
    minimum = Vector(tuple(min(v[i] for v in bounds) for i in range(3)))
    maximum = Vector(tuple(max(v[i] for v in bounds) for i in range(3)))
    center = (minimum + maximum) * 0.5
    height = maximum.z - minimum.z
    if not math.isfinite(height) or height <= 0:
        raise RuntimeError(f"Invalid source height: {height}")

    depsgraph = bpy.context.evaluated_depsgraph_get()
    tree = BVHTree.FromObject(source, depsgraph, epsilon=1e-6)
    if tree is None:
        raise RuntimeError("Could not build a BVH for the source mesh")

    rendered_views = {}
    for name in args.views:
        angle = math.radians(VIEWS[name])
        camera_direction = Vector((math.cos(angle), math.sin(angle), 0.0))
        pixels, hits = project_view(tree, center, camera_direction, height,
                                    args.resolution, args.frame_scale)
        if hits == 0:
            raise RuntimeError(f"No BVH hits in {name} view; check axis and source")
        filename = f"source_{name}.pgm"
        write_pgm(output_dir / filename, pixels, args.resolution, args.resolution)
        rendered_views[name] = {
            "image": filename,
            "camera_azimuth_degrees_about_z": VIEWS[name],
            "camera_direction_world": [float(v) for v in camera_direction],
            "projection": "orthographic CPU BVH ray cast",
            "sample_size_px": [args.resolution, args.resolution],
            "frame_height_m": height * args.frame_scale,
            "hit_pixels": hits,
            "silhouette_sample_fraction": hits / (args.resolution ** 2),
        }
        print(f"PROJECTED {name}: {hits} hit pixels -> {output_dir / filename}")

    report = {
        "schema": "ethernium.reference-fit-renders.v2",
        "blender_version": bpy.app.version_string,
        "source_file_name": Path(bpy.data.filepath).name,
        "source_file_sha256": sha256_file(bpy.data.filepath),
        "source_object": SOURCE_OBJECT,
        "source_dimensions_world_m": [float(v) for v in source.dimensions],
        "source_bounds_world_m": {"min": list(minimum), "max": list(maximum)},
        "source_mesh_counts": {
            "vertices": len(source.data.vertices),
            "edges": len(source.data.edges),
            "polygons": len(source.data.polygons),
        },
        "axes": {"front": "+X", "left_profile_camera": "+Y", "right_profile_camera": "-Y", "up": "+Z"},
        "method": "BVHTree.FromObject + orthographic ray mask; no render engine or addon",
        "source_scene_saved": False,
        "requested_views": args.views,
        "views": rendered_views,
    }
    report_path = output_dir / "projection_manifest.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"REFERENCE_FIT_MANIFEST={report_path}")
    print("SOURCE_SCENE_SAVED=False")


if __name__ == "__main__":
    main()
