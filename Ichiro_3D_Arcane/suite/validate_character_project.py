#!/usr/bin/env python3
"""Validate character-spec structure and reference-file hashes (Python stdlib)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


SCHEMA_VERSION = "0.1.0"
ENUMS = {
    "profile": {"stylized_chibi", "stylized_humanoid", "stylized_creature", "custom"},
    "canon_status": {"reference_case", "canonical", "exploration", "unreviewed"},
    "view_label": {"front", "front_left", "left", "left_back", "back", "back_right", "right", "front_right", "top", "bottom", "detail", "custom", "unknown"},
    "projection": {"orthographic", "perspective", "unknown"},
    "region": {"whole_character", "head", "face", "hair", "hands", "clothing", "accessory", "other", "unknown"},
    "authority": {"primary_canon", "approved_secondary", "exploration", "unknown"},
    "origin": {"authored_art", "photograph", "scan", "ai_generated", "render", "unknown"},
    "vrm_target": {"1.0", "0.x", "both"},
    "memory_policy": {"sequential", "adaptive", "unbounded"},
}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("character_spec", type=Path)
    args = parser.parse_args()
    spec_path = args.character_spec.expanduser().resolve()
    errors: list[str] = []
    review_flags: list[str] = []
    checked = []

    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"status": "failed", "errors": [f"Cannot read JSON: {exc}"]}, indent=2))
        return 2

    if not isinstance(spec, dict):
        errors.append("Root JSON value must be an object")
        spec = {}
    if spec.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")

    character = spec.get("character")
    build = spec.get("build")
    refs = spec.get("references")
    if not isinstance(character, dict):
        errors.append("character must be an object")
        character = {}
    if not isinstance(build, dict):
        errors.append("build must be an object")
        build = {}
    if not isinstance(refs, list) or not refs:
        errors.append("references must be a non-empty array")
        refs = []

    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,63}", str(character.get("id", ""))):
        errors.append("character.id must be a lowercase slug, 2-64 characters")
    if not isinstance(character.get("display_name"), str) or not character["display_name"].strip():
        errors.append("character.display_name is required")
    for field, enum_name in (("profile", "profile"), ("canon_status", "canon_status")):
        if character.get(field) not in ENUMS[enum_name]:
            errors.append(f"character.{field} has invalid value {character.get(field)!r}")
    if build.get("units") != "meters":
        errors.append("build.units must be meters")
    for field in ("vrm_target", "memory_policy"):
        if build.get(field) not in ENUMS[field]:
            errors.append(f"build.{field} has invalid value {build.get(field)!r}")
    if not isinstance(build.get("output_dir"), str) or not build["output_dir"].strip():
        errors.append("build.output_dir is required")

    seen_ids = set()
    seen_subview_ids = set()
    project_root = spec_path.parent.resolve()
    for index, ref in enumerate(refs, start=1):
        label = f"references[{index - 1}]"
        if not isinstance(ref, dict):
            errors.append(f"{label} must be an object")
            continue
        ref_id = ref.get("id")
        if not isinstance(ref_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,63}", ref_id):
            errors.append(f"{label}.id is invalid")
        elif ref_id in seen_ids:
            errors.append(f"Duplicate reference id: {ref_id}")
        seen_ids.add(ref_id)
        for field in ("view_label", "projection", "region", "authority", "origin"):
            if ref.get(field) not in ENUMS[field]:
                errors.append(f"{label}.{field} has invalid value {ref.get(field)!r}")
        raw_path = ref.get("path")
        digest = ref.get("sha256")
        if not isinstance(raw_path, str) or not raw_path:
            errors.append(f"{label}.path is required")
            continue
        target = (project_root / raw_path).resolve()
        if not target.is_relative_to(project_root):
            errors.append(f"{label}.path escapes the character project")
            continue
        if not target.is_file():
            errors.append(f"{label} file is missing: {raw_path}")
            continue
        actual = file_hash(target)
        hash_ok = isinstance(digest, str) and re.fullmatch(r"[a-f0-9]{64}", digest) and actual == digest
        checked.append({"id": ref_id, "path": raw_path, "sha256_match": bool(hash_ok)})
        if not hash_ok:
            errors.append(f"{label} SHA-256 is missing, malformed or mismatched")
        for field in ("view_label", "projection", "region", "authority", "origin"):
            if ref.get(field) in {"unknown", "custom"}:
                review_flags.append(f"{ref_id}: {field} requires human review")
        subviews = ref.get("subviews", [])
        if not isinstance(subviews, list):
            errors.append(f"{label}.subviews must be an array")
            continue
        for sub_index, subview in enumerate(subviews, start=1):
            sub_label = f"{label}.subviews[{sub_index - 1}]"
            if not isinstance(subview, dict):
                errors.append(f"{sub_label} must be an object")
                continue
            sub_id = subview.get("id")
            if not isinstance(sub_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,63}", sub_id):
                errors.append(f"{sub_label}.id is invalid")
            elif sub_id in seen_subview_ids:
                errors.append(f"Duplicate subview id: {sub_id}")
            seen_subview_ids.add(sub_id)
            if subview.get("view_label") not in ENUMS["view_label"]:
                errors.append(f"{sub_label}.view_label is invalid")
            crop = subview.get("crop_normalized_xyxy")
            if not isinstance(crop, list) or len(crop) != 4 or not all(isinstance(value, (int, float)) for value in crop):
                errors.append(f"{sub_label}.crop_normalized_xyxy must be four numbers")
            elif not (0 <= crop[0] < crop[2] <= 1 and 0 <= crop[1] < crop[3] <= 1):
                errors.append(f"{sub_label}.crop_normalized_xyxy must be a valid normalized XYXY rectangle")
            if subview.get("projection", ref.get("projection")) == "unknown":
                review_flags.append(f"{sub_id}: projection requires human review")

    if not isinstance(build.get("vram_budget_gb"), (int, float)) or build["vram_budget_gb"] <= 0:
        errors.append("build.vram_budget_gb must be a positive number")

    report = {
        "schema_version": SCHEMA_VERSION,
        "character_id": character.get("id"),
        "status": "failed" if errors else ("review" if review_flags else "pass"),
        "valid": not errors,
        "reference_count": len(refs),
        "subview_count": len(seen_subview_ids),
        "reference_hashes": checked,
        "review_flags": review_flags,
        "errors": errors,
        "geometry_worker_may_start": not errors,
        "canonical_geometry_approval": False,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
