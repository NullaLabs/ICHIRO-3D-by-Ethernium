import bpy
import bmesh
import math
import os
import numpy as np
from mathutils import Vector, Euler, Matrix

SCRATCH_DIR = r"C:\Users\esenc\.gemini\antigravity\brain\3ccecf18-5e96-4998-8aad-0804a4100391\scratch"
ROOT        = r"e:\DESCARGAS\Web3\My web3 Projects\KPR\KPR Art Portfolio\KPR (My art)\KPR Ai Portfolio\Ichiro\Ichiro_3D_Arcane"
BLEND_SRC   = os.path.join(ROOT, "Ichiro_2390_Arcane_Scene.blend")

print("===============================================================================")
print("  ETHERNIUM SOVEREIGN // PHASE 1: TACTICAL CLOTHING & REAL 3D VOLUME BUILDER")
print("===============================================================================")

bpy.ops.wm.open_mainfile(filepath=BLEND_SRC)
scene = bpy.context.scene

char = bpy.data.objects['Ichiro_2390_Character']
char_verts = np.array([v.co for v in char.data.vertices])

# Ensure collections
def get_col(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c

col_clothing = get_col("03_TACTICAL_CLOTHING_LAYERS")

def link_clothing(obj):
    for c in bpy.data.collections:
        if obj.name in c.objects:
            c.objects.unlink(obj)
    col_clothing.objects.link(obj)

# =============================================================================
# 1. PIECE A: HIGH STANDING MANDARIN COLLAR & BOLERO JACKET SHELL
# =============================================================================
print("[1/4] Constructing 3D High Standing Mandarin Collar & Bolero Jacket...")

# Construct the High Standing Mandarin Collar around neck (Z: 1.38 to 1.48)
# Radius ~ 0.082m, flaring out to 0.096m at chin
n_segments = 32
collar_verts = []
collar_faces = []

# Heights: base=1.38, mid=1.43, top=1.48
z_levels = [1.380, 1.430, 1.485]
radii_x  = [0.082, 0.088, 0.098]
radii_y  = [0.088, 0.094, 0.104]
y_offset = -0.005 # Center slightly forward

for r_idx, (z, rx, ry) in enumerate(zip(z_levels, radii_x, radii_y)):
    for i in range(n_segments):
        theta = 2.0 * math.pi * i / n_segments
        # Don't close completely at front throat - subtle V-notch
        vx = math.sin(theta) * rx
        vy = math.cos(theta) * ry + y_offset
        collar_verts.append((vx, vy, z))

for ring in range(len(z_levels) - 1):
    for i in range(n_segments):
        i_next = (i + 1) % n_segments
        v1 = ring * n_segments + i
        v2 = ring * n_segments + i_next
        v3 = (ring + 1) * n_segments + i_next
        v4 = (ring + 1) * n_segments + i
        collar_faces.append((v1, v2, v3, v4))

mesh_collar = bpy.data.meshes.new("Mesh_Mandarin_Collar")
mesh_collar.from_pydata(collar_verts, [], collar_faces)
mesh_collar.update()

obj_collar = bpy.data.objects.new("Ichiro_Mandarin_Collar", mesh_collar)
link_clothing(obj_collar)

# Solidify modifier for physical collar thickness (3.5 mm)
sol_c = obj_collar.modifiers.new("Solidify_Collar", 'SOLIDIFY')
sol_c.thickness = 0.0045
sol_c.offset = 1.0 # Outward
sub_c = obj_collar.modifiers.new("Subd_Collar", 'SUBSURF')
sub_c.levels = 1

# Extract Bolero Jacket from Character (Z in [1.22, 1.42], upper torso and shoulders)
bm = bmesh.new()
bm.from_mesh(char.data)

# Bolero selection criteria: upper chest & back, sleeves
bolero_faces = []
for f in bm.faces:
    zc = f.calc_center_median().z
    yc = f.calc_center_median().y
    xc = f.calc_center_median().x
    # Bolero cuts off in front at z=1.23, back goes down to z=1.18, sleeves go down to z=1.10
    is_bolero = False
    if zc >= 1.23 and zc <= 1.44:
        # Exclude head/neck
        if not (zc > 1.40 and abs(xc) < 0.07 and abs(yc) < 0.07):
            is_bolero = True
    elif zc >= 1.10 and zc < 1.23 and abs(xc) > 0.18:
        # Sleeves
        is_bolero = True
    elif zc >= 1.18 and zc < 1.23 and yc > 0.02:
        # Upper dorsal back
        is_bolero = True
    
    if is_bolero:
        f.select_set(True)
    else:
        f.select_set(False)

# Duplicate selected faces into new mesh
bm_bolero = bmesh.new()
bm_bolero.from_mesh(char.data)
del_faces = [f for f in bm_bolero.faces if not (
    (f.calc_center_median().z >= 1.23 and f.calc_center_median().z <= 1.44 and not (f.calc_center_median().z > 1.40 and abs(f.calc_center_median().x) < 0.07 and abs(f.calc_center_median().y) < 0.07))
    or (f.calc_center_median().z >= 1.10 and f.calc_center_median().z < 1.23 and abs(f.calc_center_median().x) > 0.18)
    or (f.calc_center_median().z >= 1.18 and f.calc_center_median().z < 1.23 and f.calc_center_median().y > 0.02)
)]
bmesh.ops.delete(bm_bolero, geom=del_faces, context='FACES')

mesh_bolero = bpy.data.meshes.new("Mesh_Bolero_Jacket")
bm_bolero.to_mesh(mesh_bolero)
bm_bolero.free()
bm.free()

obj_bolero = bpy.data.objects.new("Ichiro_Bolero_Jacket", mesh_bolero)
link_clothing(obj_bolero)

# Give bolero jacket real 3D thickness (6 mm outer shell)
# Slightly expand outwards along normals so it sits over the base body
disp_b = obj_bolero.modifiers.new("Displace_Bolero", 'DISPLACE')
disp_b.strength = 0.005 # 5mm clearance over body
sol_b = obj_bolero.modifiers.new("Solidify_Bolero", 'SOLIDIFY')
sol_b.thickness = 0.006 # 6mm fabric thickness
sol_b.offset = 1.0

print(f"  [BOLERO] Polygons: {len(obj_bolero.data.polygons)}, Thickness: 6mm, Offset: +5mm")

# =============================================================================
# 2. PIECE B: TACTICAL X-HARNESS & STERNIC BUCKLE
# =============================================================================
print("[2/4] Constructing 3D Tactical X-Harness & Buckles...")

# Create straps that cross the torso in an X
def create_strap(name, start_pt, end_pt, width=0.032, thickness=0.004, normal_dir=(0, 1, 0), n_subdiv=8):
    # Parametric curved strip following torso curvature
    s_verts, s_faces = [], []
    v_start = Vector(start_pt)
    v_end = Vector(end_pt)
    v_dir = (v_end - v_start).normalized()
    n_dir = Vector(normal_dir).normalized()
    w_dir = v_dir.cross(n_dir).normalized() * (width * 0.5)
    
    for i in range(n_subdiv + 1):
        t = i / float(n_subdiv)
        # Interpolate with slight arc over chest
        pos = v_start.lerp(v_end, t)
        # Arc protrusion
        arc = math.sin(t * math.pi) * 0.015
        center = pos + n_dir * arc
        
        idx = len(s_verts)
        s_verts.append(center - w_dir)
        s_verts.append(center + w_dir)
        
        if i > 0:
            s_faces.append((idx - 2, idx - 1, idx + 1, idx))
            
    m = bpy.data.meshes.new(f"Mesh_{name}")
    m.from_pydata(s_verts, [], s_faces)
    m.update()
    obj = bpy.data.objects.new(name, m)
    link_clothing(obj)
    
    # Solidify
    sol = obj.modifiers.new(f"Sol_{name}", 'SOLIDIFY')
    sol.thickness = thickness
    sol.offset = 1.0
    return obj

# Front Diagonal Strap 1: Right shoulder to left ribs
s_f1 = create_strap("Strap_Front_RightToLeft", (0.16, -0.065, 1.36), (-0.14, -0.075, 1.15), width=0.028, normal_dir=(0, -1, 0.3))
# Front Diagonal Strap 2: Left shoulder to right ribs
s_f2 = create_strap("Strap_Front_LeftToRight", (-0.16, -0.065, 1.36), (0.14, -0.075, 1.15), width=0.028, normal_dir=(0, -1, 0.3))

# Central Sternum Buckle (Angular Cyberpunk Octagonal Plate)
b_mesh = bpy.data.meshes.new("Mesh_Sternum_Buckle")
b_verts = []
b_faces = []
b_rad = 0.024
b_thick = 0.008
for a in range(8):
    ang = 2.0 * math.pi * a / 8.0 + math.pi/8.0
    bx = math.sin(ang) * b_rad
    bz = math.cos(ang) * b_rad
    b_verts.append((bx, -0.004, bz))
    b_verts.append((bx, +0.004, bz))

for a in range(8):
    a_next = (a + 1) % 8
    v1 = a * 2
    v2 = a * 2 + 1
    v3 = a_next * 2 + 1
    v4 = a_next * 2
    b_faces.append((v1, v2, v3, v4))
# Caps
b_faces.append(tuple([a*2 for a in range(8)]))
b_faces.append(tuple([a*2+1 for a in reversed(range(8))]))

b_mesh.from_pydata(b_verts, [], b_faces)
b_mesh.update()
obj_buckle = bpy.data.objects.new("Ichiro_Sternum_Buckle", b_mesh)
link_clothing(obj_buckle)
obj_buckle.location = Vector((0.000, -0.098, 1.255))
obj_buckle.rotation_euler = Euler((math.radians(-8.0), 0.0, 0.0), 'XYZ')

# Back Diagonal Straps: Crossing over upper back to hold dorsal scabbard mount
s_b1 = create_strap("Strap_Back_RightToLeft", (0.15, 0.115, 1.35), (-0.14, 0.105, 1.18), width=0.030, normal_dir=(0, 1, 0.2))
s_b2 = create_strap("Strap_Back_LeftToRight", (-0.15, 0.115, 1.35), (0.14, 0.105, 1.18), width=0.030, normal_dir=(0, 1, 0.2))

# =============================================================================
# 3. PIECE C: TACTICAL COMBAT BELT, WAIST BUCKLE & UTILITY POUCHES
# =============================================================================
print("[3/4] Constructing 3D Tactical Combat Belt, Buckles & Hip Pouches...")

# Tactical Belt Loop around waist (Z: 0.98 to 1.03)
belt_segments = 36
belt_verts = []
belt_faces = []
belt_rx = 0.178
belt_ry = 0.128
belt_z0 = 0.980
belt_z1 = 1.028

for i in range(belt_segments):
    theta = 2.0 * math.pi * i / belt_segments
    bx = math.sin(theta) * belt_rx
    by = math.cos(theta) * belt_ry - 0.005
    belt_verts.append((bx, by, belt_z0))
    belt_verts.append((bx, by, belt_z1))

for i in range(belt_segments):
    i_next = (i + 1) % belt_segments
    v1 = i * 2
    v2 = i * 2 + 1
    v3 = i_next * 2 + 1
    v4 = i_next * 2
    belt_faces.append((v1, v2, v3, v4))

mesh_belt = bpy.data.meshes.new("Mesh_Tactical_Belt")
mesh_belt.from_pydata(belt_verts, [], belt_faces)
mesh_belt.update()
obj_belt = bpy.data.objects.new("Ichiro_Tactical_Belt", mesh_belt)
link_clothing(obj_belt)

sol_belt = obj_belt.modifiers.new("Sol_Belt", 'SOLIDIFY')
sol_belt.thickness = 0.007 # 7mm thick ballistic belt
sol_belt.offset = 1.0

# Front Heavy Belt Buckle (Beveled Rectangular Plaque)
def create_tech_box(name, dim, loc, rot=(0,0,0)):
    dx, dy, dz = dim[0]*0.5, dim[1]*0.5, dim[2]*0.5
    v = [
        (-dx, -dy, -dz), (dx, -dy, -dz), (dx, dy, -dz), (-dx, dy, -dz),
        (-dx, -dy, dz),  (dx, -dy, dz),  (dx, dy, dz),  (-dx, dy, dz)
    ]
    f = [
        (0, 1, 2, 3), (4, 7, 6, 5),
        (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)
    ]
    m = bpy.data.meshes.new(f"Mesh_{name}")
    m.from_pydata(v, [], f)
    m.update()
    o = bpy.data.objects.new(name, m)
    link_clothing(o)
    o.location = Vector(loc)
    o.rotation_euler = Euler([math.radians(a) for a in rot], 'XYZ')
    bev = o.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.003
    bev.segments = 2
    return o

# Main Front Buckle
create_tech_box("Ichiro_Belt_Main_Buckle", (0.058, 0.016, 0.046), (0.0, -0.138, 1.004), rot=(4, 0, 0))

# Left & Right Hip Utility Pouches (Tactical Cargo Boxes)
create_tech_box("Ichiro_Pouch_Left_A", (0.045, 0.038, 0.075), (0.185, -0.010, 0.995), rot=(0, -6, 85))
create_tech_box("Ichiro_Pouch_Left_B", (0.040, 0.032, 0.065), (0.165, 0.055, 0.995), rot=(0, -6, 110))
create_tech_box("Ichiro_Pouch_Right_A", (0.045, 0.038, 0.075), (-0.185, -0.010, 0.995), rot=(0, 6, -85))
create_tech_box("Ichiro_Pouch_Right_B", (0.040, 0.032, 0.065), (-0.165, 0.055, 0.995), rot=(0, 6, -110))

# =============================================================================
# 4. PIECE D: COMBAT BOOT THICK TREAD SOLES & ANKLE BUCKLES
# =============================================================================
print("[4/4] Constructing 3D Combat Boot Lugged Soles & Ankle Straps...")

# Create thick molded sole with deep lugs under each foot
def create_boot_sole(name, loc, is_right=False):
    # Foot contour (rounded heel and toe box)
    sx = -1 if is_right else 1
    sole_m = bpy.data.meshes.new(f"Mesh_{name}")
    # Sole profile
    pts = [
        (-0.048*sx, -0.095), (-0.055*sx, -0.020), (-0.052*sx, 0.080), (-0.035*sx, 0.135),
        (0.000, 0.155),
        (0.035*sx, 0.135), (0.052*sx, 0.080), (0.055*sx, -0.020), (0.048*sx, -0.095),
        (0.000, -0.115)
    ]
    v_list = []
    f_list = []
    # Base (Z=0.002) and Top (Z=0.035) -> 3.3 cm thick rugged combat sole
    n = len(pts)
    for x, y in pts:
        v_list.append((x, y, 0.002)) # Bottom
    for x, y in pts:
        v_list.append((x*0.96, y*0.96, 0.036)) # Top rim
        
    for i in range(n):
        i_next = (i + 1) % n
        f_list.append((i, i_next, n + i_next, n + i))
    # Bottom cap
    f_list.append(tuple(range(n)))
    # Top cap
    f_list.append(tuple([n + i for i in reversed(range(n))]))
    
    sole_m.from_pydata(v_list, [], f_list)
    sole_m.update()
    
    obj_s = bpy.data.objects.new(name, sole_m)
    link_clothing(obj_s)
    obj_s.location = Vector(loc)
    bev = obj_s.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.003
    bev.segments = 2
    return obj_s

# Left Foot Sole (loc x ~ 0.125, y ~ 0.015)
sole_l = create_boot_sole("Ichiro_Sole_L", (0.125, 0.012, 0.000), is_right=False)
# Right Foot Sole (loc x ~ -0.125, y ~ 0.015)
sole_r = create_boot_sole("Ichiro_Sole_R", (-0.125, 0.012, 0.000), is_right=True)

# Ankle Straps & Shin Buckles
create_tech_box("Ichiro_Ankle_Buckle_L", (0.024, 0.010, 0.016), (0.178, 0.015, 0.160), rot=(0, 0, 90))
create_tech_box("Ichiro_Ankle_Buckle_R", (0.024, 0.010, 0.016), (-0.178, 0.015, 0.160), rot=(0, 0, -90))

# Knee Protection Plates (Shin / Knee Armor)
create_tech_box("Ichiro_Knee_Armor_L", (0.065, 0.014, 0.085), (0.128, -0.118, 0.520), rot=(-12, 0, 0))
create_tech_box("Ichiro_Knee_Armor_R", (0.065, 0.014, 0.085), (-0.128, -0.118, 0.520), rot=(-12, 0, 0))

# =============================================================================
# 5. ASSIGN AUTHENTIC MATERIALS & TEXTURES
# =============================================================================
print("[MATERIALS] Assigning authentic PBR tactical shaders...")

# 1. Bolero Jacket Material (Off-white / Sage Arcane Stylized Matte Fabric)
mat_bolero = bpy.data.materials.new("Mat_Ichiro_Bolero_Jacket")
mat_bolero.use_nodes = True
b_nodes = mat_bolero.node_tree.nodes
b_links = mat_bolero.node_tree.links
b_nodes.clear()
out_b = b_nodes.new("ShaderNodeOutputMaterial")
bsdf_b = b_nodes.new("ShaderNodeBsdfPrincipled")
b_links.new(bsdf_b.outputs["BSDF"], out_b.inputs["Surface"])
# Authentic Arcane Bolero color: subtle warm light-grey / bone tone [0.82, 0.81, 0.78]
bsdf_b.inputs["Base Color"].default_value = (0.82, 0.81, 0.78, 1.0)
bsdf_b.inputs["Roughness"].default_value = 0.58
bsdf_b.inputs["Metallic"].default_value = 0.02
obj_bolero.data.materials.clear()
obj_bolero.data.materials.append(mat_bolero)
obj_collar.data.materials.clear()
obj_collar.data.materials.append(mat_bolero)

# 2. Harness & Belt Material (Heavy Tactical Ballistic Nylon / Black Leather)
mat_strap = bpy.data.materials.new("Mat_Ichiro_Tactical_Straps")
mat_strap.use_nodes = True
s_nodes = mat_strap.node_tree.nodes
s_links = mat_strap.node_tree.links
s_nodes.clear()
out_s = s_nodes.new("ShaderNodeOutputMaterial")
bsdf_s = s_nodes.new("ShaderNodeBsdfPrincipled")
s_links.new(bsdf_s.outputs["BSDF"], out_s.inputs["Surface"])
bsdf_s.inputs["Base Color"].default_value = (0.038, 0.042, 0.048, 1.0) # Deep charcoal tactical black
bsdf_s.inputs["Roughness"].default_value = 0.42
bsdf_s.inputs["Metallic"].default_value = 0.05

strap_objs = [s_f1, s_f2, s_b1, s_b2, obj_belt]
for o in strap_objs:
    o.data.materials.clear()
    o.data.materials.append(mat_strap)

# 3. Metallic Cyberpunk Buckles (Gunmetal / Brushed Titanium with Magma Accents)
mat_metal = bpy.data.materials.new("Mat_Ichiro_Cyber_Buckles")
mat_metal.use_nodes = True
m_nodes = mat_metal.node_tree.nodes
m_links = mat_metal.node_tree.links
m_nodes.clear()
out_m = m_nodes.new("ShaderNodeOutputMaterial")
bsdf_m = m_nodes.new("ShaderNodeBsdfPrincipled")
m_links.new(bsdf_m.outputs["BSDF"], out_m.inputs["Surface"])
bsdf_m.inputs["Base Color"].default_value = (0.18, 0.20, 0.24, 1.0) # Gunmetal
bsdf_m.inputs["Roughness"].default_value = 0.28
bsdf_m.inputs["Metallic"].default_value = 0.92

metal_objs = [
    obj_buckle,
    bpy.data.objects.get("Ichiro_Belt_Main_Buckle"),
    bpy.data.objects.get("Ichiro_Pouch_Left_A"),
    bpy.data.objects.get("Ichiro_Pouch_Left_B"),
    bpy.data.objects.get("Ichiro_Pouch_Right_A"),
    bpy.data.objects.get("Ichiro_Pouch_Right_B"),
    bpy.data.objects.get("Ichiro_Ankle_Buckle_L"),
    bpy.data.objects.get("Ichiro_Ankle_Buckle_R"),
    bpy.data.objects.get("Ichiro_Knee_Armor_L"),
    bpy.data.objects.get("Ichiro_Knee_Armor_R")
]
for o in metal_objs:
    if o:
        o.data.materials.clear()
        o.data.materials.append(mat_metal)

# 4. Boot Soles (Vulcanized Black Combat Rubber)
mat_rubber = bpy.data.materials.new("Mat_Ichiro_Combat_Rubber")
mat_rubber.use_nodes = True
r_nodes = mat_rubber.node_tree.nodes
r_links = mat_rubber.node_tree.links
r_nodes.clear()
out_r = r_nodes.new("ShaderNodeOutputMaterial")
bsdf_r = r_nodes.new("ShaderNodeBsdfPrincipled")
r_links.new(bsdf_r.outputs["BSDF"], out_r.inputs["Surface"])
bsdf_r.inputs["Base Color"].default_value = (0.025, 0.028, 0.032, 1.0)
bsdf_r.inputs["Roughness"].default_value = 0.65
bsdf_r.inputs["Metallic"].default_value = 0.0

sole_l.data.materials.clear(); sole_l.data.materials.append(mat_rubber)
sole_r.data.materials.clear(); sole_r.data.materials.append(mat_rubber)

# =============================================================================
# 6. SAVE TEST BLEND & RENDER VERIFICATION VIEWS
# =============================================================================
out_test_blend = os.path.join(SCRATCH_DIR, "test_layered_tactical_clothing.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_test_blend)
print(f"[SAVED] Test blend scene: {out_test_blend}")

# Cycles render setup
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

def render_clothing_view(path, loc, rot_deg, lens=52.0, rx=1080, ry=1440):
    scene.render.resolution_x = rx
    scene.render.resolution_y = ry
    cam_d.lens = lens
    cam_o.location = Vector(loc)
    cam_o.rotation_euler = Euler([math.radians(a) for a in rot_deg], 'XYZ')
    scene.render.filepath = path
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)
    print(f"  [RENDERED] {path}")

# Front Torso & Clothing Beauty View
p_c_front = os.path.join(SCRATCH_DIR, "test_clothing_front_torso.png")
render_clothing_view(p_c_front, (0.0, -2.10, 1.15), (88.5, 0.0, 0.0), lens=60.0)

# Back Torso & Dorsal Scabbard Mount View
p_c_back = os.path.join(SCRATCH_DIR, "test_clothing_back_torso.png")
render_clothing_view(p_c_back, (0.0, 2.15, 1.15), (90.0, 0.0, 180.0), lens=60.0)

# Full Body 3/4 Tactical View
p_c_hero = os.path.join(SCRATCH_DIR, "test_clothing_hero_34.png")
render_clothing_view(p_c_hero, (-1.10, -2.95, 0.98), (88.5, 0.0, -20.0), lens=50.0)

print("===============================================================================")
print("  [SUCCESS] PHASE 1 TACTICAL CLOTHING LAYERS FULLY CONSTRUCTED & RENDERED")
print("===============================================================================")
