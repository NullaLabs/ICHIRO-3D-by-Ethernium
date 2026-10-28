"""Draw affine-projected canonical landmarks on the source facial render."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "FACE_REGISTRATION_PROBE_V02.json"
SOURCE = ROOT / "renders" / "skin_review_source.png"
OUTPUT = ROOT / "renders" / "face_registration_probe_v02.png"
report = json.loads(REPORT.read_text(encoding="utf-8"))
image = Image.open(SOURCE).convert("RGBA")
canvas = Image.new("RGBA", (image.width + 260, image.height), (28, 30, 36, 255))
canvas.alpha_composite(image, (0, 0))
overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)
font = ImageFont.load_default(size=11)
colors = {"skin_candidate_requires_art_review": (80, 255, 140, 255),
          "missing_skin_candidate": (255, 70, 70, 255),
          "candidate_occluded_by_front_surface": (255, 180, 50, 255),
          "missing_source_surface": (255, 60, 220, 255),
          "outside_source_render": (255, 60, 220, 255)}
for item in report["projected_landmarks"]:
    x, y = map(round, item["source_render_px"])
    color = colors[item["status"]]
    draw.ellipse((x-4, y-4, x+4, y+4), fill=color, outline=(5, 5, 5, 255), width=1)
    draw.text((x+6, y-8), item["id"], fill=color, font=font,
              stroke_width=1, stroke_fill=(0, 0, 0, 230))
legend = ImageDraw.Draw(canvas)
legend.text((image.width+10, 12), "AFFINE TRANSFER PROBE", fill=(255,235,130,255), font=font)
legend.text((image.width+10, 34), f"RMS {report['registration_rms_px']:.1f}px / eye spacing {100*report['registration_rms_over_source_eye_spacing']:.1f}%", fill=(230,230,230,255), font=font)
for i, (status, color) in enumerate(colors.items()):
    y = 62 + i*34
    legend.ellipse((image.width+12, y, image.width+22, y+10), fill=color)
    legend.text((image.width+30, y), status.replace('_', ' '), fill=color, font=font)
canvas.alpha_composite(overlay, (0, 0))
canvas.convert("RGB").save(OUTPUT, quality=96)
print(f"Wrote registration diagnostic: {OUTPUT}")
