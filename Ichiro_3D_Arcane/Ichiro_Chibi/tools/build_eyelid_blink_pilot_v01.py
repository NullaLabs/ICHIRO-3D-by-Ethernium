"""Rebuild and export a source-aligned screen-right eyelid deformation pilot.
The output is isolated, not integrated into the character or print-ready.
Run Blender --background --factory-startup --python THIS_FILE -- --out NEW_DIR.
"""
from pathlib import Path
import argparse
import hashlib
import sys
import bpy
import math
import json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
OUT=args.out.resolve()
OUT.mkdir(parents=True,exist_ok=True)
OUTPUT_PREFIX=OUT.as_posix()+'/'
output_blend=OUT/'Ichiro_Eye_R_Blink_Pilot.blend'
if output_blend.exists():
    raise RuntimeError('Choose a fresh output directory.')
input_blend=ROOT/'exports'/'rig_connectivity_v01'/'Ichiro_Chibi_Rig_Connectivity_v01.blend'
bpy.ops.wm.open_mainfile(filepath=str(input_blend))
bpy.data.collections['00_HIGHDETAIL_TARGET__READ_ONLY'].hide_render=True
scene=bpy.context.scene
for name,loc in [('FRONT',(2,.035,.268)),('OBLIQUE',(2,1.035,.268))]:
    data=bpy.data.cameras.new('EYE_REVIEW_'+name)
    camera=bpy.data.objects.new('EYE_REVIEW_'+name,data)
    scene.collection.objects.link(camera)
    camera.location=loc
    camera.rotation_euler=(Vector((0,.035,.268))-camera.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO'; data.ortho_scale=.10
scene.camera=bpy.data.objects['EYE_REVIEW_FRONT']
scene.render.resolution_x=scene.render.resolution_y=1024
scene.display.shading.color_type='TEXTURE'
scene.render.filepath=str(OUT/'source_eye_texture.png')
bpy.ops.render.render(write_still=True)
scene.display.shading.color_type='SINGLE'
scene.render.filepath=str(OUT/'source_eye_clay.png')
bpy.ops.render.render(write_still=True)
source=bpy.data.objects['ICH_CHIBI_CONNECTIVITY_CANDIDATE_v01']
tree=BVHTree.FromObject(source,bpy.context.evaluated_depsgraph_get())
xs=[235,270,320,370,420,470,520,570,620,670,720,760,790]
top=[590,528,476,446,430,413,400,388,374,361,349,340,333]
bottom=[590,588,585,581,579,576,570,560,549,530,487,425,333]
controls=[Vector((xs[i],top[i])) for i in range(13)]+[Vector((xs[i],bottom[i])) for i in range(11,0,-1)]
positions=[]
for distance in [0,12,30,60,100]:
    for i,p in enumerate(controls):
        a=(p-controls[(i-1)%24]).normalized()
        b=(controls[(i+1)%24]-p).normalized()
        outward=(Vector((a.y,-a.x))+Vector((b.y,-b.x))).normalized()
        uv=p+outward*distance
        y=.035+(uv.x/1024-.5)*.1
        z=.268+(.5-uv.y/1024)*.1
        hit,n,f,d=tree.ray_cast(Vector((1,y,z)),Vector((-1,0,0)),2)
        if hit is None:
            raise RuntimeError('A lid ring missed the source.')
        positions.append(tuple(hit+Vector((.0003,0,0))))
faces=[]
for ring in range(4):
    for i in range(24):
        j=(i+1)%24
        faces.append((ring*24+i,ring*24+j,(ring+1)*24+j,(ring+1)*24+i))
mesh=bpy.data.meshes.new('EYE_R_LID_QUADS')
mesh.from_pydata(positions,[],faces); mesh.update()
obj=bpy.data.objects.new('EYE_R_LID_DEFORMATION_PILOT_v01',mesh)
scene.collection.objects.link(obj)
mat=bpy.data.materials.new('EYELID_REVIEW_SKIN')
mat.diffuse_color=(.38,.19,.105,1)
mesh.materials.append(mat)
obj.show_wire=True; obj.show_all_edges=True
basis=obj.shape_key_add(name='Basis',from_mix=False)
blink=obj.shape_key_add(name='Blink_R',from_mix=False)
obj['status']='Isolated editable quad pilot; NOT integrated with source'
obj['side_convention']='R means screen-right from +X camera, not anatomical bone naming'
obj['ring_construction']='Outward edge-normal offsets [0,12,30,60,100] px'
import bpy
import math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
obj=bpy.data.objects['EYE_R_LID_DEFORMATION_PILOT_v01']
basis=obj.data.shape_keys.key_blocks[0]
key=obj.data.shape_keys.key_blocks['Blink_R']
tree=BVHTree.FromObject(bpy.data.objects['ICH_CHIBI_CONNECTIVITY_CANDIDATE_v01'],bpy.context.evaluated_depsgraph_get())
xs=[235,270,320,370,420,470,520,570,620,670,720,760,790]
targets={0:basis.data[0].co.copy(),12:basis.data[12].co.copy()}
for i in range(1,12):
    t=(xs[i]-235)/555
    v=590+(333-590)*t+50*math.sin(math.pi*t)
    y=.035+(xs[i]/1024-.5)*.1
    z=.268+(.5-v/1024)*.1
    hit,n,f,d=tree.ray_cast(Vector((1,y,z)),Vector((-1,0,0)),2)
    target=Vector((hit.x+.00065,y,z))
    targets[i]=target
    targets[24-i]=target
for ring,t in enumerate([0,.12,.32,.65,1]):
    for i in range(24):
        idx=ring*24+i
        key.data[idx].co=targets[i].lerp(basis.data[96+i].co,t)
obj['blink_pairing']='Shared smooth closure curve; ruled interpolation to fixed outer ring. Canthi inner positions pinned.'

key.value=0

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
source=bpy.data.objects['ICH_CHIBI_CONNECTIVITY_CANDIDATE_v01']
tree=BVHTree.FromObject(source,bpy.context.evaluated_depsgraph_get())
xs=[235,270,320,370,420,470,520,570,620,670,720,760,790]
top=[590,528,476,446,430,413,400,388,374,361,349,340,333]
bottom=[590,588,585,581,579,576,570,560,549,530,487,425,333]
verts=[]; columns=[]
for col,u in enumerate(xs):
    indices=[]
    rows=[0] if col in [0,12] else range(7)
    for row in rows:
        v=top[col]+(bottom[col]-top[col])*row/6
        y=.035+(u/1024-.5)*.1
        z=.268+(.5-v/1024)*.1
        hit,n,f,d=tree.ray_cast(Vector((1,y,z)),Vector((-1,0,0)),2)
        indices.append(len(verts)); verts.append(tuple(hit+Vector((-.0012,0,0))))
    columns.append(indices)
faces=[]
for col in range(12):
    a=columns[col]; b=columns[col+1]
    for row in range(6):
        if len(a)==1: faces.append((a[0],b[row],b[row+1]))
        elif len(b)==1: faces.append((a[row],b[0],a[row+1]))
        else: faces.append((a[row],b[row],b[row+1],a[row+1]))
mesh=bpy.data.meshes.new('EYE_R_SUPPORT_CAP_MESH'); mesh.from_pydata(verts,[],faces); mesh.update()
cap=bpy.data.objects.new('EYE_R_SURFACE_SUPPORT__NOT_FULL_GLOBE',mesh)
bpy.context.scene.collection.objects.link(cap)
white=bpy.data.materials.new('EYE_SUPPORT_IVORY'); white.diffuse_color=(.8,.83,.76,1); white.use_nodes=True
shader=next(n for n in white.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
shader.inputs['Base Color'].default_value=(.8,.83,.76,1)
mesh.materials.append(white)
cap['status']='Diagnostic ocular cap sampled from source; not a complete globe or production iris'
lid=bpy.data.objects['EYE_R_LID_DEFORMATION_PILOT_v01']
skin=lid.data.materials[0]; skin.diffuse_color=(.55,.35,.22,1); skin.use_nodes=True
shader=next(n for n in skin.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
shader.inputs['Base Color'].default_value=(.55,.35,.22,1)
dark=bpy.data.materials.new('TOPOLOGY_WIRE_DARK'); dark.diffuse_color=(.015,.025,.035,1)
lid.data.materials.append(dark)
wire=lid.copy(); wire.name='EYE_R_TOPOLOGY_WIRE__DISPLAY_ONLY'
bpy.context.scene.collection.objects.link(wire)
mod=wire.modifiers.new('Topology wire','WIREFRAME'); mod.thickness=.000055; mod.offset=1.0; mod.use_replace=True; mod.material_offset=1

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
obj=bpy.data.objects['EYE_R_LID_DEFORMATION_PILOT_v01']
key=obj.data.shape_keys.key_blocks['Blink_R']
tree=BVHTree.FromObject(bpy.data.objects['ICH_CHIBI_CONNECTIVITY_CANDIDATE_v01'],bpy.context.evaluated_depsgraph_get())
for i in range(96):
    co=key.data[i].co
    if i in [0,12]: continue
    hit,n,f,d=tree.ray_cast(Vector((1,co.y,co.z)),Vector((-1,0,0)),2)
    co.x=hit.x+.0009
key.value=0
print('Closed surface projected along +X; outer ring fixed')

import bpy
import json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
lid=bpy.data.objects['EYE_R_LID_DEFORMATION_PILOT_v01']
cap=bpy.data.objects['EYE_R_SURFACE_SUPPORT__NOT_FULL_GLOBE']
key=lid.data.shape_keys.key_blocks['Blink_R']
points=[v.co.copy() for v in cap.data.vertices]
for face in cap.data.polygons:
    center=sum((cap.data.vertices[i].co for i in face.vertices),Vector())/len(face.vertices)
    points.append(center)
clearance=.00025
history=[]
for iteration in range(6):
    changes={}
    max_penetration=0
    failures=0
    for value in [.25,.5,.75,1]:
        key.value=value; bpy.context.view_layer.update()
        tree=BVHTree.FromObject(lid,bpy.context.evaluated_depsgraph_get())
        for p in points:
            hit,normal,face,distance=tree.ray_cast(Vector((1,p.y,p.z)),Vector((-1,0,0)),2)
            if hit is None: continue
            penetration=p.x+clearance-hit.x
            if penetration>1e-7:
                failures+=1; max_penetration=max(max_penetration,penetration)
                ids=[i for i in lid.data.polygons[face].vertices if i<96 and i not in [0,12]]
                for i in ids:
                    changes[i]=max(changes.get(i,0),penetration/value*1.15)
    history.append({'iteration':iteration,'samples_needing_clearance':failures,'max_clearance_deficit':max_penetration})
    if not changes: break
    for i in range(1,12):
        amount=max(changes.get(i,0),changes.get(24-i,0))
        if amount:
            changes[i]=amount; changes[24-i]=amount
    for i,dx in changes.items(): key.data[i].co.x+=dx
key.value=0
lid['support_clearance_history']=json.dumps(history)
print(json.dumps(history))

import bpy
lid=bpy.data.objects['EYE_R_LID_DEFORMATION_PILOT_v01']
faces=[]
for p in lid.data.polygons:
    a,b,c,d=p.vertices
    faces.extend([(a,b,c),(a,c,d)])
mesh=bpy.data.meshes.new('EYE_R_GAME_FIXED_TRIANGLES')
mesh.from_pydata([tuple(v.co) for v in lid.data.vertices],[],faces); mesh.update()
game=bpy.data.objects.new('EYE_R_GAME_BLINK_PILOT',mesh)
bpy.context.scene.collection.objects.link(game)
mesh.materials.append(lid.data.materials[0])
for p in mesh.polygons: p.use_smooth=True
basis=game.shape_key_add(name='Basis',from_mix=False)
key=game.shape_key_add(name='Blink_R',from_mix=False)
for i,p in enumerate(lid.data.shape_keys.key_blocks['Blink_R'].data): key.data[i].co=p.co
game['status']='Game export pilot; fixed triangulation of editable quad source; not integrated'
lid.hide_render=True
key.value=0

key.value=0

source.hide_render=True; source.hide_set(True)
scene.display.shading.color_type='MATERIAL'
scene.render.film_transparent=False
scene.render.resolution_x=scene.render.resolution_y=768

import bpy
import json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
lid=bpy.data.objects['EYE_R_GAME_BLINK_PILOT']
cap=bpy.data.objects['EYE_R_SURFACE_SUPPORT__NOT_FULL_GLOBE']
key=lid.data.shape_keys.key_blocks['Blink_R']
basis=lid.data.shape_keys.key_blocks[0]
for ob in [lid,cap]:
    for p in ob.data.polygons: p.use_smooth=True
points=[v.co.copy() for v in cap.data.vertices]
for f in cap.data.polygons:
    coords=[cap.data.vertices[i].co for i in f.vertices]
    points.append(sum(coords,Vector())/len(coords))
    for i,p in enumerate(coords): points.append((p+coords[(i+1)%len(coords)])/2)
poses=[]
for step in range(21):
    value=step/20
    key.value=value; bpy.context.view_layer.update()
    deps=bpy.context.evaluated_depsgraph_get()
    ev=lid.evaluated_get(deps); mesh=ev.to_mesh(); mesh.calc_loop_triangles()
    triangles_negative_x=0
    for tri in mesh.loop_triangles:
        a,b,c=[mesh.vertices[i].co for i in tri.vertices]
        if (b-a).cross(c-a).x<=0: triangles_negative_x+=1
    tree=BVHTree.FromObject(lid,deps)
    penetrations=0; max_penetration=0
    for p in points:
        hit,n,f,d=tree.ray_cast(Vector((1,p.y,p.z)),Vector((-1,0,0)),2)
        if hit is not None and p.x>hit.x+1e-6:
            penetrations+=1; max_penetration=max(max_penetration,p.x-hit.x)
    poses.append({'blink':value,'minimum_face_area':min(p.area for p in mesh.polygons),'inverted_projected_triangles':triangles_negative_x,'sampled_cap_penetrations':penetrations,'max_sampled_penetration':max_penetration,'maximum_lid_pair_gap':max((mesh.vertices[i].co-mesh.vertices[24-i].co).length for i in range(1,12))})
    ev.to_mesh_clear()
key.value=0
report={'lid_vertices':len(lid.data.vertices),'game_triangles':len(lid.data.polygons),'editable_quads':96,'outer_ring_max_displacement':max((key.data[i].co-basis.data[i].co).length for i in range(96,120)),'canthi_max_displacement':max((key.data[i].co-basis.data[i].co).length for i in [0,12]),'cap_samples_per_pose':len(points),'poses':poses,'status':'isolated pilot; not integrated; no production eye globe, iris or textures','self_intersections':'not exhaustively tested'}
lid['deformation_audit']=json.dumps(report)
print(json.dumps(report))
scene=bpy.context.scene
for value,label in [(0,'open'),(.5,'half'),(1,'closed')]:
    key.value=value
    bpy.data.objects['EYE_R_LID_DEFORMATION_PILOT_v01'].data.shape_keys.key_blocks['Blink_R'].value=value
    scene.render.filepath=OUTPUT_PREFIX + 'final_'+label+'.png'
    bpy.ops.render.render(write_still=True)
key.value=0
bpy.data.objects['EYE_R_LID_DEFORMATION_PILOT_v01'].data.shape_keys.key_blocks['Blink_R'].value=0
for o in bpy.context.selected_objects: o.select_set(False)
lid.select_set(True); cap.select_set(True)
bpy.context.view_layer.objects.active=lid
bpy.ops.export_scene.gltf(filepath=OUTPUT_PREFIX + 'Ichiro_Eye_R_Blink_Pilot.glb',export_format='GLB',use_selection=True,export_morph=True,export_animations=False,export_extras=True)



audit=json.loads(bpy.data.objects['EYE_R_GAME_BLINK_PILOT']['deformation_audit'])
assert all(p['inverted_projected_triangles']==0 for p in audit['poses'])
assert all(p['sampled_cap_penetrations']==0 for p in audit['poses'])
assert audit['poses'][-1]['maximum_lid_pair_gap']<1e-7
assert audit['outer_ring_max_displacement']==0 and audit['canthi_max_displacement']==0
with input_blend.open('rb') as stream:
    audit['input_scene_sha256']=hashlib.file_digest(stream,'sha256').hexdigest()
audit['side_convention']='R means screen-right from +X camera; anatomical rig names not assigned.'
(OUT/'deformation_audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8',newline='\n')
(OUT/'source_eye_trace.json').write_text(json.dumps({'camera':{'target':[0,.035,.268],'ortho_scale':.1,'resolution':1024},'x_pixels':xs,'upper_pixels':top,'lower_pixels':bottom,'ring_offsets_pixels':[0,12,30,60,100],'trace':'manual current-source aperture; not an automatically verified eyelid edge'},indent=2)+'\n',encoding='utf-8',newline='\n')
# Keep the shipped Blender artifact small and self-contained.
# Only this background copy is cleaned; the source file is never saved.
keep={'EYE_R_LID_DEFORMATION_PILOT_v01','EYE_R_GAME_BLINK_PILOT','EYE_R_SURFACE_SUPPORT__NOT_FULL_GLOBE','EYE_R_TOPOLOGY_WIRE__DISPLAY_ONLY','EYE_REVIEW_FRONT','EYE_REVIEW_OBLIQUE'}
for ob in list(bpy.data.objects):
    if ob.name not in keep:
        bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
scene.camera=bpy.data.objects['EYE_REVIEW_FRONT']
bpy.data.objects['EYE_R_LID_DEFORMATION_PILOT_v01'].hide_set(True)
bpy.data.objects['EYE_R_TOPOLOGY_WIRE__DISPLAY_ONLY'].hide_set(True)
bpy.data.objects['EYE_R_TOPOLOGY_WIRE__DISPLAY_ONLY'].hide_render=True
game=bpy.data.objects['EYE_R_GAME_BLINK_PILOT']
for ob in bpy.context.selected_objects: ob.select_set(False)
game.select_set(True)
bpy.context.view_layer.objects.active=game
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(output_blend),compress=True)
print('EYELID PILOT COMPLETE',output_blend)
