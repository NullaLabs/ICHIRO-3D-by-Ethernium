"""Render projected landmarks from three angles, without changing saved geometry."""
import json
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
import sys
strip_mode='--strip' in sys.argv
bpy.ops.wm.open_mainfile(filepath=str(ROOT/('Ichiro_Chibi_Lower_Lid_Strip_Review.blend' if strip_mode else 'Ichiro_Chibi_Eyelid_Landmark_Review.blend')))
scene=bpy.context.scene
for obj in scene.objects:
    if obj.type=='MESH':
        obj.hide_render=not (obj.name.startswith('ICH_CHIBI_HIGHDETAIL_SOURCE') or
                            (strip_mode and obj.name.startswith('LOWER_PERIOCULAR_STRIP')))
materials={}
for name,color in [('candidate',(0.02,1,.15,1)),('occluded',(1,.35,.01,1))]:
    mat=bpy.data.materials.new('Review_'+name); mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=color
    bsdf.inputs['Emission Color'].default_value=color
    bsdf.inputs['Emission Strength'].default_value=.8
    materials[name]=mat
data=json.loads((ROOT/'docs'/'EYELID_LANDMARK_REVIEW.json').read_text())
for entry in data['results']:
    if entry['position'] is None: continue
    position=Vector(entry['position'])+Vector((.001,0,0))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.0018,location=position)
    marker=bpy.context.object
    marker.name=f"REVIEW_{entry['contour']}_{entry['index']}"
    marker.data.materials.append(materials[entry['status']])
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=768; scene.render.resolution_y=768
scene.render.resolution_percentage=100
if not scene.world: scene.world=bpy.data.worlds.new('ReviewWorld')
scene.world.color=(.08,.08,.08)
target=Vector((.04,0,.275))
bpy.ops.object.camera_add()
cam=bpy.context.object; cam.data.type='ORTHO'; cam.data.ortho_scale=.32
scene.camera=cam
for loc in [(1,-.8,.9),(.8,.6,.3)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    lamp=bpy.context.object; lamp.data.energy=25; lamp.data.size=.6
    lamp.rotation_euler=(target-lamp.location).to_track_quat('-Z','Y').to_euler()
for label,loc in [('front',(1.5,0,.275)),('negative_y',(.04,-1.5,.275)),('positive_y',(.04,1.5,.275))]:
    cam.location=loc
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    prefix='lower_strip' if strip_mode else 'landmark_depth'
    scene.render.filepath=str(ROOT/'renders'/f'{prefix}_{label}.png')
    bpy.ops.render.render(write_still=True)
