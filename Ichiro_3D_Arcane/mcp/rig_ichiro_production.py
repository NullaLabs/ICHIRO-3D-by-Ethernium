"""Build a non-destructive production-control rig for the Ichiro master scene.

Run with Blender 5.2:
  blender -b blend/Ichiro_2390_Arcane_Master.blend --python mcp/rig_ichiro_production.py

The source scene is never overwritten. This creates a rigged .blend and .glb.
The body is an image-derived relief mesh, so weights are smooth spatial weights,
not a substitute for hand-painted weights on a fully sculpted anatomy mesh.
"""
import bpy
import math
import os
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLEND_IN = os.path.join(ROOT, "blend", "Ichiro_2390_Arcane_Master.blend")
BLEND_OUT = os.path.join(ROOT, "blend", "Ichiro_2390_Arcane_Rigged.blend")
GLB_OUT = os.path.join(ROOT, "models", "Ichiro_2390_Arcane_Rigged.glb")
BODY_NAME = "Ichiro_2390_Character"
RIG_NAME = "Ichiro_Production_Rig"

scene = bpy.context.scene
body = bpy.data.objects.get(BODY_NAME)
if body is None or body.type != 'MESH':
    if os.path.exists(BLEND_IN):
        bpy.ops.wm.open_mainfile(filepath=BLEND_IN)
        scene = bpy.context.scene
        body = bpy.data.objects.get(BODY_NAME)
if body is None or body.type != 'MESH':
    raise RuntimeError(f"Required body mesh missing: {BODY_NAME}")

# Idempotent on the source master and on reruns of this output.
old = bpy.data.objects.get(RIG_NAME)
if old:
    bpy.data.objects.remove(old, do_unlink=True)
for obj in (body, bpy.data.objects.get("Ichiro_Magma_Blade_L"),
            bpy.data.objects.get("Ichiro_Magma_Blade_R"),
            bpy.data.objects.get("Ichiro_Scabbard"),
            bpy.data.objects.get("Ichiro_Earring_L"),
            bpy.data.objects.get("Ichiro_Earring_R")):
    if obj:
        for mod in list(obj.modifiers):
            if mod.type == 'ARMATURE' and mod.object is None:
                obj.modifiers.remove(mod)

arm_data = bpy.data.armatures.new("Ichiro_Production_Rig_Data")
rig = bpy.data.objects.new(RIG_NAME, arm_data)
scene.collection.objects.link(rig)
rig.show_in_front = True
arm_data.display_type = 'OCTAHEDRAL'

# name, head, tail, parent, deform
B = [
 ("CTRL-Root", (0,0,0), (0,0,.18), None, False),
 ("DEF-Hips", (0,0,.83), (0,0,1.00), "CTRL-Root", True),
 ("DEF-Spine", (0,0,1.00), (0,0,1.17), "DEF-Hips", True),
 ("DEF-Chest", (0,0,1.17), (0,0,1.36), "DEF-Spine", True),
 ("DEF-Neck", (0,0,1.36), (0,0,1.47), "DEF-Chest", True),
 ("DEF-Head", (0,0,1.47), (0,0,1.76), "DEF-Neck", True),
 ("DEF-Shoulder.L", (.055,0,1.34), (.17,0,1.34), "DEF-Chest", True),
 ("DEF-UpperArm.L", (.17,0,1.34), (.30,0,1.08), "DEF-Shoulder.L", True),
 ("DEF-Forearm.L", (.30,0,1.08), (.39,-.02,.84), "DEF-UpperArm.L", True),
 ("DEF-Hand.L", (.39,-.02,.84), (.43,-.05,.75), "DEF-Forearm.L", True),
 ("DEF-Shoulder.R", (-.055,0,1.34), (-.17,0,1.34), "DEF-Chest", True),
 ("DEF-UpperArm.R", (-.17,0,1.34), (-.30,0,1.08), "DEF-Shoulder.R", True),
 ("DEF-Forearm.R", (-.30,0,1.08), (-.39,-.02,.84), "DEF-UpperArm.R", True),
 ("DEF-Hand.R", (-.39,-.02,.84), (-.43,-.05,.75), "DEF-Forearm.R", True),
 ("DEF-Thigh.L", (.11,0,.86), (.14,0,.48), "DEF-Hips", True),
 ("DEF-Shin.L", (.14,0,.48), (.16,0,.12), "DEF-Thigh.L", True),
 ("DEF-Foot.L", (.16,0,.12), (.18,-.10,.025), "DEF-Shin.L", True),
 ("DEF-Thigh.R", (-.11,0,.86), (-.14,0,.48), "DEF-Hips", True),
 ("DEF-Shin.R", (-.14,0,.48), (-.16,0,.12), "DEF-Thigh.R", True),
 ("DEF-Foot.R", (-.16,0,.12), (-.18,-.10,.025), "DEF-Shin.R", True),
 # animator-facing controls, deliberately non-deforming
 ("CTRL-COG", (0,0,.82), (0,0,.94), "CTRL-Root", False),
 ("CTRL-Chest", (0,0,1.19), (0,0,1.31), "CTRL-COG", False),
 ("CTRL-Head", (0,0,1.49), (0,0,1.62), "CTRL-Chest", False),
]
for s in ("L", "R"):
    sx = 1 if s == "L" else -1
    B.extend([
      (f"CTRL-HandIK.{s}", (sx*.39,-.02,.84), (sx*.39,-.02,.94), "CTRL-Root", False),
      (f"CTRL-ElbowPole.{s}", (sx*.32,-.40,1.08), (sx*.32,-.40,1.16), "CTRL-Root", False),
      (f"CTRL-FootIK.{s}", (sx*.16,0,.12), (sx*.16,0,.22), "CTRL-Root", False),
      (f"CTRL-KneePole.{s}", (sx*.14,-.42,.48), (sx*.14,-.42,.56), "CTRL-Root", False),
    ])

bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for name, head, tail, parent, deform in B:
    eb = arm_data.edit_bones.new(name)
    eb.head, eb.tail = Vector(head), Vector(tail)
    eb.use_deform = deform
    if parent:
        eb.parent = arm_data.edit_bones[parent]
        eb.use_connect = False
bpy.ops.object.mode_set(mode='OBJECT')

# Smooth capsule-distance weights. Local candidate sets prevent arms/legs from
# bleeding into the torso; neighboring bones blend across each joint.
deform_names = [r[0] for r in B if r[4]]
segments = {name: (Vector(head), Vector(tail)) for name, head, tail, _, deform in B if deform}
groups = {name: body.vertex_groups.new(name=name) for name in deform_names}

def segment_distance(point, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (point-a).dot(ab) / max(ab.dot(ab), 1e-12)))
    return (point - (a + t*ab)).length

for v in body.data.vertices:
    p = v.co
    x, z = p.x, p.z
    if z >= 1.43:
        candidates = ["DEF-Head", "DEF-Neck"]
    elif z < .96 and abs(x) > .055:
        side = "L" if x >= 0 else "R"
        candidates = [f"DEF-Thigh.{side}", f"DEF-Shin.{side}", f"DEF-Foot.{side}", "DEF-Hips"]
    elif abs(x) > .18 and .70 < z < 1.42:
        side = "L" if x >= 0 else "R"
        candidates = [f"DEF-Shoulder.{side}", f"DEF-UpperArm.{side}", f"DEF-Forearm.{side}", f"DEF-Hand.{side}", "DEF-Chest"]
    elif z >= 1.34:
        candidates = ["DEF-Neck", "DEF-Chest", "DEF-Head"]
    elif z >= 1.15:
        candidates = ["DEF-Chest", "DEF-Spine", "DEF-Shoulder.L", "DEF-Shoulder.R"]
    elif z >= .97:
        candidates = ["DEF-Spine", "DEF-Hips", "DEF-Chest"]
    elif z >= .82:
        candidates = ["DEF-Hips", "DEF-Thigh.L", "DEF-Thigh.R", "DEF-Spine"]
    else:
        side = "L" if x >= 0 else "R"
        candidates = [f"DEF-Foot.{side}", f"DEF-Shin.{side}", f"DEF-Thigh.{side}"]
    ranked = sorted(((segment_distance(p, *segments[n]), n) for n in candidates), key=lambda q:q[0])[:3]
    raw = [(1.0 / (d + .018) ** 2, n) for d, n in ranked]
    total = sum(w for w, _ in raw)
    for w, name in raw:
        groups[name].add([v.index], w/total, 'REPLACE')

arm_mod = body.modifiers.new("Ichiro Production Armature", 'ARMATURE')
arm_mod.object = rig
arm_mod.use_deform_preserve_volume = True
body.parent = rig

