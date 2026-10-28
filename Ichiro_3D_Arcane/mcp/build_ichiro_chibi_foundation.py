r"""Create a non-destructive Blender foundation for canonical Ichiro Chibi.

The reference views are copied from the user-provided front/back/left/right
images into E:\WORKSPACE\Ichiro_Chibi\references. Every model part is kept as
an individual object; this file intentionally contains no joins, remeshes,
booleans, or destructive sculpt operations.
"""
import bpy
import math
import os
from mathutils import Vector

ROOT = r"E:\WORKSPACE\Ichiro_Chibi"
BLEND_PATH = os.path.join(ROOT, "blend", "Ichiro_Chibi_Foundation.blend")
RENDER_PATH = os.path.join(ROOT, "renders", "Ichiro_Chibi_Foundation_Front.png")

for folder in (ROOT, os.path.dirname(BLEND_PATH), os.path.dirname(RENDER_PATH)):
    os.makedirs(folder, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
if scene.world is None:
    scene.world = bpy.data.worlds.new("World")
scene.world.color = (0.025, 0.03, 0.045)

def collection(name, parent=None):
    col = bpy.data.collections.new(name)
    (parent.children if parent else scene.collection.children).link(col)
    return col

refs = collection("00_REFERENCE_LOCKED")
base = collection("01_BASE_360_LOCKED")
costume = collection("02_COSTUME_MODULES")
hair = collection("03_HAIR_ACCESSORIES")
detail = collection("04_HIGH_DETAIL_PLACEHOLDERS")
lights = collection("90_LIGHTS_CAMERA")

def move_to(obj, col):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    col.objects.link(obj)

def mat(name, color, metallic=0.0, roughness=0.5, emission=None):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    if emission:
        shader.inputs["Emission Color"].default_value = (*emission, 1.0)
        shader.inputs["Emission Strength"].default_value = 1.6
    return material

skin = mat("M_Skin", (0.60, 0.22, 0.15), roughness=0.62)
hair_mat = mat("M_Hair_Teal", (0.015, 0.10, 0.13), metallic=0.1, roughness=0.32)
jacket_mat = mat("M_Jacket_Ivory", (0.62, 0.65, 0.45), roughness=0.7)
armor_mat = mat("M_Armor_Charcoal", (0.026, 0.04, 0.06), metallic=0.6, roughness=0.3)
pants_mat = mat("M_Pants_Black", (0.025, 0.03, 0.045), roughness=0.62)
red_mat = mat("M_Accent_Red", (0.7, 0.018, 0.008), metallic=0.28, roughness=0.28, emission=(0.38, 0.005, 0.0))
chest_mat = mat("M_Chest_Ember", (0.58, 0.035, 0.005), metallic=0.35, roughness=0.25, emission=(1.0, 0.08, 0.006))
gold = mat("M_Gold", (0.95, 0.43, 0.05), metallic=0.85, roughness=0.24)
sole = mat("M_Boot_Sole", (0.008, 0.011, 0.016), metallic=0.25, roughness=0.38)
eye_mat = mat("M_Eye_Red", (0.9, 0.02, 0.01), metallic=0.0, roughness=0.2, emission=(0.55, 0.0, 0.0))

def assign(obj, material):
    obj.data.materials.append(material)
    return obj

def smooth(obj):
    if hasattr(obj.data, "polygons"):
        for poly in obj.data.polygons:
            poly.use_smooth = True

def add_uv(name, loc, scale, material, col, segments=32, rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth(obj); assign(obj, material); move_to(obj, col)
    return obj

def add_box(name, loc, dimensions, material, col, bevel=0.05):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod = obj.modifiers.new("ND_Bevel", 'BEVEL')
    mod.width = bevel
    mod.segments = 3
    assign(obj, material); move_to(obj, col)
    return obj

def add_cylinder(name, loc, radius, depth, material, col, rotation=(0,0,0), vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    bevel = obj.modifiers.new("ND_Bevel", 'BEVEL')
    bevel.width = min(radius * 0.18, 0.04)
    bevel.segments = 2
    smooth(obj); assign(obj, material); move_to(obj, col)
    return obj

def add_cone(name, loc, r1, r2, depth, material, col, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    bevel = obj.modifiers.new("ND_Bevel", 'BEVEL')
    bevel.width = 0.025
    bevel.segments = 2
    smooth(obj); assign(obj, material); move_to(obj, col)
    return obj

# Locked proportion scaffold: chibi target is 3.25 heads tall, 2.82m including hair.
head = add_uv("BASE_Head_Locked", (0, 0, 2.23), (0.52, 0.45, 0.56), skin, base)
head["locked_source"] = True
neck = add_cylinder("BASE_Neck_Locked", (0, 0.01, 1.76), 0.16, 0.22, skin, base)
torso = add_uv("BASE_Torso_Locked", (0, 0.025, 1.45), (0.44, 0.28, 0.47), armor_mat, base)
pelvis = add_uv("BASE_Pelvis_Locked", (0, 0.035, 1.02), (0.47, 0.31, 0.30), pants_mat, base)

# Face planes and eyes are separate, editable forms rather than texture paint.
for side in (-1, 1):
    x = side * 0.18
    eye = add_uv(f"FACE_Eye_{'L' if side < 0 else 'R'}", (x, -0.414, 2.27), (0.083, 0.026, 0.041), eye_mat, detail, 20, 12)
    brow = add_box(f"FACE_Brow_{'L' if side < 0 else 'R'}", (x, -0.438, 2.35), (0.16, 0.024, 0.026), armor_mat, detail, 0.01)
    brow.rotation_euler.y = side * math.radians(12)
add_uv("FACE_Nose", (0, -0.455, 2.18), (0.055, 0.045, 0.07), skin, detail, 20, 12)
add_box("FACE_Mouth", (0, -0.44, 2.05), (0.15, 0.018, 0.025), armor_mat, detail, 0.01)

# The jacket, chest core and armor are independent non-destructive modules.
add_box("COSTUME_Chest_Core", (0, -0.265, 1.52), (0.48, 0.08, 0.45), chest_mat, costume, 0.08)
for side in (-1, 1):
    sx = side * 0.34
    shoulder = add_uv(f"COSTUME_Jacket_Shoulder_{'L' if side < 0 else 'R'}", (sx, 0.0, 1.66), (0.28, 0.30, 0.21), jacket_mat, costume)
    forearm = add_cylinder(f"COSTUME_Gauntlet_{'L' if side < 0 else 'R'}", (side * 0.51, -0.005, 1.22), 0.16, 0.46, armor_mat, costume, rotation=(0, math.radians(13), 0))
    hand = add_uv(f"BASE_Hand_{'L' if side < 0 else 'R'}", (side * 0.57, -0.02, 0.95), (0.15, 0.13, 0.17), skin, base, 20, 12)
    hand["locked_source"] = True
    upper = add_cylinder(f"BASE_UpperArm_{'L' if side < 0 else 'R'}", (side * 0.43, 0, 1.43), 0.145, 0.38, armor_mat, base, rotation=(0, math.radians(20), 0))
    # cargo legs, shin guard and boots
    thigh = add_uv(f"COSTUME_Cargo_Thigh_{'L' if side < 0 else 'R'}", (side * 0.24, 0.04, 0.78), (0.27, 0.27, 0.42), pants_mat, costume)
    shin = add_cylinder(f"COSTUME_Shin_{'L' if side < 0 else 'R'}", (side * 0.24, 0.02, 0.40), 0.17, 0.36, armor_mat, costume)
    boot = add_box(f"COSTUME_Boot_{'L' if side < 0 else 'R'}", (side * 0.24, -0.105, 0.16), (0.34, 0.53, 0.24), sole, costume, 0.07)
    toe = add_box(f"COSTUME_Boot_Accent_{'L' if side < 0 else 'R'}", (side * 0.24, -0.37, 0.16), (0.28, 0.06, 0.12), red_mat, costume, 0.025)
    pocket = add_box(f"COSTUME_CargoPocket_{'L' if side < 0 else 'R'}", (side * 0.45, -0.02, 0.80), (0.10, 0.12, 0.24), armor_mat, costume, 0.02)

add_box("COSTUME_Belt", (0, -0.01, 1.08), (0.93, 0.58, 0.11), armor_mat, costume, 0.03)
add_box("COSTUME_Belt_Buckle", (0, -0.315, 1.08), (0.15, 0.04, 0.12), red_mat, costume, 0.015)
for side in (-1, 1):
    add_box(f"COSTUME_Harness_{'L' if side < 0 else 'R'}", (side * 0.19, -0.32, 1.54), (0.09, 0.04, 0.44), armor_mat, costume, 0.02).rotation_euler.y = side * math.radians(20)

# Hair mass and separated angular locks preserve the specific asymmetric Ichiro silhouette.
add_uv("HAIR_MainMass", (0.02, 0.06, 2.53), (0.54, 0.48, 0.40), hair_mat, hair)
hair_specs = [
    ((-0.30, -0.38, 2.39), -22, 0.16, 0.06, 0.58),
    ((-0.18, -0.42, 2.42), -12, 0.15, 0.05, 0.54),
    ((-0.02, -0.37, 2.53), 4, 0.14, 0.04, 0.45),
    ((0.20, -0.20, 2.58), 20, 0.15, 0.04, 0.43),
    ((0.34, 0.05, 2.50), 42, 0.16, 0.05, 0.45),
    ((0.26, 0.25, 2.48), 56, 0.17, 0.05, 0.48),
    ((-0.10, 0.34, 2.49), -55, 0.15, 0.05, 0.45),
]
for i, (loc, angle, r1, r2, depth) in enumerate(hair_specs):
    add_cone(f"HAIR_Lock_{i+1:02d}", loc, r1, r2, depth, hair_mat, hair, rotation=(math.radians(90), 0, math.radians(angle)))

# Shaved-temple lines and earring, held apart as editable accessory modules.
for i, z in enumerate((2.52, 2.45, 2.38)):
    line = add_box(f"HAIR_TempleLine_{i+1}", (0.43, -0.28, z), (0.08, 0.02, 0.018), red_mat, hair, 0.004)
    line.rotation_euler.y = math.radians(-25)
bpy.ops.mesh.primitive_torus_add(major_radius=0.055, minor_radius=0.012, major_segments=20, minor_segments=8, location=(0.47, -0.17, 2.18), rotation=(math.radians(80), 0, 0))
earring = bpy.context.object
earring.name = "ACCESSORY_Gold_Hoop"
smooth(earring); assign(earring, gold); move_to(earring, hair)

# Reference image empties are persistent, locked guides. They are hidden from render.
reference_specs = [
    ("REF_Front", "ichiro_chibi_front.png", (0, 0.82, 1.42), (math.radians(90), 0, math.pi)),
    ("REF_Back", "ichiro_chibi_back.png", (0, -0.82, 1.42), (math.radians(90), 0, 0)),
    ("REF_Left", "ichiro_chibi_left.png", (-0.82, 0, 1.42), (math.radians(90), 0, math.radians(90))),
    ("REF_Right", "ichiro_chibi_right.png", (0.82, 0, 1.42), (math.radians(90), 0, math.radians(-90))),
]
for name, filename, loc, rot in reference_specs:
    path = os.path.join(ROOT, "references", filename)
    image = bpy.data.images.load(path, check_existing=True)
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = 'IMAGE'
    obj.data = image
    obj.empty_display_size = 2.82
    obj.empty_image_side = 'FRONT'
    obj.color[3] = 0.35
    obj.location = loc
    obj.rotation_euler = rot
    obj.hide_render = True
    obj.lock_location = (True, True, True)
    obj.lock_rotation = (True, True, True)
    obj.lock_scale = (True, True, True)
    refs.objects.link(obj)

# Stage and camera are separate from the model.
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
floor = bpy.context.object
floor.name = "STAGE_Ground"
assign(floor, mat("M_Stage", (0.035, 0.045, 0.065), roughness=0.8)); move_to(floor, lights)

def point_light(name, loc, energy, color, size):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy, data.color, data.shape, data.size = energy, color, 'DISK', size
    obj = bpy.data.objects.new(name, data)
    obj.location = loc
    lights.objects.link(obj)
    return obj

point_light("Key_Warm", (-3.2, -4.0, 4.5), 1000, (1.0, 0.52, 0.32), 4.0)
point_light("Fill_Cool", (3.0, -2.0, 2.5), 700, (0.22, 0.65, 1.0), 3.0)
point_light("Rim", (0, 3.0, 4.0), 900, (1.0, 0.08, 0.03), 3.0)

camera_data = bpy.data.cameras.new("CAM_CharacterReview")
camera = bpy.data.objects.new("CAM_CharacterReview", camera_data)
camera.location = (3.5, -8.7, 2.8)
target = Vector((0, 0, 1.40))
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.lens = 55
lights.objects.link(camera)
scene.camera = camera

scene.render.filepath = RENDER_PATH
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
bpy.ops.render.render(write_still=True)
print("CHIBI_FOUNDATION_OK")
print(f"blend={BLEND_PATH}")
print(f"render={RENDER_PATH}")
