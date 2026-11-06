# Orbital integration experiment — 2026-11-05

User direction: preserve the original Ichiro appearance. Prioritize game deformation; printing requires a separate closed derivative. Do not promote a cosmetic redesign.

## Accepted change: persistent reference visibility

On reopening the repaired scene, the linked `ICH_CHIBI_HIGHDETAIL_SOURCE__READONLY` has `hide_render=False`, even though the working session hid it before saving. The linked reference could therefore render on top of the editable candidate. Viewport hiding alone did not prevent this.

The local collection `00_HIGHDETAIL_TARGET__READ_ONLY` now carries the persistent render exclusion. The reproduction scripts for connectivity and eyelids include this exclusion. The original source files remain unchanged.

`exports/reference_visibility_v01/Ichiro_Chibi_Original_View.blend` is the repaired original with this display correction, not a new retopology. `verify_reference_visibility.py` saved and reopened it and verified an identical SHA-256 over coordinates, edges, loop connectivity, polygon boundaries, material indices and UVs:

`013745625641322773a24f71d43215c4d2df5ec28d683f8192a44457640da971`

Evidence is in `renders/orbital_integration_v01/visibility_audit.json`, `original_face.png`, and `original_full.png`. This test establishes unchanged mesh/UV data and persistent exclusion; it does not certify self-intersections, print thickness or a game rig. Earlier connectivity comparison renders were generated before reopening and explicitly switched source/candidate visibility; this finding does not by itself invalidate their measurements.

## Rejected change: sewing the isolated eyelid into the dense face

The first experiment removed 6,978 source faces and connected the 120-vertex eyelid through 240 transition triangles to a 216-vertex cut boundary. It had zero unexpected boundary edges, wire edges, edges with more than two faces, or orientation conflicts. The 24 remaining boundary edges were the intentional eyelid aperture.

Those topological checks were insufficient: 53 new triangles faced backwards in the front projection. Projecting the existing eye color onto the replacement surface also dragged the dark upper-eye region during closure. Removing the duplicate reference render eliminated small interference spots but did not solve that texture problem. `REJECTED_projected_color_closed.png` records the failure and is NOT a deliverable appearance.

The final experimental builder uses a bounded dynamic-programming transition search with positive projected triangle area. The actual input fails that gate: 28 reachable states, no complete transition for the selected cut and initial correspondence. It writes `integration_audit.json`, exits with an error, and exports no replacement `.blend`. This is a rejection of this construction, not proof that every possible triangulation is impossible.

Broader cuts and an optional local boundary expansion were also attempted. Expansion produced a branched boundary and was rejected. All experiments occurred under `E:/WORKSPACE/Ichiro/orbital_integration_v01`; the source file SHA-256 remained `1f579e71680049fa6247f4374923cd68d90751e9e40341032d8b87d1f3ed62ff`.

## Reproduction

Run Blender with `--background --factory-startup --python-exit-code 1 --python tools/build_orbital_integration_v01.py -- --out NEW_DIRECTORY`. The exit-code option matters: Blender can otherwise return success after a Python exception. With the current source, expect a rejection audit and no exported replacement asset.

For the accepted visibility change use `tools/verify_reference_visibility.py` with the same arguments. It must print `VISIBILITY_RELOAD_PASS` after reopening the saved file. No new dependencies were installed.

## Next modeling step

Build continuous orbital topology across the eyebrow, eyelid rim and upper cheek, with a controlled outer boundary, fitted to the preserved high-poly reference. Test the fitted surface before welding it to the rest of the face. Separate the ocular surface from eyelid skin and reconstruct the skin exposed by closure; projecting the open-eye color is not sufficient. Preserve the neutral appearance with source comparisons, and test deformation against the actual surrounding face, not only an isolated cap.

The validated isolated morph remains an experiment. Its sampled collision and fixed-triangulation tests do not certify the integrated face. Neither the rejected integration nor the visibility-corrected dense reference is game-ready or print-ready.
