import bpy
import os
import time
import shutil

SCRATCH_DIR = r"C:\Users\esenc\.gemini\antigravity\brain\3ccecf18-5e96-4998-8aad-0804a4100391\scratch"
ROOT        = r"e:\DESCARGAS\Web3\My web3 Projects\KPR\KPR Art Portfolio\KPR (My art)\KPR Ai Portfolio\Ichiro\Ichiro_3D_Arcane"
TEX_DIR     = os.path.join(ROOT, "textures")
MODEL_DIR   = os.path.join(ROOT, "models")
BLEND_SRC   = os.path.join(ROOT, "Ichiro_2390_Arcane_Scene.blend")

print("===============================================================================")
print("  ETHERNIUM SOVEREIGN // MASTER 4K PBR TEXTURE ATLAS BAKING PIPELINE")
print("===============================================================================")

bpy.ops.wm.open_mainfile(filepath=BLEND_SRC)
scene = bpy.context.scene

char = bpy.data.objects['Ichiro_2390_Character']
bpy.ops.object.select_all(action='DESELECT')
char.select_set(True)
bpy.context.view_layer.objects.active = char

# 1. Non-Overlapping Single Atlas UV Layout (HeadBust V: 0.51-0.99, Body V: 0.01-0.49)
if 'UVMap_Atlas_4K' in char.data.uv_layers:
    char.data.uv_layers.remove(char.data.uv_layers['UVMap_Atlas_4K'])

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

char.data.uv_layers.active = uv_atlas
char.data.uv_layers["UVMap_Atlas_4K"].active_render = True

# 2. Cycles CPU Baking Setup (Deterministic, zero VRAM overflow)
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 1
scene.render.bake.margin = 32

BAKE_RES = 4096
print(f"[BAKE CONFIG] Resolution: {BAKE_RES}x{BAKE_RES}, Margin: 32px, Engine: Cycles CPU Multi-threaded")

def setup_bake_node(img):
    for mat in char.data.materials:
        if not mat or not mat.node_tree:
            continue
        old_n = mat.node_tree.nodes.get("Bake_Target_Node")
        if old_n:
            mat.node_tree.nodes.remove(old_n)
        node = mat.node_tree.nodes.new("ShaderNodeTexImage")
        node.name = "Bake_Target_Node"
        node.image = img
        mat.node_tree.nodes.active = node
        node.select = True

# A. BAKE DIFFUSE / BASE COLOR (4K)
print("[1/4] Baking 4K Master Diffuse / BaseColor...")
img_diff = bpy.data.images.new("Ichiro_Master_Diffuse_4K", width=BAKE_RES, height=BAKE_RES, alpha=True)
setup_bake_node(img_diff)
scene.cycles.bake_type = 'DIFFUSE'
scene.render.bake.use_pass_direct = False
scene.render.bake.use_pass_indirect = False
scene.render.bake.use_pass_color = True

t0 = time.time()
bpy.ops.object.bake(type='DIFFUSE')
dt = time.time() - t0
p_diff = os.path.join(TEX_DIR, "ichiro_master_diffuse_4k.png")
img_diff.filepath_raw = p_diff
img_diff.file_format = 'PNG'
img_diff.save()
print(f"  [SAVED] {p_diff} ({dt:.2f}s)")

# B. BAKE TANGENT NORMAL (4K)
print("[2/4] Baking 4K Master Tangent Normal...")
img_nrm = bpy.data.images.new("Ichiro_Master_Normal_4K", width=BAKE_RES, height=BAKE_RES, alpha=True)
img_nrm.colorspace_settings.name = 'Non-Color'
setup_bake_node(img_nrm)
scene.cycles.bake_type = 'NORMAL'
scene.render.bake.normal_space = 'TANGENT'

t0 = time.time()
bpy.ops.object.bake(type='NORMAL')
dt = time.time() - t0
p_nrm = os.path.join(TEX_DIR, "ichiro_master_normal_4k.png")
img_nrm.filepath_raw = p_nrm
img_nrm.file_format = 'PNG'
img_nrm.save()
print(f"  [SAVED] {p_nrm} ({dt:.2f}s)")

# C. BAKE ROUGHNESS (4K)
print("[3/4] Baking 4K Master Roughness...")
img_rgh = bpy.data.images.new("Ichiro_Master_Roughness_4K", width=BAKE_RES, height=BAKE_RES, alpha=False)
img_rgh.colorspace_settings.name = 'Non-Color'
setup_bake_node(img_rgh)
scene.cycles.bake_type = 'ROUGHNESS'

t0 = time.time()
bpy.ops.object.bake(type='ROUGHNESS')
dt = time.time() - t0
p_rgh = os.path.join(TEX_DIR, "ichiro_master_roughness_4k.png")
img_rgh.filepath_raw = p_rgh
img_rgh.file_format = 'PNG'
img_rgh.save()
print(f"  [SAVED] {p_rgh} ({dt:.2f}s)")

