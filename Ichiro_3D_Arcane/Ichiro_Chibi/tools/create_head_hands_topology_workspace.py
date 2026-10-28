"""Create a lightweight linked Blender workspace for the manual topology pass.

The high-detail source remains external and read-only.  This file deliberately
contains no automatic remesh or generated replacement geometry: it is the safe
place to build the final facial and hand topology by hand.
"""
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Ichiro_Chibi_HEAD_HANDS_Topology_Workspace.blend"
SOURCE = "//Ichiro_Chibi_HighDetail_Working.blend"
REFS = ROOT / "references"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
scene = bpy.context.scene
scene["production_status"] = "MANUAL_TOPOLOGY_PASS01 — not final, not rigged"
scene["source_policy"] = "Linked high detail is visual target only; never remesh or edit it."
scene["final_contract"] = "One final mesh object; eyes/mouth/digits remain riggable topology."

source_col = bpy.data.collections.new("00_HIGHDETAIL_TARGET__READ_ONLY")
topo_col = bpy.data.collections.new("10_HEAD_HANDS_TOPOLOGY_PASS01")
refs_col = bpy.data.collections.new("90_REFERENCE_IMAGES__ALL_SIX")
scene.collection.children.link(source_col)
scene.collection.children.link(topo_col)
scene.collection.children.link(refs_col)

# Link, rather than append, to guarantee the visual source cannot be changed
# accidentally in this workspace.
with bpy.data.libraries.load(SOURCE, link=True) as (data_from, data_to):
    data_to.objects = [name for name in data_from.objects if name.startswith("ICH_CHIBI_HIGHDETAIL_SOURCE")]
for obj in data_to.objects:
    if obj is None:
        continue
    source_col.objects.link(obj)
    obj.hide_select = True
    obj["role"] = "READ_ONLY_HIGH_DETAIL_PROJECTION_TARGET"

def marker(name, label, location):
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = 'SINGLE_ARROW'
    empty.empty_display_size = 0.12
    empty.location = location
    empty["role"] = label
    empty["instruction"] = "Start topology manually here; this marker is not geometry."
    topo_col.objects.link(empty)

marker("HEAD_TOPOLOGY__START_MANUALLY", "Face loops: eyes, lids, mouth cavity, jaw; front faces +X", (0.27, 0.0, 0.30))
marker("HAND_L_TOPOLOGY__START_MANUALLY", "Palm plus five articulated fingers", (0.02, -0.28, -0.10))
marker("HAND_R_TOPOLOGY__START_MANUALLY", "Palm plus five articulated fingers", (0.02, 0.28, -0.10))

# Make every supplied reference discoverable in the scene.  Image empties are
# kept outside the working origin so they do not obscure the character.
for index, filename in enumerate((
    "ichiro_chibi_front.png", "ichiro_chibi_back.png", "ichiro_chibi_left.png",
    "ichiro_chibi_right.png", "ichiro_chibi_8view_turnaround.png",
    "ichiro_chibi_kimi_pipeline_board.png",
)):
    path = REFS / filename
    image = bpy.data.images.load(str(path), check_existing=True)
    image.filepath = bpy.path.relpath(str(path))
    ref = bpy.data.objects.new(f"REF_{index + 1:02d}_{path.stem}", None)
    ref.empty_display_type = 'IMAGE'
    ref.data = image
    ref.empty_display_size = 0.55 if index < 4 else 0.8
    ref.location = (1.4 + (index % 2) * 0.9, 0.0, 0.6 - (index // 2) * 0.75)
    ref["authority"] = "CANONICAL_REFERENCE"
    refs_col.objects.link(ref)

# Artist-facing convention notes live in the blend as custom properties rather
# than disposable overlays.
topo_col["face_gate"] = "3–4 lid loops, 5–7 mouth rings, mouth cavity, eyes, teeth and tongue."
topo_col["hand_gate"] = "Five readable digits per hand, three flex zones per digit, open finger gaps."
topo_col["validation_gate"] = "Clay + wireframe in all 8 angles; audit non-manifold/open/loose before body merge."

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.render.resolution_percentage = 100
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
print(f"Created {OUT}")
