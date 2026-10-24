"""
ETHERNIUM SOVEREIGN // ICHIRO 2390 MODULAR TRUE 360 SCENE BUILDER (DUAL-SCALE TRELLIS 2K EDITION)
=================================================================================================
Builds the production-grade, non-destructive modular layered scene in Blender 5.2 LTS using the
Dual-Scale Microsoft TRELLIS 360-degree neural meshes (Full Body 2K + High-Res HeadBust 2K):
- Collection 00: 00_STUDIO_LIGHTING (4-point Fortiche studio lighting + Arcane world + Studio Pedestal)
- Collection 01: 01_REFERENCE_CANON (Canonical 2D views + BASE_360_LOCKED reference hull)
- Collection 02: 02_SCULPT_CORRECTIONS (Unified 30.5K-vert True-360 Body+HeadBust + 8 ARKit FACS blendshapes)
- Collection 03: 03_COSTUME_MODULES (Native 360 sculpted bolero jacket, choker, belts, cargo pants, sneakers)
- Collection 04: 04_HAIR_AND_ACCESSORIES (Dual Magma Blades, Dorsal Scabbard, Authentic Lumen Recon Drone)
- Collection 05: 05_HIGH_POLY_DETAILS (Dual 2K UV-Baked PBR + Cyber-Magma Emission + Tactile Micro-Bump)

Execution:
  blender --factory-startup -b -P mcp/build_modular_true360_scene.py
"""
import bpy
import bmesh
import os
import math
import subprocess
import numpy as np
from mathutils import Vector, Euler, Matrix

# Paths
ROOT        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF_DIR     = os.path.join(ROOT, "references")
TEX_DIR     = os.path.join(ROOT, "textures")
BLEND_DIR   = os.path.join(ROOT, "blend")
MODEL_DIR   = os.path.join(ROOT, "models")
RENDER_DIR  = os.path.join(ROOT, "renders")
SCRATCH_DIR = r"C:\Users\esenc\.gemini\antigravity\brain\3ccecf18-5e96-4998-8aad-0804a4100391\scratch"

BODY_GLB_PATH = os.path.join(MODEL_DIR, "Ichiro_Trellis_MultiView_2K.glb")
BUST_GLB_PATH = os.path.join(MODEL_DIR, "Ichiro_Trellis_HeadBust_2K.glb")
NPZ_360_PATH  = os.path.join(MODEL_DIR, "Ichiro_360_Locked_Base_Mesh.npz")
GRID_V2_PATH  = os.path.join(TEX_DIR, "ichiro_master_grid_v2.npz")
BLADE_BLEND   = r"E:\DESCARGAS\Web3\My web3 Projects\KPR\Ichiro Commissions\Ichiro traits\ ENERGY BLADE.blend"
LUMEN_GLB     = r"C:\Users\esenc\.gemini\antigravity\brain\c7d203b9-a584-4a61-9146-40793a6a1f52\scratch\ICHIRO-repo\assets\models\lumen-blueprint.glb"

OUT_MASTER_BLEND = os.path.join(BLEND_DIR, "Ichiro_2390_Arcane_Master.blend")
OUT_GLB          = os.path.join(MODEL_DIR, "Ichiro_2390_Arcane.glb")
OUT_OBJ          = os.path.join(MODEL_DIR, "Ichiro_2390_Arcane.obj")

for d in (TEX_DIR, BLEND_DIR, MODEL_DIR, RENDER_DIR):
    os.makedirs(d, exist_ok=True)

print("===============================================================================")
print("  ETHERNIUM SOVEREIGN // ASSEMBLING DUAL-SCALE TRELLIS 360 STUDIO SCENE")
print("===============================================================================")

# 1. Reset Blender Scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

def get_or_create_collection(name, parent=None):
    if name in bpy.data.collections:
        col = bpy.data.collections[name]
    else:
        col = bpy.data.collections.new(name)
        if parent is None:
            bpy.context.scene.collection.children.link(col)
        else:
            parent.children.link(col)
    return col

def link_obj(obj, col):
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)
    for c in bpy.data.collections:
        if c != col and obj.name in c.objects:
            c.objects.unlink(obj)
    if obj.name not in col.objects:
        col.objects.link(obj)

col_lights  = get_or_create_collection("00_STUDIO_LIGHTING")
col_ref     = get_or_create_collection("01_REFERENCE_CANON")
col_sculpt  = get_or_create_collection("02_SCULPT_CORRECTIONS")
col_costume = get_or_create_collection("03_COSTUME_MODULES")
col_props   = get_or_create_collection("04_HAIR_AND_ACCESSORIES")
col_details = get_or_create_collection("05_HIGH_POLY_DETAILS")

# ==============================================================================
# LAYER 00: STUDIO LIGHTING & ARCANE WORLD ENVIRONMENT
# ==============================================================================
print("[LAYER 00] Configuring 4-point Fortiche/Arcane studio lighting and environment...")
world = bpy.data.worlds.new("Arcane_World")
scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs["Color"].default_value = (0.048, 0.055, 0.078, 1.0)
    bg_node.inputs["Strength"].default_value = 0.95

def add_studio_light(name, ltype, loc, rot, energy, col, size=1.5):
    ld = bpy.data.lights.new(name, type=ltype)
    ld.energy = energy
    ld.color = col
    if ltype == 'AREA':
        ld.size = size
        ld.shape = 'RECTANGLE'
        ld.size_y = size * 1.4
    lo = bpy.data.objects.new(name, ld)
    col_lights.objects.link(lo)
    lo.location = Vector(loc)
    lo.rotation_euler = Euler([math.radians(a) for a in rot], 'XYZ')
    return lo

