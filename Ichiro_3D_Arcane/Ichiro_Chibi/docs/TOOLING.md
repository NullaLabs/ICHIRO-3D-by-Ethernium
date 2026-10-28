# Tooling and reproducibility

## Active method: calibrated silhouette blockout

`tools/build_calibrated_visual_hull.py` derives a coarse blockout from the
front, back, left and right images using paths relative to this project. V02
preserves each crop's aspect ratio, writes source-standard X-front/Y-width/
Z-up coordinates at a declared one-metre height, hashes its four inputs and
audits face winding and edge incidence. Output is isolated under
`exports/visual_hull_v02/`; earlier output under `E:/WORKSPACE` remains untouched.

This is a **volume and proportion** step, not an automatic final character.
It cannot infer hidden folds, facial planes, hair strand depth, hands or
mechanical construction. The V02 candidate is intentionally coarse and is
kept separate from the locked high-detail source; it is only a sculpting and
proportion reference after visual approval.

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
