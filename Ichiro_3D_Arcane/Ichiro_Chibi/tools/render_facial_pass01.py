"""Render a temporary front validation of the anatomical eye pass; does not save."""
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "renders" / "facial_pass01_front.png"
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 768
scene.render.resolution_y = 768
scene.render.resolution_percentage = 100
if scene.world is None:
    scene.world = bpy.data.worlds.new("ValidationWorld")
scene.world.color = (0.035, 0.035, 0.045)

def point(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()

bpy.ops.object.camera_add(location=(0.0, -1.5, 0.34))
camera = bpy.context.object
point(camera, (0, -0.02, 0.34))
camera.data.lens = 75
scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(-0.5, -0.8, 0.7))
bpy.context.object.data.energy = 550
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 0.6
point(bpy.context.object, (0, 0, 0.34))
bpy.ops.object.light_add(type='AREA', location=(0.4, -0.6, 0.3))
bpy.context.object.data.energy = 250
bpy.context.object.data.size = 0.4
point(bpy.context.object, (0, 0, 0.30))
scene.render.filepath = str(OUT)
bpy.ops.render.render(write_still=True)
print(OUT)
