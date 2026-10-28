"""Compare locked-source projections with four canonical plates and eight turnaround views.

The score is a camera-normalized silhouette diagnostic, not an artistic approval
and not a reconstruction target. Requires the existing Pillow and NumPy stack.
"""
from pathlib import Path
import argparse
from collections import deque
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REFERENCES = {
    "front": ROOT / "references" / "ichiro_chibi_front.png",
    "back": ROOT / "references" / "ichiro_chibi_back.png",
    "left": ROOT / "references" / "ichiro_chibi_left.png",
    "right": ROOT / "references" / "ichiro_chibi_right.png",
}
TURNAROUND_SHEET = ROOT / "references" / "ichiro_chibi_8view_turnaround.png"
TURNAROUND_VIEWS = (
    ("front", 0),
    ("front_left", 1),
    ("left", 2),
    ("left_back", 3),
    ("back", 4),
    ("back_right", 5),
    ("right", 6),
    ("front_right", 7),
)


def _largest_components(mask, minimum_area=8):
    """Keep coherent foreground components and discard any touching the frame."""
    h, w = mask.shape
    seen = np.zeros((h, w), dtype=bool)
    components = []
    edge_dropped_area = 0
    for y0, x0 in zip(*np.where(mask & ~seen)):
        if seen[y0, x0]:
            continue
        seen[y0, x0] = True
        queue = deque([(int(y0), int(x0))])
        pixels = []
        touches_edge = False
        while queue:
            y, x = queue.popleft()
            pixels.append((y, x))
            touches_edge |= y == 0 or x == 0 or y == h - 1 or x == w - 1
            for ny in range(max(0, y - 1), min(h, y + 2)):
                for nx in range(max(0, x - 1), min(w, x + 2)):
                    if mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        queue.append((ny, nx))
        if touches_edge:
            edge_dropped_area += len(pixels)
        elif len(pixels) >= minimum_area:
            components.append(pixels)

    if not components:
        raise RuntimeError("Foreground segmentation found no component away from image border")
    output = np.zeros((h, w), dtype=bool)
    for pixels in components:
        ys, xs = zip(*pixels)
        output[ys, xs] = True
    return output, {
        "kept_component_count": len(components),
        "kept_component_areas_px": sorted((len(c) for c in components), reverse=True),
        "discarded_border_component_area_px": edge_dropped_area,
        "minimum_kept_component_area_px": minimum_area,
    }


def reference_foreground_mask(source, threshold=24):
    image = source.convert("RGB") if isinstance(source, Image.Image) else Image.open(source).convert("RGB")
    array = np.asarray(image, dtype=np.float32)
    h, w, _ = array.shape
    # The studio backdrop is a smooth vertical gradient with a floor transition.
    # Estimate it from narrow left/right border strips, row by row, then blend
    # across X. Ignore the outer 2 px because the supplied plates have a dark
    # one-pixel frame that is not part of the character.
    strip = max(12, min(h, w) // 24)
    left = np.median(array[:, 2:2 + strip, :], axis=1)
    right = np.median(array[:, w - strip - 2:w - 2, :], axis=1)
    radius = 3
    kernel = 2 * radius + 1

    def smooth_rows(profile):
        padded = np.pad(profile, ((radius, radius), (0, 0)), mode="edge")
        windows = np.stack([padded[i:i + h] for i in range(kernel)], axis=0)
        return np.median(windows, axis=0)

    left = smooth_rows(left)
    right = smooth_rows(right)
    blend = np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :, None]
    background = left[:, None, :] * (1.0 - blend) + right[:, None, :] * blend
    residual = np.linalg.norm(array - background, axis=2)
    initial = residual > threshold
    # The source sheets include a dark border that varies sharply from the
    # smooth studio background, so it must never seed the foreground mask.
    initial[:2, :] = False
    initial[-2:, :] = False
    initial[:, :2] = False
    initial[:, -2:] = False
    binary, component_info = _largest_components(initial)
    ys, xs = np.where(binary)
    if not len(xs):
        raise RuntimeError(f"No foreground found in {path}")
    bbox = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    diagnostics = {
        "background_model": "smoothed side-border row medians, linearly blended across width",
        "foreground_threshold_rgb_residual": threshold,
        "initial_foreground_area_px": int(initial.sum()),
        "foreground_area_px": int(binary.sum()),
        "foreground_bbox_px": list(bbox),
        **component_info,
    }
    return image, binary, bbox, diagnostics


