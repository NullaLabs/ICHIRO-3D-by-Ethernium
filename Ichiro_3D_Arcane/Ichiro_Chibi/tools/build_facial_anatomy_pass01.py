"""Create non-destructive, riggable eye anatomy aligned to the locked face.

The result is a topology-pass aid only.  The final delivery will join approved
components into one mesh object after eyelid/mouth retopology is complete.
"""
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "Ichiro_Chibi_HEAD_HANDS_Topology_Workspace.blend"
bpy.ops.wm.open_mainfile(filepath=str(WORKSPACE))

source = next(o for o in bpy.context.scene.objects if o.name.startswith("ICH_CHIBI_HIGHDETAIL_SOURCE"))
world_vertices = [source.matrix_world @ v.co for v in source.data.vertices]
polygons = [tuple(poly.vertices) for poly in source.data.polygons]
bvh = BVHTree.FromPolygons(world_vertices, polygons, all_triangles=False)

collection = bpy.data.collections.get("20_FACIAL_ANATOMY_COMPONENTS__PASS01")
if collection is None:
    collection = bpy.data.collections.new("20_FACIAL_ANATOMY_COMPONENTS__PASS01")
    bpy.context.scene.collection.children.link(collection)
for obj in list(collection.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

def material(name, color, metallic=0.0, roughness=0.4):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    node = mat.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value = (*color, 1.0)
    node.inputs['Roughness'].default_value = roughness
    node.inputs['Metallic'].default_value = metallic
    return mat

sclera = material("PASS01_Eye_Sclera", (0.09, 0.075, 0.065), roughness=0.25)
iris = material("PASS01_Eye_Iris_Red", (0.55, 0.012, 0.018), roughness=0.2)
pupil = material("PASS01_Eye_Pupil", (0.004, 0.002, 0.002), roughness=0.22)

def surface_hit(lateral, z):
    # Turntable 090 is frontal: the face points toward +X, lateral axis is Y.
    hit = bvh.ray_cast(Vector((1.0, lateral, z)), Vector((-1.0, 0.0, 0.0)), 2.0)
    if hit[0] is None:
        raise RuntimeError(f"No facial surface hit at lateral={lateral}, z={z}")
    return hit[0]

def add_uv(name, location, scale, mat, role):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    obj["role"] = role
    obj["status"] = "PASS01_NON_FINAL__PRESERVE_FOR_RIG_REFERENCE"
    for linked in list(obj.users_collection): linked.objects.unlink(obj)
    collection.objects.link(obj)
    return obj

for side, x in (("L", -0.052), ("R", 0.052)):
    hit = surface_hit(x, 0.278)
    # Place the globe just behind the current high-detail eyelid surface.
    globe_center = hit + Vector((-0.022, 0.0, 0.0))
    eye = add_uv(f"EYE_GLOBE_{side}__PASS01", globe_center, (0.017, 0.020, 0.018), sclera,
                 "Rig eye globe; final object will retain as disconnected topology component")
    add_uv(f"IRIS_{side}__PASS01", globe_center + Vector((0.016, 0.0, 0.0)),
           (0.0025, 0.010, 0.010), iris, "Iris reference for eyelid framing")
    add_uv(f"PUPIL_{side}__PASS01", globe_center + Vector((0.0185, 0.0, 0.0)),
           (0.0015, 0.004, 0.005), pupil, "Pupil reference for gaze direction")
    eye["surface_hit"] = tuple(round(v, 6) for v in hit)

collection["purpose"] = "Eye anatomy targets for manual eyelid, brow and facial loop construction"
collection["final_contract"] = "Promote to final one-mesh object only after head topology validation"
collection["mouth_next"] = "Build lips and cavity only after eyelid loops have been approved against all references"
bpy.ops.wm.save_as_mainfile(filepath=str(WORKSPACE))
print('Created eye anatomy pass 01')
