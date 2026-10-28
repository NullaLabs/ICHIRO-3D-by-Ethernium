"""Construct editable quad eyelid patches and render their fit for review.

Landmarks are initial estimates from the orthographic facial diagnostic.
These patches remain separate from the source and require artist refinement.
"""
from pathlib import Path
from math import sin, cos, pi
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'Ichiro_Chibi_HEAD_HANDS_Topology_Workspace.blend'))
source = next(o for o in bpy.context.scene.objects if o.name.startswith('ICH_CHIBI_HIGHDETAIL_SOURCE'))
bvh = BVHTree.FromPolygons([source.matrix_world @ v.co for v in source.data.vertices],
                          [tuple(p.vertices) for p in source.data.polygons])
collection = bpy.data.collections.new('30_EYELID_QUAD_PATCHES__PASS02_REVIEW')
bpy.context.scene.collection.children.link(collection)
mat = bpy.data.materials.new('Topology_Review_Turquoise')
mat.diffuse_color = (0.02, 0.8, 0.55, 1)
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = mat.diffuse_color
bsdf.inputs['Emission Color'].default_value = mat.diffuse_color
bsdf.inputs['Emission Strength'].default_value = 0.7

for name, center_y, center_z in [('A', -0.065, 0.255), ('B', 0.035, 0.274)]:
    verts, faces = [], []
    for ring in range(4):
        width = 0.019 + ring * 0.003
        height = 0.006 + ring * 0.0025
        for i in range(32):
            angle = 2*pi*i/32
            y = center_y + width*cos(angle)
            z = center_z + height*sin(angle) + 0.20*(y-center_y)
            hit = bvh.ray_cast(Vector((0.5, y, z)), Vector((-1,0,0)), 1.0)[0]
            if hit is None:
                raise RuntimeError(f'Missing projection at {name}:{ring}:{i}')
            verts.append(tuple(hit + Vector((0.0015,0,0))))
    for ring in range(3):
        for i in range(32):
            j = (i+1)%32
            faces.append((ring*32+i, ring*32+j, (ring+1)*32+j, (ring+1)*32+i))
    mesh = bpy.data.meshes.new(f'Eyelid_{name}_QuadMesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(f'EYELID_{name}__PASS02_UNAPPROVED', mesh)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    obj.show_wire = True
    obj.show_all_edges = True
    obj['status'] = 'Initial projected patch; requires landmark and depth refinement'
    obj['topology'] = '4 rings of 32 vertices; 96 quads; two intentional boundary loops'
    wire = obj.modifiers.new('REVIEW_WIRES__disable_for_editing', 'WIREFRAME')
    wire.thickness = 0.00045
    wire.use_replace = True
    wire.show_viewport = False
    bm = bmesh.new(); bm.from_mesh(mesh)
    print(obj.name, 'vertices', len(bm.verts), 'quads', len(bm.faces),
          'boundary_edges', sum(e.is_boundary for e in bm.edges),
          'overconnected_edges', sum(len(e.link_faces)>2 for e in bm.edges))
    bm.free()

output = ROOT / 'Ichiro_Chibi_Eyelid_Topology_Pass02.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(output))
# Render in-memory only, preserving the editable saved scene.
DIAGNOSTIC_PREFIX = 'eyelid_pass02'
SHOW_EYE_GUIDES = False
exec(compile((ROOT/'tools'/'render_facial_pass01.py').read_text(encoding='utf-8'),
             str(ROOT/'tools'/'render_facial_pass01.py'), 'exec'))
