"""Repair source connectivity without redesigning Ichiro.
Blender --background --factory-startup --python THIS_FILE -- --out NEW_DIRECTORY
Small-patch thresholds intentionally stop the pipeline on unfamiliar defects.
"""
from pathlib import Path
import argparse
import hashlib
import sys
import bpy
ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
OUT = args.out.resolve()
OUT.mkdir(parents=True, exist_ok=True)
OUTPUT_PREFIX = OUT.as_posix() + '/'
result_path = OUT / 'Ichiro_Chibi_Rig_Connectivity_v01.blend'
if result_path.exists():
    raise RuntimeError('Choose a fresh output directory.')
source_path = ROOT / 'Ichiro_Chibi_HEAD_HANDS_Topology_Workspace.blend'
bpy.ops.wm.open_mainfile(filepath=str(source_path))
import bpy
import bmesh
import json
source=bpy.data.objects['ICH_CHIBI_HIGHDETAIL_SOURCE__READONLY']
assert bpy.data.objects.get('ICH_CHIBI_CONNECTIVITY_CANDIDATE_v01') is None
candidate=source.copy()
candidate.data=source.data.copy()
candidate.name='ICH_CHIBI_CONNECTIVITY_CANDIDATE_v01'
bpy.context.scene.collection.objects.link(candidate)
candidate.hide_select=False
candidate.hide_render=False
candidate.hide_set(False)
for obj in bpy.context.scene.objects:
    if obj.type=='MESH' and obj!=candidate:
        obj.hide_render=True
        obj.hide_set(True)
bm=bmesh.new()
bm.from_mesh(candidate.data)
def audit(mesh):
    boundary=sum(1 for e in mesh.edges if e.is_boundary)
    wire=sum(1 for e in mesh.edges if e.is_wire)
    overfull=sum(1 for e in mesh.edges if len(e.link_faces)>2)
    noncontiguous=sum(1 for e in mesh.edges if e.is_manifold and not e.is_contiguous)
    loose=sum(1 for v in mesh.verts if not v.link_edges)
    return dict(vertices=len(mesh.verts),edges=len(mesh.edges),faces=len(mesh.faces),boundary_edges=boundary,wire_edges=wire,overfull_edges=overfull,orientation_conflicts=noncontiguous,loose_vertices=loose)
before=audit(bm)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.000001)
after=audit(bm)
bm.to_mesh(candidate.data)
bm.free()
candidate.data.update()
report={'operation':'merge by distance','tolerance':0.000001,'before':before,'after':after,'status':'connectivity candidate only; not retopologized or rig ready'}
candidate['connectivity_report']=json.dumps(report)
print(json.dumps(report))

import bpy
import bmesh
import json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
def edge_index(edge):
    return edge.index
obj=bpy.data.objects['ICH_CHIBI_CONNECTIVITY_CANDIDATE_v01']
source=bpy.data.objects['ICH_CHIBI_HIGHDETAIL_SOURCE__READONLY']
bm=bmesh.new(); bm.from_mesh(obj.data)
bad_edges=[e for e in bm.edges if not e.is_manifold]
bad_verts={v for e in bad_edges for v in e.verts}
removed={f for v in bad_verts for f in v.link_faces}
removed_count=len(removed)
bmesh.ops.delete(bm,geom=list(removed),context='FACES')
boundary={e for e in bm.edges if e.is_boundary}
unseen=set(boundary); patches=[]; patch_groups=[]
while unseen:
    first=unseen.pop(); group={first}; stack=[first]
    while stack:
        edge=stack.pop()
        for v in edge.verts:
            for e in v.link_edges:
                if e in unseen:
                    unseen.remove(e); group.add(e); stack.append(e)
    verts={v for e in group for v in e.verts}
    extent=max(max(v.co[a] for v in verts)-min(v.co[a] for v in verts) for a in range(3))
    assert extent<0.008, 'Patch too large; requires manual review'
    assert all(sum(1 for e in v.link_edges if e in group)==2 for v in verts), 'Branched patch'
    patches.append({'edges':len(group),'max_extent':extent})
    patch_groups.append(group)
filled=[]
for group in patch_groups:
    first=min(group,key=edge_index)
    start=first.verts[0]
    current=first.verts[1]
    ordered=[start,current]
    previous=first
    while True:
        next_edge=next(e for e in current.link_edges if e in group and e!=previous)
        nxt=next_edge.other_vert(current)
        if nxt==start: break
        ordered.append(nxt)
        previous=next_edge
        current=nxt
        assert len(ordered)<=len(group), 'Invalid loop traversal'
    filled.append(bm.faces.new(ordered))
