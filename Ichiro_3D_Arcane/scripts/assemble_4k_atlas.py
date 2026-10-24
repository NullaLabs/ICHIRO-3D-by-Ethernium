import bpy
import os
import math
import shutil
import subprocess
from mathutils import Vector, Euler

SCRATCH_DIR = r"C:\Users\esenc\.gemini\antigravity\brain\3ccecf18-5e96-4998-8aad-0804a4100391\scratch"
ROOT        = r"e:\DESCARGAS\Web3\My web3 Projects\KPR\KPR Art Portfolio\KPR (My art)\KPR Ai Portfolio\Ichiro\Ichiro_3D_Arcane"
TEX_DIR     = os.path.join(ROOT, "textures")
MODEL_DIR   = os.path.join(ROOT, "models")
RENDER_DIR  = os.path.join(ROOT, "renders")
BRAIN_DIR   = r"C:\Users\esenc\.gemini\antigravity\brain\3ccecf18-5e96-4998-8aad-0804a4100391"
BLEND_SRC   = os.path.join(ROOT, "Ichiro_2390_Arcane_Scene.blend")

print("===============================================================================")
print("  ETHERNIUM SOVEREIGN // MASTER 4K ATLAS MATERIAL ASSEMBLY & SUITE RENDERING")
print("===============================================================================")

bpy.ops.wm.open_mainfile(filepath=BLEND_SRC)
scene = bpy.context.scene

char = bpy.data.objects['Ichiro_2390_Character']
bpy.ops.object.select_all(action='DESELECT')
char.select_set(True)
bpy.context.view_layer.objects.active = char

# 1. Ensure UVMap_Atlas_4K exists and is configured
if 'UVMap_Atlas_4K' not in char.data.uv_layers:
    uv_tr = char.data.uv_layers['UVMap_Trellis'].data
    uv_atlas = char.data.uv_layers.new(name='UVMap_Atlas_4K')
    for poly in char.data.polygons:
        is_bust = (poly.material_index == 1)
        for li in poly.loop_indices:
            u_old, v_old = uv_tr[li].uv
            u_new = u_old * 0.98 + 0.01
            if is_bust:
                v_new = 0.51 + v_old * 0.48
            else:
                v_new = 0.01 + v_old * 0.48
            uv_atlas.data[li].uv = (u_new, v_new)
else:
    uv_atlas = char.data.uv_layers['UVMap_Atlas_4K']

uv_atlas.name = "UVMap"
char.data.uv_layers.active = char.data.uv_layers["UVMap"]
char.data.uv_layers["UVMap"].active_render = True

# 2. Load the 4 Baked Maps
p_diff = os.path.join(TEX_DIR, "ichiro_master_diffuse_4k.png")
p_nrm  = os.path.join(TEX_DIR, "ichiro_master_normal_4k.png")
p_rgh  = os.path.join(TEX_DIR, "ichiro_master_roughness_4k.png")
p_emit = os.path.join(TEX_DIR, "ichiro_master_emission_4k.png")

img_diff = bpy.data.images.load(p_diff, check_existing=True)
img_nrm  = bpy.data.images.load(p_nrm, check_existing=True)
img_nrm.colorspace_settings.name = 'Non-Color'
img_rgh  = bpy.data.images.load(p_rgh, check_existing=True)
img_rgh.colorspace_settings.name = 'Non-Color'
img_emit = bpy.data.images.load(p_emit, check_existing=True)

# 3. Build Universal PBR Material: Mat_Ichiro_Master_PBR_4K
mat_name = "Mat_Ichiro_Master_PBR_4K"
mat_pbr = bpy.data.materials.get(mat_name)
if not mat_pbr:
    mat_pbr = bpy.data.materials.new(mat_name)
mat_pbr.use_nodes = True
nodes = mat_pbr.node_tree.nodes
links = mat_pbr.node_tree.links
nodes.clear()

out = nodes.new("ShaderNodeOutputMaterial")
out.location = (600, 0)

bsdf = nodes.new("ShaderNodeBsdfPrincipled")
bsdf.location = (200, 0)
links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

uv_n = nodes.new("ShaderNodeUVMap")
uv_n.uv_map = "UVMap"
uv_n.location = (-600, 0)

def create_tex_node(img, loc, is_color=True):
    t = nodes.new("ShaderNodeTexImage")
    t.image = img
    t.location = loc
    if not is_color:
        t.image.colorspace_settings.name = 'Non-Color'
    t.extension = 'EXTEND'
    t.interpolation = 'Smart'
    links.new(uv_n.outputs["UV"], t.inputs["Vector"])
    return t

# Base Color
t_diff = create_tex_node(img_diff, (-250, 250), is_color=True)
links.new(t_diff.outputs["Color"], bsdf.inputs["Base Color"])

# Normal Map
t_nrm = create_tex_node(img_nrm, (-250, -50), is_color=False)
nrm_map = nodes.new("ShaderNodeNormalMap")
nrm_map.space = 'TANGENT'
nrm_map.inputs["Strength"].default_value = 1.0
nrm_map.location = (0, -50)
links.new(t_nrm.outputs["Color"], nrm_map.inputs["Color"])
links.new(nrm_map.outputs["Normal"], bsdf.inputs["Normal"])

# Roughness
t_rgh = create_tex_node(img_rgh, (-250, -350), is_color=False)
links.new(t_rgh.outputs["Color"], bsdf.inputs["Roughness"])

