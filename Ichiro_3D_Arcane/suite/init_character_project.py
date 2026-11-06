#!/usr/bin/env python3
"""Create a provenance-preserving character input package using only stdlib.

Reference syntax (repeat --reference):
  view|region|authority|origin|projection|path

Example:
  python init_character_project.py --character-id ichiro-chibi --name "Ichiro Chibi" \
    --profile stylized_chibi --canon-status reference_case --output ../characters/ichiro_chibi \
    --reference "front|whole_character|primary_canon|authored_art|unknown|../Ichiro_Chibi/references/ichiro_chibi_front.png"

The command copies source images into the new package, hashes them, and does not
infer camera calibration or modify a Blender scene. Existing target directories
are never overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


SCHEMA_VERSION = "0.1.0"
SUITE_VERSION = "0.1.0"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp", ".exr"}
VIEW_LABELS = {
    "front", "front_left", "left", "left_back", "back",
    "back_right", "right", "front_right", "top", "bottom",
    "detail", "custom", "unknown",
}
REGIONS = {
    "whole_character", "head", "face", "hair", "hands", "clothing",
    "accessory", "other", "unknown",
}
AUTHORITIES = {"primary_canon", "approved_secondary", "exploration", "unknown"}
ORIGINS = {"authored_art", "photograph", "scan", "ai_generated", "render", "unknown"}
PROJECTIONS = {"orthographic", "perspective", "unknown"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_reference(value: str, index: int) -> dict:
    parts = value.split("|", 5)
    if len(parts) != 6:
        raise ValueError(
            "Each --reference needs view|region|authority|origin|projection|path"
        )
    view, region, authority, origin, projection, raw_path = parts
    for label, candidate, choices in (
        ("view", view, VIEW_LABELS),
        ("region", region, REGIONS),
        ("authority", authority, AUTHORITIES),
        ("origin", origin, ORIGINS),
        ("projection", projection, PROJECTIONS),
    ):
        if candidate not in choices:
            raise ValueError(f"Invalid {label} {candidate!r}; expected one of {sorted(choices)}")
    source = Path(raw_path).expanduser().resolve()
    if not source.is_file():
        raise ValueError(f"Reference file does not exist: {source}")
    if source.suffix.lower() not in IMAGE_SUFFIXES:
        raise ValueError(f"Unsupported image extension {source.suffix!r}: {source.name}")
    digest = sha256(source)
    safe_stem = re.sub(r"[^A-Za-z0-9_-]+", "_", source.stem).strip("_")[:64] or "image"
    stored_name = f"{index:02d}_{digest[:12]}_{safe_stem}{source.suffix.lower()}"
    return {
        "id": f"reference_{index:02d}",
        "source": source,
        "stored_name": stored_name,
        "sha256": digest,
        "view_label": view,
        "projection": projection,
        "region": region,
        "authority": authority,
        "origin": origin,
    }


def parse_subview(value: str) -> dict:
    parts = value.split("|")
    if len(parts) != 7:
        raise ValueError("Each --subview needs parent_id|id|view|x0|y0|x1|y1")
    parent_id, subview_id, view, *raw_box = parts
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,63}", subview_id):
        raise ValueError(f"Invalid subview id: {subview_id!r}")
    if view not in VIEW_LABELS:
        raise ValueError(f"Invalid subview view label: {view!r}")
    try:
        box = [float(value) for value in raw_box]
    except ValueError as exc:
        raise ValueError(f"Subview crop coordinates must be numbers: {value!r}") from exc
    x0, y0, x1, y1 = box
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        raise ValueError(f"Invalid normalized crop rectangle: {box!r}")
    return {"parent_id": parent_id, "id": subview_id, "view_label": view, "crop_normalized_xyxy": box}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--profile", choices=("stylized_chibi", "stylized_humanoid", "stylized_creature", "custom"), required=True)
    parser.add_argument("--canon-status", choices=("reference_case", "canonical", "exploration", "unreviewed"), default="unreviewed")
    parser.add_argument("--output", type=Path, required=True, help="New, not-yet-existing character package directory")
    parser.add_argument("--vram-budget-gb", type=float, default=8.0)
    parser.add_argument("--reference", action="append", required=True, help="view|region|authority|origin|projection|path")
    parser.add_argument("--subview", action="append", default=[], help="parent_id|id|view|x0|y0|x1|y1; XYXY coordinates normalized to the parent image")
    args = parser.parse_args()

    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,63}", args.character_id):
        parser.error("--character-id must be a lowercase slug (2-64 characters)")
    if args.vram_budget_gb <= 0:
        parser.error("--vram-budget-gb must be positive")

    try:
        references = [parse_reference(raw, index) for index, raw in enumerate(args.reference, start=1)]
        subviews = [parse_subview(raw) for raw in args.subview]
    except ValueError as exc:
        parser.error(str(exc))

    parent_ids = {f"reference_{index:02d}" for index in range(1, len(references) + 1)}
    if any(subview["parent_id"] not in parent_ids for subview in subviews):
        parser.error("Every --subview parent_id must name a reference in this package")
    if len({subview["id"] for subview in subviews}) != len(subviews):
        parser.error("Subview IDs must be unique")

    output = args.output.expanduser().resolve()
    if output.exists():
        parser.error(f"Refusing to overwrite existing character package: {output}")
    staged = output.with_name(output.name + ".init-staging")
    if staged.exists():
        parser.error(f"Refusing to overwrite staging directory: {staged}")

    try:
        staged.mkdir(parents=True)
        reference_dir = staged / "references"
        reference_dir.mkdir()
        spec_references = []
        for record in references:
            destination = reference_dir / record["stored_name"]
            shutil.copy2(record["source"], destination)
            if sha256(destination) != record["sha256"]:
                raise IOError(f"Hash changed while copying {record['source'].name}")
            spec_references.append({
                "id": record["id"],
                "path": f"references/{record['stored_name']}",
                "sha256": record["sha256"],
                "view_label": record["view_label"],
                "azimuth_deg": None,
                "elevation_deg": None,
                "projection": record["projection"],
                "region": record["region"],
                "authority": record["authority"],
                "origin": record["origin"],
                "confidence": None,
                "mask_path": None,
                "landmarks_path": None,
                "notes": "Source image copied byte-for-byte; camera and landmarks remain uncalibrated until reviewed.",
            })

        refs_by_id = {record["id"]: record for record in spec_references}
        for subview in subviews:
            parent = refs_by_id[subview["parent_id"]]
            parent.setdefault("subviews", []).append({
                "id": subview["id"],
                "view_label": subview["view_label"],
                "azimuth_deg": None,
                "elevation_deg": None,
                "crop_normalized_xyxy": subview["crop_normalized_xyxy"],
                "projection": parent["projection"],
                "region": parent["region"],
                "authority": parent["authority"],
                "origin": parent["origin"],
                "confidence": None,
                "notes": "Subview crop from the parent reference; its camera remains uncalibrated.",
            })

        spec = {
            "schema_version": SCHEMA_VERSION,
            "character": {
                "id": args.character_id,
                "display_name": args.name,
                "profile": args.profile,
                "canon_status": args.canon_status,
                "description": "",
                "author": "",
                "license": "",
            },
            "references": spec_references,
            "build": {
                "units": "meters",
                "forward_axis": "unknown",
                "vrm_target": "1.0",
                "memory_policy": "sequential",
                "vram_budget_gb": args.vram_budget_gb,
                "ram_budget_gb": None,
                "output_dir": "output",
                "random_seed": None,
                "blender_version": None,
            },
            "provenance": {
                "suite_version": SUITE_VERSION,
                "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "created_by": "init_character_project.py",
                "source_repositories": [],
            },
        }
        with (staged / "character_spec.json").open("w", encoding="utf-8", newline="\n") as spec_stream:
            spec_stream.write(json.dumps(spec, ensure_ascii=False, indent=2) + "\n")
        output.parent.mkdir(parents=True, exist_ok=True)
        staged.rename(output)
    except Exception:
        # Keep the uniquely named staging directory for diagnosis/recovery.
        # Do not recursively delete user data on failure.
        raise

    print(json.dumps({
        "status": "ready_for_reference_review",
        "character_spec": str(output / "character_spec.json"),
        "reference_count": len(spec_references),
        "subview_count": len(subviews),
        "vram_budget_gb": args.vram_budget_gb,
        "blender_scene_modified": False,
        "reference_hashes_verified": True,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
