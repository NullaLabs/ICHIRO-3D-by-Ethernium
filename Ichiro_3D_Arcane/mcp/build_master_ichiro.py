import bpy
import os
import math
import numpy as np
from mathutils import Vector, Euler

base_dir = r"e:\DESCARGAS\Web3\My web3 Projects\KPR\KPR Art Portfolio\KPR (My art)\KPR Ai Portfolio\Ichiro\Ichiro_3D_Arcane"
tex_dir  = os.path.join(base_dir, "textures")
render_dir = os.path.join(base_dir, "renders")
blade_blend = r"E:\DESCARGAS\Web3\My web3 Projects\KPR\Ichiro Commissions\Ichiro traits\ ENERGY BLADE.blend"

print("[PERFECT-TOPOLOGY] Loading watertight manifold base mesh...")
data_mesh = np.load(os.path.join(tex_dir, "ichiro_quad_mesh_base.npz"))
verts_raw = data_mesh["verts"]
faces_raw = data_mesh["faces"]

# Also load master grid for scabbard and reference
data = np.load(os.path.join(tex_dir, "ichiro_master_grid.npz"))

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

mesh = bpy.data.meshes.new("Ichiro_2390_Body_Mesh")
mesh.from_pydata(verts_raw.tolist(), [], faces_raw.tolist())
mesh.update()

ichiro_obj = bpy.data.objects.new("Ichiro_2390_Character", mesh)
scene.collection.objects.link(ichiro_obj)
bpy.context.view_layer.objects.active = ichiro_obj
ichiro_obj.select_set(True)

# Clean duplicate vertices & degenerate geometry
print("[PERFECT-TOPOLOGY] Cleaning mesh manifold geometry...")
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold=0.0005)
bpy.ops.mesh.dissolve_degenerate(threshold=0.0005)
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

# Run QuadriFlow Remesher for clean, symmetrical, quad-dominant character topology
print("[PERFECT-TOPOLOGY] Applying QuadriFlow Remesher (16,000 target quads, symmetry=X)...")
bpy.ops.object.quadriflow_remesh(
    use_mesh_symmetry=True,
    target_faces=16000,
    mode='FACES'
)
print(f"[PERFECT-TOPOLOGY] QuadriFlow complete: {len(ichiro_obj.data.vertices)} vertices, {len(ichiro_obj.data.polygons)} quad polygons!")

# Smooth normals
for poly in ichiro_obj.data.polygons:
    poly.use_smooth = True

# Generate subpixel-precise UVMap_FB
SCALE = 1.80 / 388.0
CX = 108.0
W = 216.0
H = 388.0

uv_fb_layer = ichiro_obj.data.uv_layers.new(name="UVMap_FB")
ichiro_obj.data.uv_layers.active = uv_fb_layer

for poly in ichiro_obj.data.polygons:
    for loop_idx in poly.loop_indices:
        vi = ichiro_obj.data.loops[loop_idx].vertex_index
        vco = ichiro_obj.data.vertices[vi].co
        vx, vz = vco.x, vco.z
        grid_x = vx / SCALE + CX
        grid_y = (H - 1.0) - vz / SCALE
        u = (grid_x + 0.5) / W
        v = 1.0 - (grid_y + 0.5) / H
        uv_fb_layer.data[loop_idx].uv = (u, v)

# Generate UVMap_Side for seamless lateral profile
uv_side_layer = ichiro_obj.data.uv_layers.new(name="UVMap_Side")
Y_MIN = -0.15
Y_MAX =  0.13
DY = Y_MAX - Y_MIN
for poly in ichiro_obj.data.polygons:
    for loop_idx in poly.loop_indices:
        vi = ichiro_obj.data.loops[loop_idx].vertex_index
        vco = ichiro_obj.data.vertices[vi].co
        vy, vz = vco.y, vco.z
        u_s = float(np.clip((vy - Y_MIN) / DY, 0.0, 1.0))
        v_s = float(np.clip(vz / 1.80, 0.0, 1.0))
        uv_side_layer.data[loop_idx].uv = (u_s, v_s)

