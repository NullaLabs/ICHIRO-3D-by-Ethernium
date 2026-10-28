"""Render separately labeled eye margins, brows, and occlusion for canonical v03."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "references" / "canonical_face_landmarks_v03.json"
SOURCE = ROOT / "references" / "ichiro_chibi_front.png"
OUTPUT = ROOT / "renders" / "canonical_eye_brow_regions_v03.png"
data = json.loads(DATA.read_text(encoding="utf-8"))
image = Image.open(SOURCE).convert("RGBA")
canvas = Image.new("RGBA", (image.width + 250, image.height), (28, 30, 36, 255))
canvas.alpha_composite(image, (0, 0))
overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)
font = ImageFont.load_default(size=11)
eye_colors = {"screen_left_partial": (255, 90, 100, 255), "screen_right": (80, 230, 255, 255)}
brow = (255, 210, 70, 255)
for name, points in data["eye_contours"].items():
    color = eye_colors[name]
    visibility = data["eye_contour_visibility"][name]
    for i in range(len(points)):
        j = (i+1) % len(points)
        if visibility[i] == "visible" and visibility[j] == "visible":
            draw.line((tuple(points[i]), tuple(points[j])), fill=color, width=2)
    for p, state in zip(points, visibility):
        x,y=p
        if state == "visible":
            draw.ellipse((x-2,y-2,x+2,y+2), fill=color, outline=(0,0,0,255))
        else:
            draw.line((x-3,y-3,x+3,y+3), fill=(255,70,70,255), width=2)
            draw.line((x-3,y+3,x+3,y-3), fill=(255,70,70,255), width=2)
for points in data["brow_contours"].values():
    draw.line([tuple(p) for p in points + [points[0]]], fill=brow, width=2)
legend = ImageDraw.Draw(canvas)
legend.text((image.width+10,12), "CANONICAL EYE / BROW V03", fill=(255,235,130,255), font=font)
legend.line((image.width+12,38,image.width+32,38), fill=(80,230,255,255), width=2)
legend.text((image.width+40,32), "visible eye margin", fill=(80,230,255,255), font=font)
legend.line((image.width+12,62,image.width+32,62), fill=brow, width=2)
legend.text((image.width+40,56), "brow contour", fill=brow, font=font)
legend.line((image.width+12,86,image.width+32,86), fill=(255,90,100,255), width=2)
legend.text((image.width+40,80), "left eye, visible partial", fill=(255,120,120,255), font=font)
legend.line((image.width+12,110,image.width+32,110), fill=(255,70,70,255), width=2)
legend.text((image.width+40,104), "occluded / uncertain points", fill=(255,120,120,255), font=font)
legend.text((image.width+10,145), "Upper right eye point moved", fill=(220,220,220,255), font=font)
legend.text((image.width+10,161), "off the brow and onto the", fill=(220,220,220,255), font=font)
legend.text((image.width+10,177), "visible eyeliner/eye margin.", fill=(220,220,220,255), font=font)
legend.text((image.width+10,211), "All marks are 2D review", fill=(190,190,190,255), font=font)
legend.text((image.width+10,227), "estimates, not 3D anatomy.", fill=(190,190,190,255), font=font)
canvas.alpha_composite(overlay, (0,0))
canvas.convert("RGB").save(OUTPUT, quality=96)
print(f"Wrote region-separated review: {OUTPUT}")
