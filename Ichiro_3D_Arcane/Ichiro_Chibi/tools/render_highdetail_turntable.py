"""Render eight neutral review angles from the protected high-detail source."""
from pathlib import Path
import bpy, math
from mathutils import Vector

ROOT=Path(r'E:/WORKSPACE/Ichiro_Chibi')
INFILE=ROOT/'blend'/'Ichiro_Chibi_HighDetail_Working.blend'
OUT=ROOT/'renders'/'highdetail_turntable'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(INFILE))
obj=bpy.data.objects.get('ICH_CHIBI_HIGHDETAIL_SOURCE__READONLY')
if not obj: raise RuntimeError('High source missing')
obj.hide_render=False; obj.hide_set(False)
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=512; scene.render.resolution_y=512; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world.color=(0.035,0.035,0.045)

# Avoid modifying source camera/light setup by creating temporary review tools.
for o in list(bpy.data.objects):
    if o.name.startswith('TMP_REVIEW_'): bpy.data.objects.remove(o,do_unlink=True)
def look(o,pt): o.rotation_euler=(Vector(pt)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(); cam=bpy.context.object; cam.name='TMP_REVIEW_CAMERA'
cam.data.type='ORTHO'; cam.data.ortho_scale=1.35; scene.camera=cam
for loc,energy,size in [((2,-3,3),1100,3.0),((-2,-2,1.5),700,2.5),((0,2,3),900,2.0)]:
    bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.name='TMP_REVIEW_LIGHT'; l.data.energy=energy; l.data.shape='DISK'; l.data.size=size; look(l,(0,0,0))
target=(0,0,0)
for i,angle in enumerate(range(0,360,45)):
    r=3.0; a=math.radians(angle)
    cam.location=(r*math.sin(a),-r*math.cos(a),.1); look(cam,target)
    scene.render.filepath=str(OUT/f'ichiro_chibi_high_{angle:03d}.png')
    bpy.ops.render.render(write_still=True)
print(f'RENDERED {OUT}')