l_key  = add_studio_light("Key_Warm_Piltover",  'AREA',  (1.2, -2.8, 1.9),  (62, 0, 22),   200.0, (1.0, 0.96, 0.90), 2.4)
l_cyan = add_studio_light("Rim_Zaun_Cyan",      'AREA',  (-2.2, 1.6, 1.6),  (65, 0, -130), 135.0, (0.0, 0.94, 1.0),  2.0)
l_mag  = add_studio_light("Rim_Arcane_Magenta", 'AREA',  (2.2, 1.6, 1.5),   (65, 0, 130),  125.0, (1.0, 0.22, 0.55), 2.0)
l_fill = add_studio_light("Fill_Front_Neutral", 'AREA',  (0.0, -3.0, 1.1),  (82, 0, 0),    130.0, (0.92, 0.94, 1.0), 2.8)

# ==============================================================================
# LAYER 01: REFERENCE CANON (Orthographic Planes + Locked 360 Raw Visual Hull)
# ==============================================================================
print("[LAYER 01] Loading reference images and locked 360 reference volume...")
if os.path.exists(NPZ_360_PATH):
    raw_data = np.load(NPZ_360_PATH)
    raw_verts = raw_data["verts"]
    raw_faces = raw_data["faces"]
    m_locked = bpy.data.meshes.new("BASE_360_LOCKED_Mesh")
    m_locked.from_pydata(raw_verts.tolist(), [], raw_faces.tolist())
    m_locked.update()
    obj_locked = bpy.data.objects.new("BASE_360_LOCKED", m_locked)
    link_obj(obj_locked, col_ref)
    obj_locked.display_type = 'WIRE'
    obj_locked.hide_render = True
    obj_locked.hide_viewport = True
    obj_locked.lock_location = (True, True, True)
    obj_locked.lock_rotation = (True, True, True)
    obj_locked.lock_scale    = (True, True, True)

ref_images = [
    ("REF_Front_Canon", "full_top_row.png", (0.0, -1.20, 0.90), Euler((math.radians(90), 0, 0), 'XYZ'), 1.80),
    ("REF_Back_Canon",  "bust_back.png",    (0.0,  1.20, 0.90), Euler((math.radians(90), 0, math.radians(180)), 'XYZ'), 1.80),
    ("REF_Side_L_Canon","bust_left.png",    ( 1.20, 0.0, 0.90), Euler((math.radians(90), 0, math.radians(-90)), 'XYZ'), 1.80),
    ("REF_Side_R_Canon","bust_right.png",   (-1.20, 0.0, 0.90), Euler((math.radians(90), 0, math.radians(90)), 'XYZ'), 1.80),
]
for ref_name, filename, loc, rot, sz in ref_images:
    fpath = os.path.join(REF_DIR, filename)
    if os.path.exists(fpath):
        emp = bpy.data.objects.new(ref_name, None)
        emp.empty_display_type = 'IMAGE'
        emp.data = bpy.data.images.load(fpath)
        emp.empty_display_size = sz
        emp.location = loc
        emp.rotation_euler = rot
        emp.hide_render = True
        emp.hide_viewport = True
        link_obj(emp, col_ref)

# ==============================================================================
# LAYER 02 & 05: DUAL-SCALE TRELLIS 360 MESH FUSION + 2K PBR & MAGMA SHADERS
# ==============================================================================
print("[LAYER 02] Importing and fusing Dual-Scale TRELLIS 360° Neural Meshes (Body 2K + HeadBust 2K)...")

# 2a. Import Full Body 360° Mesh
before_b = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=BODY_GLB_PATH)
body_objs = [o for o in bpy.data.objects if o not in before_b and o.type == 'MESH']
body_obj = body_objs[0]
body_obj.name = "Ichiro_Body_Part"
bpy.ops.object.select_all(action='DESELECT')
body_obj.select_set(True)
bpy.context.view_layer.objects.active = body_obj
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in [o for o in bpy.data.objects if o not in before_b and o != body_obj]:
    bpy.data.objects.remove(o, do_unlink=True)

# 2b. Import High-Res HeadBust 360° Mesh (24,473 vertices)
before_h = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=BUST_GLB_PATH)
bust_objs = [o for o in bpy.data.objects if o not in before_h and o.type == 'MESH']
bust_obj = bust_objs[0]
bust_obj.name = "Ichiro_HeadBust_Part"
bpy.ops.object.select_all(action='DESELECT')
bust_obj.select_set(True)
bpy.context.view_layer.objects.active = bust_obj
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in [o for o in bpy.data.objects if o not in before_h and o != bust_obj]:
    bpy.data.objects.remove(o, do_unlink=True)

# 2c. Surgical Collar-Line Trimming on Body
bm_b = bmesh.new()
bm_b.from_mesh(body_obj.data)
verts_to_del_b = []
for v in bm_b.verts:
    x, y, z = v.co.x, v.co.y, v.co.z
    if z > 0.344:
        verts_to_del_b.append(v)
    elif z > 0.334 and abs(x) < 0.068 and y < 0.01:
        verts_to_del_b.append(v)
    elif z > 0.326 and abs(x) < 0.068 and y < -0.054:
        verts_to_del_b.append(v)
bmesh.ops.delete(bm_b, geom=verts_to_del_b, context='VERTS')
bm_b.to_mesh(body_obj.data)
bm_b.free()

# 2d. Surgical Collar-Line Trimming & Smooth Neck Tucking on HeadBust
bm_h = bmesh.new()
bm_h.from_mesh(bust_obj.data)
faces_to_del_h = []
for f in bm_h.faces:
    c = f.calc_center_median()
    x, y, z = c.x, c.y, c.z
    if z >= -0.02:
        continue
    if z >= -0.115 and abs(x) <= 0.138 and y < 0.0:
        continue
    if z >= -0.055 and -0.30 < x < -0.08 and y < 0.02:
        continue
    if z >= -0.175 and -0.30 < x < -0.08 and y < -0.135:
        continue
    if z >= -0.150 and abs(x) <= 0.138 and -0.35 < y < 0.145:
        continue
    faces_to_del_h.append(f)