# Gold Hoop Earrings (anchored exactly through earlobes)
mat_gold = bpy.data.materials.new("Mat_Ichiro_Gold")
g_nd = mat_gold.node_tree.nodes
g_lk = mat_gold.node_tree.links
g_nd.clear()
g_out = g_nd.new("ShaderNodeOutputMaterial")
g_b = g_nd.new("ShaderNodeBsdfPrincipled")
g_b.inputs["Base Color"].default_value = (1.0, 0.80, 0.22, 1.0)
g_b.inputs["Metallic"].default_value = 0.95
g_b.inputs["Roughness"].default_value = 0.15
g_b.inputs["Emission Color"].default_value = (1.0, 0.65, 0.12, 1.0)
g_b.inputs["Emission Strength"].default_value = 0.40
g_lk.new(g_b.outputs["BSDF"], g_out.inputs["Surface"])

for side_name, sx in [("L", 0.064), ("R", -0.064)]:
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.012,
        minor_radius=0.0028,
        major_segments=24,
        minor_segments=12,
        location=(sx, -0.014, 1.542),
        rotation=Euler((math.radians(90), 0, math.radians(12 if sx > 0 else -12)), 'XYZ')
    )
    ear = bpy.context.active_object
    ear.name = f"Ichiro_Earring_{side_name}"
    for p in ear.data.polygons: p.use_smooth = True
    ear.data.materials.append(mat_gold)

# Load 2K Textures & Master Arcane Shader
img_front = bpy.data.images.load(os.path.join(tex_dir, "ichiro_front_albedo_2k.png"))
img_side  = bpy.data.images.load(os.path.join(tex_dir, "ichiro_side_albedo_2k.png"))
img_kai   = bpy.data.images.load(os.path.join(tex_dir, "ichiro_front_kai_aberrant_2k.png"))
img_back  = bpy.data.images.load(os.path.join(tex_dir, "ichiro_back_albedo_2k.png"))
img_em_f  = bpy.data.images.load(os.path.join(tex_dir, "ichiro_front_emission_2k.png"))
img_em_b  = bpy.data.images.load(os.path.join(tex_dir, "ichiro_back_emission_2k.png"))
img_nm_f  = bpy.data.images.load(os.path.join(tex_dir, "ichiro_front_normal_2k.png"))
img_nm_f.colorspace_settings.name = 'Non-Color'

mat_body = bpy.data.materials.new("Mat_Ichiro_Arcane_23D_Master")
nodes = mat_body.node_tree.nodes
links = mat_body.node_tree.links
nodes.clear()

out_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs["Roughness"].default_value = 0.58
bsdf.inputs["Specular IOR Level"].default_value = 0.26
links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

uv_fb_node = nodes.new("ShaderNodeUVMap")
uv_fb_node.uv_map = "UVMap_FB"

uv_side_node = nodes.new("ShaderNodeUVMap")
uv_side_node.uv_map = "UVMap_Side"

tex_front = nodes.new("ShaderNodeTexImage")
tex_front.image = img_front
tex_front.extension = 'EXTEND'
links.new(uv_fb_node.outputs["UV"], tex_front.inputs["Vector"])

tex_back = nodes.new("ShaderNodeTexImage")
tex_back.image = img_back
tex_back.extension = 'EXTEND'
links.new(uv_fb_node.outputs["UV"], tex_back.inputs["Vector"])

tex_side = nodes.new("ShaderNodeTexImage")
tex_side.image = img_side
tex_side.extension = 'EXTEND'
links.new(uv_side_node.outputs["UV"], tex_side.inputs["Vector"])

geom = nodes.new("ShaderNodeNewGeometry")
sep_xyz = nodes.new("ShaderNodeSeparateXYZ")
links.new(geom.outputs["Normal"], sep_xyz.inputs["Vector"])

