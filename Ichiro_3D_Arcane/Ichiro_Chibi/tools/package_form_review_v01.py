"""Assemble existing diagnostic renders; never generate or retouch reference art."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
from PIL import Image, ImageDraw, ImageOps

root = Path(__file__).resolve().parents[1]
run = Path(sys.argv[1]).resolve()
out = root / 'renders' / 'form_review_v01'
out.mkdir(parents=True, exist_ok=True)

def board(items, columns, tile, name):
    width, height = tile
    rows = (len(items) + columns - 1) // columns
    result = Image.new('RGB', (columns * width, rows * height), '#20242b')
    draw = ImageDraw.Draw(result)
    for index, (path, label) in enumerate(items):
        x, y = (index % columns) * width, (index // columns) * height
        with Image.open(path) as original:
            picture = ImageOps.contain(original.convert('RGB'), (width - 12, height - 32))
        result.paste(picture, (x + (width - picture.width)//2, y + 28))
        draw.text((x + 10, y + 8), label, fill='white')
    result.save(out / name)

board([(run / (state + '_face_' + view + '.png'), state.upper() + ' / ' + view)
       for view in ['front', 'left', 'right'] for state in ['before', 'after']],
      2, (512, 540), 'nose_before_after.png')
board([(run / ('after_full_%03d.png' % a), 'Candidate / azimuth %03d' % a)
       for a in range(0, 360, 45)], 4, (384, 410), 'candidate_eight_views.png')
refs = root / 'references'
board([(refs / ('ichiro_chibi_' + name + '.png'), name)
       for name in ['front', 'left', 'back', 'right', '8view_turnaround', 'kimi_pipeline_board']],
      3, (384, 496), 'all_six_reference_images.png')

for path in run.glob('*.png'):
    shutil.copy2(path, out / path.name)
def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
manifest = {
    'status': 'review hypothesis; not canon-approved or rig-ready',
    'source_workspace_sha256': sha(root / 'Ichiro_Chibi_HEAD_HANDS_Topology_Workspace.blend'),
    'source_geometry_blend_sha256': sha(root / 'Ichiro_Chibi_HighDetail_Working.blend'),
    'reference_sha256': {p.name: sha(p) for p in refs.glob('*.png')},
    'render_sha256': {p.name: sha(p) for p in out.glob('*.png')},
    'correction': {'center_yz': [-0.015, 0.226], 'radii_yz': [0.034, 0.038],
                   'max_depth_reduction': 0.007, 'lateral_contraction': 0.08,
                   'x_smoothstep_gate': [0.09, 0.11]},
    'live_validation': {'basis_equals_source': True, 'vertices_changed_over_1e_9': 4001,
                        'affected_triangles': 7803, 'normal_reversals': 0,
                        'triangles_cross_norm_under_1e_12': 0,
                        'maximum_displacement': 0.006997311422677403,
                        'self_intersections': 'not tested'},
    'validation_provenance': 'Measured in live Blender MCP; fixed recorded values, not recomputed by this packaging script.',
    'camera_note': 'Fixed orthographic review cameras; reference cameras remain uncalibrated. No fidelity score claimed.'
}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
print(out)
