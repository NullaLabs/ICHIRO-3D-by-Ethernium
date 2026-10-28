"""Render isolated WF-002 mask beside a matching source view. No scene save."""
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Ichiro_Chibi_Skin_Projection_Experiment.blend'))
scene=bpy.context.scene
source=next(o for o in scene.objects if o.name.startswith('ICH_CHIBI_HIGHDETAIL_SOURCE'))
mask=bpy.data.objects['SKIN_CANDIDATES__NOT_APPROVED']
for obj in scene.objects:
    if obj.type=='MESH': obj.hide_render=True
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=768
scene.render.resolution_y=768
scene.render.resolution_percentage=100
if not scene.world: scene.world=bpy.data.worlds.new('MaskReviewWorld')
scene.world.color=(.08,.08,.08)
bpy.ops.object.camera_add(location=(1.5,0,.285))
camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,.285))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO'; camera.data.ortho_scale=.32
scene.camera=camera
for location,energy in [((1,-.8,.9),35),((.8,.6,.3),15)]:
    bpy.ops.object.light_add(type='AREA',location=location)
    lamp=bpy.context.object; lamp.data.energy=energy; lamp.data.size=.6
    lamp.rotation_euler=(Vector((0,0,.28))-lamp.location).to_track_quat('-Z','Y').to_euler()
for label,obj in [('source',source),('mask',mask)]:
    obj.hide_render=False
    scene.render.filepath=str(ROOT/'renders'/f'skin_review_{label}.png')
    bpy.ops.render.render(write_still=True)
    obj.hide_render=True
