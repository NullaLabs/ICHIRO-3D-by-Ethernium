# ICHIRO 3D Suite — migration map v0.1

This map converts existing work into a truthful, reusable image-to-VRM pipeline. Existing scene files and experiments remain intact; the migration adds contracts and adapters before it replaces any authoring path.

## What is already here

| Existing path | Current evidence | Suite treatment |
|---|---|---|
| `Ichiro_Chibi/tools/score_reference_fit.py` and the CPU projection/report folders | Scores a current mesh against four plates and eight turnaround crops | Retain as an evaluation worker; calibrate each view and extend to more evidence records |
| `Ichiro_Chibi/tools/build_calibrated_visual_hull.py` and `exports/visual_hull_v02` | Four-mask volume blockout with documented limits | Retain as a proxy/blockout experiment; never describe as final retopo |
| `Ichiro_Chibi` registered eye/component tools | Isolated projection and topology review experiments | Keep review-only; do not integrate a patch until art and deformation gates pass |
| `ethernium_character_foundry/run_foundry.py` | Hard-coded Windows Blender path; fixed eight calls; completion text overstates output | Wrap behind suite job contracts; replace hard-coded paths, truthful stage state and resumable artifacts |
| `ethernium_character_foundry/modules/07_audit_and_export.py` | Exports `.glb`, renders a few views and writes a manifold-oriented report | Reuse portions of audit/render, add character-specific mesh policies and a real VRM stage |
| `Ichiro_3D_Arcane/vrm_production/build_complete_ichiro_vrm.py` | Builds/updates a Blender scene and exports `Ichiro_2390_Decoupled_Master.glb` | Reuse selected rig setup only after topology/weights audit; the current output is not a `.vrm` |
| `Ichiro_3D_Arcane/viewer` | Three.js GLB preview and experiments | Reuse for candidate inspection; add a VRM-aware runtime only when it adds validation not covered by a dedicated viewer |
| `Ichiro_3D_Arcane/models` and `Ichiro_Chibi` | Many source, generated and review assets, with mixed maturity | Catalogue by hash/status: source, reference, candidate, rejected, approved. Do not infer approval from names |

The existing nested README contains assertions about AAA geometry, rigging, and output quality that are not backed by a current end-to-end VRM validation record. Treat it as a legacy project description until its claims are individually reproduced.

## External systems to benchmark, not blindly adopt

### OpenCartridge

Useful reference for local-first workers, cartridge lifecycle and a multi-tool asset canvas. Its own README says current workers are sized around an NVIDIA GPU with roughly 24 GB VRAM; this is not the base runtime for the 8 GB laptop. Its listed Idol output is a Gaussian-splat/meshed GLB path, and its listed SkinTokens step begins from an existing mesh. Neither replaces deformation topology, artistic likeness review or a VRM export gate.

### Hunyuan3D-2MV

Useful candidate shape worker because the upstream project publishes a multiview checkpoint and separates geometry from texture. Benchmark shape-only on the RTX 3070 and keep texture synthesis as a later, separate job. The documented total memory for shape plus texture is above the local VRAM target, so do not queue both workers together.

### Blender VRM Add-on and GLB2VRM

The Blender add-on is the leading authoring/export candidate because the upstream repository documents Blender 5.2 support and an API. GLB2VRM is worth benchmarking as a separate adapter because it advertises VRM 1.0/0.x output and a checker, but its code, license, mapping quality and independent round-trip behavior must be reviewed before selecting it. Neither should be installed until the user approves that tool change.

## Target suite layout

```text
Ichiro_3D_Arcane/
├── suite/                 # CLI, contracts, stage registry and adapter interfaces
├── characters/
│   ├── ichiro_chibi/      # first end-to-end reference case
│   └── ichiro_canon/      # separate proportions and evidence
├── workers/               # thin adapters to image, geometry, Blender and VRM tools
├── docs/                  # architecture, evaluations, decisions and release records
└── viewer/                # review/preview clients
```

This is a target layout, not a mass move. Keep existing paths until scripts use relative paths and migration can prove all files resolve. A move that breaks `.blend` links is not progress.

## First implementation slices

1. Publish the status/architecture contract at repository root.
2. Define a schema for image inputs, provenance, character profile, compute budgets and output target.
3. Build a dependency-free reference intake/manifest command; reject missing files and hash mismatches before GPU or Blender starts.
4. Convert existing projection and report scripts into adapters with machine-readable status and output hashes.
5. Add a measured memory-aware worker runner with checkpoints and per-stage cleanup.
6. Benchmark a candidate multiview model, including 4/8/all-reference conditions and GPU peaks; record GPU, RAM, runtime, geometry and view-fit metrics.
7. Add retopology/rig review gates and a true VRM exporter/importer loop.
8. Prove reuse by running a second character spec after Ichiro Chibi passes.

## Decision log

- **Image-to-VRM is the product boundary.** Blender and AI models are replaceable workers.
- **VRM 1.0 is the first release target.** VRM 0.x is a compatibility export later, not a hidden format downgrade.
- **The 8 GB GPU is a design constraint.** Memory is measured per stage; stage splitting is not claimed to solve an operation's own peak allocation.
- **The SNN chooses work; geometry algorithms construct geometry.** A 50M LIF speed or quality benefit must be demonstrated against a deterministic baseline.
- **No tool/add-on/model/dependency is installed by this migration without user approval.**
