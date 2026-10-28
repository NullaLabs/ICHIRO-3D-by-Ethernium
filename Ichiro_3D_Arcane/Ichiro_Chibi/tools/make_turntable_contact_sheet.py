"""Build a labeled 4x2 review sheet from the protected-source turntable renders."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"E:\WORKSPACE\Ichiro_Chibi\renders\highdetail_turntable")
ANGLES = (0, 45, 90, 135, 180, 225, 270, 315)
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
              f"ICH_CHIBI_HIGHDETAIL / {angle:03d} deg", fill=(230, 236, 242), font=font)

output = ROOT / "ichiro_chibi_highdetail_turntable_contact_sheet.png"
canvas.save(output, quality=95)
print(output)
