# Tooling and reproducibility

## Active method: calibrated silhouette volume

The first Chibi geometry is computed from the supplied front, back, left and
right renders.  The process estimates a neutral-background mask, registers the
four silhouettes into one normalized frame, and keeps only voxels supported by
both the front/back and the left/right evidence.  It creates a locked OBJ
source, masks for inspection, and a Blender scene that never overwrites the
references.

This is a **volume and proportion** step, not an automatic final character.
It deliberately cannot infer hidden folds, facial planes, hair strand depth or
mechanical construction.  Those are authored in the separate non-destructive
costume, hair, and sculpt layers after silhouette approval.

## Optional AI candidate tool

`tools/Hunyuan3D-2.1` is an unmodified checkout of Tencent's Hunyuan3D 2.1.
Its environment is `tools/hunyuan-venv`, and its pip cache/temp are under
`E:/WORKSPACE/_cache` so the nearly-full C: drive is not used.  It is not yet
accepted as a production dependency: the initial dependency installation did
not complete, and the RTX 3070 Laptop GPU has 8 GB VRAM, below the vendor's
published full-pipeline recommendation.  Any generated mesh is therefore a
candidate for comparison only, never a canonical source or replacement for
the multi-view evidence.

## Quality gates

1. Inspect the four extracted masks and correct a mask before geometry is made.
2. Compare the locked volume to all four orthographic anchors and the eight-view
   turnaround.
3. Build clothing, hair, face and props as named modules; do not merge or
   destructively remesh the locked source.
4. Only after a render review: approved sculpt, retopology, UV/bake, PBR and
   final presentation/rig readiness.