# IK targets: animator moves the hand/foot controls; pole controls establish bend.
for side in ("L", "R"):
    hand = rig.pose.bones[f"DEF-Forearm.{side}"]
    ik = hand.constraints.new('IK')
    ik.name = f"Arm IK | {side}"
    ik.target, ik.subtarget = rig, f"CTRL-HandIK.{side}"
    ik.pole_target, ik.pole_subtarget = rig, f"CTRL-ElbowPole.{side}"
    ik.chain_count = 2
    ik.pole_angle = 0.0
    foot = rig.pose.bones[f"DEF-Shin.{side}"]
    ik = foot.constraints.new('IK')
    ik.name = f"Leg IK | {side}"
    ik.target, ik.subtarget = rig, f"CTRL-FootIK.{side}"
    ik.pole_target, ik.pole_subtarget = rig, f"CTRL-KneePole.{side}"
    ik.chain_count = 2
    ik.pole_angle = 0.0

# Simple animator-facing body controls drive the matching deform joints in FK.
# IK remains layered on the arm/leg chains for posing the extremities.
for deform_name, ctrl_name in (("DEF-Hips", "CTRL-COG"),
                               ("DEF-Chest", "CTRL-Chest"),
                               ("DEF-Head", "CTRL-Head")):
    c = rig.pose.bones[deform_name].constraints.new('COPY_ROTATION')
    c.name = f"FK Control | {deform_name}"
    c.target, c.subtarget = rig, ctrl_name
    c.owner_space = 'LOCAL'
    c.target_space = 'LOCAL'
    c.mix_mode = 'REPLACE'

# Use bone parenting while preserving each prop's current world transform.
def parent_to_bone(obj_name, bone_name):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        return
    world = obj.matrix_world.copy()
    obj.parent = rig
    obj.parent_type = 'BONE'
    obj.parent_bone = bone_name
    obj.matrix_parent_inverse = (rig.matrix_world @ arm_data.bones[bone_name].matrix_local).inverted()
    obj.matrix_world = world

parent_to_bone("Ichiro_Magma_Blade_L", "DEF-Hand.L")
parent_to_bone("Ichiro_Magma_Blade_R", "DEF-Hand.R")
parent_to_bone("Ichiro_Scabbard", "DEF-Chest")
parent_to_bone("Ichiro_Earring_L", "DEF-Head")
parent_to_bone("Ichiro_Earring_R", "DEF-Head")
parent_to_bone("Ichiro_Hair_Bangs_3D", "DEF-Head")
parent_to_bone("Ichiro_Hair_Crest_3D", "DEF-Head")
parent_to_bone("Ichiro_Forehead_Lock_3D", "DEF-Head")
parent_to_bone("Ichiro_Cyber_Collar_3D", "DEF-Neck")
parent_to_bone("Ichiro_Collar_Clasp_Badge", "DEF-Neck")
parent_to_bone("Ichiro_Clavicle_Harness_3D", "DEF-Chest")
parent_to_bone("Ichiro_Jacket_Lapels_3D", "DEF-Chest")
parent_to_bone("Ichiro_Back_Harness_3D", "DEF-Chest")
parent_to_bone("Ichiro_Dorsal_Buckle", "DEF-Chest")
parent_to_bone("Ichiro_Tactical_Belts_3D", "DEF-Hips")
parent_to_bone("Ichiro_Belt_Buckle", "DEF-Hips")
parent_to_bone("Ichiro_Belt_Buckle_2", "DEF-Hips")
parent_to_bone("Ichiro_Hip_Pouch", "DEF-Hips")
parent_to_bone("Ichiro_Cargo_Pocket_L", "DEF-Thigh.L")
parent_to_bone("Ichiro_Cargo_Flap_L", "DEF-Thigh.L")
parent_to_bone("Ichiro_Cargo_Pocket_R", "DEF-Thigh.R")
parent_to_bone("Ichiro_Cargo_Flap_R", "DEF-Thigh.R")
parent_to_bone("Ichiro_Gauntlet_Cuff_L", "DEF-Forearm.L")
parent_to_bone("Ichiro_Gauntlet_LED_L", "DEF-Forearm.L")
parent_to_bone("Ichiro_Gauntlet_Cuff_R", "DEF-Forearm.R")
parent_to_bone("Ichiro_Gauntlet_LED_R", "DEF-Forearm.R")
parent_to_bone("Ichiro_KPR_Emblem_L", "DEF-Foot.L")
parent_to_bone("Ichiro_KPR_Emblem_R", "DEF-Foot.R")
parent_to_bone("Ichiro_Sneaker_Pods_L", "DEF-Foot.L")
parent_to_bone("Ichiro_Sneaker_Pods_R", "DEF-Foot.R")
parent_to_bone("Lumen_Core_Hull", "CTRL-Root")
parent_to_bone("Lumen_Eye_L", "CTRL-Root")
parent_to_bone("Lumen_Eye_R", "CTRL-Root")
parent_to_bone("Lumen_Pupil_L", "CTRL-Root")
parent_to_bone("Lumen_Pupil_R", "CTRL-Root")
parent_to_bone("Lumen_Orbital_Ring", "CTRL-Root")

