"""Fit a review-only 2D registration and probe its landmarks against skin candidates.

Runs in Blender 5.2 on the saved projection experiment. Writes JSON only;
does not create geometry or alter the user's live Blender session.
"""
import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
CANON_PATH = ROOT / "references" / "canonical_face_landmarks_v02.json"
SOURCE_LANDMARKS_PATH = ROOT / "references" / "source_face_landmarks_estimate_v02.json"
BLEND_PATH = ROOT / "Ichiro_Chibi_Skin_Projection_Experiment.blend"
OUTPUT = ROOT / "docs" / "FACE_REGISTRATION_PROBE_V02.json"

canonical = json.loads(CANON_PATH.read_text(encoding="utf-8"))
source_landmarks = json.loads(SOURCE_LANDMARKS_PATH.read_text(encoding="utf-8"))
lm = canonical["landmarks"]

def mean(points):
    return [sum(p[i] for p in points) / len(points) for i in range(2)]

def group_center(prefix):
    return mean([item["point"] for item in lm if item["id"].startswith(prefix)])

canonical_anchors = {
    "eye_screen_left_center": group_center("screen_left_eye_"),
    "eye_screen_right_center": group_center("screen_right_eye_"),
    "nose_tip": next(item["point"] for item in lm if item["id"] == "nose_tip"),
    "mouth_center": mean([item["point"] for item in lm if item["id"].startswith("mouth_")]),
    "chin_center": next(item["point"] for item in lm if item["id"] == "chin_center"),
}
observed = source_landmarks["anchors"]

def solve3(matrix, rhs):
    a = [list(map(float, row)) + [float(rhs[i])] for i, row in enumerate(matrix)]
    for col in range(3):
        pivot = max(range(col, 3), key=lambda row: abs(a[row][col]))
        if abs(a[pivot][col]) < 1e-12:
            raise ValueError("Singular landmark registration system")
        a[col], a[pivot] = a[pivot], a[col]
        divisor = a[col][col]
        a[col] = [v / divisor for v in a[col]]
        for row in range(3):
            if row == col:
                continue
            factor = a[row][col]
            a[row] = [a[row][k] - factor * a[col][k] for k in range(4)]
    return [a[i][3] for i in range(3)]

rows = [[*canonical_anchors[name], 1.0] for name in canonical_anchors]
normal = [[sum(row[i] * row[j] for row in rows) for j in range(3)] for i in range(3)]
target_x = [observed[name]["point"][0] for name in canonical_anchors]
target_y = [observed[name]["point"][1] for name in canonical_anchors]
coef_x = solve3(normal, [sum(rows[k][i] * target_x[k] for k in range(len(rows))) for i in range(3)])
coef_y = solve3(normal, [sum(rows[k][i] * target_y[k] for k in range(len(rows))) for i in range(3)])

def transform(point):
    return [coef_x[0]*point[0] + coef_x[1]*point[1] + coef_x[2],
            coef_y[0]*point[0] + coef_y[1]*point[1] + coef_y[2]]

residuals = {}
for name, point in canonical_anchors.items():
    pred = transform(point)
    actual = observed[name]["point"]
    residuals[name] = {"predicted_px": pred, "observed_px": actual,
                       "error_px": math.dist(pred, actual)}
errors = [row["error_px"] for row in residuals.values()]
rms = math.sqrt(sum(e*e for e in errors) / len(errors))
source_eye_spacing = math.dist(observed["eye_screen_left_center"]["point"],
                               observed["eye_screen_right_center"]["point"])

bpy.ops.wm.open_mainfile(filepath=str(BLEND_PATH))
source = next(o for o in bpy.context.scene.objects if o.name.startswith("ICH_CHIBI_HIGHDETAIL_SOURCE"))
skin = bpy.data.objects["SKIN_CANDIDATES__NOT_APPROVED"]
def tree(obj):
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    polys = [tuple(p.vertices) for p in obj.data.polygons]
    return BVHTree.FromPolygons(points, polys)
full_bvh, skin_bvh = tree(source), tree(skin)
width, height = source_landmarks["image_size_px"]
cam = source_landmarks["camera"]

probe_points = []
def classify_projection(projected):
    u, v = projected
    row = {"source_render_px": projected}
    if not (0 <= u < width and 0 <= v < height):
        row["status"] = "outside_source_render"
    else:
        lateral = (u / width - 0.5) * cam["ortho_scale"]
        z = cam["target_z"] + (0.5 - v / height) * cam["ortho_scale"]
        origin, direction = Vector((0.5, lateral, z)), Vector((-1, 0, 0))
        full_hit = full_bvh.ray_cast(origin, direction, 1.0)
        skin_hit = skin_bvh.ray_cast(origin, direction, 1.0)
        fh, sh = full_hit[0], skin_hit[0]
        if fh is None:
            row["status"] = "missing_source_surface"
        elif sh is None:
            row["status"] = "missing_skin_candidate"
        elif fh.x - sh.x > 0.01:
            row["status"] = "candidate_occluded_by_front_surface"
        else:
            row["status"] = "skin_candidate_requires_art_review"
        row["full_hit"] = list(fh) if fh is not None else None
        row["skin_candidate_hit"] = list(sh) if sh is not None else None
        row["front_surface_delta_x"] = float(fh.x-sh.x) if fh is not None and sh is not None else None
    return row

for item in lm:
    projected = transform(item["point"])
    row = {"id": item["id"], "canonical_px": item["point"],
           "confidence": item["confidence"], "visibility": item["visibility"]}
    row.update(classify_projection(projected))
    probe_points.append(row)

counts = {}
for row in probe_points:
    counts[row["status"]] = counts.get(row["status"], 0) + 1
contour_probes = {}
contour_counts = {}
for name, points in canonical["eye_contours"].items():
    rows = []
    for index, point in enumerate(points):
        row = {"index": index, "canonical_px": point}
        row.update(classify_projection(transform(point)))
        rows.append(row)
        contour_counts[row["status"]] = contour_counts.get(row["status"], 0) + 1
    contour_probes[name] = rows
report = {
    "schema": "ethernium.face-registration-probe/0.2",
    "method": "five-anchor affine 2D fit, followed by orthographic ray casts into source and warm-color candidate mask",
    "canonical_sha256": hashlib.sha256(CANON_PATH.read_bytes()).hexdigest(),
    "source_landmarks_sha256": hashlib.sha256(SOURCE_LANDMARKS_PATH.read_bytes()).hexdigest(),
    "blend_sha256": hashlib.sha256(BLEND_PATH.read_bytes()).hexdigest(),
    "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "camera": cam,
    "affine_canonical_to_source_pixels": {"x": coef_x, "y": coef_y},
    "anchor_residuals": residuals,
    "registration_rms_px": rms,
    "registration_rms_over_source_eye_spacing": rms / source_eye_spacing,
    "projected_landmark_counts": counts,
    "projected_landmarks": probe_points,
    "projected_eye_contour_counts": contour_counts,
    "projected_eye_contours": contour_probes,
    "decision": "DIAGNOSTIC_MAPPING_ONLY__NO_GEOMETRY_GENERATED",
    "limitations": ["manual correspondences and partial occlusion", "unknown canonical camera model",
                    "warm-color skin mask is not semantic truth", "ray hits do not validate anatomy or topology"]
}
OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(OUTPUT), "rms_px": rms,
                  "rms_over_eye_spacing": rms/source_eye_spacing,
                  "counts": counts, "decision": report["decision"]}, indent=2))
