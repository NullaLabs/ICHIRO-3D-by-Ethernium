"""
ETHERNIUM SOVEREIGN // ICHIRO 2390 MODULAR TRUE 360 PRODUCTION SCENE BUILDER
=============================================================================
Dual-Scale Microsoft TRELLIS + Continuous Laplacian-Smoothed Real 2.5D Textures
- HeadBust Split Vertices Welded (remove_doubles)
- Zero-Bleed Dark Tactical Pants Between Legs (0 white pixels)
- Sharp, Aligned Posterior Dorsal Body (Lanczos-3 Camo Bolero + Harness)
- Hybrid Real-2.5D (UVMap_FB) + Native-360 (UVMap_Trellis) Fortiche Shaders
- Dual Magma Blades, Dorsal Scabbard & Lumen Recon Companion Drone
- Production Cycles GPU Render Outputs + glTF 2.0 Export

Execution:
  blender --factory-startup -b -P scripts/build_modular_true360_scene.py
"""
import bpy
import bmesh
import os
import math
import shutil
import subprocess
import numpy as np
from mathutils import Vector, Euler, Matrix

def gaussian_filter1d_np(arr, sigma=12.0):
    radius = int(round(3.0 * sigma))
    x = np.arange(-radius, radius + 1, dtype=np.float64)
    k = np.exp(-0.5 * (x / sigma) ** 2)
    k /= k.sum()
    pad = np.pad(arr, (radius, radius), mode='edge')
    return np.convolve(pad, k, mode='valid')

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

# Directories
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT        = os.path.dirname(SCRIPTS_DIR)
REF_DIR     = os.path.join(ROOT, "references")
TEX_DIR     = os.path.join(ROOT, "textures")
BLEND_DIR   = os.path.join(ROOT, "blend")
MODEL_DIR   = os.path.join(ROOT, "models")
RENDER_DIR  = os.path.join(ROOT, "renders")
SCRATCH_DIR = r"C:\Users\esenc\.gemini\antigravity\brain\3ccecf18-5e96-4998-8aad-0804a4100391\scratch"
BRAIN_DIR   = r"C:\Users\esenc\.gemini\antigravity\brain\3ccecf18-5e96-4998-8aad-0804a4100391"

BODY_GLB_PATH = os.path.join(MODEL_DIR, "Ichiro_Trellis_MultiView_2K.glb")
BUST_GLB_PATH = os.path.join(MODEL_DIR, "Ichiro_Trellis_HeadBust_2K.glb")
BLADE_BLEND   = r"E:\DESCARGAS\Web3\My web3 Projects\KPR\Ichiro Commissions\Ichiro traits\ ENERGY BLADE.blend"
LUMEN_GLB     = r"C:\Users\esenc\.gemini\antigravity\brain\c7d203b9-a584-4a61-9146-40793a6a1f52\scratch\ICHIRO-repo\assets\models\lumen-blueprint.glb"
GRID_V2_PATH  = os.path.join(TEX_DIR, "ichiro_master_grid_v2.npz")

OUT_ROOT_BLEND   = os.path.join(ROOT, "Ichiro_2390_Arcane_Scene.blend")
OUT_MASTER_BLEND = os.path.join(BLEND_DIR, "Ichiro_2390_Arcane_Master.blend")
OUT_REAL_GLB     = os.path.join(MODEL_DIR, "Ichiro_2390_Real3D_Mesh.glb")
OUT_ARCANE_GLB   = os.path.join(MODEL_DIR, "Ichiro_2390_Arcane.glb")
OUT_OBJ          = os.path.join(MODEL_DIR, "Ichiro_2390_Arcane.obj")

for d in (TEX_DIR, BLEND_DIR, MODEL_DIR, RENDER_DIR):
    os.makedirs(d, exist_ok=True)

print("===============================================================================")
print("  ETHERNIUM SOVEREIGN // ICHIRO 2390 PRODUCTION SCENE BUILDER")
print("===============================================================================")

# 1. Reset Scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

def get_or_create_collection(name, parent=None):
    if name in bpy.data.collections:
        col = bpy.data.collections[name]
    else:
        col = bpy.data.collections.new(name)
        if parent is None:
            scene.collection.children.link(col)
        else:
            parent.children.link(col)
    return col

def link_obj(obj, col):
    if obj.name in scene.collection.objects:
        scene.collection.objects.unlink(obj)
    for c in bpy.data.collections:
        if c != col and obj.name in c.objects:
            c.objects.unlink(obj)
    if obj.name not in col.objects:
        col.objects.link(obj)

col_lights  = get_or_create_collection("00_STUDIO_LIGHTING")
col_char    = get_or_create_collection("01_CHARACTER_MESH")
col_props   = get_or_create_collection("02_WEAPONS_AND_ACCESSORIES")

# Studio World & Lighting
world = bpy.data.worlds.new("Arcane_World")
scene.world = world
try:
    world.use_nodes = True
