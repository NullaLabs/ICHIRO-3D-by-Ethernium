"""Reproduce the reversible nasal form hypothesis and fixed-camera evidence.
Run with Blender --background --factory-startup --python THIS_FILE -- --out NEW_DIR.
Uses the existing source workspace; refuses to overwrite an existing review.
"""
from pathlib import Path
import argparse
import sys
import bpy

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
OUT = args.out.resolve()
OUT.mkdir(parents=True, exist_ok=True)
OUTPUT_PREFIX = OUT.as_posix() + "/"
blend = OUT / "Ichiro_Chibi_Form_Review_v01.blend"
if blend.exists():
    raise RuntimeError("Choose a new output directory; existing review is preserved.")
bpy.ops.wm.open_mainfile(filepath=str(ROOT / "Ichiro_Chibi_HEAD_HANDS_Topology_Workspace.blend"))
bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
import bpy
import math
from mathutils import Vector
scene=bpy.context.scene
source=bpy.data.objects['ICH_CHIBI_HIGHDETAIL_SOURCE__READONLY']
for o in scene.objects:
    if o.type=='MESH':
        o.hide_render=(o!=source)
    if o.type=='EMPTY': o.hide_set(True)
try:
    scene.render.engine='BLENDER_WORKBENCH'
except TypeError as e:
    print(e)
scene.render.resolution_x=768
scene.render.resolution_y=768
scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='SINGLE'
scene.display.shading.single_color=(0.65,0.65,0.65)
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.background_type='WORLD'
if scene.world is None: scene.world=bpy.data.worlds.new('REVIEW_WORLD')
scene.world.color=(0.07,0.07,0.07)
scene.render.image_settings.file_format='PNG'
for angle in range(0,360,45):
    name='REVIEW_FULL_%03d'%angle
    data=bpy.data.cameras.new(name)
    cam=bpy.data.objects.new(name,data)
    scene.collection.objects.link(cam)
    a=math.radians(angle)
    cam.location=(3*math.cos(a),3*math.sin(a),0)
    cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO'
    data.ortho_scale=1.12
for name,location,target,scale in [('FACE_FRONT',(2,0,.285),(0,0,.285),.36),('FACE_LEFT',(0,2,.285),(0,0,.285),.36),('FACE_RIGHT',(0,-2,.285),(0,0,.285),.36),('HANDS_FRONT',(2,0,-.15),(0,0,-.15),.60)]:
    data=bpy.data.cameras.new('REVIEW_'+name)
    cam=bpy.data.objects.new('REVIEW_'+name,data)
    scene.collection.objects.link(cam)
    cam.location=location
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO'
    data.ortho_scale=scale
scene.camera=bpy.data.objects['REVIEW_FACE_FRONT']
scene.render.filepath=OUTPUT_PREFIX + 'before_face_front.png'
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Fixed review cameras saved')
import bpy
source=bpy.data.objects['ICH_CHIBI_HIGHDETAIL_SOURCE__READONLY']
assert bpy.data.filepath.endswith('Ichiro_Chibi_Form_Review_v01.blend')
assert bpy.data.objects.get('ICH_CHIBI_FORM_CANDIDATE_v01') is None
candidate=source.copy()
candidate.data=source.data.copy()
candidate.name='ICH_CHIBI_FORM_CANDIDATE_v01'
bpy.context.scene.collection.objects.link(candidate)
candidate.hide_select=False
candidate.hide_render=False
candidate.hide_set(False)
source.hide_render=True
source.hide_set(True)
basis=candidate.shape_key_add(name='Basis_SOURCE_UNCHANGED')
key=candidate.shape_key_add(name='REVIEW_Nose_Projection_Reduction')
changed=0
max_distance=0.0
for i,v in enumerate(candidate.data.vertices):
    x,y,z=v.co
    r2=((y+0.015)/0.034)**2+((z-0.226)/0.038)**2
    if r2<1.0 and x>0.09:
        t=min(1.0,max(0.0,(x-0.09)/0.02))
        gate=t*t*(3.0-2.0*t)
        w=(1.0-r2)**2*gate
        dx=-0.007*w
        dy=-0.08*(y+0.015)*w
        key.data[i].co.x+=dx
        key.data[i].co.y+=dy
        changed+=1
        max_distance=max(max_distance,(dx*dx+dy*dy)**0.5)
key.value=1.0
candidate['review_status']='LOCAL FORM HYPOTHESIS; not approved anatomy or rig topology'
candidate['correction']='Compact smooth nasal depth reduction; center y=-0.015,z=0.226; radii .034,.038; max dx -.007; lateral contraction .08; x gate .09-.11'
candidate['changed_vertices']=changed
candidate['maximum_displacement']=max_distance
print('CANDIDATE',changed,'vertices; max displacement',max_distance)
scene=bpy.context.scene
scene.render.resolution_x=768
scene.render.resolution_y=768
for label in ['FACE_FRONT','FACE_LEFT','FACE_RIGHT']:
    scene.camera=bpy.data.objects['REVIEW_'+label]
    scene.render.filepath=OUTPUT_PREFIX + 'after_'+label.lower()+'.png'
    bpy.ops.render.render(write_still=True)
scene.camera=bpy.data.objects['REVIEW_FACE_FRONT']
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

# Render exactly the same cameras for both shape-key states.
scene.display.shading.color_type = 'SINGLE'
for state, value in [('before', 0.0), ('after', 1.0)]:
    key.value = value
    for label in ['FACE_FRONT', 'FACE_LEFT', 'FACE_RIGHT', 'HANDS_FRONT']:
        scene.camera = bpy.data.objects['REVIEW_' + label]
        scene.render.resolution_x = scene.render.resolution_y = 768
        scene.render.filepath = str(OUT / (state + '_' + label.lower() + '.png'))
        bpy.ops.render.render(write_still=True)
    for angle in range(0, 360, 45):
        scene.camera = bpy.data.objects['REVIEW_FULL_%03d' % angle]
        scene.render.resolution_x = scene.render.resolution_y = 512
        scene.render.filepath = str(OUT / (state + '_full_%03d.png' % angle))
        bpy.ops.render.render(write_still=True)
key.value = 1.0
scene.camera = bpy.data.objects['REVIEW_FACE_FRONT']
scene.render.resolution_x = scene.render.resolution_y = 768
bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
print('REVIEW COMPLETE', blend)