triangles=bmesh.ops.triangulate(bm,faces=filled)['faces']
tree=BVHTree.FromObject(source,bpy.context.evaluated_depsgraph_get())
source_uv=source.data.uv_layers.active
uv=bm.loops.layers.uv.active
max_projection_distance=0.0
for f in triangles:
    center=f.calc_center_median()
    nearest,normal,index,distance=tree.find_nearest(center)
    max_projection_distance=max(max_projection_distance,distance)
    # One source triangle per patch triangle avoids interpolating across atlas islands.
    original=source.data.polygons[index]
    vs=[source.data.vertices[i].co for i in original.vertices]
    uvs=[Vector((source_uv.data[i].uv.x,source_uv.data[i].uv.y,0)) for i in original.loop_indices]
    for loop in f.loops:
        mapped=barycentric_transform(loop.vert.co,vs[0],vs[1],vs[2],uvs[0],uvs[1],uvs[2])
        loop[uv].uv=(mapped.x,mapped.y)
    f.smooth=original.use_smooth
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
remaining_edges=sum(1 for e in bm.edges if not e.is_manifold)
remaining_vertices=sum(1 for v in bm.verts if not v.is_manifold)
degenerate=sum(1 for f in bm.faces if f.calc_area()<1e-12)
assert remaining_edges==0 and remaining_vertices==0, 'Repair incomplete; keep previous mesh'
report={'removed_faces':removed_count,'patches':len(patches),'max_patch_extent':max(p['max_extent'] for p in patches),'new_triangles':len(triangles),'max_patch_centroid_distance_to_source':max_projection_distance,'vertices':len(bm.verts),'edges':len(bm.edges),'faces':len(bm.faces),'nonmanifold_edges':remaining_edges,'nonmanifold_vertices':remaining_vertices,'tiny_faces':degenerate,'signed_volume':bm.calc_volume(signed=True),'self_intersections':'not tested','uv_policy':'source triangle at patch centroid; local extrapolation; inspect texture'}
bm.to_mesh(obj.data); bm.free(); obj.data.update()
obj['local_patch_report']=json.dumps(report)
obj['production_status']='Closed manifold high-poly projection source; NOT game topology or bound rig'
print(json.dumps(report))



import math
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.single_color=(0.65,0.65,0.65)
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.background_type='WORLD'
if scene.world is None:
    scene.world=bpy.data.worlds.new('REVIEW_WORLD')
scene.world.color=(0.07,0.07,0.07)
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
for angle in range(0,360,45):
    name='REVIEW_FULL_%03d'%angle
    data=bpy.data.cameras.new(name)
    cam=bpy.data.objects.new(name,data)
    scene.collection.objects.link(cam)
    radians=math.radians(angle)
    cam.location=(3*math.cos(radians),3*math.sin(radians),0)
    cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO'
    data.ortho_scale=1.12
data=bpy.data.cameras.new('REVIEW_FACE_FRONT')
cam=bpy.data.objects.new('REVIEW_FACE_FRONT',data)
scene.collection.objects.link(cam)
cam.location=(2,0,.285)
cam.rotation_euler=(Vector((0,0,.285))-cam.location).to_track_quat('-Z','Y').to_euler()
data.type='ORTHO'
data.ortho_scale=.36

import bpy
scene=bpy.context.scene
source=bpy.data.objects['ICH_CHIBI_HIGHDETAIL_SOURCE__READONLY']
candidate=bpy.data.objects['ICH_CHIBI_CONNECTIVITY_CANDIDATE_v01']
scene.display.shading.color_type='TEXTURE'
scene.render.film_transparent=True
scene.render.image_settings.color_mode='RGBA'
scene.render.resolution_x=512
scene.render.resolution_y=512
for label,visible,hidden in [('source',source,candidate),('repaired',candidate,source)]:
    visible.hide_render=False; visible.hide_set(False)
    hidden.hide_render=True; hidden.hide_set(True)
    for angle in range(0,360,45):
        scene.camera=bpy.data.objects['REVIEW_FULL_%03d'%angle]
        scene.render.filepath=OUTPUT_PREFIX + ''+label+'_%03d.png'%angle
        bpy.ops.render.render(write_still=True)
    scene.camera=bpy.data.objects['REVIEW_FACE_FRONT']
    scene.render.resolution_x=768
    scene.render.resolution_y=768
    scene.render.filepath=OUTPUT_PREFIX + ''+label+'_face.png'
    bpy.ops.render.render(write_still=True)
    scene.render.resolution_x=512
    scene.render.resolution_y=512
print('WELD_REPORT',candidate['connectivity_report'])
print('PATCH_REPORT',candidate['local_patch_report'])
scene.camera=bpy.data.objects['REVIEW_FULL_045']



candidate['user_direction']='Original appearance preserved. Game deformation topology is next; print derivative separate.'
bpy.ops.wm.save_as_mainfile(filepath=str(result_path),compress=True)
def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()
audit={
    'weld':json.loads(candidate['connectivity_report']),
    'repair':json.loads(candidate['local_patch_report']),
    'source_workspace_sha256':sha(source_path),
    'source_geometry_sha256':sha(ROOT / 'Ichiro_Chibi_HighDetail_Working.blend'),
    'blender':bpy.app.version_string,
    'self_intersections':'not tested',
    'rig_ready':False,
}
(OUT/'geometry_audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8',newline='\n')
print('CONNECTIVITY REVIEW COMPLETE',result_path)
