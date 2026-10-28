"""Render orthographic facial diagnostics, including isolated eyes; never saves the blend."""
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "renders" / "facial_pass01_front.png"
scene = bpy.context.scene
for obj in bpy.data.collections['20_FACIAL_ANATOMY_COMPONENTS__PASS01'].objects:
    obj.hide_render = False
    obj.hide_set(False)
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 768
scene.render.resolution_y = 768
scene.render.resolution_percentage = 100
if scene.world is None:
    scene.world = bpy.data.worlds.new("ValidationWorld")
scene.world.color = (0.035, 0.035, 0.045)

def point(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()

bpy.ops.object.camera_add(location=(1.5, 0.0, 0.34))
camera = bpy.context.object
point(camera, (0, 0, 0.34))
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 0.40
scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(1.0, -0.8, 0.9))
bpy.context.object.data.energy = 35
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 0.6
point(bpy.context.object, (0, 0, 0.34))
bpy.ops.object.light_add(type='AREA', location=(0.8, 0.6, 0.3))
bpy.context.object.data.energy = 15
bpy.context.object.data.size = 0.4
point(bpy.context.object, (0, 0, 0.30))
for label, location in (
    ('front', (1.5, 0.0, 0.29)),
    ('profile_negative_y', (0.0, -1.5, 0.29)),
    ('profile_positive_y', (0.0, 1.5, 0.29)),
):
    camera.location = location
    point(camera, (0, 0, 0.29))
    scene.render.filepath = str(OUT.with_name(f'facial_pass01_{label}.png'))
    bpy.ops.render.render(write_still=True)

for obj in scene.objects:
    if obj.type == 'MESH' and obj.name not in bpy.data.collections['20_FACIAL_ANATOMY_COMPONENTS__PASS01'].objects:
        obj.hide_render = True
camera.location = (1.5, 0, 0.278)
point(camera, (0, 0, 0.278))
camera.data.ortho_scale = 0.18
scene.render.filepath = str(OUT.with_name('facial_pass01_eyes_isolated.png'))
bpy.ops.render.render(write_still=True)