map_fb = nodes.new("ShaderNodeMapRange")
map_fb.inputs["From Min"].default_value = -0.12
map_fb.inputs["From Max"].default_value = 0.12
links.new(sep_xyz.outputs["Y"], map_fb.inputs["Value"])

mix_fb = nodes.new("ShaderNodeMix")
mix_fb.data_type = 'RGBA'
links.new(map_fb.outputs["Result"], mix_fb.inputs["Factor"])
links.new(tex_front.outputs["Color"], mix_fb.inputs["A"])
links.new(tex_back.outputs["Color"], mix_fb.inputs["B"])

# Lateral blend with side texture for |Nx| > 0.68
abs_x = nodes.new("ShaderNodeMath")
abs_x.operation = 'ABSOLUTE'
links.new(sep_xyz.outputs["X"], abs_x.inputs[0])

map_side = nodes.new("ShaderNodeMapRange")
map_side.inputs["From Min"].default_value = 0.68
map_side.inputs["From Max"].default_value = 0.92
links.new(abs_x.outputs["Value"], map_side.inputs["Value"])

mix_side = nodes.new("ShaderNodeMix")
mix_side.data_type = 'RGBA'
links.new(map_side.outputs["Result"], mix_side.inputs["Factor"])
links.new(mix_fb.outputs["Result"], mix_side.inputs["A"])
links.new(tex_side.outputs["Color"], mix_side.inputs["B"])
links.new(mix_side.outputs["Result"], bsdf.inputs["Base Color"])

tex_emf = nodes.new("ShaderNodeTexImage")
tex_emf.image = img_em_f
links.new(uv_fb_node.outputs["UV"], tex_emf.inputs["Vector"])

tex_emb = nodes.new("ShaderNodeTexImage")
tex_emb.image = img_em_b
links.new(uv_fb_node.outputs["UV"], tex_emb.inputs["Vector"])

mix_em = nodes.new("ShaderNodeMix")
mix_em.data_type = 'RGBA'
links.new(map_fb.outputs["Result"], mix_em.inputs["Factor"])
links.new(tex_emf.outputs["Color"], mix_em.inputs["A"])
links.new(tex_emb.outputs["Color"], mix_em.inputs["B"])
links.new(mix_em.outputs["Result"], bsdf.inputs["Emission Color"])
bsdf.inputs["Emission Strength"].default_value = 1.65

tex_nm = nodes.new("ShaderNodeTexImage")
tex_nm.image = img_nm_f
links.new(uv_fb_node.outputs["UV"], tex_nm.inputs["Vector"])
nm_node = nodes.new("ShaderNodeNormalMap")
nm_node.inputs["Strength"].default_value = 0.40
links.new(tex_nm.outputs["Color"], nm_node.inputs["Color"])
links.new(nm_node.outputs["Normal"], bsdf.inputs["Normal"])

ichiro_obj.data.materials.append(mat_body)

# Append Authentic Magma Blades from ENERGY BLADE.blend
with bpy.data.libraries.load(blade_blend) as (data_from, data_to):
    data_to.objects = ["Plane.001"]

auth_blade = data_to.objects[0]
scene.collection.objects.link(auth_blade)
auth_blade.name = "Ichiro_Magma_Blade_R"

bpy.context.view_layer.objects.active = auth_blade
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Re-center origin to handle grip (X=6.0, Y=-1.0, Z=0.0)
for v in auth_blade.data.vertices:
    v.co.x -= 6.0
    v.co.y += 1.0

# Scale to canonical 0.98m length: original length along X was 27.8308
scale_factor = 0.98 / 27.8308
auth_blade.scale = (scale_factor, scale_factor, scale_factor)
bpy.ops.object.transform_apply(scale=True)

