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
BLEND_DIR   = os.path.join(ROOT, "blend")
BRAIN_DIR   = r"C:\Users\esenc\.gemini\antigravity\brain\3ccecf18-5e96-4998-8aad-0804a4100391"
BLEND_SRC   = os.path.join(ROOT, "Ichiro_2390_Arcane_4K_Atlas.blend")

print("===============================================================================")
print("  ETHERNIUM SOVEREIGN // GENERATING UNREAL ENGINE 5 LODS & INSPECTION SUITE")
print("===============================================================================")

bpy.ops.wm.open_mainfile(filepath=BLEND_SRC)
scene = bpy.context.scene

char = bpy.data.objects['Ichiro_2390_Character']
bpy.ops.object.select_all(action='DESELECT')
char.select_set(True)
bpy.context.view_layer.objects.active = char

# 1. Setup Camera and Lighting for Inspection
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

scene.cycles.samples = 64
scene.cycles.use_denoising = True

cam_o = scene.objects.get("Cam_Production")
if not cam_o:
    cam_d = bpy.data.cameras.new("Cam_Production")
    cam_o = bpy.data.objects.new("Cam_Production", cam_d)
    scene.collection.objects.link(cam_o)
else:
    cam_d = cam_o.data

scene.camera = cam_o

# 2. Build LOD Hierarchy
print("[LOD] Creating LOD0, LOD1, and LOD2...")

# LOD0: Original high-detail hero mesh
lod0 = char
lod0.name = "Ichiro_2390_LOD0"

# LOD1: Mid-detail (ratio 0.20 -> ~34k polys)
lod1 = char.copy()
lod1.data = char.data.copy()
lod1.name = "Ichiro_2390_LOD1"
scene.collection.objects.link(lod1)
bpy.ops.object.select_all(action='DESELECT')
lod1.select_set(True)
bpy.context.view_layer.objects.active = lod1
dec1 = lod1.modifiers.new("Decimate_LOD1", 'DECIMATE')
dec1.ratio = 0.20
dec1.use_symmetry = True
bpy.ops.object.modifier_apply(modifier="Decimate_LOD1")

# LOD2: Distant low-poly (ratio 0.05 -> ~9.3k polys)
lod2 = char.copy()
lod2.data = char.data.copy()
lod2.name = "Ichiro_2390_LOD2"
scene.collection.objects.link(lod2)
bpy.ops.object.select_all(action='DESELECT')
lod2.select_set(True)
bpy.context.view_layer.objects.active = lod2
dec2 = lod2.modifiers.new("Decimate_LOD2", 'DECIMATE')
dec2.ratio = 0.05
dec2.use_symmetry = True
bpy.ops.object.modifier_apply(modifier="Decimate_LOD2")

# Create UE5 LODGroup empty parent
lod_group = bpy.data.objects.new("Ichiro_2390_LODGroup", None)
lod_group.empty_display_type = 'PLAIN_AXES'
scene.collection.objects.link(lod_group)

lod0.parent = lod_group
lod1.parent = lod_group
lod2.parent = lod_group

# Hide LOD1 and LOD2 from render by default
lod1.hide_render = True
lod2.hide_render = True

print(f"  [LOD0] Polys: {len(lod0.data.polygons):,}, Verts: {len(lod0.data.vertices):,}")
print(f"  [LOD1] Polys: {len(lod1.data.polygons):,}, Verts: {len(lod1.data.vertices):,}")
print(f"  [LOD2] Polys: {len(lod2.data.polygons):,}, Verts: {len(lod2.data.vertices):,}")

# 3. Export Standalone LODs and UE5 Package
p_lod0 = os.path.join(MODEL_DIR, "Ichiro_2390_LOD0.glb")
p_lod1 = os.path.join(MODEL_DIR, "Ichiro_2390_LOD1.glb")
p_lod2 = os.path.join(MODEL_DIR, "Ichiro_2390_LOD2.glb")
p_ue5_group = os.path.join(MODEL_DIR, "Ichiro_2390_UE5_LODGroup.glb")

def export_obj_glb(obj, path):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format='GLB',
        use_selection=True,
        export_apply=False,
        export_yup=True,
        export_morph=True,
        export_materials='EXPORT'
    )
    print(f"  [EXPORTED] {path} ({os.path.getsize(path):,} bytes)")

