# ICHIRO 3D // BY ETHERNIUM
### Studio-Grade 3D Production Pipeline, Discrete Differential Geometry & ARKit 52 Retopology
**Asset:** Ichiro (Keeper #2390 — Arcane Cyberpunk Variant)  
**Standard:** Unreal Engine 5 Nanite/LOD + Film-Ready Facial Rigging  
**Ecosystem:** [Ethernium Sovereign Engine](https://github.com/NullaLabs)  

---

## Overview

**ICHIRO 3D** is the authoritative high-fidelity 3D production repository for **Ichiro (Keeper #2390)**, meticulously engineered to combine the expressive painterly aesthetic of *Fortiche / Arcane* with game-ready performance and anatomical deformation integrity.

This repository houses the full 3D asset suite, procedural Python build scripts for Blender 5.2, 4K PBR texture atlases, multi-LOD packages for Unreal Engine 5, and canonical reference sheets.

---

## Mathematical Architecture & Manifold Geometry Core

The 3D model conforms to 2-manifold geometric invariants embedded in $\mathbb{R}^3$:

- **Euler Characteristic Invariant:**
  $$\chi(\mathcal{M}) = V - E + F = 2(1 - g) - b$$
  Every closed submesh maintains genus $g=0$ with zero non-manifold edges and zero degenerate pinch vertices.
- **Laplace-Beltrami Conformal Smoothing:**
  Discrete differential cotangent-weighted operators applied to eliminate marching-cubes high-frequency artifacts while locking volumetric silhouette boundaries:
  $$(\Delta_{\mathcal{M}} f)_i = \frac{1}{2 A_i} \sum_{j \in \mathcal{N}(i)} (\cot \alpha_{ij} + \cot \beta_{ij}) (f_j - f_i)$$
- **Canonical ARKit 52 / FACS Facial Loop Architecture:**
  Concentric quad rings for the *Orbicularis Oculi* (eyelids/blink), *Orbicularis Oris* (lips/speech), nasolabial smile flow, sharp anime V-line jaw contour, and cylindrical cervical rings.

---

## Key Design Specifications

1. **Clean Tactical Bolero (No Scabbard / No X-Harness):**
   The back of the cropped bolero jacket and compression undersuit is kept completely clean and uncluttered, strictly omitting dorsal scabbards and chest harness straps.
2. **Inseam UV Unwrapping (Zero White Bleed):**
   The inner thighs and crotch feature an anatomical inseam unwrap with hand-inversion and dark charcoal tactical fabric inpainting (`#141518`), eliminating 100% of 2D cutout background bleed.
3. **Lateral 360 Texture Projection:**
   Eliminates orthogonal planar stretch on flanks and ribs through smooth cosine-weighted triplanar and cylindrical projection.
4. **Unified 4K PBR Texture Atlas:**
   $4096 \times 4096$ Master maps:
   - `ichiro_master_diffuse_4k.png`: Albedo with hand-painted Arcane chiaroscuro.
   - `ichiro_master_normal_4k.png`: High-frequency tangent space normals.
   - `ichiro_master_roughness_4k.png`: Micro-roughness specular control.
   - `ichiro_master_emission_4k.png`: Glowing magma forehead fracture and cybernetic eyes.

---

## Repository Layout

```
Ichiro/
├── Ichiro_3D_Arcane/
│   ├── blend/
│   │   ├── Ichiro_2390_Arcane_Scene.blend         # Master production scene
│   │   ├── Ichiro_2390_Arcane_4K_Atlas.blend      # 4K Texture baking rig
│   │   └── Ichiro_2390_UE5_LOD_Package.blend      # Hierarchical LOD triad
│   ├── models/
│   │   ├── Ichiro_2390_LOD0.glb                   # Hero Cinematic (97k quads)
│   │   ├── Ichiro_2390_LOD1.glb                   # Gameplay Medium (34k tris)
│   │   ├── Ichiro_2390_LOD2.glb                   # Mobile / Crowd (9k tris)
│   │   └── Ichiro_2390_UE5_LODGroup.glb           # Complete nested LOD group
│   ├── textures/
│   │   ├── ichiro_master_diffuse_4k.png           # 4K Diffuse / BaseColor
│   │   ├── ichiro_master_normal_4k.png            # 4K Tangent Normal
│   │   ├── ichiro_master_roughness_4k.png         # 4K Roughness
│   │   └── ichiro_master_emission_4k.png          # 4K Magma / Eye Emission
│   ├── scripts/
│   │   ├── assemble_4k_atlas.py                   # Automated atlas assembler
│   │   ├── bake_unified_4k_atlas.py               # Deterministic CPU baker
│   │   ├── build_modular_true360_scene.py         # Full scene constructor
│   │   ├── build_tactical_clothing_layers.py      # Non-destructive layer generator
│   │   ├── generate_ue5_lods.py                   # Decimation & LOD exporter
│   │   └── composite_inspection_huds.py           # Verification HUD renderer
│   ├── renders/                                   # 4-View turnarounds & HUDs
│   ├── references/                                # Canonical 2D turnarounds
│   └── viewer/                                    # Interactive Three.js WebGL viewer
├── .gitignore
└── README.md
```

---

## Automated Headless Build Pipeline (Blender 5.2)

To rebuild or bake the entire character asset headlessly from command line:

```powershell
# 1. Assemble Modular True360 Scene
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P "Ichiro_3D_Arcane\scripts\build_modular_true360_scene.py"

# 2. Bake Unified 4K PBR Atlas
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P "Ichiro_3D_Arcane\scripts\bake_unified_4k_atlas.py"

# 3. Generate Unreal Engine 5 LOD Group
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P "Ichiro_3D_Arcane\scripts\generate_ue5_lods.py"

# 4. Composite Inspection Telemetry HUDs
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P "Ichiro_3D_Arcane\scripts\composite_inspection_huds.py"
```

---

## Interactive WebGL Experience

Explore the online interactive portal:  
[ICHIRO — Legacy of Rebirth](https://steveblackbeard.github.io/ICHIRO-LegacyOfRebirth-by-Ethernium/)

---

## License & Attribution

Creative design, meshes, textures, and sovereign pipeline code are protected under the Ethernium Sovereign Protocol.  
Copyright © 2026 NullaLabs / Ethernium. All rights reserved.
