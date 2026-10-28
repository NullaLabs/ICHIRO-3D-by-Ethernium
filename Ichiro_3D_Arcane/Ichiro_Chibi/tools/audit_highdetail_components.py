"""Report disconnected mesh islands in the locked high-detail source.

Used only to identify projection targets for manual face/hand topology.  It
does not edit or save the source blend.
"""
import bpy
from mathutils import Vector

obj = next(o for o in bpy.context.scene.objects if o.name.startswith("ICH_CHIBI_HIGHDETAIL_SOURCE"))
mesh = obj.data
adjacency = [[] for _ in mesh.vertices]
for edge in mesh.edges:
    a, b = edge.vertices
    adjacency[a].append(b)
    adjacency[b].append(a)

seen = bytearray(len(mesh.vertices))
components = []
for start in range(len(mesh.vertices)):
    if seen[start]:
        continue
    stack, indices = [start], []
    seen[start] = 1
    while stack:
        i = stack.pop()
        indices.append(i)
        for j in adjacency[i]:
            if not seen[j]:
                seen[j] = 1
                stack.append(j)
    vertices = [obj.matrix_world @ mesh.vertices[i].co for i in indices]
    low = Vector((min(v.x for v in vertices), min(v.y for v in vertices), min(v.z for v in vertices)))
    high = Vector((max(v.x for v in vertices), max(v.y for v in vertices), max(v.z for v in vertices)))
    center = (low + high) * 0.5
    components.append((len(indices), tuple(round(x, 4) for x in center), tuple(round(x, 4) for x in (high-low))))

components.sort(reverse=True)
print('component_count', len(components))
for rank, (count, center, size) in enumerate(components[:80], 1):
    print(f'{rank:02d} verts={count:7d} center={center} size={size}')
