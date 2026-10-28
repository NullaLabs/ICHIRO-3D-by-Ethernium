"""Render a non-destructive, material-colored map of disconnected source islands.

Run with Blender 5.2 and the topology workspace open as the input blend. The
locked source object is never edited; only an in-memory duplicate receives
component colors. The script writes diagnostic renders and a JSON manifest,
never a blend file.
"""
import argparse
import colorsys
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector
sys.path.insert(0, str(Path(__file__).resolve().parent))
from component_islands import audit_components, find_root


ROOT = Path(__file__).resolve().parents[1]
SOURCE_OBJECT = "ICH_CHIBI_HIGHDETAIL_SOURCE__READONLY"
EXPECTED_BLENDER = (5, 2)


def arguments():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "renders" / "component_map_review_v01")
    parser.add_argument("--resolution", type=int, default=768)
    parser.add_argument("--frame-scale", type=float, default=1.12)
    args = parser.parse_args(argv)
    if not 256 <= args.resolution <= 2048:
        parser.error("--resolution must be between 256 and 2048")
    if not math.isfinite(args.frame_scale) or args.frame_scale < 1.01:
        parser.error("--frame-scale must be finite and at least 1.01")
    return args


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def set_if_available(owner, name, value):
    if hasattr(owner, name):
        setattr(owner, name, value)


def main():
    if bpy.app.version[:2] != EXPECTED_BLENDER:
        raise RuntimeError(f"Expected Blender 5.2.x, got {bpy.app.version_string}")
    if not bpy.data.filepath:
        raise RuntimeError("Open the head/hands topology workspace before running this review")

    args = arguments()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=True)
    source = bpy.data.objects.get(SOURCE_OBJECT)
    if source is None or source.type != "MESH":
        raise RuntimeError(f"Missing locked source object: {SOURCE_OBJECT}")

    parent, root_to_id, ordered_roots, counts, bounds, face_counts = audit_components(source.data)
    duplicate = source.copy()
    duplicate.data = source.data.copy()
    duplicate.name = "ICH_CHIBI_COMPONENT_MAP__DIAGNOSTIC_ONLY"
    duplicate.data.name = "ICH_CHIBI_COMPONENT_MAP_MESH__DIAGNOSTIC_ONLY"
    bpy.context.scene.collection.objects.link(duplicate)
    duplicate.hide_render = False
    duplicate.hide_set(False)

    duplicate.data.materials.clear()
    components = []
    for component_id, root in enumerate(ordered_roots):
        hue = (component_id * 0.6180339887498949) % 1.0
        rgb = colorsys.hsv_to_rgb(hue, 0.78, 0.96)
        material = bpy.data.materials.new(f"COMPONENT_MAP_{component_id:03d}")
        material.diffuse_color = (*rgb, 1.0)
        duplicate.data.materials.append(material)
        box = bounds[root]
        components.append({
            "component_id": component_id,
            "stable_root_vertex_index": int(root),
            "vertex_count": int(counts[root]),
            "face_count": int(face_counts[component_id]),
            "display_rgb": [round(float(value), 6) for value in rgb],
            "bounds_local_m": [[round(float(box[i]), 7), round(float(box[i + 3]), 7)] for i in range(3)],
            "center_local_m": [round(float((box[i] + box[i + 3]) * 0.5), 7) for i in range(3)],
            "role": "unclassified; inspect against all source views",
        })

    for polygon in duplicate.data.polygons:
        polygon.material_index = root_to_id[find_root(parent, polygon.vertices[0])]

    source.hide_render = True
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = args.resolution
    scene.render.resolution_y = args.resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    shading = scene.display.shading
    shading.light = "FLAT"
    shading.color_type = "MATERIAL"
    shading.background_type = "WORLD"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("COMPONENT_MAP_WORLD")
    scene.world.color = (0.12, 0.12, 0.12)
    set_if_available(shading, "show_shadows", False)
    set_if_available(shading, "show_cavity", False)
    set_if_available(shading, "show_specular_highlight", False)
    set_if_available(shading, "show_outline", False)

    camera_data = bpy.data.cameras.new("COMPONENT_MAP_ORTHO_CAMERA")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = args.frame_scale
    camera = bpy.data.objects.new("COMPONENT_MAP_ORTHO_CAMERA", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera

    world_corners = [source.matrix_world @ Vector(corner) for corner in source.bound_box]
    minimum = Vector(tuple(min(point[axis] for point in world_corners) for axis in range(3)))
    maximum = Vector(tuple(max(point[axis] for point in world_corners) for axis in range(3)))
    center = (minimum + maximum) * 0.5
    distance = max((maximum - minimum).length * 3.0, 2.0)
    views = {
        "front_plus_x": Vector((1.0, 0.0, 0.0)),
        "back_minus_x": Vector((-1.0, 0.0, 0.0)),
        "side_plus_y": Vector((0.0, 1.0, 0.0)),
        "side_minus_y": Vector((0.0, -1.0, 0.0)),
        "three_quarter": Vector((1.0, -1.0, 0.12)).normalized(),
    }
    render_records = {}
    for name, direction in views.items():
        camera.location = center + direction * distance
        camera.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(output / f"{name}.png")
        bpy.ops.render.render(write_still=True)
        render_records[name] = {
            "image": f"{name}.png",
            "camera_direction_from_target": [round(float(value), 6) for value in direction],
            "projection": "orthographic",
        }
        print(f"RENDERED {name}: {scene.render.filepath}")

    source_path = Path(bpy.data.filepath)
    manifest = {
        "schema": "ethernium.ichiro-component-map.v1",
        "blender_version": bpy.app.version_string,
        "source_file": source_path.name,
        "source_file_sha256": sha256_file(source_path),
        "source_object": SOURCE_OBJECT,
        "diagnostic_object": duplicate.name,
        "component_count": len(components),
        "vertex_count": len(source.data.vertices),
        "edge_count": len(source.data.edges),
        "face_count": len(source.data.polygons),
        "source_material_count": len(source.data.materials),
        "method": "union-find over source mesh edges; deterministic component ordering by descending vertex count then root index",
        "component_colors": "diagnostic palette only; no anatomical roles inferred",
        "views": render_records,
        "components": components,
        "source_scene_saved": False,
        "limitations": [
            "Disconnected islands are geometric groups, not verified anatomical labels.",
            "The map does not distinguish skin from hair or painted eye regions within one connected island.",
            "The diagnostic copy replaces the source material with flat component colors.",
            "No retopology, sculpt, texture, rig, or source geometry is modified.",
        ],
    }
    manifest_path = output / "component_map_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"COMPONENT_COUNT={len(components)}")
    print(f"MANIFEST={manifest_path}")
    print("SOURCE_SCENE_SAVED=False")


if __name__ == "__main__":
    main()
