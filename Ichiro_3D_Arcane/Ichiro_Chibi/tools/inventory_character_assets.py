"""Create a deterministic, read-only inventory of Ichiro Chibi project assets.

Uses only the Python standard library. It never edits, renames, moves, or deletes
inputs. Classification is deliberately conservative: filenames suggest roles,
but candidates are not promoted to approved masters automatically.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = SCRIPT_ROOT / "docs" / "ASSET_INVENTORY.json"
SUPPORTED = {
    ".blend", ".blend1", ".obj", ".fbx", ".glb", ".gltf", ".abc",
    ".usd", ".usda", ".usdc", ".stl", ".png", ".jpg", ".jpeg",
    ".webp", ".tif", ".tiff", ".exr", ".json", ".md", ".py",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify(path: Path, root: Path) -> tuple[str, str]:
    rel = path.relative_to(root).as_posix().lower()
    name = path.name.lower()
    if "pre_foundry_recovery" in name:
        return "recovery_snapshot", "Local pre-change recovery copy; not the active working file"
    if path.suffix.lower() == ".blend1" or name.endswith(".blend1"):
        return "backup", "Blender automatic backup; not a production authority"
    if rel.startswith("references/"):
        return "reference", "Reference/source evidence; confirm its authority in the manifest"
    if "visual_hull_v02" in rel:
        return "blockout_candidate", "Generated silhouette blockout; never final sculpt or rig topology"
    if "review" in name or "experiment" in name or "_pass" in name:
        return "review_candidate", "Review or experimental artifact; not approved by filename"
    if "candidate" in name:
        return "candidate", "Candidate asset; approval requires project status and visual review"
    if name == "ichiro_chibi_highdetail_working.blend":
        return "declared_master", "Active high-detail source declared by PROJECT_STATUS.md"
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".exr"}:
        if rel.startswith("renders/"):
            return "render_evidence", "Rendered evidence; not source geometry"
        return "image_unclassified", "Image outside references/renders; role needs review"
    if path.suffix.lower() == ".blend" and "highdetail" in name:
        return "source_candidate", "High-detail source candidate; verify against PROJECT_STATUS and scene contents"
    if path.suffix.lower() in {".blend", ".obj", ".fbx", ".glb", ".gltf", ".abc", ".usd", ".usda", ".usdc", ".stl"}:
        return "geometry_unclassified", "Geometry file; role and approval need review"
    if path.suffix.lower() in {".py", ".json", ".md"}:
        return "workflow_source", "Workflow code or documentation"
    return "other", "Role not inferred"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=SCRIPT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    if not root.is_dir():
        parser.error(f"asset root is not a directory: {root}")

    entries = []
    hash_groups: dict[str, list[str]] = defaultdict(list)
    for path in sorted(root.rglob("*"), key=lambda p: p.as_posix().casefold()):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if path.resolve() == output:
            continue
        if path.suffix.lower() not in SUPPORTED:
            continue
        relative = path.relative_to(root).as_posix()
        category, note = classify(path, root)
        digest = sha256_file(path)
        entries.append({
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": digest,
            "category": category,
            "classification_note": note,
        })
        hash_groups[digest].append(relative)

    duplicates = [
        {"sha256": digest, "paths": paths}
        for digest, paths in sorted(hash_groups.items()) if len(paths) > 1
    ]
    counts: dict[str, int] = defaultdict(int)
    for entry in entries:
        counts[entry["category"]] += 1
    report = {
        "schema": "ethernium.character_asset_inventory.v1",
        "scope": ".",
        "classification_policy": "Filename and folder heuristics only; never approval.",
        "file_count": len(entries),
        "category_counts": dict(sorted(counts.items())),
        "exact_duplicate_groups": duplicates,
        "assets": entries,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "report": output.relative_to(root).as_posix() if output.is_relative_to(root) else str(output),
        "file_count": len(entries),
        "category_counts": report["category_counts"],
        "exact_duplicate_groups": len(duplicates),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