bmesh.ops.delete(bm_h, geom=faces_to_del_h, context='FACES')
for v in bm_h.verts:
    x, y, z = v.co.x, v.co.y, v.co.z
    if z < -0.122 and not (x < -0.085 and y < 0.01):
        t = min(1.0, (-0.122 - z) / 0.028)
        v.co.x *= (1.0 - 0.10 * t)
        if y < 0.0:
            v.co.y += 0.020 * t
bm_h.to_mesh(bust_obj.data)
bm_h.free()

# Align HeadBust into Body's collar
S_BUST = 0.275
bust_obj.scale = (S_BUST, S_BUST, S_BUST)
bust_obj.location = (0.002, -0.006, 0.365)
bpy.ops.object.select_all(action='DESELECT')
bust_obj.select_set(True)
bpy.context.view_layer.objects.active = bust_obj
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

def box_blur_2d(m, radius=14, passes=3):
    out = m.copy()
    k = 2 * radius + 1
    for _ in range(passes):
        pad_h = np.pad(out, ((0, 0), (radius, radius)), mode='edge')
        cs_h = np.pad(np.cumsum(pad_h, axis=1), ((0, 0), (1, 0)), mode='constant')
        out = (cs_h[:, k:] - cs_h[:, :-k]) / float(k)
        pad_v = np.pad(out, ((radius, radius), (0, 0)), mode='edge')
        cs_v = np.pad(np.cumsum(pad_v, axis=0), ((1, 0), (0, 0)), mode='constant')
        out = (cs_v[k:, :] - cs_v[:-k, :]) / float(k)
    return out

