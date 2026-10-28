"""Build a limited lower periocular quad strip from reviewed source landmarks.

Not a full eyelid: no globe contact, thickness, blink or final anatomy claim.
Nearest mask projection is bounded; fails rather than bridges unsupported areas.
"""
import bpy
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Ichiro_Chibi_Eyelid_Landmark_Review.blend'))
data=json.loads((ROOT/'docs'/'EYELID_LANDMARK_REVIEW.json').read_text())
anchors={p['index']:Vector(p['position']) for p in data['results']
         if p['contour']=='SCREEN_RIGHT' and p['status']=='candidate'}
target=bpy.data.objects['SKIN_CANDIDATES__NOT_APPROVED']
bvh=BVHTree.FromPolygons([target.matrix_world@v.co for v in target.data.vertices],
                        [tuple(f.vertices) for f in target.data.polygons])
path=[]
for a,b in [(7,6),(6,5)]:
    path.extend(anchors[a].lerp(anchors[b],i/4) for i in range(4))
path.append(anchors[5])
verts=[]; distances=[]
for offset in [0,.003,.006]:
    for p in path:
        query=p+Vector((0,0,-offset))
        hit,normal,index,distance=bvh.find_nearest(query,.004)
        if hit is None: raise RuntimeError('Unsupported strip point; review mask')
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
output=ROOT/'Ichiro_Chibi_Lower_Lid_Strip_Review.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(output))
report=dict(vertices=len(verts),quads=len(faces),max_projection_distance=max(distances),
    projection_limit=.004,source_landmarks=[7,6,5],production_approved=False,
    limitations=['Partial lower skin band','No thickness or globe contact','No deformation test'])
(ROOT/'docs'/'LOWER_LID_STRIP_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n')
print('STRIP',report)
