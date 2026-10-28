"""Dependency-free geometry gate for frontal patches in review packet 0.1.

Exit 0: geometric checks pass (not artistic approval); 2: review blocked.
Coordinates must be viewer +Z front, +Y up. Does not modify the packet.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import median


def inspect_mesh(mesh):
    flat = mesh['positions']
    if not flat or len(flat) % 3 or not all(math.isfinite(v) for v in flat):
        raise ValueError('Positions must contain finite XYZ triples')
    points = [flat[i:i+3] for i in range(0, len(flat), 3)]
    edges, backwards, degenerate = {}, [], []
    faces = mesh['quadFaces']
    if not faces:
        raise ValueError('Empty face list')
    for fi, face in enumerate(faces):
        if len(face) != 4 or len(set(face)) != 4:
            raise ValueError('Expected four distinct indices per quad')
        if any(type(i) is not int or i < 0 or i >= len(points) for i in face):
            raise ValueError('Face index outside vertex buffer')
        # Newell normal: robust for nonplanar authored quads.
        normal = [0., 0., 0.]
        for a, b in zip(face, face[1:]+face[:1]):
            p, q = points[a], points[b]
            for axis in range(3):
                j, k = (axis+1)%3, (axis+2)%3
                normal[axis] += (p[j]-q[j])*(p[k]+q[k])
            edge = tuple(sorted((a, b)))
            edges[edge] = edges.get(edge, 0)+1
        magnitude = math.sqrt(sum(v*v for v in normal))
        if magnitude < 1e-12:
            degenerate.append(fi)
        elif normal[2]/magnitude < -0.1:
            backwards.append(fi)
    lengths = {edge: math.dist(points[edge[0]], points[edge[1]]) for edge in edges}
    typical = median(lengths.values())
    depth_jumps = [list(e) for e in edges
                   if abs(points[e[0]][2]-points[e[1]][2]) > 3*typical]
    reasons = []
    if backwards: reasons.append('back_facing_frontal_faces')
    if degenerate: reasons.append('degenerate_faces')
    if any(n > 2 for n in edges.values()): reasons.append('overconnected_edges')
    if typical <= 1e-12: reasons.append('collapsed_edge_sampling')
    if depth_jumps: reasons.append('depth_discontinuity_requires_review')
    return dict(name=mesh['name'], blocked=bool(reasons), reasons=reasons,
                backwards_faces=backwards, degenerate_faces=degenerate,
                depth_jump_edges=depth_jumps, median_edge_length=typical,
                max_edge_length=max(lengths.values()),
                boundary_edges=sum(n == 1 for n in edges.values()))


def validate(packet):
    if packet.get('schema') != 'ethernium.character-review/0.1':
        raise ValueError('Unsupported packet schema')
    if packet.get('coordinates', {}).get('target') != {'front': '+Z', 'up': '+Y'}:
        raise ValueError('Unexpected coordinate frame')
    if not packet.get('meshes'):
        raise ValueError('No geometry to inspect')
    results = [inspect_mesh(m) for m in packet['meshes']]
    return dict(schema='ethernium.frontal-patch-gate/0.1', meshes=results,
                geometry_gate='blocked' if any(m['blocked'] for m in results) else 'pass',
                production_approved=False,
                limitations=['Frontal patches only', 'No intersection or deformation test',
                             'No reference fidelity evaluation', 'Base mesh only'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.packet.read_bytes()
    report = validate(json.loads(raw))
    report['packet_sha256'] = hashlib.sha256(raw).hexdigest()
    report['validator_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(report['geometry_gate'], [(m['name'], m['reasons']) for m in report['meshes']])
    return 2 if report['geometry_gate'] == 'blocked' else 0


if __name__ == '__main__':
    raise SystemExit(main())
