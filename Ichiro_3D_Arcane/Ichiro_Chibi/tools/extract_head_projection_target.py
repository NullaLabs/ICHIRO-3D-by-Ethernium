"""Add a reversible high-detail head projection target to the topology workspace.

This extracts existing disconnected source islands by height.  It is NOT a
retopology, never replaces the final mesh, and starts hidden to avoid z-fight.
"""
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "Ichiro_Chibi_HEAD_HANDS_Topology_Workspace.blend"
OUT = ROOT / "Ichiro_Chibi_HEAD_HANDS_Topology_Workspace.blend"

bpy.ops.wm.open_mainfile(filepath=str(WORKSPACE))
source = next(o for o in bpy.context.scene.objects if o.name.startswith("ICH_CHIBI_HIGHDETAIL_SOURCE"))
mesh = source.data
adj = [[] for _ in mesh.vertices]
for edge in mesh.edges:
    a, b = edge.vertices
    adj[a].append(b); adj[b].append(a)

seen = bytearray(len(mesh.vertices))
component_id = [-1] * len(mesh.vertices)
keep = set()
for start in range(len(mesh.vertices)):
    if seen[start]: continue
    stack, indices = [start], []
    seen[start] = 1
    while stack:
        i = stack.pop(); indices.append(i)
        for j in adj[i]:
            if not seen[j]: seen[j] = 1; stack.append(j)
    center_z = sum((source.matrix_world @ mesh.vertices[i].co).z for i in indices) / len(indices)
    cid = start
    for i in indices: component_id[i] = cid
    # Head + hair + ears + neck transition.  The source is centered at z=0.
    if center_z >= 0.185:
        keep.add(cid)

vertex_map, vertices = {}, []
faces, materials = [], []
for polygon in mesh.polygons:
    if component_id[polygon.vertices[0]] not in keep:
        continue
    new_face = []
    for old in polygon.vertices:
        if old not in vertex_map:
            vertex_map[old] = len(vertices)
            vertices.append(mesh.vertices[old].co.copy())
        new_face.append(vertex_map[old])
    faces.append(new_face)
    materials.append(polygon.material_index)

collection = bpy.data.collections.get("01_DERIVED_PROJECTION_TARGETS")
if collection is None:
    collection = bpy.data.collections.new("01_DERIVED_PROJECTION_TARGETS")
    bpy.context.scene.collection.children.link(collection)
old = bpy.data.objects.get("HEAD_HIGHDETAIL_PROJECTION_TARGET__NOT_FINAL")
if old:
    bpy.data.objects.remove(old, do_unlink=True)
target_mesh = bpy.data.meshes.new("HEAD_HIGHDETAIL_PROJECTION_TARGET_MESH")
target_mesh.from_pydata(vertices, [], faces)
target_mesh.materials.clear()
for material in mesh.materials:
    target_mesh.materials.append(material)
for index, polygon in enumerate(target_mesh.polygons):
    polygon.material_index = materials[index]
target_mesh.update()
target = bpy.data.objects.new("HEAD_HIGHDETAIL_PROJECTION_TARGET__NOT_FINAL", target_mesh)
target.matrix_world = source.matrix_world.copy()
collection.objects.link(target)
target.hide_render = True
target.hide_set(True)
target["role"] = "TEMPORARY_READ_ONLY_SHRINKWRAP_TARGET"
target["scope"] = "Head, hair, ears and upper-neck source islands only"
target["warning"] = "Not clean topology. Do not join, rig, bake or export as final mesh."
collection["purpose"] = "Projection support for manual facial topology only"
collection["source_preserved"] = source.name
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
print(f"head_projection_vertices={len(vertices)} faces={len(faces)}")