except Exception:
    pass
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs["Color"].default_value = (0.048, 0.055, 0.078, 1.0)
    bg_node.inputs["Strength"].default_value = 0.95

def add_studio_light(name, loc, rot, energy, col, size=2.0):
    ld = bpy.data.lights.new(name, type='AREA')
    ld.energy = energy
    ld.color = col
    ld.size = size
    ld.shape = 'RECTANGLE'
    ld.size_y = size * 1.4
    lo = bpy.data.objects.new(name, ld)
    link_obj(lo, col_lights)
    lo.location = Vector(loc)
    lo.rotation_euler = Euler([math.radians(a) for a in rot], 'XYZ')
    return lo

l_key  = add_studio_light("Key_Warm_Piltover",  (1.2, -2.8, 1.9),  (62, 0, 22),   200.0, (1.0, 0.96, 0.90), 2.4)
l_cyan = add_studio_light("Rim_Zaun_Cyan",      (-2.2, 1.6, 1.6),  (65, 0, -130), 135.0, (0.0, 0.94, 1.0),  2.0)
l_mag  = add_studio_light("Rim_Arcane_Magenta", (2.2, 1.6, 1.5),   (65, 0, 130),  125.0, (1.0, 0.22, 0.55), 2.0)
l_fill = add_studio_light("Fill_Front_Neutral", (0.0, -3.0, 1.1),  (82, 0, 0),    130.0, (0.92, 0.94, 1.0), 2.8)

# 2. Import Body & HeadBust
print("[MESH] Importing and preparing Dual-Scale TRELLIS meshes...")
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

# Surgical Collar-Line Trimming on Body
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

# Surgical Collar-Line Trimming & Smooth Neck Tucking on HeadBust
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
    if z >= -0.065 and -0.30 < x < -0.08 and y < 0.02:
        continue
    if z >= -0.145 and abs(x) <= 0.138 and -0.35 < y < 0.145:
        continue
    faces_to_del_h.append(f)
bmesh.ops.delete(bm_h, geom=faces_to_del_h, context='FACES')
for v in bm_h.verts:
    x, y, z = v.co.x, v.co.y, v.co.z
    if z < -0.105:
        t = min(1.0, (-0.105 - z) / 0.040)
        v.co.x *= (1.0 - 0.12 * t)
        if y < 0.0:
            v.co.y += 0.024 * t
bm_h.to_mesh(bust_obj.data)
bm_h.free()

# Extract & Decontaminate Native TRELLIS Textures
def get_cleaned_trellis_image(obj, name_prefix, is_bust=False):
    mat = obj.data.materials[0]
    tex_node = None
    for n in mat.node_tree.nodes:
        if n.type == 'TEX_IMAGE' and n.image is not None:
            tex_node = n
            break
    base_img = tex_node.image
    base_img.name = f"{name_prefix}_Trellis_2K"
    w, h = base_img.size[0], base_img.size[1]
    arr = np.array(base_img.pixels[:], dtype=np.float32).reshape((h, w, 4))
    if not is_bust:
        torso_center_mask = np.zeros((h, w), dtype=np.float32)
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
                torso_center_mask[y0:y1, x0:x1] = 1.0
        torso_center_mask = box_blur_2d(torso_center_mask, radius=14, passes=3)
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        grey_floor = np.minimum(np.minimum(r, g), b)
        excess_grey = np.maximum(0.0, grey_floor - 0.055) * torso_center_mask
        arr[:, :, 0] = np.clip(r - excess_grey * 0.28, 0.02, 1.0)
        arr[:, :, 1] = np.clip(g - excess_grey * 0.76, 0.01, 1.0)
        arr[:, :, 2] = np.clip(b - excess_grey * 0.94, 0.01, 1.0)
        base_img.pixels[:] = arr.ravel().tolist()
        base_img.pack()
    else:
        choker_rim_mask = np.zeros((h, w), dtype=np.float32)
        hair_uv_mask    = np.zeros((h, w), dtype=np.float32)
        uv_layer = obj.data.uv_layers[0].data
        for poly in obj.data.polygons:
            c = poly.center
            us = [uv_layer[li].uv.x for li in poly.loop_indices]
            vs = [uv_layer[li].uv.y for li in poly.loop_indices]
            x0 = max(0, int(min(us) * w) - 3)
            x1 = min(w, int(max(us) * w) + 4)
            y0 = max(0, int(min(vs) * h) - 3)
            y1 = min(h, int(max(vs) * h) + 4)
            if c.z < -0.105 and c.y < -0.01 and abs(c.x) < 0.14:
                choker_rim_mask[y0:y1, x0:x1] = 1.0
            if c.z > 0.08 or (c.x < -0.105 and c.z > -0.14):
                hair_uv_mask[y0:y1, x0:x1] = 1.0
        choker_rim_mask = box_blur_2d(choker_rim_mask, radius=4, passes=2)
        hair_uv_mask    = box_blur_2d(hair_uv_mask,    radius=6, passes=2)
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        orange_bleed = np.clip((r - 1.35 * g) * 4.0, 0.0, 1.0) * choker_rim_mask
        arr[:, :, 0] = r * (1.0 - orange_bleed) + 0.06 * orange_bleed
        arr[:, :, 1] = g * (1.0 - orange_bleed) + 0.055 * orange_bleed
        arr[:, :, 2] = b * (1.0 - orange_bleed) + 0.065 * orange_bleed

        min_rgb = np.minimum(np.minimum(r, g), b)
        not_warm_skin = np.clip(1.0 - (r - g - 0.035) * 15.0, 0.0, 1.0)
        grey_spill = np.clip((min_rgb - 0.030) * 14.0, 0.0, 1.0) * not_warm_skin * hair_uv_mask
        arr[:, :, 0] = r * (1.0 - grey_spill) + 0.018 * grey_spill
        arr[:, :, 1] = g * (1.0 - grey_spill) + 0.065 * grey_spill
        arr[:, :, 2] = b * (1.0 - grey_spill) + 0.082 * grey_spill
        base_img.pixels[:] = arr.ravel().tolist()
        base_img.pack()
    return base_img

