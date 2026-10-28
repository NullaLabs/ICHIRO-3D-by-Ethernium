"""Memory-efficient connected-island indexing for Blender mesh diagnostics."""
from array import array


def find_root(parent, index):
    while parent[index] != index:
        parent[index] = parent[parent[index]]
        index = parent[index]
    return index


def audit_components(mesh):
    """Return deterministic component IDs, counts and local bounds for a mesh.

    IDs sort by descending vertex count, then by the component's smallest root
    vertex index. The routine reads the mesh and never changes its geometry.
    """
    vertex_count = len(mesh.vertices)
    parent = array("I", range(vertex_count))
    size = array("I", [1]) * vertex_count

    for edge in mesh.edges:
        left = find_root(parent, edge.vertices[0])
        right = find_root(parent, edge.vertices[1])
        if left != right:
            if size[left] < size[right]:
                left, right = right, left
            parent[right] = left
            size[left] += size[right]

    counts = {}
    bounds = {}
    for index, vertex in enumerate(mesh.vertices):
        root = find_root(parent, index)
        counts[root] = counts.get(root, 0) + 1
        point = vertex.co
        box = bounds.get(root)
        if box is None:
            bounds[root] = [point.x, point.y, point.z, point.x, point.y, point.z]
        else:
            if point.x < box[0]: box[0] = point.x
            if point.y < box[1]: box[1] = point.y
            if point.z < box[2]: box[2] = point.z
            if point.x > box[3]: box[3] = point.x
            if point.y > box[4]: box[4] = point.y
            if point.z > box[5]: box[5] = point.z

    def count_key(root):
        return (-counts[root], root)

    ordered_roots = sorted(counts, key=count_key)
    root_to_id = {root: component_id for component_id, root in enumerate(ordered_roots)}
    face_counts = [0] * len(ordered_roots)
    for polygon in mesh.polygons:
        face_counts[root_to_id[find_root(parent, polygon.vertices[0])]] += 1
    return parent, root_to_id, ordered_roots, counts, bounds, face_counts


def component_id_for_polygon(audit, polygon):
    parent, root_to_id = audit[0], audit[1]
    return root_to_id[find_root(parent, polygon.vertices[0])]
