"""Build a labeled 4x2 review sheet from the protected-source turntable renders."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1] / "renders" / "highdetail_turntable"
ANGLES = (0, 45, 90, 135, 180, 225, 270, 315)
LABELS = {
    0: "FRONT +X", 45: "FRONT 3/4 +Y", 90: "SIDE +Y", 135: "BACK 3/4 +Y",
    180: "BACK -X", 225: "BACK 3/4 -Y", 270: "SIDE -Y", 315: "FRONT 3/4 -Y",
}
CELL_W, CELL_H, LABEL_H = 512, 512, 42

canvas = Image.new("RGB", (CELL_W * 4, (CELL_H + LABEL_H) * 2), (24, 28, 33))
draw = ImageDraw.Draw(canvas)
font = ImageFont.load_default()
for i, angle in enumerate(ANGLES):
    source = ROOT / f"ichiro_chibi_high_{angle:03d}.png"
    image = Image.open(source).convert("RGB")
    image.thumbnail((CELL_W, CELL_H), Image.Resampling.LANCZOS)
    x = (i % 4) * CELL_W + (CELL_W - image.width) // 2
    y = (i // 4) * (CELL_H + LABEL_H) + (CELL_H - image.height) // 2
    canvas.paste(image, (x, y))
    draw.text(((i % 4) * CELL_W + 14, (i // 4) * (CELL_H + LABEL_H) + CELL_H + 13),
              f"ICH_CHIBI_HIGHDETAIL / {LABELS[angle]} / {angle:03d}",
              fill=(230, 236, 242), font=font)

output = ROOT / "ichiro_chibi_highdetail_turntable_contact_sheet.png"
canvas.save(output, quality=95)
print(output)
