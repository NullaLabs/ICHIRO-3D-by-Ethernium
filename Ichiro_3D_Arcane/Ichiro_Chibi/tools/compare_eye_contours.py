"""Measure manually traced source eye contours against registered canonical contours."""
import json
import hashlib
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "references" / "source_eye_contours_estimate_v01.json"
REGISTRATION = ROOT / "docs" / "FACE_REGISTRATION_PROBE_V02.json"
OUTPUT = ROOT / "docs" / "EYE_CONTOUR_ALIGNMENT_V01.json"
source = json.loads(SOURCE.read_text(encoding="utf-8"))
registered = json.loads(REGISTRATION.read_text(encoding="utf-8"))
eye_spacing = math.dist(
    registered["anchor_residuals"]["eye_screen_left_center"]["observed_px"],
    registered["anchor_residuals"]["eye_screen_right_center"]["observed_px"])
results = {}
for name, src in source["contours"].items():
    mapped = registered["projected_eye_contours"][name]
    rows = []
    for index, (manual, projected) in enumerate(zip(src["points"], mapped)):
        pred = projected["source_render_px"]
        dx, dy = pred[0]-manual[0], pred[1]-manual[1]
        rows.append({"index": index, "source_edge_px": manual,
                     "registered_canonical_px": pred,
                     "delta_px": [dx, dy], "distance_px": math.hypot(dx, dy),
                     "projection_surface_status": projected["status"]})
    rms = math.sqrt(sum(r["distance_px"]**2 for r in rows) / len(rows))
    upper = rows[1:5]
    results[name] = {
        "source_visibility": src["visibility"],
        "trace_confidence": src["confidence"],
        "rms_px": rms,
        "rms_over_interocular_spacing": rms / eye_spacing,
        "mean_upper_arc_vertical_delta_px": sum(r["delta_px"][1] for r in upper)/len(upper),
        "max_error_px": max(r["distance_px"] for r in rows),
        "samples": rows
    }
report = {
    "schema": "ethernium.eye-contour-alignment/0.1",
    "method": "paired 10-point manual contour traces compared to five-anchor affine transfer",
    "source_contours": "references/source_eye_contours_estimate_v01.json",
    "registration_report": "docs/FACE_REGISTRATION_PROBE_V02.json",
    "source_contours_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "registration_sha256": hashlib.sha256(REGISTRATION.read_bytes()).hexdigest(),
    "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "mean_source_interocular_spacing_px": eye_spacing,
    "results": results,
    "decision": "DO_NOT_BUILD_EYELID_PATCH_FROM_GLOBAL_AFFINE; UPPER_ARC_MISMATCH_REQUIRES_FACE_AND_EYE_REVIEW",
    "limitations": ["source traces follow rendered eyeliner silhouette, not proven anatomy",
                    "left eye is occluded", "manual pixels have uncertain placement",
                    "affine image registration is not camera calibration", 
                    "this comparison does not identify which image is artistically correct"]
}
OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({name: {"rms_px": v["rms_px"], "rms_eye_spacing_percent": 100*v["rms_over_interocular_spacing"],
                         "upper_arc_vertical_delta_px": v["mean_upper_arc_vertical_delta_px"],
                         "max_px": v["max_error_px"]} for name,v in results.items()}, indent=2))
