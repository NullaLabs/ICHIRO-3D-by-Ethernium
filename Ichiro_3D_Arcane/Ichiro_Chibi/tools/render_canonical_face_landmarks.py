"""Render a review overlay for manually estimated canonical 2D face landmarks."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "references" / "canonical_face_landmarks_v01.json"
SOURCE = ROOT / "references" / "ichiro_chibi_front.png"
OUTPUT = ROOT / "renders" / "canonical_face_landmarks_v01.png"

data = json.loads(DATA.read_text(encoding="utf-8"))
image = Image.open(SOURCE).convert("RGBA")
canvas = Image.new("RGBA", (image.width + 230, image.height), (28, 30, 36, 255))
canvas.alpha_composite(image, (0, 0))
overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)
font = ImageFont.load_default(size=10)
palette = {"eye_screen_left": (255, 80, 80, 240), "eye_screen_right": (80, 230, 255, 240),
           "nose": (255, 230, 60, 240), "mouth": (255, 80, 220, 240), "jaw": (100, 255, 130, 240)}

for key, points in data["eye_contours"].items():
    color = palette["eye_screen_left" if key.startswith("screen_left") else "eye_screen_right"]
    draw.line([tuple(p) for p in points + [points[0]]], fill=color, width=1)
legend = ImageDraw.Draw(canvas)
legend.text((image.width + 10, 10), "REVIEW ESTIMATES — NOT APPROVED", fill=(255, 235, 130, 255), font=font)
for index, item in enumerate(data["landmarks"], 1):
    x, y = item["point"]
    color = palette[item["region"]]
    radius = 2
    draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color, outline=(15, 15, 18, 255))
    draw.text((x+3, y-7), str(index), fill=color, font=font, stroke_width=1, stroke_fill=(10, 10, 12, 210))
    legend.text((image.width + 10, 28 + 26*(index-1)),
                f"{index:02d} {item['id']}  c={item['confidence']:.2f} {item['visibility']}",
                fill=color, font=font)

canvas.alpha_composite(overlay, (0, 0))
canvas.convert("RGB").save(OUTPUT, quality=96)
print(f"Wrote review-only overlay: {OUTPUT}")