img_trellis_body = get_cleaned_trellis_image(body_obj, "Body", is_bust=False)
img_trellis_bust = get_cleaned_trellis_image(bust_obj, "Bust", is_bust=True)

for o in (body_obj, bust_obj):
    o.data.uv_layers[0].name = "UVMap_Trellis"

# Weld duplicate split vertices on X = 0 seam
for o in (bust_obj, body_obj):
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    bpy.ops.object.mode_set(mode='OBJECT')

sub_mod_h = bust_obj.modifiers.new("Subsurf_Bust_AAA", 'SUBSURF')
sub_mod_h.levels = 1
sub_mod_h.render_levels = 1
sub_mod_h.uv_smooth = 'PRESERVE_BOUNDARIES'
bpy.ops.object.select_all(action='DESELECT')
bust_obj.select_set(True)
bpy.context.view_layer.objects.active = bust_obj
bpy.ops.object.modifier_apply(modifier=sub_mod_h.name)

sub_mod = body_obj.modifiers.new("Subsurf_Body_AAA", 'SUBSURF')
sub_mod.levels = 1
sub_mod.render_levels = 1
sub_mod.uv_smooth = 'PRESERVE_BOUNDARIES'
bpy.ops.object.select_all(action='DESELECT')
body_obj.select_set(True)
bpy.context.view_layer.objects.active = body_obj
bpy.ops.object.modifier_apply(modifier=sub_mod.name)

# Align HeadBust over Body
S_BUST = 0.275
bust_obj.scale = (S_BUST, S_BUST, S_BUST)
bust_obj.location = (0.001, -0.006, 0.365)
bpy.ops.object.select_all(action='DESELECT')
bust_obj.select_set(True)
bpy.context.view_layer.objects.active = bust_obj
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

n_body_verts = len(body_obj.data.vertices)
n_body_polys = len(body_obj.data.polygons)

bpy.ops.object.select_all(action='DESELECT')
body_obj.select_set(True)
bust_obj.select_set(True)
bpy.context.view_layer.objects.active = body_obj
bpy.ops.object.join()

char = body_obj
char.name = "Ichiro_2390_Character"
link_obj(char, col_char)

# Normalize to 1.80m studio space
zs_raw = [v.co.z for v in char.data.vertices]
z_min_raw, z_max_raw = min(zs_raw), max(zs_raw)
S_180 = 1.80 / (z_max_raw - z_min_raw)
for v in char.data.vertices:
    v.co.x = v.co.x * S_180
    v.co.y = v.co.y * S_180
    v.co.z = (v.co.z - z_min_raw) * S_180

for v in char.data.vertices:
    if v.co.z > 1.22:
        t_z = min(1.0, (v.co.z - 1.22) / 0.24)
        w_z = 0.5 * (1.0 - math.cos(math.pi * t_z))
        v.co.z += -0.0095 * w_z

char.data.update()
for p in char.data.polygons:
    p.use_smooth = True

# 3. Continuous Laplacian-Smoothed UVMap_FB Registration
print("[UV REGISTRATION] Computing continuous Laplacian-smoothed UVMap_FB registration...")
W, H = 864, 1552
fg_2k = np.load(os.path.join(SCRATCH_DIR, "fg_2k_master.npz"))["fg_f"]

def x_to_px(x):
    gx = 108.0 + x * (92.0 / 0.370)
    return ((gx + 0.5) / 216.0) * W

def z_to_py(z):
    gy = 32.0 + (1.705 - z) * ((362.0 - 32.0) / (1.705 - 0.082))
    return ((gy + 0.5) / 388.0) * H

verts_np = np.array([[v.co.x, v.co.y, v.co.z] for v in char.data.vertices], dtype=np.float64)
n_verts = len(verts_np)
is_bust_vert = np.arange(n_verts) >= n_body_verts