# D. BAKE CYBER-MAGMA EMISSION (4K)
print("[4/4] Baking 4K Master Cyber-Magma Emission (Isolated)...")
stored_outputs = []
for mat in char.data.materials:
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    out = [n for n in nodes if n.type == 'OUTPUT_MATERIAL'][0]
    old_link = out.inputs["Surface"].links[0] if out.inputs["Surface"].links else None
    
    # Create isolated emission shader
    em_bake_node = nodes.new("ShaderNodeEmission")
    em_bake_node.name = "Temp_Bake_Emission"
    em_bake_node.inputs["Strength"].default_value = 1.0
    
    # Connect Mix.003 (the pure cyber-magma crack & eye glow) to the emission shader
    m3 = nodes.get("Mix.003")
    if m3:
        links.new(m3.outputs["Result"], em_bake_node.inputs["Color"])
    else:
        # Fallback: check Image Texture.007
        t7 = nodes.get("Image Texture.007")
        if t7:
            links.new(t7.outputs["Color"], em_bake_node.inputs["Color"])
            
    links.new(em_bake_node.outputs["Emission"], out.inputs["Surface"])
    stored_outputs.append((out, old_link, em_bake_node))

img_emit = bpy.data.images.new("Ichiro_Master_Emission_4K", width=BAKE_RES, height=BAKE_RES, alpha=True)
setup_bake_node(img_emit)
scene.cycles.bake_type = 'EMIT'

t0 = time.time()
bpy.ops.object.bake(type='EMIT')
dt = time.time() - t0
p_emit = os.path.join(TEX_DIR, "ichiro_master_emission_4k.png")
img_emit.filepath_raw = p_emit
img_emit.file_format = 'PNG'
img_emit.save()
print(f"  [SAVED] {p_emit} ({dt:.2f}s)")

# Restore original material trees
for out, old_link, temp_n in stored_outputs:
    mat = out.id_data
    if old_link:
        mat.node_tree.links.new(old_link.from_socket, out.inputs["Surface"])
    mat.node_tree.nodes.remove(temp_n)

# 3. Clean and Build Unified Universal Master Material (Mat_Ichiro_Master_PBR_4K)
print("[MATERIAL] Assembling Universal 100% standard Principled BSDF PBR material...")
mat_pbr = bpy.data.materials.new("Mat_Ichiro_Master_PBR_4K")
try:
    mat_pbr.use_nodes = True
except Exception:
    pass
nodes = mat_pbr.node_tree.nodes
links = mat_pbr.node_tree.links
nodes.clear()

out = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

uv_n = nodes.new("ShaderNodeUVMap")
uv_n.uv_map = "UVMap"

def add_tex(img, is_color=True):
    t = nodes.new("ShaderNodeTexImage")
    t.image = img
    if not is_color:
        t.image.colorspace_settings.name = 'Non-Color'
    t.extension = 'EXTEND'
    links.new(uv_n.outputs["UV"], t.inputs["Vector"])
    return t

t_diff = add_tex(img_diff, is_color=True)
links.new(t_diff.outputs["Color"], bsdf.inputs["Base Color"])

t_nrm = add_tex(img_nrm, is_color=False)
nrm_map = nodes.new("ShaderNodeNormalMap")
nrm_map.space = 'TANGENT'
nrm_map.inputs["Strength"].default_value = 1.0
links.new(t_nrm.outputs["Color"], nrm_map.inputs["Color"])
links.new(nrm_map.outputs["Normal"], bsdf.inputs["Normal"])

t_rgh = add_tex(img_rgh, is_color=False)
links.new(t_rgh.outputs["Color"], bsdf.inputs["Roughness"])

t_emit = add_tex(img_emit, is_color=True)
links.new(t_emit.outputs["Color"], bsdf.inputs["Emission Color"])
bsdf.inputs["Emission Strength"].default_value = 1.2
bsdf.inputs["Metallic"].default_value = 0.0

# Assign mat_pbr as the single unified material on char
char.data.materials.clear()
char.data.materials.append(mat_pbr)
for p in char.data.polygons:
    p.material_index = 0

# Set UVMap_Atlas_4K as primary UVMap
char.data.uv_layers["UVMap_Atlas_4K"].name = "UVMap"
char.data.uv_layers.active = char.data.uv_layers["UVMap"]
char.data.uv_layers["UVMap"].active_render = True

# 4. Save and Export Standard PBR Assets
out_blend = os.path.join(ROOT, "Ichiro_2390_Arcane_4K_Atlas.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
print(f"[SUCCESS] Saved Master 4K Scene: {out_blend}")

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
print(f"[SUCCESS] Exported Universal 4K PBR GLB: {out_glb}")

# 5. Render Verification Render (Cycles CPU/GPU safe)
print("[RENDER] Rendering verification render of baked 4K PBR model...")
scene.render.resolution_x = 1080
scene.render.resolution_y = 1440
scene.render.filepath = os.path.join(SCRATCH_DIR, "test_baked_4k_hero_render.png")
cam = scene.objects.get("Cam_Production")
if not cam:
    cam = scene.objects.get("Cam_Test")
if cam:
    scene.camera = cam

# Use GPU for render if available, fallback to CPU
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    scene.cycles.device = 'GPU'
except Exception:
    scene.cycles.device = 'CPU'

scene.cycles.samples = 64
bpy.ops.render.render(write_still=True)
print(f"[SUCCESS] Saved verification render: {scene.render.filepath}")

print("===============================================================================")
print("  [4K ATLAS BAKING PIPELINE COMPLETE] 1 MATERIAL, 1 UV SET, ZERO DEPENDENCY")
print("===============================================================================")
