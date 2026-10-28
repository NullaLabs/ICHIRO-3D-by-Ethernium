"""Constrained depth regularization of inferred vertices; not contact approval."""
import bpy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Ichiro_Chibi_Closed_Eye_Review.blend'))
obj=bpy.data.objects['LOWER_PERIOCULAR_STRIP__CLOSED_REVIEW']
report=json.loads((ROOT/'docs'/'CLOSED_EYE_REVIEW.json').read_text())
free=set(report['inferred_vertex_indices'])
original=[v.co.copy() for v in obj.data.vertices]
adj=[set() for v in original]
for edge in obj.data.edges:
    a,b=edge.vertices; adj[a].add(b); adj[b].add(a)
x=[p.x for p in original]
def roughness(values):
    return sum((values[i]-sum(values[j] for j in adj[i])/len(adj[i]))**2 for i in free)
before=roughness(x)
for iteration in range(40):
    next_x=x.copy()
    for i in free:
        mean=sum(x[j] for j in adj[i])/len(adj[i])
        proposal=.5*x[i]+.5*mean
        next_x[i]=max(original[i].x-.004,min(original[i].x+.004,proposal))
    x=next_x
for i,vertex in enumerate(obj.data.vertices): vertex.co.x=x[i]
obj.data.update()
if any(f.area<1e-10 or f.normal.x<=0 for f in obj.data.polygons):
    raise RuntimeError('Depth regularization invalidated faces')
assert all(obj.data.vertices[i].co==original[i] for i in range(len(x)) if i not in free)
obj.shape_key_add(name='Basis')
key=obj.shape_key_add(name='Before_Depth_Regularization')
for p,co in zip(key.data,original): p.co=co
key.value=0
result=dict(schema='ethernium.depth-regularization/0.1',iterations=40,
    adjusted_vertex_count=len(free),fixed_vertex_count=len(x)-len(free),
    max_displacement=max(abs(x[i]-original[i].x) for i in free),
    squared_laplacian_before=before,squared_laplacian_after=roughness(x),
    production_approved=False,contact_status='not_revalidated',
    limitations=['Smoothness is not anatomical accuracy','Inferred points may leave source surface',
                 'No globe contact or blink validation'])
(ROOT/'docs'/'CLOSED_EYE_RELAX_REVIEW.json').write_text(json.dumps(result,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Ichiro_Chibi_Closed_Eye_Relax_Review.blend'))
print('RELAX',result)
