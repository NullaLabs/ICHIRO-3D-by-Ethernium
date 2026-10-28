"""Build a limited lower periocular quad strip from reviewed source landmarks.

Not a full eyelid: no globe contact, thickness, blink or final anatomy claim.
Nearest mask projection is bounded; fails rather than bridges unsupported areas.
"""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
outer_mode='--outer' in sys.argv
upper_mode='--upper' in sys.argv
smooth_mode='--smooth' in sys.argv
upper_mode=upper_mode or smooth_mode
outer_mode=outer_mode or upper_mode
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Ichiro_Chibi_Eyelid_Landmark_Review.blend'))
data=json.loads((ROOT/'docs'/'EYELID_LANDMARK_REVIEW.json').read_text())
anchors={p['index']:Vector(p['position']) for p in data['results']
         if p['contour']=='SCREEN_RIGHT' and p['status']=='candidate'}
target=bpy.data.objects['SKIN_CANDIDATES__NOT_APPROVED']
bvh=BVHTree.FromPolygons([target.matrix_world@v.co for v in target.data.vertices],
                        [tuple(f.vertices) for f in target.data.polygons])
path=[]
anchor_order=[7,6,5,4] if outer_mode else [7,6,5]
if upper_mode: anchor_order=[7,6,5,4,3,2]
for a,b in zip(anchor_order,anchor_order[1:]):
    path.extend(anchors[a].lerp(anchors[b],i/4) for i in range(4))
path.append(anchors[anchor_order[-1]])
original_path=[p.copy() for p in path]
if smooth_mode:
    # Corner cutting is an explicit shape proposal; endpoints remain fixed.
    curve=[anchors[i].copy() for i in anchor_order]
    for iteration in range(3):
        refined=[curve[0]]
        for a,b in zip(curve,curve[1:]):
            refined.extend((a.lerp(b,.25),a.lerp(b,.75)))
        refined.append(curve[-1]); curve=refined
    cumulative=[0.]
    for a,b in zip(curve,curve[1:]): cumulative.append(cumulative[-1]+(b-a).length)
    path=[]
    for i in range(len(original_path)):
        distance=cumulative[-1]*i/(len(original_path)-1)
        segment=next((j for j in range(len(curve)-1) if cumulative[j+1]>=distance),len(curve)-2)
        length=cumulative[segment+1]-cumulative[segment]
        path.append(curve[segment].lerp(curve[segment+1],(distance-cumulative[segment])/length))
verts=[]; distances=[]
for offset in [0,.003,.006]:
    for i,p in enumerate(path):
        tangent=path[min(i+1,len(path)-1)]-path[max(i-1,0)]
        outward=Vector((0,tangent.z,-tangent.y)).normalized() if outer_mode else Vector((0,0,-1))
        width_factor=1-.5*max(0,min(1,(i-8)/8)) if upper_mode else 1
        query=p+offset*width_factor*outward
        hit,normal,index,distance=bvh.find_nearest(query,.004)
        if hit is None: raise RuntimeError(f'Unsupported strip point {i}, offset {offset}; review mask')
        verts.append(hit+Vector((.0008,0,0))); distances.append(distance)
n=len(path)
faces=[]
for row in range(2):
    for i in range(n-1):
        faces.append((row*n+i,(row+1)*n+i,(row+1)*n+i+1,row*n+i+1))
mesh=bpy.data.meshes.new('Lower_Periocular_Strip_Mesh')
mesh.from_pydata(verts,[],faces); mesh.update()
if any(p.normal.x<=0 for p in mesh.polygons):
    raise RuntimeError('Reversed strip orientation')
if any(p.area<1e-10 for p in mesh.polygons):
    raise RuntimeError('Collapsed projected face')
collection=bpy.data.collections.new('WF003_LOWER_STRIP__REVIEW')
bpy.context.scene.collection.children.link(collection)
obj=bpy.data.objects.new('LOWER_PERIOCULAR_STRIP__NOT_FINAL',mesh)
collection.objects.link(obj)
obj.show_wire=True; obj.show_all_edges=True
obj['status']='Partial skin strip only; requires anatomical and deformation review'
mat=bpy.data.materials.new('StripReview'); mat.diffuse_color=(.02,.8,.3,1)
mesh.materials.append(mat)
wire=obj.modifiers.new('ReviewWire','WIREFRAME'); wire.thickness=.00035
wire.show_viewport=False
output=ROOT/('Ichiro_Chibi_Outer_Lid_Strip_Review.blend' if outer_mode else 'Ichiro_Chibi_Lower_Lid_Strip_Review.blend')
if upper_mode: output=ROOT/'Ichiro_Chibi_Upper_Lid_Strip_Review.blend'
if smooth_mode: output=ROOT/'Ichiro_Chibi_Smooth_Lid_Strip_Review.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(output))
report=dict(vertices=len(verts),quads=len(faces),max_projection_distance=max(distances),
    projection_limit=.004,source_landmarks=anchor_order,production_approved=False,
    limitations=['Partial lower skin band','No thickness or globe contact','No deformation test'])
report['minimum_face_area']=min(p.area for p in mesh.polygons)
report['upper_width_factor']=.5 if upper_mode else 1
report_name='UPPER_LID_STRIP_REVIEW.json' if upper_mode else ('OUTER_LID_STRIP_REVIEW.json' if outer_mode else 'LOWER_LID_STRIP_REVIEW.json')
if smooth_mode: report_name='SMOOTH_LID_STRIP_REVIEW.json'
report['guide_method']='three_corner_cutting_passes_equal_arc_spacing' if smooth_mode else 'linear_per_anchor'
def max_turn(points):
    from math import degrees
    return max(degrees((b-a).angle(c-b)) for a,b,c in zip(points,points[1:],points[2:]) if (b-a).length>1e-9 and (c-b).length>1e-9)
report['guide_max_turn_degrees']=max_turn(path)
report['projected_inner_max_turn_degrees']=max_turn(verts[:n])
report['original_guide_max_turn_degrees']=max_turn(original_path)
(ROOT/'docs'/report_name).write_text(json.dumps(report,indent=2)+'\n')
print('STRIP',report)
