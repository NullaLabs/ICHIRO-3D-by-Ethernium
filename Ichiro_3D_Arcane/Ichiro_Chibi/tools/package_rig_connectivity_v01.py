"""Measure fixed-camera preservation and assemble evidence from actual renders."""
from pathlib import Path
import json
import shutil
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageOps

root = Path(__file__).resolve().parents[1]
run = Path(sys.argv[1]).resolve()
out = root / 'renders' / 'rig_connectivity_v01'
out.mkdir(parents=True, exist_ok=True)
metrics = []
for angle in range(0, 360, 45):
    source = np.array(Image.open(run / f'source_{angle:03d}.png').convert('RGBA'))
    repaired = np.array(Image.open(run / f'repaired_{angle:03d}.png').convert('RGBA'))
    assert source.shape == repaired.shape
    a, b = source[:, :, 3] > 127, repaired[:, :, 3] > 127
    intersection, union = a & b, a | b
    assert union.any() and intersection.any(), 'Empty comparison'
    difference = np.abs(source[:, :, :3].astype(float) - repaired[:, :, :3])[intersection]
    metrics.append({
        'angle': angle, 'resolution': list(source.shape[:2]),
        'silhouette_iou': float(intersection.sum() / union.sum()),
        'silhouette_different_pixels': int((a ^ b).sum()),
        'foreground_rgb_mean_absolute_difference_0_255': float(difference.mean()),
        'foreground_rgb_max_absolute_difference_0_255': float(difference.max()),
        'foreground_pixels_any_channel_difference_over_10_fraction': float((difference.max(axis=1) > 10).mean()),
    })
report = {'views': metrics, 'alpha_threshold': 127,
          'limitation': 'Raster agreement at 512px is not zero geometric error, full Hausdorff distance, or self-intersection certification.'}
(out / 'appearance_comparison.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')

def board(items, columns, tile, filename):
    w, h = tile
    result = Image.new('RGB', (columns*w, ((len(items)+columns-1)//columns)*h), '#292d34')
    draw = ImageDraw.Draw(result)
    for i, (path, label) in enumerate(items):
        x, y = (i % columns)*w, (i // columns)*h
        with Image.open(path) as original:
            picture = ImageOps.contain(original.convert('RGBA'), (w-12, h-30))
        result.paste(picture, (x+(w-picture.width)//2, y+26), picture.getchannel('A'))
        draw.text((x+8, y+7), label, fill='white')
    result.save(out / filename)

board([(run/f'{state}_face.png', label) for state,label in [('source','Original'),('repaired','Connectivity repaired / original design')]],
      2, (512, 540), 'original_vs_repaired_face.png')
board([(run/f'repaired_{a:03d}.png', f'Repaired / {a:03d} degrees') for a in range(0,360,45)],
      4, (320, 350), 'repaired_eight_views.png')
for path in run.glob('*.png'):
    shutil.copy2(path, out / path.name)
if (run/'geometry_audit.json').exists():
    shutil.copy2(run/'geometry_audit.json', out/'geometry_audit.json')
print(json.dumps(report, indent=2))