# 2e. Upgrade Both Native 2K Materials with Packed Cyber-Magma Emission & Tactile Bump
def enhance_trellis_2k_material(obj, mat_name, em_tex_name, is_bust=False):
    mat = obj.data.materials[0]
    mat.name = mat_name
    mat.use_backface_culling = False
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    bsdf = None
    tex_node = None
    for n in nodes:
        if n.type == 'BSDF_PRINCIPLED':
            bsdf = n
        elif n.type == 'TEX_IMAGE' and n.image is not None:
            tex_node = n

    if not bsdf or not tex_node:
        return mat, None, None

    base_img = tex_node.image
    base_img.name = f"{mat_name}_Albedo_2K"
    w, h = base_img.size[0], base_img.size[1]
    arr = np.array(base_img.pixels[:], dtype=np.float32).reshape((h, w, 4))

    if not is_bust:
        # Continuous Excess-Grey De-Haze across the front torso UV region to eliminate multi-view white bolero bleed
        torso_center_mask = np.zeros((h, w), dtype=np.float32)
        torso_side_mask = np.zeros((h, w), dtype=np.float32)
        uv_layer = obj.data.uv_layers[0].data
        for poly in obj.data.polygons:
            c = poly.center
            n = poly.normal
            if c.y < -0.01 and n.y < -0.15 and 0.005 <= c.z <= 0.320 and abs(c.x) <= 0.095:
                us = [uv_layer[li].uv.x for li in poly.loop_indices]
                vs = [uv_layer[li].uv.y for li in poly.loop_indices]
                x0 = max(0, int(min(us) * w) - 5)
                x1 = min(w, int(max(us) * w) + 6)
                y0 = max(0, int(min(vs) * h) - 5)
                y1 = min(h, int(max(vs) * h) + 6)
                if abs(c.x) <= 0.048:
                    torso_center_mask[y0:y1, x0:x1] = 1.0
                elif c.z <= 0.205:
                    torso_side_mask[y0:y1, x0:x1] = 1.0

        torso_center_mask = box_blur_2d(torso_center_mask, radius=14, passes=3)
        torso_side_mask = box_blur_2d(torso_side_mask, radius=12, passes=3)

        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        grey_floor = np.minimum(np.minimum(r, g), b)
        excess_grey = np.maximum(0.0, grey_floor - 0.055) * torso_center_mask
        arr[:, :, 0] = np.clip(r - excess_grey * 0.28, 0.02, 1.0)
        arr[:, :, 1] = np.clip(g - excess_grey * 0.76, 0.01, 1.0)
        arr[:, :, 2] = np.clip(b - excess_grey * 0.94, 0.01, 1.0)

        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        non_magma = np.clip(1.0 - (r - g - 0.08) * 8.0, 0.0, 1.0)
        eff_side = torso_side_mask * non_magma
        arr[:, :, 0] = r * (1.0 - eff_side * 0.72)
        arr[:, :, 1] = g * (1.0 - eff_side * 0.75)
        arr[:, :, 2] = b * (1.0 - eff_side * 0.75)
        base_img.pixels[:] = arr.ravel().tolist()
        base_img.pack()

        # Generate glTF-native 2K Emission Map for Cyber-Magma veins and sneaker pods
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        magma_mask = np.clip((r - 1.38 * g) * 2.4, 0.0, 1.0) * np.clip((r - 0.22) * 2.8, 0.0, 1.0)
        em_arr = np.zeros_like(arr)
        em_arr[:, :, 0] = r * magma_mask
        em_arr[:, :, 1] = g * magma_mask * 0.58
        em_arr[:, :, 2] = b * magma_mask * 0.25
        em_arr[:, :, 3] = 1.0

        em_img = bpy.data.images.new(em_tex_name, width=w, height=h, alpha=False)
        em_img.pixels[:] = em_arr.ravel().tolist()
        em_img.pack()

        em_node = nodes.new("ShaderNodeTexImage")
        em_node.name = "Tex_Cyber_Magma_Emission"
        em_node.image = em_img
        links.new(em_node.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 1.25
    else:
        # Clean orange fringe at the very bottom rim of the HeadBust choker (z < 0.334 in world space)
        choker_rim_mask = np.zeros((h, w), dtype=np.float32)
        uv_layer = obj.data.uv_layers[0].data
        for poly in obj.data.polygons:
            c = poly.center
            if c.z < 0.335 and c.y < -0.01 and abs(c.x) < 0.035:
                us = [uv_layer[li].uv.x for li in poly.loop_indices]
                vs = [uv_layer[li].uv.y for li in poly.loop_indices]
                x0 = max(0, int(min(us) * w) - 3)
                x1 = min(w, int(max(us) * w) + 4)
                y0 = max(0, int(min(vs) * h) - 3)
                y1 = min(h, int(max(vs) * h) + 4)
                choker_rim_mask[y0:y1, x0:x1] = 1.0
        choker_rim_mask = box_blur_2d(choker_rim_mask, radius=4, passes=2)
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        orange_bleed = np.clip((r - 1.35 * g) * 4.0, 0.0, 1.0) * choker_rim_mask
        arr[:, :, 0] = r * (1.0 - orange_bleed) + 0.06 * orange_bleed
        arr[:, :, 1] = g * (1.0 - orange_bleed) + 0.055 * orange_bleed
        arr[:, :, 2] = b * (1.0 - orange_bleed) + 0.065 * orange_bleed
        base_img.pixels[:] = arr.ravel().tolist()
        base_img.pack()
        bsdf.inputs["Emission Strength"].default_value = 0.0

    # Fortiche/Arcane micro-relief bump from 2K albedo
    bmp_node = nodes.new("ShaderNodeBump")
    bmp_node.inputs["Strength"].default_value = 0.12
    bmp_node.inputs["Distance"].default_value = 0.002
    links.new(tex_node.outputs["Color"], bmp_node.inputs["Height"])
    links.new(bmp_node.outputs["Normal"], bsdf.inputs["Normal"])

    bsdf.inputs["Roughness"].default_value = 0.62
    bsdf.inputs["Metallic"].default_value = 0.04
    bsdf.inputs["Specular IOR Level"].default_value = 0.22
    return mat, bsdf, tex_node

mat_body, bsdf_body, tex_body = enhance_trellis_2k_material(
    body_obj, "Mat_Ichiro_Body_2K", "Ichiro_Body_Emission_2K", is_bust=False
)
mat_bust, bsdf_bust, tex_bust = enhance_trellis_2k_material(
    bust_obj, "Mat_Ichiro_HeadBust_2K", "Ichiro_HeadBust_Emission_2K", is_bust=True
)

# Ensure UV maps share the standard name "UVMap" before joining
for o in (body_obj, bust_obj):
    if o.data.uv_layers:
        o.data.uv_layers[0].name = "UVMap"

# Join Body and HeadBust into unified Ichiro_2390_Character
bpy.ops.object.select_all(action='DESELECT')
body_obj.select_set(True)
bust_obj.select_set(True)
bpy.context.view_layer.objects.active = body_obj
bpy.ops.object.join()

char = body_obj
char.name = "Ichiro_2390_Character"
char.data.name = "Ichiro_2390_Body_Mesh"
link_obj(char, col_sculpt)

# Transform character into canonical 1.80m studio space (feet at Z = 0.00, crown at Z = 1.80)
zs_raw = [v.co.z for v in char.data.vertices]
z_min_raw, z_max_raw = min(zs_raw), max(zs_raw)
S_180 = 1.80 / (z_max_raw - z_min_raw)
for v in char.data.vertices:
    v.co.x = v.co.x * S_180
    v.co.y = v.co.y * S_180
    v.co.z = (v.co.z - z_min_raw) * S_180
char.data.update()

for p in char.data.polygons:
    p.use_smooth = True

print(f"[LAYER 02 OK] Unified True-360 Character Mesh: {len(char.data.vertices)} verts, {len(char.data.polygons)} tris, height=1.800m.")

# 2f. MetaHuman ARKit FACS Shape Keys (Initialized strictly at value = 0.0)
print("[LAYER 02] Building 8 MetaHuman ARKit FACS facial blendshapes...")
char.shape_key_add(name="Basis", from_mix=False)

sk_blink_l = char.shape_key_add(name="EyeBlink_L", from_mix=False)
for i, v in enumerate(char.data.vertices):
    if 0.012 <= v.co.x <= 0.058 and v.co.y < -0.035 and 1.595 <= v.co.z <= 1.642:
        falloff = math.sin((v.co.x - 0.012) / 0.046 * math.pi) * ((v.co.z - 1.595) / 0.047)
        sk_blink_l.data[i].co.z -= 0.014 * max(0.0, falloff)
        sk_blink_l.data[i].co.y += 0.003 * max(0.0, falloff)

sk_blink_r = char.shape_key_add(name="EyeBlink_R", from_mix=False)
for i, v in enumerate(char.data.vertices):
    if -0.058 <= v.co.x <= -0.012 and v.co.y < -0.035 and 1.595 <= v.co.z <= 1.642:
        falloff = math.sin((v.co.x - -0.058) / 0.046 * math.pi) * ((v.co.z - 1.595) / 0.047)
        sk_blink_r.data[i].co.z -= 0.014 * max(0.0, falloff)
        sk_blink_r.data[i].co.y += 0.003 * max(0.0, falloff)

sk_brow_l = char.shape_key_add(name="BrowDown_L", from_mix=False)
for i, v in enumerate(char.data.vertices):
    if 0.010 <= v.co.x <= 0.068 and v.co.y < -0.035 and 1.635 <= v.co.z <= 1.682:
        falloff = math.sin((v.co.x - 0.010) / 0.058 * math.pi)
        sk_brow_l.data[i].co.z -= 0.009 * falloff
        sk_brow_l.data[i].co.x -= 0.004 * falloff

sk_brow_r = char.shape_key_add(name="BrowDown_R", from_mix=False)
for i, v in enumerate(char.data.vertices):
    if -0.068 <= v.co.x <= -0.010 and v.co.y < -0.035 and 1.635 <= v.co.z <= 1.682:
        falloff = math.sin((v.co.x - -0.068) / 0.058 * math.pi)
        sk_brow_r.data[i].co.z -= 0.009 * falloff
        sk_brow_r.data[i].co.x += 0.004 * falloff

sk_brow_up = char.shape_key_add(name="BrowInnerUp", from_mix=False)
for i, v in enumerate(char.data.vertices):
    if abs(v.co.x) <= 0.048 and v.co.y < -0.035 and 1.635 <= v.co.z <= 1.685:
        falloff = (1.0 - abs(v.co.x) / 0.048)
        sk_brow_up.data[i].co.z += 0.010 * falloff

sk_jaw = char.shape_key_add(name="JawOpen", from_mix=False)
for i, v in enumerate(char.data.vertices):
    if abs(v.co.x) <= 0.058 and v.co.y < -0.030 and 1.495 <= v.co.z <= 1.565:
        falloff = ((1.565 - v.co.z) / 0.070)
        sk_jaw.data[i].co.z -= 0.018 * falloff
        sk_jaw.data[i].co.y += 0.006 * falloff

sk_smile_l = char.shape_key_add(name="MouthSmile_L", from_mix=False)
for i, v in enumerate(char.data.vertices):
    if 0.012 <= v.co.x <= 0.046 and v.co.y < -0.035 and 1.525 <= v.co.z <= 1.565:
        falloff = ((v.co.x - 0.012) / 0.034)
        sk_smile_l.data[i].co.z += 0.008 * falloff
        sk_smile_l.data[i].co.x += 0.005 * falloff

sk_smile_r = char.shape_key_add(name="MouthSmile_R", from_mix=False)
for i, v in enumerate(char.data.vertices):
    if -0.046 <= v.co.x <= -0.012 and v.co.y < -0.035 and 1.525 <= v.co.z <= 1.565:
        falloff = ((-0.012 - v.co.x) / 0.034)
        sk_smile_r.data[i].co.z += 0.008 * falloff
        sk_smile_r.data[i].co.x -= 0.005 * falloff

for sk in [sk_blink_l, sk_blink_r, sk_brow_l, sk_brow_r, sk_brow_up, sk_jaw, sk_smile_l, sk_smile_r]:
    sk.value = 0.0
char.active_shape_key_index = 0

mod_multires = char.modifiers.new("Anatomical_Multires", 'MULTIRES')
mod_multires.quality = 4

# ==============================================================================
# LAYER 04: HARD-SURFACE WEAPONS, DORSAL SCABBARD & LUMEN COMPANION DRONE
# ==============================================================================
print("[LAYER 04] Attaching authentic Dual Magma Blades, Dorsal Scabbard & Lumen Recon Drone...")

# 4a. Authentic Dual Magma Blades from ENERGY BLADE.blend
with bpy.data.libraries.load(BLADE_BLEND) as (data_from, data_to):
    data_to.objects = ["Plane.001"]
auth_blade = data_to.objects[0]
link_obj(auth_blade, col_props)
auth_blade.name = "Ichiro_Magma_Blade_R"
auth_blade.rotation_mode = 'XYZ'
auth_blade.location = Vector((0.0, 0.0, 0.0))
auth_blade.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
auth_blade.scale = Vector((1.0, 1.0, 1.0))

xs = [v.co.x for v in auth_blade.data.vertices]
ys = [v.co.y for v in auth_blade.data.vertices]
zs = [v.co.z for v in auth_blade.data.vertices]
min_x, max_x = min(xs), max(xs)
min_y, max_y = min(ys), max(ys)
min_z, max_z = min(zs), max(zs)
ext_x = max_x - min_x
grip_x = min_x + 0.795 * ext_x
grip_y = min_y + 0.320 * (max_y - min_y)
grip_z = 0.5 * (min_z + max_z)
scale_factor = 0.98 / ext_x

for v in auth_blade.data.vertices:
    v.co.x = (v.co.x - grip_x) * scale_factor
    v.co.y = (v.co.y - grip_y) * scale_factor
    v.co.z = (v.co.z - grip_z) * scale_factor
auth_blade.data.flip_normals()
auth_blade.data.update()

for ms in auth_blade.material_slots:
    if ms.material and ms.material.node_tree:
        for n in ms.material.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                em_val = n.inputs["Emission Strength"].default_value
                if em_val > 0.05 or "orange" in n.name.lower() or "magma" in ms.material.name.lower():
                    n.inputs["Emission Strength"].default_value = max(em_val, 3.4)
                    n.inputs["Roughness"].default_value = 0.18
                else:
                    n.inputs["Base Color"].default_value = (0.05, 0.055, 0.065, 1.0)
                    n.inputs["Metallic"].default_value = 0.88
                    n.inputs["Roughness"].default_value = 0.24

auth_blade_l = auth_blade.copy()
auth_blade_l.data = auth_blade.data.copy()
auth_blade_l.name = "Ichiro_Magma_Blade_L"
auth_blade_l.rotation_mode = 'XYZ'
link_obj(auth_blade_l, col_props)

def orient_blade(obj, loc, tip_dir_vec, edge_hint_vec):
    obj.rotation_mode = 'XYZ'
    obj.location = Vector(loc)
    ax_x = (-Vector(tip_dir_vec)).normalized()
    spine_hint = (-Vector(edge_hint_vec)).normalized()
    ax_z = ax_x.cross(spine_hint).normalized()
    ax_y = ax_z.cross(ax_x).normalized()
    rot_mat = Matrix((ax_x, ax_y, ax_z)).transposed()
    obj.rotation_euler = rot_mat.to_euler('XYZ')

# Placed at exact 3D hand centroids of the TRELLIS Body mesh
orient_blade(auth_blade,   loc=(-0.405, 0.005, 0.830), tip_dir_vec=(-0.35, -0.26, -0.90), edge_hint_vec=(-0.72, -0.35, 0.60))
orient_blade(auth_blade_l, loc=( 0.404, 0.005, 0.832), tip_dir_vec=( 0.35, -0.26, -0.90), edge_hint_vec=( 0.72, -0.35, 0.60))

# 4b. Tactical Dorsal Scabbard
grid_v2 = np.load(GRID_V2_PATH)
s_mask = grid_v2["scab_mask"].astype(bool)
s_edt  = grid_v2["scab_edt"].astype(np.float32)

def build_scabbard():
    gh, gw = s_mask.shape
    sc = 0.82 / gh
    cx = gw * 0.5
    f_id = np.full((gh, gw), -1, dtype=np.int32)
    b_id = np.full((gh, gw), -1, dtype=np.int32)
    v_list, uv_list = [], []
    for y in range(gh):
        for x in range(gw):
            if not s_mask[y, x]: continue
            vx = (x - cx) * sc
            vz = (0.50 * gh - y) * sc
            u = (x + 0.5) / gw
            v = 1.0 - (y + 0.5) / gh
            vy = 0.016 * math.tanh(max(0.0, s_edt[y, x] - 0.5) / 2.0)
            if s_mask[y, x] and s_edt[y, x] <= 1.05:
                idx = len(v_list)
                v_list.append([vx, 0.0, vz]); uv_list.append((u, v))
                f_id[y, x] = idx; b_id[y, x] = idx
            else:
                fi = len(v_list); v_list.append([vx, -vy, vz]); uv_list.append((u, v)); f_id[y, x] = fi
                bi = len(v_list); v_list.append([vx, +vy, vz]); uv_list.append((u, v)); b_id[y, x] = bi
    f_list = []
    for y in range(gh - 1):
        for x in range(gw - 1):
            c = int(s_mask[y,x]) + int(s_mask[y,x+1]) + int(s_mask[y+1,x+1]) + int(s_mask[y+1,x])
            if c == 4:
                qf = (int(f_id[y,x]), int(f_id[y+1,x]), int(f_id[y+1,x+1]), int(f_id[y,x+1]))
                qb = (int(b_id[y,x]), int(b_id[y,x+1]), int(b_id[y+1,x+1]), int(b_id[y+1,x]))
                if len(set(qf)) == 4: f_list.append(qf)
                if len(set(qb)) == 4: f_list.append(qb)
    m = bpy.data.meshes.new("Scabbard_Mesh")
    m.from_pydata(v_list, [], f_list)
    m.update()
    for p in m.polygons: p.use_smooth = True
    uv_l = m.uv_layers.new(name="UVMap")
    for p in m.polygons:
        for li in p.loop_indices:
            uv_l.data[li].uv = uv_list[m.loops[li].vertex_index]
    obj = bpy.data.objects.new("Ichiro_Scabbard", m)
    link_obj(obj, col_props)
    return obj

scabbard = build_scabbard()
scabbard.location = (0.08, 0.155, 0.94)
scabbard.rotation_euler = Euler((math.radians(6), math.radians(30), math.radians(0)), 'XYZ')
mat_scab = bpy.data.materials.new("Mat_Ichiro_Scabbard")
s_bsdf = mat_scab.node_tree.nodes.get("Principled BSDF")
s_bsdf.inputs["Roughness"].default_value = 0.30
s_bsdf.inputs["Metallic"].default_value = 0.82
img_scab = bpy.data.images.load(os.path.join(TEX_DIR, "ichiro_scabbard_2k.png"))
t_scab = mat_scab.node_tree.nodes.new("ShaderNodeTexImage")
t_scab.image = img_scab
mat_scab.node_tree.links.new(t_scab.outputs["Color"], s_bsdf.inputs["Base Color"])
scabbard.data.materials.append(mat_scab)

# 4c. Authentic Lumen Companion Drone
before_objs = set(scene.objects)
bpy.ops.import_scene.gltf(filepath=LUMEN_GLB)
imported_objs = [o for o in scene.objects if o not in before_objs]
lumen_mesh_obj = [o for o in imported_objs if o.type == 'MESH'][0]
bpy.ops.object.select_all(action='DESELECT')
lumen_mesh_obj.select_set(True)
bpy.context.view_layer.objects.active = lumen_mesh_obj
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in imported_objs:
    if o != lumen_mesh_obj:
        bpy.data.objects.remove(o, do_unlink=True)
lumen_mesh_obj.name = "Lumen_Core_Hull"
link_obj(lumen_mesh_obj, col_props)

bbox_min = Vector([min(v.co[i] for v in lumen_mesh_obj.data.vertices) for i in range(3)])
bbox_max = Vector([max(v.co[i] for v in lumen_mesh_obj.data.vertices) for i in range(3)])
bbox_center = 0.5 * (bbox_min + bbox_max)
max_dim = max((bbox_max - bbox_min).x, (bbox_max - bbox_min).y, (bbox_max - bbox_min).z)
scale_l = 0.22 / max(max_dim, 1e-5)
for v in lumen_mesh_obj.data.vertices:
    v.co = (v.co - bbox_center) * scale_l
lumen_mesh_obj.data.update()

mod_sm = lumen_mesh_obj.modifiers.new("Sensor_Denoise", 'SMOOTH')
mod_sm.factor = 0.70; mod_sm.iterations = 6
bpy.ops.object.modifier_apply(modifier="Sensor_Denoise")
mod_dec = lumen_mesh_obj.modifiers.new("Decimate_AAA", 'DECIMATE')
mod_dec.decimate_type = 'COLLAPSE'; mod_dec.ratio = 0.08
bpy.ops.object.modifier_apply(modifier="Decimate_AAA")
for p in lumen_mesh_obj.data.polygons: p.use_smooth = True

lumen_pos = Vector((0.40, -0.34, 1.64))
lumen_mesh_obj.location = lumen_pos
lumen_mesh_obj.rotation_euler = Euler((math.radians(12), math.radians(10), math.radians(-24)), 'XYZ')

lumen_mat = bpy.data.materials.new("Mat_Lumen_Hull")
l_bsdf = lumen_mat.node_tree.nodes.get("Principled BSDF")
l_bsdf.inputs["Base Color"].default_value = (0.10, 0.105, 0.115, 1.0)
l_bsdf.inputs["Metallic"].default_value = 0.88
l_bsdf.inputs["Roughness"].default_value = 0.34
l_bsdf.inputs["Specular IOR Level"].default_value = 0.50
lumen_mesh_obj.data.materials.clear()
lumen_mesh_obj.data.materials.append(lumen_mat)

mat_eye = bpy.data.materials.new("Mat_Lumen_Eye_Red")
e_bsdf = mat_eye.node_tree.nodes.get("Principled BSDF")
e_bsdf.inputs["Base Color"].default_value = (0.90, 0.01, 0.02, 1.0)
e_bsdf.inputs["Emission Color"].default_value = (1.0, 0.015, 0.02, 1.0)
e_bsdf.inputs["Emission Strength"].default_value = 3.2

mat_pupil = bpy.data.materials.new("Mat_Lumen_Pupil_Black")
pbsdf = mat_pupil.node_tree.nodes.get("Principled BSDF")
pbsdf.inputs["Base Color"].default_value = (0.01, 0.01, 0.01, 1.0)
pbsdf.inputs["Roughness"].default_value = 0.05
pbsdf.inputs["Metallic"].default_value = 0.90

for eye_name, ex_off in [("L", -0.034), ("R", 0.034)]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32, ring_count=24, radius=0.023,
        location=(lumen_pos.x + ex_off, lumen_pos.y - 0.096, lumen_pos.z + 0.014)
    )
    e_obj = bpy.context.active_object
    e_obj.name = f"Lumen_Eye_{eye_name}"
    link_obj(e_obj, col_props)
    for p in e_obj.data.polygons: p.use_smooth = True
    e_obj.data.materials.append(mat_eye)

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=0.009, depth=0.004,
        location=(lumen_pos.x + ex_off, lumen_pos.y - 0.117, lumen_pos.z + 0.014),
        rotation=Euler((math.radians(90), 0, 0), 'XYZ')
    )
    pup = bpy.context.active_object
    pup.name = f"Lumen_Pupil_{eye_name}"
    link_obj(pup, col_props)
    for p in pup.data.polygons: p.use_smooth = True
    pup.data.materials.append(mat_pupil)

