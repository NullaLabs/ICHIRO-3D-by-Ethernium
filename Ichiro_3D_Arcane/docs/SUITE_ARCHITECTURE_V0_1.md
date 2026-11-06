# ICHIRO 3D Suite — architecture v0.1

**Purpose:** convert one or more authored character images into a high-quality, deformable 3D avatar and a validated VRM, while preserving reviewability and reproducibility.

**Status:** architecture and migration contract. This document does not claim that every stage is implemented or that Ichiro is already a production VRM.

## Product boundary

The product is not a one-click image-to-mesh novelty. Its output is a usable avatar whose identity, volume, face, hands, clothing, materials, humanoid mapping, expressions, and VRM metadata have all passed evidence-based gates.

The suite treats image-to-3D models as candidate generators. Their hidden surfaces and facial details are hypotheses until checked against reference evidence and artist review. A generated turnaround can guide exploration but never silently become canon.

## Pipeline

| Stage | Input | Work | Required output and gate |
|---|---|---|---|
| 0. Character package | One or more images and a character spec | Hash sources; label view, angle, projection, region, authority, confidence, masks, and landmarks | Immutable evidence manifest; uncertain labels remain `unknown` |
| 1. Image analysis | Evidence manifest | Subject masks, landmarks, camera estimates, scale and uncertainty | Review sheet; do not start geometry when the primary silhouette is ambiguous |
| 2. View planning | All references and uncertainty | Choose the next useful view/region; identify gaps and redundant images | N-view coverage map with evidence provenance |
| 3. Candidate generation | Best-supported image subset | Run one shape worker; optionally run separate texture worker; unload between stages | Candidate mesh plus runtime, peak VRAM, duration, model/license and checkpoint record |
| 4. Geometric reconstruction | Candidate mesh, all view constraints | Align cameras; compare silhouettes/depth/landmarks; fuse or sculpt only supported corrections | Versioned blockout and eight-view/N-view residuals; unsupported areas tagged inferred |
| 5. Sculpt and retopology | Approved blockout | Human-guided form correction, face/hand construction, deformation-aware quad flow | Low-density deformation mesh plus separate high-detail source; deformation tests pass |
| 6. Surface and appearance | Approved meshes and reference color/style | UVs, texture baking/painting, PBR or MToon-compatible appearance | Maps/material audit and multi-angle color/face review |
| 7. Humanoid and face | Approved retopo and surfaces | VRM humanoid mapping, weights, expressions, gaze, hair/clothing spring-bone setup | Required bones map; blink, gaze, jaw and visemes visibly work; no orphan weighted geometry |
| 8. VRM package | Rigged scene | Set orientation/units, metadata, expressions, first-person settings and VRM extensions | `.vrm` exported, parsed against the selected spec, re-imported, previewed and report saved |
| 9. Delivery | Validated package | Produce source scene, `.vrm`, evidence, manifest and a lightweight preview | One versioned release bundle; no “complete” label without all blocking gates |

The humanoid avatar standard covers pose, facial expression, gaze, humanoid bones, material options, first-person setup, and spring bones. Therefore the VRM gate must validate more than the GLB container or the existence of an armature. The first target is VRM 1.0; a 0.x export can be added as a compatibility profile after 1.0 passes.

## Reference model: N views, not eight hard-coded inputs

Each image has its own record: `view_id`, file path and SHA-256, `view_label`, optional azimuth/elevation, projection (`orthographic`, `perspective`, or `unknown`), region, source authority, mask/landmark references, confidence and `observed|inferred|synthetic` provenance.

The eight direction labels (front, front-left, left, left-back, back, back-right, right, front-right) are canonical evaluation anchors when available. Their exact azimuths are measured per reference; the labels alone do not prove calibrated 45-degree camera spacing. Extra photographs, details, top/bottom views and authored poses are supported as additional evidence. They are not forced into those eight bins.

The current Chibi turnaround contact sheet is 360×240 px. Its fixed 4×2 segmentation yields panels of only 86×82 px after gutters/captions are removed. Those eight crops are useful as coarse continuity constraints; the system flags them as too small for face, retopology or texture detail. The four individual plates carry the main silhouette evidence.

An image model may accept only a subset of views. That is a worker limit, not a suite limit. Keep the full evidence package for camera fitting, silhouette checks and geometry refinement. Do not average inconsistent views blindly: flag camera, perspective, pose, outfit and identity conflicts for resolution.

## RTX 3070 / 8 GB memory policy

1. Query free GPU memory before a worker starts and record the baseline.
2. Run shape, texture, baking and VRM export as separate jobs. Do not keep two diffusion workers resident together.
3. Prefer a smaller/fast shape checkpoint for blockout; refine with Blender CPU and bounded local operations.
4. Permit CPU offload/tiled inference only where the worker implements it. Stage splitting alone does not shrink a single model's peak tensor allocation.
5. Save input hashes, model revision/license, settings, logs, intermediate file hash, peak VRAM/RAM, elapsed time and resume state per stage.
6. On OOM, keep the last valid checkpoint, lower the supported workload or mark the stage blocked; never silently degrade the mesh.

Tencent's Hunyuan3D repository documents a staged shape/texture design, a multiview shape checkpoint, and a VRAM estimate of about 6 GB for shape versus 16 GB for shape plus texture in total. This makes shape-only inference a candidate to benchmark on the 3070, not an established guarantee for this machine or every checkpoint. The suite should keep the texture worker separate and measure the actual peak.