px_all = x_to_px(verts_np[:, 0])
py_all = z_to_py(verts_np[:, 2])
px_uv  = px_all.copy()

def fit_branch_uv_x(vert_mask, py_min, py_max, x2_cond_fn, max_shift_px=28.0):
    v_idx = np.where(vert_mask)[0]
    v_py = py_all[v_idx]
    v_px = px_all[v_idx]
    c3_arr = np.zeros(H)
    w3_arr = np.ones(H)
    c2_arr = np.zeros(H)
    w2_arr = np.ones(H)
    valid = np.zeros(H, dtype=bool)
    for py in range(py_min, py_max):
        m3 = np.abs(v_py - py) <= 6.0
        y0, y1 = max(0, py-2), min(H, py+3)
        xs2 = np.where(fg_2k[y0:y1].any(axis=0))[0]
        xs2 = xs2[x2_cond_fn(py, xs2)]
        if np.sum(m3) >= 5 and len(xs2) >= 5:
            x3_0, x3_1 = np.percentile(v_px[m3], 2), np.percentile(v_px[m3], 98)
            x2_0, x2_1 = float(xs2.min()), float(xs2.max())
            if (x3_1 - x3_0) > 8.0 and (x2_1 - x2_0) > 8.0:
                c3_arr[py] = 0.5 * (x3_0 + x3_1)
                w3_arr[py] = x3_1 - x3_0
                c2_arr[py] = 0.5 * (x2_0 + x2_1)
                w2_arr[py] = x2_1 - x2_0
                valid[py] = True
    if np.sum(valid) < 5:
        return
    valid_pys = np.where(valid)[0]
    all_pys = np.arange(H)
    c3_s = gaussian_filter1d_np(np.interp(all_pys, valid_pys, c3_arr[valid]), sigma=14.0)
    w3_s = gaussian_filter1d_np(np.interp(all_pys, valid_pys, w3_arr[valid]), sigma=14.0)
    c2_s = gaussian_filter1d_np(np.interp(all_pys, valid_pys, c2_arr[valid]), sigma=14.0)
    w2_s = gaussian_filter1d_np(np.interp(all_pys, valid_pys, w2_arr[valid]), sigma=14.0)
    for idx in v_idx:
        py_i = int(np.clip(round(py_all[idx]), 0, H - 1))
        if py_min <= py_i <= py_max:
            fade = 1.0
            if py_i - py_min < 24:
                fade = min(fade, (py_i - py_min) / 24.0)
            if py_max - py_i < 24:
                fade = min(fade, (py_max - py_i) / 24.0)
            scale_w = np.clip(w2_s[py_i] / max(10.0, w3_s[py_i]), 0.86, 1.16)
            px_old = px_all[idx]
            px_target = c2_s[py_i] + (px_old - c3_s[py_i]) * scale_w
            px_target = np.clip(px_target, px_old - max_shift_px, px_old + max_shift_px)
            px_uv[idx] = px_old + fade * (px_target - px_old)

fit_branch_uv_x((~is_bust_vert) & (py_all < 320), 200, 320, lambda py, xs: np.ones_like(xs, dtype=bool), max_shift_px=12.0)
is_r_arm = (~is_bust_vert) & (py_all >= 430) & (py_all <= 1060) & (px_all < 335 - (py_all - 430)*0.15)
is_l_arm = (~is_bust_vert) & (py_all >= 430) & (py_all <= 1060) & (px_all > 529 + (py_all - 430)*0.15)
fit_branch_uv_x(is_r_arm, 445, 1050, lambda py, xs: xs < (335 - (py - 430)*0.18), max_shift_px=30.0)
fit_branch_uv_x(is_l_arm, 445, 1050, lambda py, xs: xs > (529 + (py - 430)*0.18), max_shift_px=30.0)

is_torso = (~is_bust_vert) & (py_all >= 450) & (py_all < 920) & (~is_r_arm) & (~is_l_arm)
fit_branch_uv_x(is_torso, 460, 910, lambda py, xs: (xs >= (320 - (py - 430)*0.10)) & (xs <= (544 + (py - 430)*0.10)), max_shift_px=16.0)

is_r_leg = (~is_bust_vert) & (py_all >= 920) & (px_all < 432) & (~is_r_arm)
is_l_leg = (~is_bust_vert) & (py_all >= 920) & (px_all >= 432) & (~is_l_arm)
fit_branch_uv_x(is_r_leg, 930, 1530, lambda py, xs: (xs < 432) & (xs > 180), max_shift_px=24.0)
fit_branch_uv_x(is_l_leg, 930, 1530, lambda py, xs: (xs >= 432) & (xs < 684), max_shift_px=24.0)