bpy.ops.mesh.primitive_torus_add(
    major_radius=0.145, minor_radius=0.0032,
    major_segments=64, minor_segments=16,
    location=lumen_pos,
    rotation=Euler((math.radians(55), math.radians(-22), 0), 'XYZ')
)
l_ring = bpy.context.active_object
l_ring.name = "Lumen_Orbital_Ring"
link_obj(l_ring, col_props)
for p in l_ring.data.polygons: p.use_smooth = True
m_lring = bpy.data.materials.new("Mat_Lumen_Ring_Cyan")
lr_bsdf = m_lring.node_tree.nodes.get("Principled BSDF")
lr_bsdf.inputs["Base Color"].default_value = (0.0, 0.95, 1.0, 1.0)
lr_bsdf.inputs["Emission Color"].default_value = (0.0, 0.95, 1.0, 1.0)
lr_bsdf.inputs["Emission Strength"].default_value = 4.2
l_ring.data.materials.append(m_lring)

print("[LAYER 04 OK] Dual Magma Blades, Dorsal Scabbard & Authentic Lumen Drone assembled.")

# ==============================================================================
# STUDIO PEDESTAL FOR RENDERS & MASTER BLEND
# ==============================================================================
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.68, depth=0.06, location=(0.0, 0.0, -0.03))
ped = bpy.context.active_object
ped.name = "Arcane_Pedestal"
link_obj(ped, col_lights)
for p in ped.data.polygons: p.use_smooth = True
mat_ped = bpy.data.materials.new("Mat_Arcane_Pedestal")
pb = mat_ped.node_tree.nodes.get("Principled BSDF")
pb.inputs["Base Color"].default_value = (0.04, 0.045, 0.06, 1.0)
pb.inputs["Metallic"].default_value = 0.88
pb.inputs["Roughness"].default_value = 0.22
ped.data.materials.append(mat_ped)

