"""Native non-destructive Shrinkwrap experiment on inferred eye vertices only."""
import bpy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Ichiro_Chibi_Closed_Eye_Relax_Review.blend'))
obj=bpy.data.objects['LOWER_PERIOCULAR_STRIP__CLOSED_REVIEW']
target=bpy.data.objects['SKIN_CANDIDATES__NOT_APPROVED']
modifier=obj.modifiers.new('SHRINKWRAP_SKIN_REVIEW','SHRINKWRAP')
modifier.target=target
modifier.wrap_method='NEAREST_SURFACEPOINT'
modifier.wrap_mode='ON_SURFACE'
modifier.offset=.0008
modifier.vertex_group='INFERRED_DEPTH_REVIEW'
# Full weights expose the actual effect; don't disguise bad target selection.
modifier.show_in_editmode=True
with bpy.context.temp_override(object=obj,active_object=obj):
    bpy.ops.object.modifier_move_up(modifier=modifier.name)
wire=obj.modifiers.get('ReviewWire')
wire.show_viewport=False
bpy.context.view_layer.update()
evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh=evaluated.to_mesh()
distances=[(a.co-b.co).length for a,b in zip(mesh.vertices,obj.data.vertices)]
report=dict(method=modifier.wrap_method,target=target.name,vertex_group=modifier.vertex_group,
    base_vertices=len(obj.data.vertices),evaluated_vertices=len(mesh.vertices),
    max_displacement=max(distances),vertices_over_004=[i for i,d in enumerate(distances) if d>.004],
    degenerate_faces=sum(f.area<1e-10 for f in mesh.polygons),
    backwards_faces=sum(f.normal.x<=0 for f in mesh.polygons),
    applied=False,production_approved=False,
    limitations=['Skin target remains incomplete color mask','Nearest mode has no configured distance cap',
                 'No globe contact or deformation validation'])
evaluated.to_mesh_clear()
obj['shrinkwrap_status']='Experimental native modifier; target mask not anatomically approved'
(ROOT/'docs'/'SHRINKWRAP_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Ichiro_Chibi_Shrinkwrap_Review.blend'))
print('SHRINKWRAP',report)