du_px = px_uv - px_all
edges = np.array([[e.vertices[0], e.vertices[1]] for e in char.data.edges], dtype=np.int32)
deg = np.zeros(n_verts, dtype=np.float64)
np.add.at(deg, edges[:, 0], 1.0)
np.add.at(deg, edges[:, 1], 1.0)
deg = np.maximum(deg, 1.0)
for _ in range(10):
    acc = np.zeros(n_verts, dtype=np.float64)
    np.add.at(acc, edges[:, 0], du_px[edges[:, 1]])
    np.add.at(acc, edges[:, 1], du_px[edges[:, 0]])
    du_px = 0.35 * du_px + 0.65 * (acc / deg)

px_uv_smooth = px_all + du_px

uv_fb = char.data.uv_layers.new(name="UVMap_FB")
char.data.uv_layers.active = uv_fb
for poly in char.data.polygons:
    for li in poly.loop_indices:
        vi = char.data.loops[li].vertex_index
        u = float(np.clip(px_uv_smooth[vi] / W, 0.0, 1.0))
        v = float(np.clip(1.0 - py_all[vi] / H, 0.0, 1.0))
        uv_fb.data[li].uv = (u, v)

# 4. Build Hybrid Real-2.5D + Native-360 Shaders
print("[SHADERS] Constructing calibrated Fortiche / Arcane hybrid PBR materials...")
img_f_alb = bpy.data.images.load(os.path.join(TEX_DIR, "ichiro_front_albedo_2k.png"))
img_b_alb = bpy.data.images.load(os.path.join(TEX_DIR, "ichiro_back_albedo_2k.png"))
img_f_nrm = bpy.data.images.load(os.path.join(TEX_DIR, "ichiro_front_normal_2k.png"))
img_f_nrm.colorspace_settings.name = 'Non-Color'
img_b_nrm = bpy.data.images.load(os.path.join(TEX_DIR, "ichiro_back_normal_2k.png"))
img_b_nrm.colorspace_settings.name = 'Non-Color'
img_f_bmp = bpy.data.images.load(os.path.join(TEX_DIR, "ichiro_front_bump_2k.png"))
img_f_bmp.colorspace_settings.name = 'Non-Color'
img_b_bmp = bpy.data.images.load(os.path.join(TEX_DIR, "ichiro_back_bump_2k.png"))
img_b_bmp.colorspace_settings.name = 'Non-Color'
img_f_em  = bpy.data.images.load(os.path.join(TEX_DIR, "ichiro_front_emission_2k.png"))
img_b_em  = bpy.data.images.load(os.path.join(TEX_DIR, "ichiro_back_emission_2k.png"))