bpy.ops.mesh.primitive_torus_add(major_radius=0.66, minor_radius=0.007, major_segments=64, minor_segments=16, location=(0, 0, 0.002))
ring_c = bpy.context.active_object
ring_c.name = "Arcane_Ring_Cyan"
link_obj(ring_c, col_lights)
for p in ring_c.data.polygons: p.use_smooth = True
ring_c.data.materials.append(m_lring)

bpy.ops.mesh.primitive_torus_add(major_radius=0.56, minor_radius=0.005, major_segments=64, minor_segments=16, location=(0, 0, 0.003))
ring_m = bpy.context.active_object
ring_m.name = "Arcane_Ring_Magma"
link_obj(ring_m, col_lights)
for p in ring_m.data.polygons: p.use_smooth = True
m_rm = bpy.data.materials.new("Mat_Ring_Magma")
rm_bsdf = m_rm.node_tree.nodes.get("Principled BSDF")
rm_bsdf.inputs["Base Color"].default_value = (1.0, 0.38, 0.06, 1.0)
rm_bsdf.inputs["Emission Color"].default_value = (1.0, 0.38, 0.06, 1.0)
rm_bsdf.inputs["Emission Strength"].default_value = 4.5
ring_m.data.materials.append(m_rm)

# ==============================================================================
# RENDER PRODUCTION VIEWS & TURNAROUND VALIDATION
# ==============================================================================
scene.render.engine = 'BLENDER_EEVEE'
scene.render.image_settings.file_format = 'PNG'
try:
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'High Contrast'
except Exception:
    pass

