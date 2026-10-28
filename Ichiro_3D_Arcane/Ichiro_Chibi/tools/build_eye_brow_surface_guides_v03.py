"""Build non-final 3D curve guides from corrected canonical eye/brow lines.

Opens a derived review scene, uses the previously computed 3D surface hits,
and saves a new review blend. It never opens or saves into the user's live
Blender session or source blend. Viewport inspection is preferred to headless
rendering because the dense source mesh can exhaust EEVEE buffer memory.
"""
import bpy
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "references" / "canonical_face_landmarks_v03.json"
REGISTRATION = ROOT / "docs" / "FACE_REGISTRATION_PROBE_V03.json"
INPUT = ROOT / "Ichiro_Chibi_HEAD_HANDS_Topology_Workspace.blend"
OUTPUT = ROOT / "Ichiro_Chibi_Eye_Brow_Surface_Guides_v03.blend"
RENDERS = ROOT / "renders"

canonical = json.loads(CANON.read_text(encoding="utf-8"))
registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
bpy.ops.wm.open_mainfile(filepath=str(INPUT))
source = next(o for o in bpy.context.scene.objects if o.name.startswith("ICH_CHIBI_HIGHDETAIL_SOURCE"))
for obj in bpy.context.scene.objects:
    if obj.type == "MESH" and obj != source:
        obj.hide_render = True
        obj.hide_set(True)
source.hide_render = False
source.hide_set(False)

def catmull3(points3d, closed, steps=8):
    n = len(points3d)
    result = []
    segments = n if closed else n-1
    for i in range(segments):
        p1 = points3d[i]
        p2 = points3d[(i+1) % n]
        p0 = points3d[(i-1) % n] if closed or i > 0 else p1
        p3 = points3d[(i+2) % n] if closed or i+2 < n else p2
        for j in range(steps):
            t = j / steps
            t2, t3 = t*t, t*t*t
            q = []
            for k in range(3):
                q.append(0.5*((2*p1[k]) + (-p0[k]+p2[k])*t +
                    (2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*t2 +
                    (-p0[k]+3*p1[k]-3*p2[k]+p3[k])*t3))
            result.append(q)
    if not closed:
        result.append(list(points3d[-1]))
    return result

def source_hits(rows):
    return [row["full_hit"] for row in rows if row.get("full_hit") is not None]

def make_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color,1)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color,1)
    bsdf.inputs["Emission Color"].default_value = (*color,1)
    bsdf.inputs["Emission Strength"].default_value = 1.0
    return mat

collection = bpy.data.collections.new("CANONICAL_EYE_BROW_GUIDES_V03__REVIEW_ONLY")
bpy.context.scene.collection.children.link(collection)
collection["status"] = "2D landmarks projected to source surface; not eyelid geometry"
collection["source_mesh"] = source.name
materials = {"eye_right":make_material("GUIDE_EYE_CYAN",(0.02,.75,1.0)),
             "eye_left":make_material("GUIDE_EYE_CORAL",(1.0,.08,.12)),
             "brow":make_material("GUIDE_BROW_GOLD",(1.0,.62,.03))}
validation = {}

def add_guide(name, pts, closed, mat, role):
    control_points = source_hits(pts)
    if len(control_points) < 2:
        validation[name] = {"points":len(control_points),"missing":len(pts)-len(control_points),"created":False}
        return
    world_points = [Vector(p) for p in catmull3(control_points, closed)]
    # The source camera looks along +X; a tiny display lift prevents z-fighting.
    world_points = [p + Vector((0.00035,0,0)) for p in world_points]
    curve = bpy.data.curves.new(name+"__CURVE", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 1
    curve.bevel_depth = .00032
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(len(world_points)-1)
    for point, co in zip(spline.points, world_points):
        point.co = (*co,1)
    spline.use_cyclic_u = closed and len(control_points) == len(pts)
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    curve.materials.append(mat)
    obj["role"] = role
    obj["status"] = "REVIEW_GUIDE_NOT_PRODUCTION_GEOMETRY"
    obj["sampled_points"] = len(world_points)
    obj["missing_control_hits"] = len(pts)-len(control_points)
    validation[name] = {"points":len(world_points),"missing_controls":len(pts)-len(control_points),"created":True,"closed":spline.use_cyclic_u}

# The left eye's occluded arc remains open; use only the visible segment.
left = registration["projected_eye_contours"]["screen_left_partial"]
add_guide("EYE_SCREEN_LEFT_VISIBLE_SEGMENT__V03", left[2:8], False, materials["eye_left"],
          "Visible eyelid/liner guide only; fringe-occluded ends intentionally omitted")
right = registration["projected_eye_contours"]["screen_right"]
add_guide("EYE_SCREEN_RIGHT_CONTOUR__V03", right, True,
          materials["eye_right"], "Corrected visible eye margin; closed review curve")
brow_right = registration["projected_brow_contours"]["screen_right"]
add_guide("BROW_SCREEN_RIGHT_CONTOUR__V03", brow_right, True,
          materials["brow"], "Separate brow guide; must not be joined to eyelid")

# Keep the partly hidden left brow as an explicitly incomplete guide.
brow_left = registration["projected_brow_contours"]["screen_left_partial"]
add_guide("BROW_SCREEN_LEFT_VISIBLE_SEGMENT__V03", brow_left[2:7],
          False, materials["brow"], "Visible brow segment only; hair-occluded region omitted")

bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
print(json.dumps({"blend":str(OUTPUT),"validation":validation},indent=2))
