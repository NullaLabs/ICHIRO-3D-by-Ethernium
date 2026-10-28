"""Export evaluated review geometry for an Ethernium viewer, without modifying Blender.

Run with Blender --background --factory-startup <pass02.blend> --python this.py.
The packet preserves authored quads alongside display triangles. It is a data
contract for integration, not a claim that remote services are connected.
"""
import bpy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'exports' / 'ethernium_review_packet.json'

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

packet = {
    'schema': 'ethernium.character-review/0.1',
    'asset': 'Ichiro Chibi',
    'status': 'experimental_eyelid_patches_requires_art_review',
    'coordinates': {
        'source': {'front': '+X', 'up': '+Z'},
        'target': {'front': '+Z', 'up': '+Y'},
        'mapping': '[source.y, source.z, source.x]',
        'scale': 1.0,
        'physical_units': 'uncalibrated_model_units',
    },
    'source_blend': Path(bpy.data.filepath).name,
    'source_sha256': digest(Path(bpy.data.filepath)),
    'reviewed_upstream': {
        'KREATIVE-GENERATOR-by-Ethernium': '10c3b12df3f2d2604602db9e173f2bb4e39055e4',
        'LEGION-by-Ethernium': '70ae98efd0ac9991542e8df900fca2965f6c1f6d',
        'NOISIA-by-Ethernium': 'e86356510b67fdc81eeaa2b5b84d914a45a34d13',
    },
    'meshes': [],
    'references': [],
    'acceptance': {'shape': 'pending', 'deformation': 'not_tested', 'rig': 'absent'},
}
for obj in sorted(bpy.context.scene.objects, key=lambda o:o.name):
    if obj.type != 'MESH' or not obj.name.startswith('EYELID_'):
        continue
    mesh = obj.data
    mesh.calc_loop_triangles()
    positions = []
    for vertex in mesh.vertices:
        p = obj.matrix_world @ vertex.co
        positions.extend([float(p.y), float(p.z), float(p.x)])
    faces = [list(p.vertices) for p in mesh.polygons]
    edge_use = {}
    for face in faces:
        for a,b in zip(face, face[1:]+face[:1]):
            edge = tuple(sorted((a,b)))
            edge_use[edge] = edge_use.get(edge,0)+1
    assert all(len(f)==4 for f in faces), 'Expected authored quad patches'
    assert all(n<=2 for n in edge_use.values()), 'Overconnected edge'
    assert len(positions)==3*len(mesh.vertices)
    packet['meshes'].append({
        'name': obj.name,
        'positions': positions,
        'indices': [i for t in mesh.loop_triangles for i in t.vertices],
        'quadFaces': faces,
        'metrics': {'vertices': len(mesh.vertices), 'quads': len(faces),
                    'boundary_edges': sum(n==1 for n in edge_use.values())},
        'modifiers_applied': False,
    })
assert len(packet['meshes'])==2, 'Open the eyelid Pass02 scene'
for path in sorted((ROOT/'references').glob('*.png')):
    packet['references'].append({'path': path.relative_to(ROOT).as_posix(),
                                 'sha256': digest(path)})
assert len(packet['references'])==6, 'Expected all six reference images'
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(packet, indent=2, allow_nan=False), encoding='utf-8')
print('REVIEW_PACKET', OUT, 'meshes', len(packet['meshes']), 'references', len(packet['references']))
