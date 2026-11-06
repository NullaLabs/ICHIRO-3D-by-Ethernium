"""Verify the pilot's exported neutral and blink vertices after GLB import."""
from pathlib import Path
import argparse
import json
import sys
import bpy
from mathutils.kdtree import KDTree

parser=argparse.ArgumentParser()
parser.add_argument('--dir',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
folder=args.dir.resolve()
bpy.ops.wm.open_mainfile(filepath=str(folder/'Ichiro_Eye_R_Blink_Pilot.blend'))
reference=bpy.data.objects['EYE_R_GAME_BLINK_PILOT']
reference_open=[reference.matrix_world @ p.co for p in reference.data.shape_keys.key_blocks[0].data]
reference_closed=[reference.matrix_world @ p.co for p in reference.data.shape_keys.key_blocks['Blink_R'].data]
tree=KDTree(len(reference_open))
for i,p in enumerate(reference_open): tree.insert(p,i)
tree.balance()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(folder/'Ichiro_Eye_R_Blink_Pilot.glb'))
objects=[o for o in bpy.data.objects if o.type=='MESH' and o.data.shape_keys and o.data.shape_keys.key_blocks.get('Blink_R')]
assert len(objects)==1, 'Expected one exported morph-capable mesh'
obj=objects[0]
basis=obj.data.shape_keys.key_blocks[0]
blink=obj.data.shape_keys.key_blocks['Blink_R']
errors_open=[]; errors_closed=[]; correspondences=set()
for i,p in enumerate(basis.data):
    world=obj.matrix_world @ p.co
    nearest,index,distance=tree.find(world)
    correspondences.add(index)
    errors_open.append(distance)
    errors_closed.append(((obj.matrix_world @ blink.data[i].co)-reference_closed[index]).length)
result={'exported_vertices':len(basis.data),'reference_vertices':len(reference_open),
        'unique_correspondences':len(correspondences),'maximum_neutral_error':max(errors_open),
        'maximum_blink_error':max(errors_closed),'morph_target':'Blink_R',
        'has_animation_actions':bool(bpy.data.actions),
        'validation_scope':'Blender GLB re-import, not Unreal/Unity runtime validation'}
assert len(correspondences)==len(reference_open)
assert max(errors_open)<1e-6 and max(errors_closed)<1e-6
assert not bpy.data.actions
(folder/'glb_roundtrip_audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print('ROUNDTRIP_PASS',json.dumps(result))