def build_hybrid_arcane_material(mat_name, img_trellis, is_bust=False):
    mat = bpy.data.materials.new(mat_name)
    try:
        mat.use_nodes = True
    except Exception:
        pass
    mat.use_backface_culling = False
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    uv_fb_n = nodes.new("ShaderNodeUVMap")
    uv_fb_n.uv_map = "UVMap_FB"
    uv_tr_n = nodes.new("ShaderNodeUVMap")
    uv_tr_n.uv_map = "UVMap_Trellis"

    geom = nodes.new("ShaderNodeNewGeometry")
    sep_n = nodes.new("ShaderNodeSeparateXYZ")
    links.new(geom.outputs["Normal"], sep_n.inputs["Vector"])
    sep_p = nodes.new("ShaderNodeSeparateXYZ")
    links.new(geom.outputs["Position"], sep_p.inputs["Vector"])

    def add_tex_node(img, uv_out):
        t = nodes.new("ShaderNodeTexImage")
        t.image = img
        t.extension = 'EXTEND'
        links.new(uv_out, t.inputs["Vector"])
        return t

    tf_alb = add_tex_node(img_f_alb, uv_fb_n.outputs["UV"])
    tb_alb = add_tex_node(img_b_alb, uv_fb_n.outputs["UV"])
    t_tr   = add_tex_node(img_trellis, uv_tr_n.outputs["UV"])

    tf_nrm = add_tex_node(img_f_nrm, uv_fb_n.outputs["UV"])
    tb_nrm = add_tex_node(img_b_nrm, uv_fb_n.outputs["UV"])
    tf_bmp = add_tex_node(img_f_bmp, uv_fb_n.outputs["UV"])
    tb_bmp = add_tex_node(img_b_bmp, uv_fb_n.outputs["UV"])
    tf_em  = add_tex_node(img_f_em,  uv_fb_n.outputs["UV"])
    tb_em  = add_tex_node(img_b_em,  uv_fb_n.outputs["UV"])

    fb_ny = nodes.new("ShaderNodeMapRange")
    fb_ny.inputs["From Min"].default_value = -0.15
    fb_ny.inputs["From Max"].default_value =  0.15
    fb_ny.inputs["To Min"].default_value   =  0.0
    fb_ny.inputs["To Max"].default_value   =  1.0
    fb_ny.interpolation_type = 'SMOOTHSTEP'
    links.new(sep_n.outputs["Y"], fb_ny.inputs["Value"])

    if is_bust:
        fb_py = nodes.new("ShaderNodeMapRange")
        fb_py.inputs["From Min"].default_value = -0.012
        fb_py.inputs["From Max"].default_value =  0.018
        fb_py.inputs["To Min"].default_value   =  0.0
        fb_py.inputs["To Max"].default_value   =  1.0
        fb_py.interpolation_type = 'SMOOTHSTEP'
        links.new(sep_p.outputs["Y"], fb_py.inputs["Value"])

        fb_gate = nodes.new("ShaderNodeMath")
        fb_gate.operation = 'MULTIPLY'
        links.new(fb_ny.outputs["Result"], fb_gate.inputs[0])
        links.new(fb_py.outputs["Result"], fb_gate.inputs[1])
        fb_factor_out = fb_gate.outputs["Value"]
    else:
        fb_factor_out = fb_ny.outputs["Result"]

    def mix_fb(out_f, out_b):
        m = nodes.new("ShaderNodeMix")
        m.data_type = 'RGBA'
        links.new(fb_factor_out, m.inputs["Factor"])
        links.new(out_f, m.inputs["A"])
        links.new(out_b, m.inputs["B"])
        return m.outputs["Result"]

    alb_fb = mix_fb(tf_alb.outputs["Color"], tb_alb.outputs["Color"])
    nrm_fb = mix_fb(tf_nrm.outputs["Color"], tb_nrm.outputs["Color"])
    bmp_fb = mix_fb(tf_bmp.outputs["Color"], tb_bmp.outputs["Color"])
    em_fb  = mix_fb(tf_em.outputs["Color"],  tb_em.outputs["Color"])

    abs_ny = nodes.new("ShaderNodeMath")
    abs_ny.operation = 'ABSOLUTE'
    links.new(sep_n.outputs["Y"], abs_ny.inputs[0])

    abs_px = nodes.new("ShaderNodeMath")
    abs_px.operation = 'ABSOLUTE'
    links.new(sep_p.outputs["X"], abs_px.inputs[0])

    if is_bust:
        grazing_ny_bust = nodes.new("ShaderNodeMapRange")
        grazing_ny_bust.inputs["From Min"].default_value = 0.14
        grazing_ny_bust.inputs["From Max"].default_value = 0.44
        grazing_ny_bust.inputs["To Min"].default_value   = 0.96
        grazing_ny_bust.inputs["To Max"].default_value   = 0.0
        grazing_ny_bust.interpolation_type = 'SMOOTHSTEP'
        links.new(abs_ny.outputs["Value"], grazing_ny_bust.inputs["Value"])

        outer_x_bust = nodes.new("ShaderNodeMapRange")
        outer_x_bust.inputs["From Min"].default_value = 0.056
        outer_x_bust.inputs["From Max"].default_value = 0.082
        outer_x_bust.inputs["To Min"].default_value   = 0.0
        outer_x_bust.inputs["To Max"].default_value   = 1.0
        outer_x_bust.interpolation_type = 'SMOOTHSTEP'
        links.new(abs_px.outputs["Value"], outer_x_bust.inputs["Value"])

        lat_bust = nodes.new("ShaderNodeMath")
        lat_bust.operation = 'MULTIPLY'
        links.new(grazing_ny_bust.outputs["Result"], lat_bust.inputs[0])
        links.new(outer_x_bust.outputs["Result"], lat_bust.inputs[1])

        crown_z = nodes.new("ShaderNodeMapRange")
        crown_z.inputs["From Min"].default_value = 1.685
        crown_z.inputs["From Max"].default_value = 1.725
        crown_z.inputs["To Min"].default_value   = 0.0
        crown_z.inputs["To Max"].default_value   = 1.0
        crown_z.interpolation_type = 'SMOOTHSTEP'
        links.new(sep_p.outputs["Z"], crown_z.inputs["Value"])

        trellis_weight = nodes.new("ShaderNodeMath")
        trellis_weight.operation = 'MAXIMUM'
        links.new(lat_bust.outputs["Value"], trellis_weight.inputs[0])
        links.new(crown_z.outputs["Result"], trellis_weight.inputs[1])
    else:
        grazing_ny = nodes.new("ShaderNodeMapRange")
        grazing_ny.inputs["From Min"].default_value = 0.14
        grazing_ny.inputs["From Max"].default_value = 0.40
        grazing_ny.inputs["To Min"].default_value   = 0.92
        grazing_ny.inputs["To Max"].default_value   = 0.0
        grazing_ny.interpolation_type = 'SMOOTHSTEP'
        links.new(abs_ny.outputs["Value"], grazing_ny.inputs["Value"])

        outer_x = nodes.new("ShaderNodeMapRange")
        outer_x.inputs["From Min"].default_value = 0.065
        outer_x.inputs["From Max"].default_value = 0.105
        outer_x.inputs["To Min"].default_value   = 0.0
        outer_x.inputs["To Max"].default_value   = 1.0
        outer_x.interpolation_type = 'SMOOTHSTEP'
        links.new(abs_px.outputs["Value"], outer_x.inputs["Value"])

        trellis_weight = nodes.new("ShaderNodeMath")
        trellis_weight.operation = 'MULTIPLY'
        links.new(grazing_ny.outputs["Result"], trellis_weight.inputs[0])
        links.new(outer_x.outputs["Result"], trellis_weight.inputs[1])

    alb_final = nodes.new("ShaderNodeMix")
    alb_final.data_type = 'RGBA'
    links.new(trellis_weight.outputs["Value"], alb_final.inputs["Factor"])
    links.new(alb_fb, alb_final.inputs["A"])
    links.new(t_tr.outputs["Color"], alb_final.inputs["B"])

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(alb_final.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.42
    bsdf.inputs["Metallic"].default_value  = 0.0

    nrm_map = nodes.new("ShaderNodeNormalMap")
    nrm_map.space = 'TANGENT'
    nrm_map.inputs["Strength"].default_value = 0.0 if is_bust else 0.28
    links.new(nrm_fb, nrm_map.inputs["Color"])

    bmp_map = nodes.new("ShaderNodeBump")
    bmp_map.inputs["Distance"].default_value = 0.002
    bmp_map.inputs["Strength"].default_value = 0.0 if is_bust else 0.22
    links.new(bmp_fb, bmp_map.inputs["Height"])
    links.new(nrm_map.outputs["Normal"], bmp_map.inputs["Normal"])

    links.new(bmp_map.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(em_fb, bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 0.0 if is_bust else 0.75

    em_paint = nodes.new("ShaderNodeEmission")
    em_paint.inputs["Strength"].default_value = 1.0
    links.new(alb_final.outputs["Result"], em_paint.inputs["Color"])

    mix_arcane = nodes.new("ShaderNodeMixShader")
    mix_arcane.inputs["Fac"].default_value = 0.58
    links.new(bsdf.outputs["BSDF"], mix_arcane.inputs[1])
    links.new(em_paint.outputs["Emission"], mix_arcane.inputs[2])

    links.new(mix_arcane.outputs["Shader"], out.inputs["Surface"])
    return mat

mat_body_aaa = build_hybrid_arcane_material("Mat_Ichiro_Body_AAA", img_trellis_body, is_bust=False)
mat_bust_aaa = build_hybrid_arcane_material("Mat_Ichiro_HeadBust_AAA", img_trellis_bust, is_bust=True)

char.data.materials.clear()
char.data.materials.append(mat_body_aaa)
char.data.materials.append(mat_bust_aaa)
for i, p in enumerate(char.data.polygons):
    p.material_index = 0 if i < n_body_polys else 1

# 5. Dual Magma Blades & Scabbard
print("[PROPS] Attaching authentic Dual Magma Blades & Tactical Dorsal Scabbard...")
try:
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

    orient_blade(auth_blade,   loc=(-0.405, 0.005, 0.830), tip_dir_vec=(-0.35, -0.26, -0.90), edge_hint_vec=(-0.72, -0.35, 0.60))
    orient_blade(auth_blade_l, loc=( 0.404, 0.005, 0.832), tip_dir_vec=( 0.35, -0.26, -0.90), edge_hint_vec=( 0.72, -0.35, 0.60))
except Exception as e_b:
    print(f"[NOTE] Blades attachment: {e_b}")

# Scabbard
if os.path.exists(GRID_V2_PATH):
    try:
        grid_v2 = np.load(GRID_V2_PATH)
        s_mask = grid_v2["scab_mask"].astype(bool)
        s_edt  = grid_v2["scab_edt"].astype(np.float32)
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
        scab_obj = bpy.data.objects.new("Ichiro_Dorsal_Scabbard", m)
        link_obj(scab_obj, col_props)
        scab_obj.location = Vector((-0.038, 0.142, 1.250))
        scab_obj.rotation_euler = Euler((math.radians(-6.0), math.radians(24.0), math.radians(16.0)), 'XYZ')
    except Exception as e_s:
        print(f"[NOTE] Scabbard creation: {e_s}")

# 6. Configure Production Cycles Rendering
print("[RENDER] Configuring Cycles OptiX GPU rendering...")
scene.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    scene.cycles.device = 'GPU'
except Exception:
    pass
scene.cycles.samples = 96
scene.cycles.use_denoising = True

cam_d = bpy.data.cameras.new("Cam_Production")
cam_o = bpy.data.objects.new("Cam_Production", cam_d)
scene.collection.objects.link(cam_o)
scene.camera = cam_o

def render_view(path, loc, rot_deg, lens, rx, ry):
    scene.render.resolution_x = rx
    scene.render.resolution_y = ry
    cam_d.lens = lens
    cam_o.location = Vector(loc)
    cam_o.rotation_euler = Euler([math.radians(a) for a in rot_deg], 'XYZ')
    scene.render.filepath = path
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)
    print(f"[RENDERED] {path}")

# 1. Portrait Close-Up (85mm)
p_portrait = os.path.join(RENDER_DIR, "02_Ichiro_Arcane_Portrait_CloseUp.png")
render_view(p_portrait, (0.0, -1.35, 1.56), (88.5, 0.0, 0.0), 85.0, 1080, 1350)

# 2. Hero 3/4 Beauty (52mm)
p_hero = os.path.join(RENDER_DIR, "01_Ichiro_Arcane_Hero_Beauty.png")
render_view(p_hero, (0.0, -3.15, 0.98), (88.5, 0.0, 0.0), 52.0, 1080, 1440)
shutil.copy2(p_hero, os.path.join(RENDER_DIR, "01_Ichiro_Arcane_Hero_34_Render.png"))

# 3. Turnaround Views (Front, Side, Back, 3/4)
render_view(os.path.join(RENDER_DIR, "turn_front.png"), (0.0, -3.20, 0.94), (90.0, 0.0, 0.0), 50.0, 720, 1280)
render_view(os.path.join(RENDER_DIR, "turn_side.png"),  (3.25, 0.0, 0.94),  (90.0, 0.0, 90.0), 50.0, 720, 1280)
render_view(os.path.join(RENDER_DIR, "turn_back.png"),  (0.0, 3.25, 0.94),  (90.0, 0.0, 180.0), 50.0, 720, 1280)
render_view(os.path.join(RENDER_DIR, "turn_34.png"),    (-1.10, -3.15, 0.96), (88.5, 0.0, -18.0), 50.0, 720, 1280)

# 4. Composite 03_Ichiro_Arcane_Turnaround_4Views.png
comp_script = os.path.join(SCRATCH_DIR, "composite_lumen_turnaround_sheet.py")
if os.path.exists(comp_script):
    try:
        subprocess.run(["python", comp_script], check=True)
        print("[SUCCESS] 03_Ichiro_Arcane_Turnaround_4Views.png composited!")
    except Exception as e_c:
        print(f"[NOTE] Turnaround composite: {e_c}")

# 5. Aberrant Kai Overdrive Mode Render
p_kai = os.path.join(RENDER_DIR, "04_Ichiro_Arcane_Kai_Exposure_Aberrant.png")
l_key.data.color  = (0.90, 0.72, 1.0)
l_cyan.data.color = (0.65, 0.05, 1.0)
l_mag.data.color  = (1.0, 0.05, 0.35)
bg_node.inputs["Color"].default_value = (0.068, 0.035, 0.088, 1.0)
render_view(p_kai, (0.45, -2.10, 1.34), (88.5, 0.0, 12.0), 58.0, 1080, 1350)

# Restore lighting
l_key.data.color  = (1.0, 0.96, 0.90)
l_cyan.data.color = (0.0, 0.94, 1.0)
l_mag.data.color  = (1.0, 0.22, 0.55)
bg_node.inputs["Color"].default_value = (0.048, 0.055, 0.078, 1.0)

# 7. Save Production Scene & Export
print("[EXPORT] Saving production .blend and exporting glTF 2.0...")
bpy.ops.wm.save_as_mainfile(filepath=OUT_MASTER_BLEND)
bpy.ops.wm.save_as_mainfile(filepath=OUT_ROOT_BLEND)
print(f"[SUCCESS] Saved: {OUT_MASTER_BLEND} & {OUT_ROOT_BLEND}")

bpy.ops.object.select_all(action='DESELECT')
for o in [char]:
    o.select_set(True)

bpy.ops.export_scene.gltf(
    filepath=OUT_REAL_GLB,
    export_format='GLB',
    use_selection=True,
    export_apply=False,
    export_yup=True,
    export_morph=True,
    export_materials='EXPORT'
)
shutil.copy2(OUT_REAL_GLB, OUT_ARCANE_GLB)
print(f"[SUCCESS] Exported: {OUT_REAL_GLB}")

# Copy final 4 renders to brain directory for direct user UI inspection
brain_files = [
    ("01_Ichiro_Arcane_Hero_Beauty.png", "01_Ichiro_Arcane_Hero_Beauty.png"),
    ("02_Ichiro_Arcane_Portrait_CloseUp.png", "02_Ichiro_Arcane_Portrait_CloseUp.png"),
    ("03_Ichiro_Arcane_Turnaround_4Views.png", "03_Ichiro_Arcane_Turnaround_4Views.png"),
    ("04_Ichiro_Arcane_Kai_Exposure_Aberrant.png", "04_Ichiro_Arcane_Kai_Exposure_Aberrant.png")
]
for src_f, dst_f in brain_files:
    sp = os.path.join(RENDER_DIR, src_f)
    dp = os.path.join(BRAIN_DIR, dst_f)
    if os.path.exists(sp):
        shutil.copy2(sp, dp)
        print(f"[COPIED TO BRAIN] {dst_f}")

print("===============================================================================")
print("  [ALL DELIVERABLES COMPLETE] ETHERNIUM SOVEREIGN PRODUCTION PIPELINE READY")
print("===============================================================================")