# Enhance materials
for ms in auth_blade.material_slots:
    if ms.material and ms.material.node_tree:
        for n in ms.material.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                em_val = n.inputs["Emission Strength"].default_value
                if em_val > 0.05 or "orange" in n.name.lower() or "magma" in ms.material.name.lower():
                    n.inputs["Emission Strength"].default_value = max(em_val, 3.2)
                    n.inputs["Roughness"].default_value = 0.18
                else:
                    n.inputs["Base Color"].default_value = (0.05, 0.055, 0.065, 1.0)
                    n.inputs["Metallic"].default_value = 0.88
                    n.inputs["Roughness"].default_value = 0.25

auth_blade_l = auth_blade.copy()
auth_blade_l.data = auth_blade.data.copy()
auth_blade_l.name = "Ichiro_Magma_Blade_L"
scene.collection.objects.link(auth_blade_l)

# Pose Dual Blades in Bladewalker Combat Stance (blades sweep forward and down, 100% inside Hero frame)
auth_blade.location = (-0.41, -0.05, 0.77)
auth_blade.rotation_euler = Euler((math.radians(-64), math.radians(16), math.radians(12)), 'XYZ')

auth_blade_l.location = (0.41, -0.05, 0.77)
auth_blade_l.rotation_euler = Euler((math.radians(-56), math.radians(38), math.radians(-14)), 'XYZ')

# Build Scabbard
s_mask = data["scab_mask"].astype(bool)
s_edt  = data["scab_edt"].astype(np.float32)

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
            vy = 0.015 * math.tanh(max(0.0, s_edt[y, x] - 0.5) / 2.0)
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
                qf = (int(f_id[y,x]), int(f_id[y+1,x]), int(f_id[y+1,x+1]), int(f_id[y+1,x+1]))
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
    scene.collection.objects.link(obj)
    return obj

scabbard = build_scabbard()
scabbard.location = (0.10, 0.13, 0.90)
scabbard.rotation_euler = Euler((math.radians(6), math.radians(30), math.radians(0)), 'XYZ')

mat_scab = bpy.data.materials.new("Mat_Ichiro_Scabbard")
s_bsdf = mat_scab.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
s_bsdf.inputs["Roughness"].default_value = 0.30
s_bsdf.inputs["Metallic"].default_value = 0.82
mat_scab.node_tree.links.new(s_bsdf.outputs["BSDF"], mat_scab.node_tree.nodes["Material Output"].inputs["Surface"])
img_scab = bpy.data.images.load(os.path.join(tex_dir, "ichiro_scabbard_2k.png"))
t_scab = mat_scab.node_tree.nodes.new("ShaderNodeTexImage")
t_scab.image = img_scab
mat_scab.node_tree.links.new(t_scab.outputs["Color"], s_bsdf.inputs["Base Color"])
scabbard.data.materials.append(mat_scab)

# Pedestal & Rings
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.68, depth=0.06, location=(0.0, 0.0, -0.03))
pedestal = bpy.context.active_object
pedestal.name = "Arcane_Pedestal"
for p in pedestal.data.polygons: p.use_smooth = True

mat_ped = bpy.data.materials.new("Mat_Arcane_Pedestal")
p_b = mat_ped.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
p_b.inputs["Base Color"].default_value = (0.04, 0.045, 0.06, 1.0)
p_b.inputs["Metallic"].default_value = 0.88
p_b.inputs["Roughness"].default_value = 0.22
mat_ped.node_tree.links.new(p_b.outputs["BSDF"], mat_ped.node_tree.nodes["Material Output"].inputs["Surface"])
pedestal.data.materials.append(mat_ped)

def make_emissive_mat(name, color_rgba, strength=5.0):
    m = bpy.data.materials.new(name)
    nd = m.node_tree.nodes
    lk = m.node_tree.links
    nd.clear()
    o = nd.new("ShaderNodeOutputMaterial")
    b = nd.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = color_rgba
    b.inputs["Emission Color"].default_value = color_rgba
    b.inputs["Emission Strength"].default_value = strength
    lk.new(b.outputs["BSDF"], o.inputs["Surface"])
    return m

