"""Render approximate source-render face anchors for human review."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "references" / "source_face_landmarks_estimate_v01.json"
SOURCE = ROOT / "renders" / "skin_review_source.png"
OUTPUT = ROOT / "renders" / "source_face_landmarks_estimate_v01.png"

data = json.loads(DATA.read_text(encoding="utf-8"))
image = Image.open(SOURCE).convert("RGBA")
overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)
font = ImageFont.load_default(size=12)
colors = {"eye_screen_left_center": (255, 90, 90, 255),
          "eye_screen_right_center": (80, 230, 255, 255),
          "nose_tip": (255, 230, 70, 255),
          "chin_center": (100, 255, 130, 255)}
for name, entry in data["landmarks"].items():
    x, y = entry["point"]
    c = colors[name]
    draw.line((x-8, y, x+8, y), fill=c, width=2)
    draw.line((x, y-8, x, y+8), fill=c, width=2)
    draw.ellipse((x-3, y-3, x+3, y+3), fill=c, outline=(0, 0, 0, 255))
    draw.text((x+8, y-9), name, fill=c, font=font, stroke_width=1, stroke_fill=(0,0,0,220))
image = Image.alpha_composite(image, overlay).convert("RGB")
image.save(OUTPUT, quality=96)
print(f"Wrote approximate source landmark overlay: {OUTPUT}")