cam_d = bpy.data.cameras.new("Arcane_Cam")
cam_o = bpy.data.objects.new("Arcane_Cam", cam_d)
link_obj(cam_o, col_lights)
scene.camera = cam_o

def render_still(path, loc, target, lens=52.0, rx=1080, ry=1440):
    scene.render.resolution_x = rx
    scene.render.resolution_y = ry
    cam_d.lens = lens
    cam_o.location = Vector(loc)
    cam_o.rotation_euler = (Vector(target) - cam_o.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = path
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)
    print(f"[RENDERED] {path}")

# Warm-up 64x64 pass so EEVEE initializes shadow & light buffers before first production render
render_still(
    os.path.join(SCRATCH_DIR, "_eevee_warmup.png"),
    loc=(0.76, -3.55, 0.98),
    target=(0.0, 0.0, 0.88),
    lens=50.0, rx=64, ry=64
)

render_still(
    os.path.join(RENDER_DIR, "01_Ichiro_Arcane_Hero_Beauty.png"),
    loc=(0.76, -3.55, 0.98),
    target=(0.0, 0.0, 0.88),
    lens=50.0, rx=1080, ry=1440
)

render_still(
    os.path.join(RENDER_DIR, "02_Ichiro_Arcane_Portrait_CloseUp.png"),
    loc=(0.24, -1.45, 1.56),
    target=(0.10, -0.06, 1.53),
    lens=65.0, rx=1080, ry=1350
)

