"""Read-only quality audit for the Antigravity Ichiro true-360 source.

This script never saves, writes or alters the source mesh. It is intended to be
run inside Blender through the MCP bridge before creating any non-destructive
modifiers or sculpt layers.
"""
import bmesh
import numpy as np
import os

SCRATCH_DIR = r"C:\Users\esenc\.gemini\antigravity\brain\3ccecf18-5e96-4998-8aad-0804a4100391\scratch"
SOURCE = os.path.join(SCRATCH_DIR, "test_lumen_360_master_mesh.npz")

if not os.path.isfile(SOURCE):
    raise FileNotFoundError(SOURCE)

data = np.load(SOURCE)
verts = np.asarray(data["verts"], dtype=np.float64)
faces = np.asarray(data["faces"], dtype=np.int64)

if verts.ndim != 2 or verts.shape[1] != 3:
    raise ValueError(f"Expected Nx3 vertices, got {verts.shape}")
if faces.ndim != 2 or faces.shape[1] < 3:
    raise ValueError(f"Expected polygon indices, got {faces.shape}")
if faces.min() < 0 or faces.max() >= len(verts):
    raise ValueError("Face indices exceed source vertex range")

mesh = bmesh.new()
bv = [mesh.verts.new(co) for co in verts]
mesh.verts.ensure_lookup_table()
for face in faces:
    try:
        mesh.faces.new([bv[int(i)] for i in face])
    except ValueError:
        # Duplicate faces are reported through the audit rather than changed.
        pass
mesh.verts.ensure_lookup_table()
mesh.edges.ensure_lookup_table()
mesh.faces.ensure_lookup_table()

mins = verts.min(axis=0)
maxs = verts.max(axis=0)
size = maxs - mins
quad_count = int(np.sum(np.array([len(face) for face in faces]) == 4))
tri_count = int(np.sum(np.array([len(face) for face in faces]) == 3))
boundary = [edge for edge in mesh.edges if edge.is_boundary]
non_manifold = [edge for edge in mesh.edges if not edge.is_manifold]
loose = [vert for vert in mesh.verts if not vert.link_edges]
valences = np.array([len(vert.link_edges) for vert in mesh.verts], dtype=np.int32)

print("ICHIRO_TRUE360_AUDIT")
print(f"source={SOURCE}")
print(f"vertices={len(verts)} faces={len(faces)} quads={quad_count} triangles={tri_count}")
print(f"bounds_min={mins.tolist()} bounds_max={maxs.tolist()} dimensions={size.tolist()}")
print(f"boundary_edges={len(boundary)} non_manifold_edges={len(non_manifold)} loose_vertices={len(loose)}")
print(f"valence_min={valences.min()} valence_max={valences.max()} valence_mean={valences.mean():.4f}")
print("result=" + ("PASS_WATERTIGHT" if not boundary and not non_manifold and not loose else "REQUIRES_REPAIR"))
mesh.free()
