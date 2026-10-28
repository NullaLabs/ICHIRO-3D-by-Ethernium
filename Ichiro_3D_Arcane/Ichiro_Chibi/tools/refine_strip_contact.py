"""Bounded front-surface contact experiment; retains source and previous strip.

Front visibility is not semantic anatomy. Reject large or missing corrections.
"""
import bpy
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Ichiro_Chibi_Depth_Lid_Strip_Review.blend'))
source=next(o for o in bpy.context.scene.objects if o.name.startswith('ICH_CHIBI_HIGHDETAIL_SOURCE'))
strip=bpy.data.objects['LOWER_PERIOCULAR_STRIP__NOT_FINAL']
bvh=BVHTree.FromPolygons([source.matrix_world@v.co for v in source.data.vertices],
                        [tuple(p.vertices) for p in source.data.polygons])
original=[v.co.copy() for v in strip.data.vertices]
corrections=[]
for vertex in strip.data.vertices:
    p=vertex.co
    hit=bvh.ray_cast(Vector((.5,p.y,p.z)),Vector((-1,0,0)),1)[0]
    delta=None if hit is None else hit.x+.0008-p.x
    status='rejected' if delta is None or abs(delta)>.004 else 'accepted'
    corrections.append(dict(vertex=vertex.index,delta_x=delta,status=status))
    if status=='accepted': vertex.co.x+=delta
strip.data.update()
invalid=[p.index for p in strip.data.polygons if p.area<1e-10 or p.normal.x<=0]
if invalid:
    raise RuntimeError(f'Contact correction invalidates faces: {invalid}')
report=dict(schema='ethernium.strip-contact/0.1',max_correction=.004,
    display_offset=.0008,corrections=corrections,production_approved=False,
    limitations=['Front visibility only, not anatomical segmentation',
                 'Rejected vertices retain previous position', 'No globe or blink validation'])
report['accepted']=sum(c['status']=='accepted' for c in corrections)
report['rejected']=len(corrections)-report['accepted']
(ROOT/'docs'/'STRIP_CONTACT_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n')
# Preserve the previous positions as a shape key for explicit comparison.
strip.shape_key_add(name='Basis')
before=strip.shape_key_add(name='Before_Contact_Review')
for point,position in zip(before.data,original): point.co=position
before.value=0
strip['status']='Contact experiment; source surface may include painted/raised eye features'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Ichiro_Chibi_Contact_Lid_Strip_Review.blend'))
print('CONTACT',report['accepted'],'accepted',report['rejected'],'rejected')