bpy.ops.mesh.primitive_torus_add(major_radius=0.64, minor_radius=0.008, major_segments=64, minor_segments=12, location=(0.0, 0.0, 0.002))
rc = bpy.context.active_object
rc.name = "Arcane_Ring_Cyan"
rc.data.materials.append(make_emissive_mat("Mat_Ring_Cyan", (0.0, 0.94, 1.0, 1.0), 5.0))

bpy.ops.mesh.primitive_torus_add(major_radius=0.52, minor_radius=0.006, major_segments=64, minor_segments=12, location=(0.0, 0.0, 0.003))
rm = bpy.context.active_object
rm.name = "Arcane_Ring_Magma"
rm.data.materials.append(make_emissive_mat("Mat_Ring_Magma", (1.0, 0.35, 0.05, 1.0), 5.0))

# Lighting
world = bpy.data.worlds.new("Arcane_World")
scene.world = world
bg_node = world.node_tree.nodes["Background"]
bg_node.inputs["Color"].default_value = (0.048, 0.055, 0.078, 1.0)
bg_node.inputs["Strength"].default_value = 0.90

def add_light(name, ltype, loc, rot_deg, energy, color, size=1.5):
    ld = bpy.data.lights.new(name, type=ltype)
    ld.energy = energy
    ld.color = color
    if ltype == 'AREA': ld.size = size
    lo = bpy.data.objects.new(name, ld)
    scene.collection.objects.link(lo)
    lo.location = loc
    lo.rotation_euler = Euler([math.radians(a) for a in rot_deg], 'XYZ')
    return lo

l_key  = add_light("Key_Warm_Piltover",  'AREA',  (1.2, -2.8, 2.0),  (58, 0, 22),   195.0, (1.0, 0.94, 0.86), 2.2)
l_cyan = add_light("Rim_Zaun_Cyan",      'AREA',  (-2.2, 1.6, 1.6),  (65, 0, -130), 280.0, (0.0, 0.94, 1.0),  1.8)
l_mag  = add_light("Rim_Arcane_Magenta", 'AREA',  (2.2, 1.6, 1.5),   (65, 0, 130),  260.0, (1.0, 0.18, 0.55), 1.8)
l_fill = add_light("Fill_Magma_Lower",   'POINT', (0.0, -1.6, 0.55), (0, 0, 0),     75.0,  (1.0, 0.42, 0.08), 0.5)

scene.render.image_settings.file_format = 'PNG'
try:
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'High Contrast'
except Exception:
    pass

cam_data = bpy.data.cameras.new("Arcane_Cam")
cam_obj = bpy.data.objects.new("Arcane_Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

def set_cam_and_render(filepath, loc, target, lens, res_x, res_y):
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    cam_data.lens = lens
    cam_obj.location = Vector(loc)
    direction = Vector(target) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = filepath
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)
    print(f"[PERFECTION] Rendered: {filepath}", flush=True)

# 1. Hero Beauty (3/4 dynamic stance on pedestal)
set_cam_and_render(
    os.path.join(render_dir, "01_Ichiro_Arcane_Hero_Beauty.png"),
    loc=(0.72, -3.35, 0.98), target=(0.0, 0.0, 0.88), lens=52.0, res_x=1080, res_y=1440
)

# 2. Portrait Close-Up (Cinematic close-up on head, eyes, earrings, and collar)
set_cam_and_render(
    os.path.join(render_dir, "02_Ichiro_Arcane_Portrait_CloseUp.png"),
    loc=(0.18, -1.22, 1.52), target=(0.0, 0.0, 1.50), lens=72.0, res_x=1080, res_y=1350
)

