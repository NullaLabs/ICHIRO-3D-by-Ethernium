"""Persist reference exclusion on a local collection; verify after reopening.

Does not modify geometry, UVs or the input file. No retopology claim.
Blender --background --factory-startup --python-exit-code 1 --python THIS -- --out NEW_DIR
"""
from pathlib import Path
from array import array
import argparse
import hashlib
import json
import sys
import bpy

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
OUT=args.out.resolve()
OUT.mkdir(parents=True,exist_ok=True)
target=OUT/'Ichiro_Chibi_Original_View.blend'
assert not target.exists(), 'Choose a fresh output directory'
source=ROOT/'exports/rig_connectivity_v01/Ichiro_Chibi_Rig_Connectivity_v01.blend'
source_sha=hashlib.sha256(source.read_bytes()).hexdigest()

def mesh_digest(mesh):
    digest=hashlib.sha256()
    for collection,field,length,code in [
        (mesh.vertices,'co',3,'f'), (mesh.edges,'vertices',2,'i'),
        (mesh.loops,'vertex_index',1,'i'),(mesh.polygons,'loop_start',1,'i'),
        (mesh.polygons,'loop_total',1,'i'),(mesh.polygons,'material_index',1,'i')]:
        values=array(code,[0])*(len(collection)*length)
        collection.foreach_get(field,values)
        digest.update(values.tobytes())
    for layer in mesh.uv_layers:
        values=array('f',[0])*(len(layer.data)*2)
        layer.data.foreach_get('uv',values)
        digest.update(values.tobytes())
    return digest.hexdigest()

bpy.ops.wm.open_mainfile(filepath=str(source))
candidate=bpy.data.objects['ICH_CHIBI_CONNECTIVITY_CANDIDATE_v01']
before=mesh_digest(candidate.data)
reference=bpy.data.objects['ICH_CHIBI_HIGHDETAIL_SOURCE__READONLY']
before_hide_render=reference.hide_render
collection=bpy.data.collections['00_HIGHDETAIL_TARGET__READ_ONLY']
assert not collection.library
collection.hide_render=True
collection.hide_viewport=True
candidate.hide_render=False
candidate.hide_set(False)
for obj in bpy.context.view_layer.objects:
    obj.select_set(obj==candidate)
bpy.context.view_layer.objects.active=candidate
scene=bpy.context.scene
scene.camera=bpy.data.objects['REVIEW_FULL_045']
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.shading.color_type='TEXTURE'
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(target))
after=mesh_digest(bpy.data.objects['ICH_CHIBI_CONNECTIVITY_CANDIDATE_v01'].data)
persisted=bpy.data.collections['00_HIGHDETAIL_TARGET__READ_ONLY'].hide_render
assert before==after
assert persisted
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
scene=bpy.context.scene
scene.render.resolution_x=scene.render.resolution_y=768
for label,camera in [('original_face','REVIEW_FACE_FRONT'),('original_full','REVIEW_FULL_045')]:
    scene.camera=bpy.data.objects[camera]
    scene.render.filepath=str(OUT/(label+'.png'))
    bpy.ops.render.render(write_still=True)
report={'status':'PASS_RELOAD_VISIBILITY_ONLY','source_file_sha256':source_sha,
        'mesh_topology_material_indices_uv_sha256_before':before,
        'mesh_topology_material_indices_uv_sha256_after_reload':after,
        'linked_reference_hide_render_before_fix':before_hide_render,
        'local_collection_hidden_after_reload':persisted,
        'source_file_unchanged':True,'geometry_uvs_unchanged':True,
        'limitation':'Reference visibility fix only; no game rig or print readiness claim.'}
(OUT/'visibility_audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('VISIBILITY_RELOAD_PASS',json.dumps(report))