## Role of Synkronia SNN / 50M LIF

The SNN is a decision/controller module, not the mesh decoder. Its useful early jobs are:

- prioritize which view or anatomical region to inspect next;
- select a small informative subset of references for a limited-view model;
- detect where view evidence is inconsistent or insufficient;
- choose whether a refinement pass is worth its GPU and human-review cost.

Start with a deterministic baseline and a small LIF controller. Reward decisions by held-out improvement in silhouette IoU, landmark reprojection, depth consistency and artist acceptance, with a penalty for runtime and memory. Compare SNN-on against SNN-off on fixed cases. Scale to the 50M LIF implementation only after its spike path, outputs, buffer bounds, timing and improvement are measured on the actual runtime. Do not claim 50M neurons at a target FPS from a design document or simulated count alone.

## Integration boundaries in the NullaLabs / Ethernium ecosystem

Keep these as adapters with explicit input/output contracts; do not duplicate their responsibilities inside Blender scripts.

| Existing area | Suite responsibility to reuse | Boundary to verify |
|---|---|---|
| KPR / ComfyUI / KREATIVE Generator / I+D Lab | Image preparation, local model workers, mask/depth/mesh experiments | Which local runner is real on this machine; exact models, licenses and memory behavior |
| ICHIRO 3D | Blender authoring, sculpt/retopo, materials, avatar quality gates | Replace absolute user paths and distinguish GLB from actual VRM export |
| LEGION 3D | Reusable character/geometry orchestration if API is implemented | Avoid a second incompatible character spec or exporter |
| FRUGAL / PAMP / Chronolith | Budgeting, jobs, checkpoint/recovery and traceability | Connect only through stable job/checkpoint contracts |
| Synkronia SNN | Evidence selection and active-view controller | Benchmark against deterministic ablation; never replace geometric solver |
| Blender MCP | Interactive review and small isolated scene operations | Not required for headless reproducible builds; live scene currently unreachable |

Adapters must record exact repository revision, API and license. Names in an ecosystem map do not count as verified integrations.

## Quality gates and metrics

**Evidence gate:** every image is hashed and labelled; synthetic and inferred references are distinguishable from authored canon.

**Form gate:** compare the same calibrated orthographic cameras against masks for all available anchors; report per-view IoU, silhouette distance and landmark reprojection residual. Scores locate disagreements but do not approve art direction.

**Mesh gate:** finite coordinates, intended connected components, self-intersection and boundary policy per module, UV/material checks, scale/orientation, and target budget. Do not require every hair card or clothing shell to be closed manifold.

**Rig gate:** required humanoid mapping, weight coverage and influence limits, pose neutrality, and static bend tests for shoulders, elbows, wrists, hips, knees, fingers, blink, gaze, jaw and visemes.

**VRM gate:** create a real `.vrm` with the chosen version extension and metadata; parse/check its extension structure and references; re-import into Blender or another independent VRM viewer; test expressions, gaze and secondary motion. A `.glb` renamed to `.vrm` is a hard failure.

Automated outcome is `PASS`, `REVIEW` or `BLOCKED`. Only a human can approve identity and canonical likeness.

## Build strategy for Ichiro

1. **Started:** `characters/ichiro_chibi/character_spec.json` is the first six-image Chibi evidence package, with eight normalized panel crops recorded under the turnaround sheet. The four primary views are marked canonical; the eight-view sheet is supporting evidence; the Kimi pipeline board is exploration-only. All six image byte hashes were checked during intake. Camera and projection remain `unknown` until calibrated. Keep canonical Ichiro evidence separate.
2. Make one controlled baseline blockout from the actual Ichiro references. Compare 4-view, 8-view and full-evidence constraint sets using the same cameras and metrics.
3. Benchmark one small multiview image-to-shape worker on the RTX 3070; use it as a candidate, not as final facial topology. Keep current locked/high-detail source unchanged.
4. Correct head, hair, face, hands, clothes and silhouette with staged Blender work. Build deformation topology and face controls before detail baking.
5. Produce a VRM 1.0 using a version-compatible exporter, validate/re-import it, and record all criteria and evidence.
6. Extract reusable modules only after Ichiro Chibi passes the release checklist. Then repeat the test on one unrelated character spec to prove it is a suite rather than an Ichiro-only script collection.

## Research sources

- Tencent Hunyuan3D official repository: https://github.com/Tencent-Hunyuan/Hunyuan3D-2
- VRM Consortium feature and behavior overview: https://vrm.dev/en/vrm/vrm_features/
- VRM Consortium development conventions: https://vrm.dev/en/vrm/vrm_development/
- VRM specification repository: https://github.com/vrm-c/vrm-specification
- VRM Add-on for Blender (upstream; repository documents Blender 2.93–5.2 support and mixed licenses): https://github.com/saturday06/VRM-Addon-for-Blender
- OpenCartridge (local ComfyUI cartridge suite; current repo documents ~24 GB VRAM for its workers): https://github.com/camenduru/OpenCartridge
- GLB2VRM (candidate conversion/validation adapter, not a character reconstruction or topology solution): https://github.com/camenduru/GLB2VRM

The initial intake uses only Python's standard library. No model weights, Blender add-on, skill or third-party dependency was installed.