# 3. Turnaround Views
turn_views = [
    ("turn_front.png", (0.0, -3.55, 0.94),   (0.0, 0.0, 0.90), 52.0),
    ("turn_side.png",  (3.45, 0.0, 0.94),    (0.0, 0.0, 0.90), 52.0),
    ("turn_back.png",  (0.0, 3.55, 0.94),    (0.0, 0.0, 0.90), 52.0),
    ("turn_34.png",    (-1.05, -3.35, 0.96), (0.0, 0.0, 0.88), 52.0),
]
for vname, vloc, vtarg, vlens in turn_views:
    set_cam_and_render(
        os.path.join(render_dir, vname),
        loc=vloc, target=vtarg, lens=vlens, res_x=720, res_y=1280
    )

# 4. Kai Aberrant Mode
tex_front.image = img_kai
bsdf.inputs["Emission Strength"].default_value = 2.25
l_key.data.color = (0.90, 0.72, 1.0)
l_cyan.data.color = (0.65, 0.05, 1.0)
l_mag.data.color = (1.0, 0.05, 0.35)
bg_node.inputs["Color"].default_value = (0.068, 0.035, 0.088, 1.0)

set_cam_and_render(
    os.path.join(render_dir, "04_Ichiro_Arcane_Kai_Exposure_Aberrant.png"),
    loc=(0.50, -2.10, 1.32), target=(0.0, 0.0, 1.24), lens=56.0, res_x=1080, res_y=1350
)

# Restore Standard
tex_front.image = img_front
bsdf.inputs["Emission Strength"].default_value = 1.65
l_key.data.color = (1.0, 0.94, 0.86)
l_cyan.data.color = (0.0, 0.94, 1.0)
l_mag.data.color = (1.0, 0.18, 0.55)
bg_node.inputs["Color"].default_value = (0.048, 0.055, 0.078, 1.0)

# Save Master .blend
blend_path = os.path.join(base_dir, "blend", "Ichiro_2390_Arcane_Master.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"[PERFECTION] Saved Master Blend: {blend_path}")

# glTF Native Materials for GLB Export
mat_gltf_front = bpy.data.materials.new("Mat_Ichiro_Front_GLTF")
m_b = mat_gltf_front.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
m_b.inputs["Roughness"].default_value = 0.58
m_b.inputs["Metallic"].default_value = 0.15
mat_gltf_front.node_tree.links.new(m_b.outputs["BSDF"], mat_gltf_front.node_tree.nodes["Material Output"].inputs["Surface"])
ta = mat_gltf_front.node_tree.nodes.new("ShaderNodeTexImage")
ta.image = img_front
mat_gltf_front.node_tree.links.new(ta.outputs["Color"], m_b.inputs["Base Color"])

mat_gltf_back = bpy.data.materials.new("Mat_Ichiro_Back_GLTF")
mb_b = mat_gltf_back.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
mb_b.inputs["Roughness"].default_value = 0.58
mb_b.inputs["Metallic"].default_value = 0.15
mat_gltf_back.node_tree.links.new(mb_b.outputs["BSDF"], mat_gltf_back.node_tree.nodes["Material Output"].inputs["Surface"])
tb = mat_gltf_back.node_tree.nodes.new("ShaderNodeTexImage")
tb.image = img_back
mat_gltf_back.node_tree.links.new(tb.outputs["Color"], mb_b.inputs["Base Color"])

ichiro_obj.data.materials.clear()
ichiro_obj.data.materials.append(mat_gltf_front)
ichiro_obj.data.materials.append(mat_gltf_back)

glb_path = os.path.join(base_dir, "models", "Ichiro_2390_Arcane.glb")
bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB', export_apply=False, export_yup=True)
print(f"[PERFECTION] Exported GLB: {glb_path}")

obj_path = os.path.join(base_dir, "models", "Ichiro_2390_Arcane.obj")
bpy.ops.wm.obj_export(filepath=obj_path)
print(f"[PERFECTION] Exported OBJ: {obj_path}")
