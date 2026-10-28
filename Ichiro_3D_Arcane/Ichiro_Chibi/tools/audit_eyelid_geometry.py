"""Read-only base-mesh audit; Blender --background --factory-startup --python FILE.

Front-facing normals are expected only for these frontal eyelid patches.
Depth/sampling thresholds are diagnostics, not anatomical acceptance criteria.
"""
import json
from pathlib import Path
from statistics import median
import bpy
import bmesh

ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'Ichiro_Chibi_Eyelid_Topology_Pass02.blend'))
results = []
for obj in sorted(bpy.context.scene.objects, key=lambda o: o.name):
    if not obj.name.startswith('EYELID_'):
        continue
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(obj.matrix_world)
    bm.normal_update()
    lengths = [e.calc_length() for e in bm.edges]
    typical = median(lengths)
    jumps = [e.index for e in bm.edges if abs(e.verts[0].co.x-e.verts[1].co.x) > 3*typical]
    reversed_faces = [f.index for f in bm.faces if f.normal.x < -0.1]
    results.append(dict(name=obj.name, vertices=len(bm.verts), faces=len(bm.faces),
        non_quads=sum(len(f.verts)!=4 for f in bm.faces),
        degenerate_faces=sum(f.calc_area()<1e-12 for f in bm.faces),
        boundary_edges=sum(e.is_boundary for e in bm.edges),
        overconnected_edges=sum(len(e.link_faces)>2 for e in bm.edges),
        median_edge_length=typical, max_edge_length=max(lengths),
        max_to_median_edge_ratio=max(lengths)/typical,
        back_facing_face_indices=reversed_faces, depth_jump_edge_indices=jumps,
        production_approved=False))
    bm.free()
if len(results) != 2:
    raise RuntimeError('Expected two eyelid patches')
report = dict(schema='ichiro.geometry_audit.v1', source=bpy.data.filepath,
    limitations=['No self-intersection test', 'No anatomical fit or deformation validation',
                  'Base geometry only; modifiers excluded'], meshes=results)
output = ROOT / 'docs' / 'EYELID_GEOMETRY_AUDIT.json'
output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print(json.dumps(results, indent=2))