export_obj_glb(lod0, p_lod0)
export_obj_glb(lod1, p_lod1)
export_obj_glb(lod2, p_lod2)

# Export complete LODGroup
bpy.ops.object.select_all(action='DESELECT')
lod_group.select_set(True)
lod0.select_set(True)
lod1.select_set(True)
lod2.select_set(True)
bpy.ops.export_scene.gltf(
    filepath=p_ue5_group,
    export_format='GLB',
    use_selection=True,
    export_apply=False,
    export_yup=True,
    export_morph=True,
    export_materials='EXPORT'
)
print(f"  [EXPORTED UE5 GROUP] {p_ue5_group} ({os.path.getsize(p_ue5_group):,} bytes)")

# Save LOD .blend package
p_blend_ue5 = os.path.join(ROOT, "Ichiro_2390_UE5_LOD_Package.blend")
bpy.ops.wm.save_as_mainfile(filepath=p_blend_ue5)
print(f"  [SAVED BLEND] {p_blend_ue5}")

# 4. RENDER SUITE
def render_cam(path, loc, rot_deg, lens, rx, ry):
    scene.render.resolution_x = rx
    scene.render.resolution_y = ry
    cam_d.lens = lens
    cam_o.location = Vector(loc)
    cam_o.rotation_euler = Euler([math.radians(a) for a in rot_deg], 'XYZ')
    scene.render.filepath = path
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)
    print(f"  [RENDERED] {path}")

# A. RENDER UV CHECKERBOARD INSPECTION
print("[INSPECTION A] Rendering UV Checkerboard Calibration...")
checker_path = os.path.join(SCRATCH_DIR, "uv_checker_4k.png")
if os.path.exists(checker_path):
    img_chk = bpy.data.images.load(checker_path, check_existing=True)
    mat_chk = bpy.data.materials.new("Mat_UV_Checker_Inspection")
    mat_chk.use_nodes = True
    c_nodes = mat_chk.node_tree.nodes
    c_links = mat_chk.node_tree.links
    c_nodes.clear()
    c_out = c_nodes.new("ShaderNodeOutputMaterial")
    c_bsdf = c_nodes.new("ShaderNodeBsdfPrincipled")
    c_bsdf.inputs["Roughness"].default_value = 0.5
    c_links.new(c_bsdf.outputs["BSDF"], c_out.inputs["Surface"])
    
    c_uv = c_nodes.new("ShaderNodeUVMap")
    c_uv.uv_map = "UVMap"
    c_tex = c_nodes.new("ShaderNodeTexImage")
    c_tex.image = img_chk
    c_links.new(c_uv.outputs["UV"], c_tex.inputs["Vector"])
    c_links.new(c_tex.outputs["Color"], c_bsdf.inputs["Base Color"])
    
    orig_mat = lod0.data.materials[0]
    lod0.data.materials[0] = mat_chk
    
    # Render UV Checker Hero
    p_chk_hero = os.path.join(SCRATCH_DIR, "inspect_uv_checker_hero.png")
    render_cam(p_chk_hero, (0.0, -3.15, 0.98), (88.5, 0.0, 0.0), 52.0, 1080, 1440)
    
    # Render UV Checker CloseUp
    p_chk_close = os.path.join(SCRATCH_DIR, "inspect_uv_checker_close.png")
    render_cam(p_chk_close, (0.0, -1.35, 1.56), (88.5, 0.0, 0.0), 85.0, 1080, 1350)
    
    # Restore PBR material
    lod0.data.materials[0] = orig_mat

# B. RENDER CLAY TOPOLOGY INSPECTION (LOD0 Wireframe / Clay)
print("[INSPECTION B] Rendering Clay & Topology Wireframes...")
mat_clay = bpy.data.materials.new("Mat_Clay_Inspection")
mat_clay.use_nodes = True
cl_nodes = mat_clay.node_tree.nodes
cl_links = mat_clay.node_tree.links
cl_nodes.clear()
cl_out = cl_nodes.new("ShaderNodeOutputMaterial")
cl_bsdf = cl_nodes.new("ShaderNodeBsdfPrincipled")
cl_bsdf.inputs["Base Color"].default_value = (0.72, 0.74, 0.78, 1.0)
cl_bsdf.inputs["Roughness"].default_value = 0.45
cl_links.new(cl_bsdf.outputs["BSDF"], cl_out.inputs["Surface"])

