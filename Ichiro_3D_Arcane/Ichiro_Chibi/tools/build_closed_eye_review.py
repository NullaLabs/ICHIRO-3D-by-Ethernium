"""Closed periocular review topology with explicit inferred depth provenance.

Uses source-render landmarks, not approved canonical anatomy. No rig claim.
"""
import bpy
import bmesh
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Ichiro_Chibi_Eyelid_Landmark_Review.blend'))
landmarks=json.loads((ROOT/'references'/'eyelid_landmarks_review.json').read_text())
review=json.loads((ROOT/'docs'/'EYELID_LANDMARK_REVIEW.json').read_text())
known={p['index']:Vector(p['position']) for p in review['results']
       if p['contour']=='SCREEN_RIGHT' and p['position'] is not None}
pixels=landmarks['contours'][1]['pixels']; camera=landmarks['camera']
# Missing landmark 1 has an observed image coordinate but no accepted skin depth.
px,py=pixels[1]
known[1]=Vector(((known[0].x+known[2].x)/2,
                (px/camera['width']-.5)*camera['scale'],
                camera['target_z']+(.5-py/camera['height'])*camera['scale']))
order=[7,6,5,4,3,2,1,0]
curve=[known[i] for i in order]
for iteration in range(2):
    curve=[p for a,b in zip(curve,curve[1:]+curve[:1]) for p in (a.lerp(b,.25),a.lerp(b,.75))]
closed=curve+[curve[0]]; lengths=[0.]
for a,b in zip(closed,closed[1:]): lengths.append(lengths[-1]+(b-a).length)
path=[]; n=32
for i in range(n):
    d=lengths[-1]*i/n
    j=next(j for j in range(len(curve)) if lengths[j+1]>=d)
    path.append(closed[j].lerp(closed[j+1],(d-lengths[j])/(lengths[j+1]-lengths[j])))
source=next(o for o in bpy.context.scene.objects if o.name.startswith('ICH_CHIBI_HIGHDETAIL_SOURCE'))
bvh=BVHTree.FromPolygons([source.matrix_world@v.co for v in source.data.vertices],
                        [tuple(f.vertices) for f in source.data.polygons])
vertices=[]; samples=[]
for row,offset in enumerate((0,.0015,.003)):
    for i,p in enumerate(path):
        tangent=path[(i+1)%n]-path[(i-1)%n]
        query=p+offset*Vector((0,tangent.z,-tangent.y)).normalized()
        hit=bvh.ray_cast(Vector((.5,query.y,query.z)),Vector((-1,0,0)),1)[0]
        delta=None if hit is None else hit.x-query.x
        accepted=delta is not None and abs(delta)<=.004
        # Rejected observations stay on the authored hypothesis and are tagged.
        x=hit.x if accepted else query.x
        vertices.append(Vector((x+.0008,query.y,query.z)))
        samples.append(dict(vertex=len(vertices)-1,observed_depth_delta=delta,
                            status='source_contact_candidate' if accepted else 'inferred_depth_requires_review'))
faces=[(r*n+i,(r+1)*n+i,(r+1)*n+(i+1)%n,r*n+(i+1)%n)
       for r in range(2) for i in range(n)]
mesh=bpy.data.meshes.new('Closed_Periocular_Review'); mesh.from_pydata(vertices,[],faces); mesh.update()
if any(f.normal.x<=0 or f.area<1e-10 for f in mesh.polygons):
    raise RuntimeError('Invalid closed candidate faces')
bm=bmesh.new(); bm.from_mesh(mesh)
boundary=sum(e.is_boundary for e in bm.edges)
overconnected=sum(len(e.link_faces)>2 for e in bm.edges)
bm.free()
if boundary!=64 or overconnected: raise RuntimeError('Unexpected ring connectivity')
collection=bpy.data.collections.new('WF004_CLOSED_EYE__EXPERIMENT')
bpy.context.scene.collection.children.link(collection)
obj=bpy.data.objects.new('LOWER_PERIOCULAR_STRIP__CLOSED_REVIEW',mesh)
collection.objects.link(obj); obj.show_wire=True; obj.show_all_edges=True
obj['status']='Closed skin band only, inferred depth; no anatomical or rig approval'
group=obj.vertex_groups.new(name='INFERRED_DEPTH_REVIEW')
unresolved=[s['vertex'] for s in samples if s['status'].startswith('inferred')]
if unresolved: group.add(unresolved,1,'REPLACE')
wire=obj.modifiers.new('ReviewWire','WIREFRAME'); wire.thickness=.00035; wire.show_viewport=False
report=dict(vertices=len(vertices),quads=len(faces),boundary_edges=boundary,
    inferred_control_landmarks=[1],inferred_vertex_indices=unresolved,samples=samples,
    production_approved=False,depth_tolerance=.004,
    limitations=['Source render estimates, not canon-approved','Rejected contact retains explicitly inferred geometry',
                 'Corner cutting moves image landmarks','No lid margin, thickness or globe validation'])
(ROOT/'docs'/'CLOSED_EYE_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Ichiro_Chibi_Closed_Eye_Review.blend'))
print('CLOSED',len(vertices),len(faces),'unresolved',unresolved)
