# ICHIRO 3D Suite

**Local-first image-to-VRM character production, with Ichiro as the reference case.**

This repository is becoming a reusable character-production suite: it should turn a documented image set into an artist-reviewable, deformable 3D character and a standards-compliant `.vrm`. Ichiro Chibi is the first end-to-end case; canonical Ichiro is a separate profile and must not inherit Chibi proportions.

## Current status

The repository contains Blender scenes and scripts, a character-foundry prototype, image/reference comparison tools, and VRM-oriented experiments. These are useful source material, but the pipeline is **not yet a verified image-to-VRM product**:

- The existing foundry export stage creates `.glb`; it does not certify a `.vrm` file.
- The current “VRM production” scripts also export GLB and need an actual VRM extension/export-and-reimport gate.
- Eight-view comparison exists, while N-view geometric fusion is still a planned capability.
- Generated or voxel-derived meshes remain candidates until silhouette, surface, facial topology, and deformation review passes.
- No new model, add-on, skill, or Python dependency has been installed for this suite work.

## Product contract

For each character, the suite will preserve source images and their hashes, separate observed evidence from inferred surfaces, make each build reproducible, checkpoint expensive stages, and report measurable failures instead of declaring success because a script finished. The art direction and human approval remain explicit gates.

Target flow:

`reference images → evidence package → multi-view reconstruction candidates → sculpt + retopology → materials → humanoid rig + face controls → VRM 1.0 export → schema/import/preview validation`

The pipeline accepts eight canonical directions and additional reference images. Models may consume a subset of views; the suite retains all views as geometric constraints and evaluation evidence. AI-generated turns are hypotheses, clearly distinguished from authored reference art.

## Start here

- [Suite architecture and staged plan](Ichiro_3D_Arcane/docs/SUITE_ARCHITECTURE_V0_1.md)
- [Migration map from the current prototypes](Ichiro_3D_Arcane/docs/SUITE_MIGRATION_MAP_V0_1.md)
- [Character spec schema](Ichiro_3D_Arcane/suite/character_spec.schema.json), [reference intake](Ichiro_3D_Arcane/suite/init_character_project.py), [package verifier](Ichiro_3D_Arcane/suite/validate_character_project.py), and [multi-view crop extraction](Ichiro_3D_Arcane/suite/extract_spec_subviews.py)
- [Ichiro Chibi reference package](Ichiro_3D_Arcane/characters/ichiro_chibi/character_spec.json)
- [Current Ichiro Chibi production status](Ichiro_3D_Arcane/Ichiro_Chibi/PROJECT_STATUS.md)
- [Existing project assets and experiments](Ichiro_3D_Arcane/README.md)
- [Archived pre-suite README and claims](Ichiro_3D_Arcane/docs/LEGACY_ROOT_README_2026.md)

## Hardware approach

The design targets a local-first workflow that can operate on an 8 GB GPU by staging model inference, unloading each worker between stages, and storing checkpoints on disk. This is a design target, not a current performance guarantee. A stage that cannot fit must offer CPU/offload, a smaller model, or a clearly reported external option; it must not silently run out of memory or pretend to have completed.

## Scope

The suite builds a finished, usable VRM avatar. Motion generation and VRMA authoring are later optional modules; they are not the definition of a finished character.
