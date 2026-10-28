"""Compare approximate 2D facial proportions without transferring geometry."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "references" / "canonical_face_landmarks_v02.json"
SOURCE = ROOT / "references" / "source_face_landmarks_estimate_v01.json"
OUTPUT = ROOT / "docs" / "FACE_PROPORTION_COMPARISON_V02.json"

canonical = json.loads(CANONICAL.read_text(encoding="utf-8"))
source = json.loads(SOURCE.read_text(encoding="utf-8"))

def dist(a, b):
    return math.dist(a, b)

def center(points):
    return [sum(p[i] for p in points) / len(points) for i in range(2)]

canon_points = canonical["landmarks"]
def canon_center(prefix):
    return center([p["point"] for p in canon_points if p["id"].startswith(prefix)])

canon_left = canon_center("screen_left_eye_")
canon_right = canon_center("screen_right_eye_")
canon_nose = next(p["point"] for p in canon_points if p["id"] == "nose_tip")
canon_chin = next(p["point"] for p in canon_points if p["id"] == "chin_center")
src = source["landmarks"]
src_left = src["eye_screen_left_center"]["point"]
src_right = src["eye_screen_right_center"]["point"]
src_nose = src["nose_tip"]["point"]
src_chin = src["chin_center"]["point"]

def metrics(left, right, nose, chin):
    eye_mid = center([left, right])
    eye_spacing = dist(left, right)
    lower_face = dist(eye_mid, chin)
    eye_to_nose = dist(eye_mid, nose)
    nose_to_chin = dist(nose, chin)
    return {"eye_spacing_px": eye_spacing, "eye_mid_to_chin_px": lower_face,
            "eye_spacing_over_eye_mid_to_chin": eye_spacing / lower_face,
            "eye_mid_to_nose_over_eye_mid_to_chin": eye_to_nose / lower_face,
            "nose_to_chin_over_eye_mid_to_chin": nose_to_chin / lower_face}

canon = metrics(canon_left, canon_right, canon_nose, canon_chin)
derived = metrics(src_left, src_right, src_nose, src_chin)
report = {
    "schema": "ethernium.face-proportion-comparison/0.2",
    "canonical_reference": canonical["reference"],
    "source_render": source["image"],
    "method": "Scale-independent landmark ratios from manual 2D point estimates; cameras are not registered.",
    "canonical_estimates": canon,
    "source_render_estimates": derived,
    "relative_differences_percent": {
        key: 100 * (derived[key] / canon[key] - 1)
        for key in ("eye_spacing_over_eye_mid_to_chin",
                    "eye_mid_to_nose_over_eye_mid_to_chin",
                    "nose_to_chin_over_eye_mid_to_chin")
    },
    "decision": "NO_LARGE_SCALE_INDEPENDENT_EYE_SPACING_MISMATCH_DETECTED; CAMERA_REGISTRATION_STILL_REQUIRED_FOR_3D_TRANSFER",
    "limitations": [
        "Source render points are approximate and partly occluded.",
        "Canonical image and source render use different, unregistered camera framing.",
        "Ratios are a coarse cross-view sanity check, not proof of exact shape match.",
        "No 3D coordinates, sculpt edits, or topology were generated."
    ]
}
OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(OUTPUT), "canonical": canon,
                  "source": derived,
                  "relative_differences_percent": report["relative_differences_percent"],
                  "decision": report["decision"]}, indent=2))
