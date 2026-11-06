"""Sew the validated eyelid to a COPY of the repaired character.

Experimental transition on the dense reference, not final game retopology.
Blender --background --factory-startup --python-exit-code 1 --python THIS_FILE -- --out NEW_DIR
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--expand-boundary', action='store_true', help='Experimental boundary cleanup; can reject branched cuts')
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
OUT = args.out.resolve()
OUT.mkdir(parents=True, exist_ok=True)
assert not (OUT/'Ichiro_Orbital_Integration_v01.blend').exists(), 'Use a fresh output directory'
source_path = ROOT/'exports/rig_connectivity_v01/Ichiro_Chibi_Rig_Connectivity_v01.blend'
source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'exports/eyelid_blink_pilot_v01/Ichiro_Eye_R_Blink_Pilot.blend'))
pilot = bpy.data.objects['EYE_R_GAME_BLINK_PILOT']
positions = [v.co.copy() for v in pilot.data.vertices]
closed = [v.co.copy() for v in pilot.data.shape_keys.key_blocks['Blink_R'].data]
faces = [tuple(p.vertices) for p in pilot.data.polygons]
cap = bpy.data.objects['EYE_R_SURFACE_SUPPORT__NOT_FULL_GLOBE']
cap_positions = [tuple(v.co) for v in cap.data.vertices]
cap_faces = [tuple(p.vertices) for p in cap.data.polygons]
bpy.ops.wm.open_mainfile(filepath=str(source_path))
scene = bpy.context.scene
source = bpy.data.objects['ICH_CHIBI_CONNECTIVITY_CANDIDATE_v01']
# Linked object visibility flags can reset on reload. The LOCAL collection
# carries the persistent render exclusion instead.
bpy.data.collections['00_HIGHDETAIL_TARGET__READ_ONLY'].hide_render = True
camera_data = bpy.data.cameras.new('ORBITAL_REVIEW')
camera = bpy.data.objects.new('ORBITAL_REVIEW', camera_data)
scene.collection.objects.link(camera)
camera.location = (2, .035, .268)
camera.rotation_euler = (Vector((0,.035,.268))-camera.location).to_track_quat('-Z','Y').to_euler()
camera_data.type = 'ORTHO'
camera_data.ortho_scale = .10
scene.camera = camera
scene.render.resolution_x = scene.render.resolution_y = 1024
scene.render.resolution_percentage = 100
scene.render.engine = 'BLENDER_WORKBENCH'
shade = scene.display.shading
shade.light = 'FLAT'
shade.color_type = 'TEXTURE'
shade.show_shadows = False
shade.show_cavity = False
shade.show_specular_highlight = False
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.view_settings.exposure = 0
scene.view_settings.gamma = 1
scene.render.filepath = str(OUT/'original_color_projection.png')
bpy.ops.render.render(write_still=True)

# Projected source colors, explicitly local: not a final PBR texture bake.
image = bpy.data.images.load(str(OUT/'original_color_projection.png'))
image.pack()
material = bpy.data.materials.new('ORBITAL_SOURCE_COLOR_PROJECTION')
material.use_nodes = True
texture = material.node_tree.nodes.new('ShaderNodeTexImage')
texture.image = image
material.node_tree.links.new(texture.outputs['Color'], material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
material.node_tree.nodes.active = texture

candidate = source.copy()
candidate.data = source.data.copy()
candidate.name = 'ICH_CHIBI_ORBITAL_INTEGRATION_EXPERIMENT_v01'
scene.collection.objects.link(candidate)
candidate.hide_select = False
candidate.hide_render = False
candidate.hide_set(False)
source.hide_render = True
source.hide_set(True)
bm = bmesh.new()
bm.from_mesh(candidate.data)
uv_layer = bm.loops.layers.uv.active
outer = [Vector((v.y,v.z)) for v in positions[96:120]]
center = sum(outer, Vector((0,0)))/24
cut_polygon = [center + (v-center)*1.12 for v in outer]

def inside(y,z):
    hit = False
    for i,a in enumerate(cut_polygon):
        b = cut_polygon[(i+1)%24]
        if (a.y>z) != (b.y>z) and y < (b.x-a.x)*(z-a.y)/(b.y-a.y)+a.x:
            hit = not hit
    return hit

removed = []
for face in bm.faces:
    p = face.calc_center_median()
    if p.x > 0 and inside(p.y,p.z):
        removed.append(face)
bmesh.ops.delete(bm, geom=removed, context='FACES')
def area(points):
    return sum(a.y*points[(i+1)%len(points)].z-points[(i+1)%len(points)].y*a.z for i,a in enumerate(points))

def trace_boundary():
    boundary = [e for e in bm.edges if e.is_boundary]
    vertices = {v for e in boundary for v in e.verts}
    assert all(sum(e.is_boundary for e in v.link_edges)==2 for v in vertices), 'Cut boundary branches'
    start = min(vertices, key=lambda v: (v.co.y-positions[96].y)**2+(v.co.z-positions[96].z)**2)
    ordered = [start]
    previous = None
    current = start
    while True:
        neighbors = [e.other_vert(current) for e in current.link_edges if e.is_boundary and e.other_vert(current)!=previous]
        nxt = neighbors[0]
        if nxt == start:
            break
        assert nxt not in ordered, 'Repeated boundary vertex'
        ordered.append(nxt)
        previous,current = current,nxt
    assert len(ordered)==len(vertices), 'More than one cut boundary; integration rejected'
    if area([v.co for v in ordered])*area(positions[96:120])<0:
        ordered = [ordered[0]]+list(reversed(ordered[1:]))
    return ordered

cleanup_removed = 0
for cleanup_step in range(16 if args.expand_boundary else 0):
    ordered = trace_boundary()
    winding = 1 if area([v.co for v in ordered])>0 else -1
    bad_faces = set()
    for i,a in enumerate(ordered):
        b = ordered[(i+1)%len(ordered)]
        cross = (b.co.y-a.co.y)*(center.y-a.co.z)-(b.co.z-a.co.z)*(center.x-a.co.y)
        if cross*winding <= 1e-12:
            edge = bm.edges.get((a,b))
            bad_faces.update(edge.link_faces)
    if not bad_faces:
        break
    cleanup_removed += len(bad_faces)
    assert cleanup_removed<1200, 'Transition expansion exceeded its local budget'
    bmesh.ops.delete(bm,geom=list(bad_faces),context='FACES')
ordered = trace_boundary()
new_vertices = [bm.verts.new(p) for p in positions]
material_index = len(candidate.data.materials)
candidate.data.materials.append(material)
created = []

def add_face(verts):
    f = bm.faces.new(verts)
    f.material_index = material_index
    for loop in f.loops:
        p = loop.vert.co
        loop[uv_layer].uv = ((p.y-.035)/.1+.5, (p.z-.268)/.1+.5)
    created.append(f)

for face in faces:
    add_face([new_vertices[i] for i in face])

# A dense fixed transition is deliberately confined outside the deforming rings.
low = new_vertices[96:120]
high = ordered
orientation = -1 if area([v.co for v in low])>0 else 1
def bridge_cost(triangle):
    a,b,c = [v.co for v in triangle]
    signed = ((b.y-a.y)*(c.z-a.z)-(b.z-a.z)*(c.y-a.y))*orientation
    if signed <= 1e-12:
        return float('inf')
    return ((a-b).length_squared+(b-c).length_squared+(c-a).length_squared)/signed

# Dynamic programming rejects inverted projected triangles instead of assuming
# equal arc lengths on the two contours imply a valid correspondence.
cost = {(0,0):0.0}
previous = {}
for i in range(25):
    for j in range(len(high)+1):
        current_cost = cost.get((i,j),float('inf'))
        if current_cost==float('inf'):
            continue
        steps = []
        if i<24:
            steps.append(((i+1,j),[low[i%24],low[(i+1)%24],high[j%len(high)]]))
        if j<len(high):
            steps.append(((i,j+1),[low[i%24],high[(j+1)%len(high)],high[j%len(high)]]))
        for dest,triangle in steps:
            new_cost = current_cost+bridge_cost(triangle)
            if new_cost<cost.get(dest,float('inf')):
                cost[dest] = new_cost
                previous[dest] = ((i,j),triangle)
cursor = (24,len(high))
(OUT/'transition_diagnostic.json').write_text(json.dumps({'low':[list(v.co) for v in low],'high':[list(v.co) for v in high], 'orientation':orientation,'reachable_states':len(previous)},indent=2),encoding='utf-8',newline='\n')
if cursor not in previous:
    rejection = {'status':'REJECTED_NO_ASSET_EXPORTED',
                 'reason':'No non-inverted projected transition exists for the selected cut and start correspondence',
                 'source_sha256':source_hash,'removed_faces':len(removed),
                 'boundary_vertices':len(high),'reachable_dynamic_program_states':len(previous),
                 'source_unchanged':hashlib.sha256(source_path.read_bytes()).hexdigest()==source_hash,
                 'next_action':'Retopologize a continuous orbital region; do not weld the current outer ring blindly into the dense source.'}
    (OUT/'integration_audit.json').write_text(json.dumps(rejection,indent=2)+'\n',encoding='utf-8',newline='\n')
    raise RuntimeError(rejection['reason'])
while cursor!=(0,0):
    cursor,triangle = previous[cursor]
    add_face(triangle)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.verts.index_update()
pilot_indices = [v.index for v in new_vertices]
boundary_after = [e for e in bm.edges if e.is_boundary]
report = {
    'status':'experimental dense-head integration; not game-ready or printable',
    'source_sha256':source_hash,
    'removed_faces':len(removed), 'cut_boundary_vertices':len(high),
    'additional_boundary_cleanup_faces':cleanup_removed,
    'transition_triangles':len(high)+24, 'pilot_vertices':120,
    'intentional_aperture_boundary_edges':len(boundary_after),
    'unexpected_boundary_edges':sum(any(v not in new_vertices[:24] for v in e.verts) for e in boundary_after),
    'overfull_edges':sum(len(e.link_faces)>2 for e in bm.edges),
    'wire_edges':sum(e.is_wire for e in bm.edges),
    'orientation_conflicts':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),
    'minimum_new_triangle_area':min(f.calc_area() for f in created),
    'new_projected_negative_triangles':sum(f.normal.x<=0 for f in created),
    'limitations':['One eye only, R denotes screen-right.', 'Intentional open eyelid aperture; no oral cavity or complete ocular globe.', 'Dense body is a reference, not final deforming game topology.', 'Local projected color has no new PBR claim; review neutral appearance.', 'No exhaustive self-intersection or game-engine validation.']
}
assert report['intentional_aperture_boundary_edges']==24
assert report['unexpected_boundary_edges']==report['overfull_edges']==report['wire_edges']==report['orientation_conflicts']==0
assert report['minimum_new_triangle_area']>1e-12
assert report['new_projected_negative_triangles']==0
bm.to_mesh(candidate.data)
bm.free()
candidate.data.update()
basis = candidate.shape_key_add(name='Basis')
key = candidate.shape_key_add(name='Blink_screen_right')
for i,index in enumerate(pilot_indices):
    key.data[index].co = closed[i]
group = candidate.vertex_groups.new(name='ORBITAL_PILOT_120')
group.add(pilot_indices,1.0,'REPLACE')
candidate['validation_report'] = json.dumps(report)
cap_mesh = bpy.data.meshes.new('OCULAR_SUPPORT_DIAGNOSTIC')
cap_mesh.from_pydata(cap_positions,[],cap_faces)
cap_obj = bpy.data.objects.new('OCULAR_SUPPORT_NOT_COMPLETE_GLOBE',cap_mesh)
scene.collection.objects.link(cap_obj)
cap_mesh.materials.append(material)
uv = cap_mesh.uv_layers.new(name='LocalProjection')
for loop in cap_mesh.loops:
    p = cap_mesh.vertices[loop.vertex_index].co
    uv.data[loop.index].uv = ((p.y-.035)/.1+.5,(p.z-.268)/.1+.5)
for label,value in [('integrated_open',0),('integrated_half',.5),('integrated_closed',1)]:
    key.value = value
    scene.render.filepath = str(OUT/(label+'.png'))
    bpy.ops.render.render(write_still=True)
key.value = 0
bpy.context.view_layer.objects.active = candidate
for obj in bpy.context.view_layer.objects:
    obj.select_set(obj==candidate)
scene.camera = bpy.data.objects.get('REVIEW_FACE_FRONT',camera)
scene.render.filepath = str(OUT/'integrated_face.png')
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Ichiro_Orbital_Integration_v01.blend'),compress=True)
assert hashlib.sha256(source_path.read_bytes()).hexdigest()==source_hash
(OUT/'integration_audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print('INTEGRATION_AUDIT',json.dumps(report))
