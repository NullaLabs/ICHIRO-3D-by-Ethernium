#!/usr/bin/env python3
"""Extract declared normalized subview crops and write a provenance manifest.

Requires Pillow, which is already used by the existing Ichiro reference scorer.
Source images and the character spec are read-only. An existing output folder is
never overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # No automatic install: keep the tool side-effect free.
    raise SystemExit("Pillow is required for crop extraction; install only with user approval.") from exc


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("character_spec", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    spec_path = args.character_spec.expanduser().resolve()
    output = args.out.expanduser().resolve()
    if output.exists():
        parser.error(f"Refusing to overwrite existing output folder: {output}")

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    root = spec_path.parent.resolve()
    crops = []
    for reference in spec.get("references", []):
        for subview in reference.get("subviews", []):
            source = (root / reference["path"]).resolve()
            if not source.is_relative_to(root) or not source.is_file():
                raise RuntimeError(f"Subview parent image is missing or escapes the package: {reference.get('path')}")
            expected_hash = reference.get("sha256")
            actual_hash = sha256(source)
            if actual_hash != expected_hash:
                raise RuntimeError(f"Parent image hash mismatch for {reference['id']}: {source}")
            crop = subview.get("crop_normalized_xyxy")
            if not isinstance(crop, list) or len(crop) != 4:
                raise RuntimeError(f"Invalid crop box for {subview.get('id')}")
            with Image.open(source) as image:
                image.load()
                width, height = image.size
                x0, y0, x1, y1 = (int(round(crop[0] * width)), int(round(crop[1] * height)),
                                  int(round(crop[2] * width)), int(round(crop[3] * height)))
                if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
                    raise RuntimeError(f"Crop box is out of bounds for {subview['id']}: {(x0, y0, x1, y1)}")
                image_crop = image.crop((x0, y0, x1, y1)).convert("RGBA")
                safe_id = re.sub(r"[^A-Za-z0-9_-]+", "_", subview["id"])
                safe_view = re.sub(r"[^A-Za-z0-9_-]+", "_", subview["view_label"])
                crops.append({
                    "reference_id": reference["id"],
                    "parent_path": reference["path"],
                    "parent_sha256": actual_hash,
                    "subview_id": subview["id"],
                    "view_label": subview["view_label"],
                    "authority": subview.get("authority", reference.get("authority", "unknown")),
                    "origin": subview.get("origin", reference.get("origin", "unknown")),
                    "projection": subview.get("projection", reference.get("projection", "unknown")),
                    "crop_normalized_xyxy": crop,
                    "crop_pixel_xyxy": [x0, y0, x1, y1],
                    "source_size_px": [width, height],
                    "short_side_px": min(image_crop.size),
                    "resolution_class": "view_cue_only" if min(image_crop.size) < 128 else "detail_candidate",
                    "quality_warning": "Panel crop is below 128 px on its short side; use only for coarse view continuity, not facial/retopo detail." if min(image_crop.size) < 128 else None,
                    "image": image_crop,
                    "filename": f"{safe_id}__{safe_view}.png",
                })

    if not crops:
        parser.error("No references with declared subviews were found in the spec")
    output.mkdir(parents=True)
    entries = []
    for item in crops:
        target = output / item["filename"]
        item["image"].save(target, format="PNG", optimize=False)
        entries.append({key: value for key, value in item.items() if key not in {"image", "filename"}} | {
            "output_file": target.name,
            "output_size_px": list(item["image"].size),
            "short_side_px": item["short_side_px"],
            "resolution_class": item["resolution_class"],
            "quality_warning": item["quality_warning"],
            "output_sha256": sha256(target),
            "status": "review",
        })

    manifest = {
        "schema": "ichiro-3d-suite.extracted-subviews.v0.1",
        "character_id": spec.get("character", {}).get("id"),
        "character_spec": spec_path.name,
        "character_spec_sha256": sha256(spec_path),
        "crop_algorithm": "normalized_xyxy_rounded_to_nearest_pixel",
        "source_images_modified": False,
        "canonical_approval": False,
        "subview_count": len(entries),
        "resolution_warnings": sum(entry["quality_warning"] is not None for entry in entries),
        "subviews": entries,
    }
    manifest_path = output / "subview_manifest.json"
    with manifest_path.open("w", encoding="utf-8", newline="") as stream:
        stream.write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "status": "review",
        "output_dir": str(output),
        "manifest": str(manifest_path),
        "subview_count": len(entries),
        "resolution_warnings": manifest["resolution_warnings"],
        "source_images_modified": False,
        "canonical_approval": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
