"""WF-002 experiment: texture-assisted skin candidate mask, never semantic truth.

Runs headlessly; reads source and writes a NEW review blend plus measurements.
Warm-color bounds are Ichiro-specific hypotheses. Occluded/missing hits stay
unresolved. No interpolation or invented replacement surface is performed.
"""
import bpy
import hashlib
import json
from array import array
from math import sin, cos, pi
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
source_path = ROOT / 'Ichiro_Chibi_Eyelid_Topology_Pass02.blend'
bpy.ops.wm.open_mainfile(filepath=str(source_path))
source = next(o for o in bpy.context.scene.objects if o.name.startswith('ICH_CHIBI_HIGHDETAIL_SOURCE'))
mesh = source.data
uv = mesh.uv_layers.active
image = next(n.image for n in mesh.materials[0].node_tree.nodes
             if n.type == 'TEX_IMAGE' and n.image and n.image.name.startswith('Color_'))
pixels = array('f', [0]) * (image.size[0]*image.size[1]*4)
image.pixels.foreach_get(pixels)
width, height = image.size
points = [source.matrix_world @ v.co for v in mesh.vertices]
faces, ids = [], []
for face in mesh.polygons:
    center = sum((points[i] for i in face.vertices), Vector()) / len(face.vertices)
    if not (0.18 <= center.z <= 0.37 and center.x > 0):
        continue
    coord = sum((uv.data[i].uv for i in face.loop_indices), Vector((0,0))) / len(face.loop_indices)
    px, py = int((coord.x % 1)*width), int((coord.y % 1)*height)
    offset = 4*(py*width+px)
    r,g,b = pixels[offset:offset+3]
    if r > 0.15 and r > 1.25*g and g > 1.05*b:
        faces.append(tuple(face.vertices)); ids.append(face.index)
if not faces:
    raise RuntimeError('No mask candidates; inspect texture color space and thresholds')
skin = BVHTree.FromPolygons(points, faces)
full = BVHTree.FromPolygons(points, [tuple(p.vertices) for p in mesh.polygons])
samples = []
for name, cy, cz in [('A',-.065,.255),('B',.035,.274)]:
    for ring in range(4):
        for i in range(32):
            angle=2*pi*i/32
            y=cy+(.019+.003*ring)*cos(angle)
            z=cz+(.006+.0025*ring)*sin(angle)+.20*(y-cy)
            origin, direction=Vector((.5,y,z)),Vector((-1,0,0))
            original=full.ray_cast(origin,direction,1)[0]
            hit,normal,index,distance=skin.ray_cast(origin,direction,1)
            reason = 'missing_skin_candidate' if hit is None else 'candidate_requires_art_review'
            if hit is not None and original is not None and original.x-hit.x > .01:
                reason='occluded_candidate_requires_art_review'
            samples.append(dict(patch=name, ring=ring, point=i, status=reason,
                original=list(original) if original is not None else None,
                candidate=list(hit) if hit is not None else None,
                source_polygon=ids[index] if index is not None else None))
# A visible mask object, with original UVs, allows an artist to inspect false positives.
collection=bpy.data.collections.new('WF002_SKIN_MASK__EXPERIMENT_ONLY')
bpy.context.scene.collection.children.link(collection)
remap={}; verts=[]; compact=[]
for face in faces:
    row=[]
    for index in face:
        if index not in remap: remap[index]=len(verts); verts.append(points[index])
        row.append(remap[index])
    compact.append(row)
mask=bpy.data.meshes.new('Skin_Color_Candidates')
mask.from_pydata(verts,[],compact); mask.update()
mask.materials.append(mesh.materials[0])
layer=mask.uv_layers.new(name='UVMap')
for out_face, original_id in zip(mask.polygons,ids):
    for out_loop, original_loop in zip(out_face.loop_indices,mesh.polygons[original_id].loop_indices):
        layer.data[out_loop].uv=uv.data[original_loop].uv
obj=bpy.data.objects.new('SKIN_CANDIDATES__NOT_APPROVED',mask)
collection.objects.link(obj)
obj.hide_render=True; obj.hide_set(True)
obj['warning']='Color heuristic only; inspect false positives and missing eyelid margins. Not production geometry.'
output=ROOT/'Ichiro_Chibi_Skin_Projection_Experiment.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(output))
report=dict(schema='ethernium.skin-projection-probe/0.1',
    script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    input_sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(),
    mask_faces=len(faces), mask_vertices=len(verts), samples=samples,
    counts={s:sum(p['status']==s for p in samples) for s in sorted(set(p['status'] for p in samples))},
    production_approved=False, thresholds=dict(x_min=0,z_range=[.18,.37],r_min=.15,r_over_g=1.25,g_over_b=1.05),
    limitations=['Texture color is not semantic segmentation','UV centroid samples only',
                 'No automatic skin completion','No anatomical landmark correction'])
(ROOT/'docs'/'SKIN_PROJECTION_PROBE.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('MASK',len(faces),'PROBE',report['counts'],'SAVED',output)