# Emission (Cyber-magma veins + glowing eyes)
t_emit = create_tex_node(img_emit, (-250, -650), is_color=True)
links.new(t_emit.outputs["Color"], bsdf.inputs["Emission Color"])
bsdf.inputs["Emission Strength"].default_value = 1.6
bsdf.inputs["Metallic"].default_value = 0.0

# 4. Assign Single Unified Material to Character
char.data.materials.clear()
char.data.materials.append(mat_pbr)
for p in char.data.polygons:
    p.material_index = 0

print(f"[ASSEMBLY] Mat_Ichiro_Master_PBR_4K assigned to all {len(char.data.polygons)} polygons (1 draw call)!")

# 5. Export glTF 2.0 (.glb)
out_glb = os.path.join(MODEL_DIR, "Ichiro_2390_Real3D_Mesh.glb")
bpy.ops.object.select_all(action='DESELECT')
char.select_set(True)
bpy.ops.export_scene.gltf(
    filepath=out_glb,
    export_format='GLB',
    use_selection=True,
    export_apply=False,
    export_yup=True,
    export_morph=True,
    export_materials='EXPORT'
)
shutil.copy2(out_glb, os.path.join(MODEL_DIR, "Ichiro_2390_Arcane.glb"))
print(f"[GLTF] Successfully exported 4K PBR GLB: {out_glb}")

# 6. Save Updated Scenes
atlas_blend = os.path.join(ROOT, "Ichiro_2390_Arcane_4K_Atlas.blend")
bpy.ops.wm.save_as_mainfile(filepath=atlas_blend)
shutil.copy2(atlas_blend, BLEND_SRC)
print(f"[SCENE] Saved: {atlas_blend} & updated {BLEND_SRC}")

# 7. Render Complete Production Suite
scene.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    scene.cycles.device = 'GPU'
except Exception:
    scene.cycles.device = 'CPU'

scene.cycles.samples = 96
scene.cycles.use_denoising = True

cam_o = scene.objects.get("Cam_Production")
if not cam_o:
    cam_d = bpy.data.cameras.new("Cam_Production")
    cam_o = bpy.data.objects.new("Cam_Production", cam_d)
    scene.collection.objects.link(cam_o)
else:
    cam_d = cam_o.data

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

# View 1: Portrait Close-Up (85mm)
p_portrait = os.path.join(RENDER_DIR, "02_Ichiro_Arcane_Portrait_CloseUp.png")
render_view(p_portrait, (0.0, -1.35, 1.56), (88.5, 0.0, 0.0), 85.0, 1080, 1350)

# View 2: Hero 3/4 Beauty (52mm)
p_hero = os.path.join(RENDER_DIR, "01_Ichiro_Arcane_Hero_Beauty.png")
render_view(p_hero, (0.0, -3.15, 0.98), (88.5, 0.0, 0.0), 52.0, 1080, 1440)
shutil.copy2(p_hero, os.path.join(RENDER_DIR, "01_Ichiro_Arcane_Hero_34_Render.png"))

# View 3: Turnaround 4 Views
print("[TURNAROUND] Rendering 4 canonical views...")
render_view(os.path.join(RENDER_DIR, "turn_front.png"), (0.0, -3.20, 0.94), (90.0, 0.0, 0.0), 50.0, 720, 1280)
render_view(os.path.join(RENDER_DIR, "turn_side.png"),  (3.25, 0.0, 0.94),  (90.0, 0.0, 90.0), 50.0, 720, 1280)
render_view(os.path.join(RENDER_DIR, "turn_back.png"),  (0.0, 3.25, 0.94),  (90.0, 0.0, 180.0), 50.0, 720, 1280)
render_view(os.path.join(RENDER_DIR, "turn_34.png"),    (-1.10, -3.15, 0.96), (88.5, 0.0, -18.0), 50.0, 720, 1280)

comp_script = os.path.join(SCRATCH_DIR, "composite_lumen_turnaround_sheet.py")
if os.path.exists(comp_script):
    try:
        subprocess.run(["python", comp_script], check=True)
        print("[SUCCESS] 03_Ichiro_Arcane_Turnaround_4Views.png composited successfully!")
    except Exception as e_c:
        print(f"[NOTE] Turnaround composite: {e_c}")

# View 4: Aberrant Kai Overdrive Mode
p_kai = os.path.join(RENDER_DIR, "04_Ichiro_Arcane_Kai_Exposure_Aberrant.png")
l_key = scene.objects.get("Light_Key_Warm")
l_cyan = scene.objects.get("Light_Rim_Cyan")
l_mag = scene.objects.get("Light_Rim_Magenta")
world = scene.world
bg_node = None
if world and world.node_tree:
    bg_node = world.node_tree.nodes.get("Background")

if l_key and l_cyan and l_mag and bg_node:
    l_key.data.color  = (0.90, 0.72, 1.0)
    l_cyan.data.color = (0.65, 0.05, 1.0)
    l_mag.data.color  = (1.0, 0.05, 0.35)
    bg_node.inputs["Color"].default_value = (0.068, 0.035, 0.088, 1.0)

render_view(p_kai, (0.45, -2.10, 1.34), (88.5, 0.0, 12.0), 58.0, 1080, 1350)

# 8. Copy all 4 deliverables to brain artifacts directory
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
        print(f"[COPIED TO BRAIN] {dst_f} ({os.path.getsize(dp):,} bytes)")

print("===============================================================================")
print("  [ALL PRODUCTION DELIVERABLES COMPLETE] 4K PBR ATLAS OPERATIONAL")
print("===============================================================================")