# Clear pose selection, label the rig in Blender, and make controls easy to find.
for name, color in (("CTRL-Root", "THEME03"), ("CTRL-COG", "THEME04"),
                    ("CTRL-Chest", "THEME04"), ("CTRL-Head", "THEME04")):
    if name in arm_data.bones:
        arm_data.bones[name].color.palette = color
for s in ("L", "R"):
    for prefix in ("CTRL-HandIK", "CTRL-FootIK"):
        arm_data.bones[f"{prefix}.{s}"].color.palette = "THEME05"
    for prefix in ("CTRL-ElbowPole", "CTRL-KneePole"):
        arm_data.bones[f"{prefix}.{s}"].color.palette = "THEME06"
rig["rig_version"] = "1.0"
rig["ik_arms"] = 0.0
rig["ik_legs"] = 0.0
rig.id_properties_ui("ik_arms").update(min=0.0, max=1.0, description="Blend arm IK controls on/off")
rig.id_properties_ui("ik_legs").update(min=0.0, max=1.0, description="Blend leg IK controls on/off")
rig["notes"] = "FK deform chains + blendable hand/foot IK; relief-mesh weights require deformation review."

# Keep the rest pose exactly aligned with the source silhouette. Animators can
# blend IK in with the two custom properties on the rig object.
for pbone in rig.pose.bones:
    for con in pbone.constraints:
        if con.type != 'IK':
            continue
        key = 'ik_arms' if 'Arm IK' in con.name else 'ik_legs'
        fcurve = con.driver_add("influence")
        driver = fcurve.driver
        driver.type = 'SCRIPTED'
        var = driver.variables.new()
        var.name = "blend"
        var.type = 'SINGLE_PROP'
        var.targets[0].id = rig
        var.targets[0].data_path = f'["{key}"]'
        driver.expression = "blend"

# Guard against accidental rest-pose regressions and vertices without skinning.
unweighted = sum(1 for v in body.data.vertices if not v.groups)
if unweighted:
    raise RuntimeError(f"Weight generation left {unweighted} vertices unweighted")

# Ensure facial shape keys are at 0.0 (neutral rest expression) for rest-pose delta verification
if body.data.shape_keys:
    for kb in body.data.shape_keys.key_blocks:
        if kb != body.data.shape_keys.reference_key:
            kb.value = 0.0
    body.active_shape_key_index = 0

rig.update_tag()
scene.frame_set(scene.frame_current)
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated_body = body.evaluated_get(depsgraph).to_mesh()
rest_delta = max((evaluated_body.vertices[i].co - body.data.vertices[i].co).length
                 for i in range(len(body.data.vertices)))
body.evaluated_get(depsgraph).to_mesh_clear()
if rest_delta > 1e-5:
    raise RuntimeError(f"Neutral pose changed the body mesh (max delta {rest_delta:.8f} m)")
print(f"NEUTRAL_CHECK_OK max_delta={rest_delta:.9g}m", flush=True)

# Preserve all original scene content, save new native file, then export a rigged GLB.
os.makedirs(os.path.dirname(BLEND_OUT), exist_ok=True)
os.makedirs(os.path.dirname(GLB_OUT), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
bpy.ops.object.select_all(action='DESELECT')
for obj in scene.objects:
    if obj.type in {'MESH', 'ARMATURE'} and not obj.hide_render and not obj.name.startswith(("BASE_360", "Arcane_Pedestal", "Arcane_Ring_")):
        obj.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.export_scene.gltf(filepath=GLB_OUT, export_format='GLB', export_yup=True,
                          use_selection=True,
                          export_apply=False, export_skins=True, export_animations=True,
                          export_def_bones=True, export_morph=True,
                          export_materials='EXPORT')
print(f"RIG_BUILD_OK bones={len(arm_data.bones)} weighted_vertices={len(body.data.vertices)}")
print(f"BLEND={BLEND_OUT}\nGLB={GLB_OUT}")