def projected_mask(path):
    image = Image.open(path).convert("L")
    binary = np.asarray(image) > 127
    ys, xs = np.where(binary)
    if not len(xs):
        raise RuntimeError(f"No projected foreground found in {path}")
    return image, binary, (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def align_candidate(candidate, source_bbox, canvas_size, target_bbox):
    cw, ch = canvas_size
    tx0, ty0, tx1, ty1 = target_bbox
    sx0, sy0, sx1, sy1 = source_bbox
    source_height = sy1 - sy0
    target_height = ty1 - ty0
    if source_height <= 0 or target_height <= 0:
        raise RuntimeError("Invalid silhouette height")
    scale = target_height / source_height
    target_cx = (tx0 + tx1 - 1) * 0.5
    target_cy = (ty0 + ty1 - 1) * 0.5
    source_cx = (sx0 + sx1 - 1) * 0.5
    source_cy = (sy0 + sy1 - 1) * 0.5
    ys, xs = np.where(candidate)
    x2 = np.rint(target_cx + (xs - source_cx) * scale).astype(np.int32)
    y2 = np.rint(target_cy + (ys - source_cy) * scale).astype(np.int32)
    inside = (x2 >= 0) & (x2 < cw) & (y2 >= 0) & (y2 < ch)
    output = np.zeros((ch, cw), dtype=bool)
    output[y2[inside], x2[inside]] = True
    return output, scale


def score_pair(reference, candidate):
    intersection = int(np.logical_and(reference, candidate).sum())
    union = int(np.logical_or(reference, candidate).sum())
    ref_area = int(reference.sum())
    candidate_area = int(candidate.sum())
    iou = intersection / union if union else 0.0
    dice = 2 * intersection / (ref_area + candidate_area) if ref_area + candidate_area else 0.0
    return {"intersection_px": intersection, "union_px": union,
            "reference_area_px": ref_area, "candidate_area_px": candidate_area,
            "iou": iou, "dice": dice}


def write_overlay(path, reference, candidate):
    out = np.zeros((*reference.shape, 3), dtype=np.uint8)
    out[reference] = (255, 64, 64)
    out[candidate] = (32, 192, 255)
    out[reference & candidate] = (245, 245, 245)
    Image.fromarray(out, "RGB").save(path)


def crop_turnaround_panels(sheet):
    """Crop the eight figures from the fixed 4x2 reference contact sheet."""
    width, height = sheet.size
    if width % 4 or height % 2:
        raise RuntimeError(f"Expected a 4x2 turnaround sheet, got {width}x{height}")
    cell_w, cell_h = width // 4, height // 2
    # Inset the printed panel separators and omit caption rows beneath each figure.
    x_inset = max(1, round(cell_w * 0.02))
    y_inset = max(1, round(cell_h * 0.02))
    crop_bottom = min(cell_h - 1, round(cell_h * 0.70))
    crops = []
    for panel in range(8):
        row, col = divmod(panel, 4)
        x0 = col * cell_w + x_inset
        x1 = (col + 1) * cell_w - x_inset
        y0 = row * cell_h + y_inset
        y1 = row * cell_h + crop_bottom
        crops.append(sheet.crop((x0, y0, x1, y1)))
    return crops, {
        "layout": "4 columns x 2 rows",
        "panel_size_px": [cell_w, cell_h],
        "crop_inset_px": [x_inset, y_inset],
        "crop_bottom_row_px_relative_to_panel": crop_bottom,
        "caption_area_excluded": True,
    }


def compare_view(view, reference_image, reference_mask, reference_bbox,
                 segmentation, candidate_path, output_dir, output_stem):
    _, source_mask, source_bbox = projected_mask(candidate_path)
    aligned, scale = align_candidate(source_mask, source_bbox,
                                     reference_image.size, reference_bbox)
    metrics = score_pair(reference_mask, aligned)
    metrics.update({
        "reference_bbox_px": list(reference_bbox),
        "reference_segmentation": segmentation,
        "source_render_bbox_px": list(source_bbox),
        "reference_bbox_aspect_width_over_height": (
            (reference_bbox[2] - reference_bbox[0]) / (reference_bbox[3] - reference_bbox[1])
        ),
        "render_bbox_aspect_width_over_height": (
            (source_bbox[2] - source_bbox[0]) / (source_bbox[3] - source_bbox[1])
        ),
        "height_normalization_scale": scale,
        "alignment": "bbox center + height only; width is never scaled independently",
    })
    overlay_path = output_dir / f"overlay_{output_stem}.png"
    mask_path = output_dir / f"reference_mask_{output_stem}.png"
    write_overlay(overlay_path, reference_mask, aligned)
    Image.fromarray(reference_mask.astype(np.uint8) * 255, "L").save(mask_path)
    metrics["overlay"] = overlay_path.name
    metrics["reference_mask"] = mask_path.name
    return metrics, overlay_path


def write_labeled_sheet(path, entries, columns, cell_size, label_height=24):
    cell_w, cell_h = cell_size
    rows = (len(entries) + columns - 1) // columns
    sheet = Image.new("RGB", (cell_w * columns, (cell_h + label_height) * rows), (28, 30, 34))
    draw = ImageDraw.Draw(sheet)
    for i, (label, image_path, score) in enumerate(entries):
        image = Image.open(image_path).convert("RGB")
        image = image.resize((cell_w, cell_h), Image.Resampling.NEAREST)
        x, y = (i % columns) * cell_w, (i // columns) * (cell_h + label_height)
        sheet.paste(image, (x, y))
        draw.text((x + 6, y + cell_h + 6), f"{label}  IoU {score:.3f}",
                  fill=(240, 240, 240), font=ImageFont.load_default())
    sheet.save(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--renders", type=Path, default=ROOT / "renders" / "reference_fit_v02_cpu" / "projections")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "renders" / "reference_fit_v02_cpu" / "comparison")
    parser.add_argument("--turnaround-sheet", type=Path, default=TURNAROUND_SHEET)
    parser.add_argument("--threshold", type=float, default=24)
    args = parser.parse_args()
    args.renders = args.renders.resolve()
    args.output_dir = args.output_dir.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    canonical_results = {}
    canonical_overlays = []
    for view, reference_path in REFERENCES.items():
        candidate_path = args.renders / f"source_{view}.pgm"
        if not candidate_path.is_file():
            raise FileNotFoundError(candidate_path)
        ref_image, ref_mask, ref_bbox, segmentation = reference_foreground_mask(reference_path, args.threshold)
        overlay_stem = f"ortho_{view}"
        metrics, overlay_path = compare_view(view, ref_image, ref_mask, ref_bbox,
                                             segmentation, candidate_path,
                                             args.output_dir, overlay_stem)
        metrics.update({"reference": str(reference_path.relative_to(ROOT)),
                        "source_render": str(candidate_path.relative_to(ROOT))})
        canonical_results[view] = metrics
        canonical_overlays.append((view, overlay_path, metrics["iou"]))

    turnaround_results = {}
    turnaround_overlays = []
    crop_dir = args.output_dir / "turnaround_reference_crops"
    crop_dir.mkdir(parents=True, exist_ok=True)
    turnaround_sheet = Image.open(args.turnaround_sheet).convert("RGB")
    crops, crop_metadata = crop_turnaround_panels(turnaround_sheet)
    for view, panel_index in TURNAROUND_VIEWS:
        candidate_path = args.renders / f"source_{view}.pgm"
        if not candidate_path.is_file():
            raise FileNotFoundError(candidate_path)
        crop_path = crop_dir / f"reference_{view}.png"
        crops[panel_index].save(crop_path)
        ref_image, ref_mask, ref_bbox, segmentation = reference_foreground_mask(crops[panel_index], args.threshold)
        overlay_stem = f"turnaround_{view}"
        metrics, overlay_path = compare_view(view, ref_image, ref_mask, ref_bbox,
                                             segmentation, candidate_path,
                                             args.output_dir, overlay_stem)
        metrics.update({"source_sheet": str(args.turnaround_sheet.resolve().relative_to(ROOT)),
                        "source_panel_index_zero_based": panel_index,
                        "reference_crop": str(crop_path.relative_to(ROOT)),
                        "source_render": str(candidate_path.relative_to(ROOT))})
        turnaround_results[view] = metrics
        turnaround_overlays.append((view, overlay_path, metrics["iou"]))

    report = {
        "schema": "ethernium.reference-fit-silhouette-score.v2",
        "purpose": "camera-normalized diagnostic across the four large orthographic references and eight turnaround panels; not canon approval",
        "reference_mask_threshold_rgb_residual": args.threshold,
        "projection_mask_threshold": 127,
        "canonical_four_view_metrics": canonical_results,
        "turnaround_eight_view_metrics": turnaround_results,
        "turnaround_crop_method": crop_metadata,
        "interpretation": (
            "IoU compares silhouettes after matching each image's figure height and "
            "bbox center. It cannot recover depth, anatomy, concavities, expression, "
            "or topology, and can be biased by perspective, shadows, pose, low panel "
            "resolution, or masks. The four separate ortho plates are the primary "
            "silhouette constraints; turnaround panel scores are secondary rotation "
            "consistency evidence."
        ),
    }
    report_path = args.output_dir / "reference_fit_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    canonical_sheet_path = args.output_dir / "reference_fit_4view_contact_sheet.png"
    write_labeled_sheet(canonical_sheet_path, canonical_overlays, 2, (384, 472), label_height=24)
    turnaround_sheet_path = args.output_dir / "reference_fit_8view_contact_sheet.png"
    write_labeled_sheet(turnaround_sheet_path, turnaround_overlays, 4, (180, 172), label_height=22)
    print(json.dumps({
        "report": str(report_path),
        "four_view_contact_sheet": str(canonical_sheet_path),
        "eight_view_contact_sheet": str(turnaround_sheet_path),
        "four_view_iou": {k: round(v["iou"], 4) for k, v in canonical_results.items()},
        "eight_view_iou": {k: round(v["iou"], 4) for k, v in turnaround_results.items()},
    }, indent=2))


if __name__ == "__main__":
    main()