# Create wireframe shader (mix clay with wireframe lines)
wf_node = cl_nodes.new("ShaderNodeWireframe")
wf_node.inputs["Size"].default_value = 0.5
mix_wf = cl_nodes.new("ShaderNodeMix")
mix_wf.data_type = 'RGBA'
mix_wf.inputs["Factor"].default_value = 1.0
cl_links.new(wf_node.outputs["Fac"], mix_wf.inputs["Factor"])
mix_wf.inputs[6].default_value = (0.72, 0.74, 0.78, 1.0) # Clay
mix_wf.inputs[7].default_value = (0.05, 0.20, 0.35, 1.0) # Cyan wireframe edge
cl_links.new(mix_wf.outputs["Result"], cl_bsdf.inputs["Base Color"])

# Render LOD0 Clay Wireframe
lod0.data.materials[0] = mat_clay
p_wf_hero = os.path.join(SCRATCH_DIR, "inspect_lod0_wireframe_hero.png")
render_cam(p_wf_hero, (0.0, -3.15, 0.98), (88.5, 0.0, 0.0), 52.0, 1080, 1440)

p_wf_close = os.path.join(SCRATCH_DIR, "inspect_lod0_wireframe_close.png")
render_cam(p_wf_close, (0.0, -1.35, 1.56), (88.5, 0.0, 0.0), 85.0, 1080, 1350)

# C. RENDER LOD COMPARISON TRIAD (LOD0 vs LOD1 vs LOD2)
print("[INSPECTION C] Rendering LOD0 vs LOD1 vs LOD2 Triad Views...")
lod0.data.materials[0] = orig_mat
lod1.data.materials.clear()
lod1.data.materials.append(orig_mat)
lod2.data.materials.clear()
lod2.data.materials.append(orig_mat)

# LOD0 Render
lod0.hide_render = False
lod1.hide_render = True
lod2.hide_render = True
p_triad_lod0 = os.path.join(SCRATCH_DIR, "triad_lod0.png")
render_cam(p_triad_lod0, (0.0, -3.15, 0.98), (88.5, 0.0, 0.0), 52.0, 720, 1280)

# LOD1 Render
lod0.hide_render = True
lod1.hide_render = False
lod2.hide_render = True
p_triad_lod1 = os.path.join(SCRATCH_DIR, "triad_lod1.png")
render_cam(p_triad_lod1, (0.0, -3.15, 0.98), (88.5, 0.0, 0.0), 52.0, 720, 1280)

# LOD2 Render
lod0.hide_render = True
lod1.hide_render = True
lod2.hide_render = False
p_triad_lod2 = os.path.join(SCRATCH_DIR, "triad_lod2.png")
render_cam(p_triad_lod2, (0.0, -3.15, 0.98), (88.5, 0.0, 0.0), 52.0, 720, 1280)

# Render LOD Wireframes for comparison
lod0.data.materials[0] = mat_clay
lod1.data.materials[0] = mat_clay
lod2.data.materials[0] = mat_clay

lod0.hide_render = False
lod1.hide_render = True
lod2.hide_render = True
p_triad_wf_lod0 = os.path.join(SCRATCH_DIR, "triad_wf_lod0.png")
render_cam(p_triad_wf_lod0, (0.0, -3.15, 0.98), (88.5, 0.0, 0.0), 52.0, 720, 1280)

lod0.hide_render = True
lod1.hide_render = False
lod2.hide_render = True
p_triad_wf_lod1 = os.path.join(SCRATCH_DIR, "triad_wf_lod1.png")
render_cam(p_triad_wf_lod1, (0.0, -3.15, 0.98), (88.5, 0.0, 0.0), 52.0, 720, 1280)

lod0.hide_render = True
lod1.hide_render = True
lod2.hide_render = False
p_triad_wf_lod2 = os.path.join(SCRATCH_DIR, "triad_wf_lod2.png")
render_cam(p_triad_wf_lod2, (0.0, -3.15, 0.98), (88.5, 0.0, 0.0), 52.0, 720, 1280)

# Reset state
lod0.data.materials[0] = orig_mat
lod0.hide_render = False
lod1.hide_render = True
lod2.hide_render = True

print("===============================================================================")
print("  [SUCCESS] ALL LOD ASSETS AND BASE RENDERS READY FOR HUD COMPOSITING")
print("===============================================================================")
