"""Import or refresh only the V02 silhouette blockout in the current scene.

Run from the project-root Blender file. The candidate is kept separate, hidden
from viewport/render by default, and never replaces the linked high-detail source.
"""
import bpy

OBJ_PATH = bpy.path.abspath("//exports/visual_hull_v02/Ichiro_Chibi_VisualHull_BLOCKOUT_V02.obj")
COLLECTION_NAME = "ICH_CHIBI_VISUAL_HULL_BLOCKOUT_V02__CANDIDATE"
OBJECT_NAME = "VISUAL_HULL_BLOCKOUT_V02__REVIEW_ONLY"

collection = bpy.data.collections.get(COLLECTION_NAME)
if collection is None:
    collection = bpy.data.collections.new(COLLECTION_NAME)
    bpy.context.scene.collection.children.link(collection)

previous = bpy.data.objects.get(OBJECT_NAME)
if previous is not None:
    bpy.data.objects.remove(previous, do_unlink=True)

before = set(bpy.data.objects)
bpy.ops.wm.obj_import(
    filepath=OBJ_PATH,
    forward_axis="Y",
    up_axis="Z",
    global_scale=1.0,
    validate_meshes=True,
)
created = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
if len(created) != 1:
    raise RuntimeError(f"Expected one blockout mesh, imported {len(created)}")

obj = created[0]
obj.name = OBJECT_NAME
obj.data.name = "VISUAL_HULL_BLOCKOUT_V02_MESH"
for current_collection in list(obj.users_collection):
    current_collection.objects.unlink(obj)
collection.objects.link(obj)
obj["status"] = "CANDIDATE_BLOCKOUT_NOT_CANON_NOT_RIGGABLE"
obj["generator"] = "tools/build_calibrated_visual_hull.py v02"
obj["purpose"] = "one-metre blockout; front +X, width Y, up Z"
obj.hide_render = True
obj.hide_set(True)

print({
    "object": obj.name,
    "vertices": len(obj.data.vertices),
    "faces": len(obj.data.polygons),
    "dimensions_xyz": tuple(round(value, 6) for value in obj.dimensions),
    "collection": collection.name,
    "hidden_by_default": True,
})