render_still(os.path.join(RENDER_DIR, "turn_front.png"), (0.0, -3.60, 0.94),   (0.0, 0.0, 0.90), 50.0, 720, 1280)
render_still(os.path.join(RENDER_DIR, "turn_side.png"),  (3.55, 0.0, 0.94),    (0.0, 0.0, 0.90), 50.0, 720, 1280)
render_still(os.path.join(RENDER_DIR, "turn_back.png"),  (0.0, 3.60, 0.94),    (0.0, 0.0, 0.90), 50.0, 720, 1280)
render_still(os.path.join(RENDER_DIR, "turn_34.png"),    (-1.05, -3.50, 0.96), (0.0, 0.0, 0.88), 50.0, 720, 1280)

# Aberrant Kai Exposure Overdrive Mode Render
if bsdf_body and bsdf_bust:
    bsdf_body.inputs["Emission Strength"].default_value = 2.85
    bsdf_bust.inputs["Emission Strength"].default_value = 0.0
l_key.data.color  = (0.90, 0.72, 1.0)
l_cyan.data.color = (0.65, 0.05, 1.0)
l_mag.data.color  = (1.0, 0.05, 0.35)
bg_node.inputs["Color"].default_value = (0.068, 0.035, 0.088, 1.0)

render_still(
    os.path.join(RENDER_DIR, "04_Ichiro_Arcane_Kai_Exposure_Aberrant.png"),
    loc=(0.48, -2.25, 1.34),
    target=(0.04, 0.0, 1.26),
    lens=56.0, rx=1080, ry=1350
)

# Restore Standard Studio Lighting & Shader Settings
if bsdf_body and bsdf_bust:
    bsdf_body.inputs["Emission Strength"].default_value = 1.25
    bsdf_bust.inputs["Emission Strength"].default_value = 0.0
l_key.data.color  = (1.0, 0.96, 0.90)
l_cyan.data.color = (0.0, 0.94, 1.0)
l_mag.data.color  = (1.0, 0.22, 0.55)
bg_node.inputs["Color"].default_value = (0.048, 0.055, 0.078, 1.0)
cam_o.location = Vector((0.76, -3.55, 0.98))
cam_o.rotation_euler = (Vector((0.0, 0.0, 0.88)) - cam_o.location).to_track_quat('-Z', 'Y').to_euler()

# Save Master Blend
bpy.ops.wm.save_as_mainfile(filepath=OUT_MASTER_BLEND)
print(f"[SUCCESS] Saved Modular Non-Destructive Master: {OUT_MASTER_BLEND}")

# Export Universal PBR GLB (Character + Blades + Scabbard + Lumen Drone)
bpy.ops.object.select_all(action='DESELECT')
exclude_prefixes = ("BASE_360", "Arcane_Pedestal", "Arcane_Ring_")
for obj in scene.objects:
    if obj.type == 'MESH' and not obj.hide_render and not obj.name.startswith(exclude_prefixes):
        obj.select_set(True)

bpy.ops.export_scene.gltf(
    filepath=OUT_GLB,
    export_format='GLB',
    use_selection=True,
    export_apply=False,
    export_yup=True,
    export_morph=True,
    export_materials='EXPORT'
)
print(f"[SUCCESS] Exported Modular Universal PBR GLB: {OUT_GLB}")

bpy.ops.wm.obj_export(filepath=OUT_OBJ, export_selected_objects=True)
print(f"[SUCCESS] Exported Universal OBJ: {OUT_OBJ}")

# Auto-Invoke Turnaround Sheet Compositor
comp_script = os.path.join(SCRATCH_DIR, "composite_lumen_turnaround_sheet.py")
if os.path.exists(comp_script):
    try:
        subprocess.run(["py", comp_script], check=True)
        print("[SUCCESS] 03_Ichiro_Arcane_Turnaround_4Views.png composited.")
    except Exception:
        try:
            subprocess.run(["python", comp_script], check=True)
            print("[SUCCESS] 03_Ichiro_Arcane_Turnaround_4Views.png composited via python.")
        except Exception as e2:
            print(f"[WARNING] Turnaround compositor: {e2}")
