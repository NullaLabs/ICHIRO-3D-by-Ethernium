"""Project explicitly reviewed pixel estimates onto the candidate mask.

Creates review markers only. Missing/occluded landmarks remain unresolved.
Never produces an apparently continuous lid by bridging missing observations.
"""
import bpy
import json
import hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Ichiro_Chibi_Skin_Projection_Experiment.blend'))
path=ROOT/'references'/'eyelid_landmarks_review.json'
data=json.loads(path.read_text(encoding='utf-8'))
camera=data['camera']
target=bpy.data.objects['SKIN_CANDIDATES__NOT_APPROVED']
bvh=BVHTree.FromPolygons([target.matrix_world@v.co for v in target.data.vertices],
                        [tuple(f.vertices) for f in target.data.polygons])
collection=bpy.data.collections.new('WF002B_LANDMARK_REVIEW__NOT_ANATOMY')
bpy.context.scene.collection.children.link(collection)
results=[]
for contour in data['contours']:
    for index,(px,py) in enumerate(contour['pixels']):
        y=(px/camera['width']-.5)*camera['scale']
        z=camera['target_z']+(.5-py/camera['height'])*camera['scale']
        hit=bvh.ray_cast(Vector((.5,y,z)),Vector((-1,0,0)),1)[0]
        occluded=index in contour['occluded_indices']
        status='occluded' if occluded else ('missing' if hit is None else 'candidate')
        results.append(dict(contour=contour['name'],index=index,pixel=[px,py],
                            status=status,position=list(hit) if hit is not None else None))
        if hit is not None and not occluded:
            marker=bpy.data.objects.new(f"LANDMARK_{contour['name']}_{index:02d}__REVIEW",None)
            marker.empty_display_type='SPHERE'; marker.empty_display_size=.002
            marker.location=hit; marker.show_in_front=True
            marker['status']='Candidate skin point, not an approved eyelid margin'
            collection.objects.link(marker)
report=dict(schema='ethernium.landmark-projection/0.1',
    landmark_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    results=results,production_approved=False)
(ROOT/'docs'/'EYELID_LANDMARK_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Ichiro_Chibi_Eyelid_Landmark_Review.blend'))
print('LANDMARKS', {s:sum(p['status']==s for p in results) for s in ('candidate','missing','occluded')})
