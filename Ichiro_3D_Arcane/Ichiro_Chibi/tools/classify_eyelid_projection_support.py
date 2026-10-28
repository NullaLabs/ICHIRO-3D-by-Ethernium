"""WF-006: classify eyelid projection support before generating another patch.

Reads the high-detail source, associates each ray hit with a disconnected mesh
component and samples its UV color as weak semantic evidence. Emits JSON only.
"""
import bpy, json, hashlib, sys
from collections import Counter
from pathlib import Path
from math import sin, cos, pi
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from component_islands import audit_components, component_id_for_polygon

SOURCE=ROOT/'Ichiro_Chibi_HEAD_HANDS_Topology_Workspace.blend'
OUT=ROOT/'docs'/'EYELID_SUPPORT_CLASSIFICATION.json'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
obj=next(o for o in bpy.context.scene.objects if o.name.startswith('ICH_CHIBI_HIGHDETAIL_SOURCE'))
mesh=obj.data
component_audit=audit_components(mesh)
world=[obj.matrix_world @ v.co for v in mesh.vertices]
all_bvh=BVHTree.FromPolygons(world,[tuple(p.vertices) for p in mesh.polygons])
# UV texture labels are weak evidence only. Record material slots and sampled color.
uv=mesh.uv_layers.active
img=None
for slot in mesh.materials:
    if slot and slot.node_tree:
        img=next((n.image for n in slot.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and n.image.name.startswith('Color_')),None)
        if img: break
pixels=None
if img:
    from array import array
    pixels=array('f',[0])*(img.size[0]*img.size[1]*4)
    img.pixels.foreach_get(pixels)
samples=[]
hit_components=Counter()
skin_candidate_components=Counter()
for patch,cy,cz in [('A',-.065,.255),('B',.035,.274)]:
  for ring in range(4):
    for i in range(32):
      a=2*pi*i/32; y=cy+(.019+.003*ring)*cos(a); z=cz+(.006+.0025*ring)*sin(a)+.20*(y-cy)
      hit,n,poly_idx,dist=all_bvh.ray_cast(Vector((.5,y,z)),Vector((-1,0,0)),1)
      row={'patch':patch,'ring':ring,'sample':i,'status':'no_source_hit'}
      if hit is not None and poly_idx is not None:
        poly=mesh.polygons[poly_idx]
        component_id=component_id_for_polygon(component_audit,poly)
        component_root=component_audit[2][component_id]
        row.update(status='source_hit_unclassified',source_polygon=int(poly_idx),
                   material_index=int(poly.material_index),material=(mesh.materials[poly.material_index].name if poly.material_index<len(mesh.materials) and mesh.materials[poly.material_index] else None),
                   component_id=int(component_id),
                   component_vertex_count=int(component_audit[3][component_root]),
                   component_face_count=int(component_audit[5][component_id]),
                   hit_world=[round(float(v),7) for v in hit],normal=[round(float(v),5) for v in n],distance=float(dist))
        hit_components[int(component_id)]+=1
        if img and uv:
          coord=sum((uv.data[k].uv for k in poly.loop_indices),Vector((0,0)))/len(poly.loop_indices)
          px=int((coord.x%1)*img.size[0]); py=int((coord.y%1)*img.size[1]); off=4*(py*img.size[0]+px)
          rgb=[float(pixels[off+j]) for j in range(3)]
          row['uv_centroid_rgb']=[round(v,5) for v in rgb]
          row['color_heuristic_skin_candidate']=bool(rgb[0]>.15 and rgb[0]>1.25*rgb[1] and rgb[1]>1.05*rgb[2])
          if row['color_heuristic_skin_candidate']: skin_candidate_components[int(component_id)]+=1
      samples.append(row)
counts={}
for s in samples: counts[s['status']]=counts.get(s['status'],0)+1
candidate=sum(bool(s.get('color_heuristic_skin_candidate')) for s in samples)
component_rows=[]
for component_id in sorted(hit_components):
 root=component_audit[2][component_id]
 component_rows.append({'component_id':component_id,
     'vertex_count':int(component_audit[3][root]),
     'face_count':int(component_audit[5][component_id]),
     'ray_hit_samples':int(hit_components[component_id]),
     'skin_color_heuristic_samples':int(skin_candidate_components[component_id]),
     'bounds_local_m':[[round(float(component_audit[4][root][i]),7),round(float(component_audit[4][root][i+3]),7)] for i in range(3)]})
report={'schema':'ethernium.eyelid-support-classification/0.2','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'method':'ray hits against full high-detail source; each hit is mapped through its polygon vertex to a deterministic connected-component ID; polygon material index + UV-centroid texture evidence','component_count':len(component_audit[2]),'component_indexing':'descending vertex count, then stable root vertex index','component_hit_summary':component_rows,'counts':counts,'color_candidates':candidate,'total':len(samples),'samples':samples,'production_approved':False,'limitations':['component IDs are geometric groups, not verified anatomical labels','material labels and UV-centroid colors are proxies, not semantic surface truth','single frontal ray may select occluding hair or eyelid surface','landmark positions remain provisional','no eye globe/contact/deformation validation']}
OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print({'report':str(OUT),'counts':counts,'color_candidates':candidate,'total':len(samples),'approved':False})
