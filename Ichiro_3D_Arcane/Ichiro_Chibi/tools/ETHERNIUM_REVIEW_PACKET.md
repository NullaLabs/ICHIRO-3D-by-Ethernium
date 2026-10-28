# Ethernium review packet 0.1

Run export_ethernium_review_packet.py with Blender against the saved eyelid
Pass02 scene. It writes exports/ethernium_review_packet.json without saving or
changing the scene. No new packages are required.

Each mesh has flat positions and triangle indices for a Three.js BufferGeometry,
plus quadFaces preserving the actual authored topology. Source world coordinates
(front +X, up +Z) map to viewer coordinates (front +Z, up +Y) as [y,z,x].
The transform preserves handedness. Model scale is uncalibrated, not meters.
Hashes identify the exact source blend and all six references.

The packet does not include the full character, textures, weights or a rig.
There is no live KREATIVE/LEGION connection yet. A viewer importer must validate
the schema, load positions/indices, and retain quadFaces for wireframe inspection.
Shape and deformation acceptance remain explicitly pending.

## Basis for integration choices

Read-only review of selected source modules, not a comprehensive audit or
execution of upstream test suites. Upstream revisions are pinned in the packet.

- KREATIVE src/api/characterMeshBuilder.js creates front/back heightfield shells
  with a silhouette seam and optional side-envelope guidance. Its quad-edge
  display and diagonal selection do not establish animation-oriented face loops.
  Reuse candidates: viewer/export conventions and comparative mesh diagnostics.
- KREATIVE src/api/scanner360.js includes hardcoded facial profile functions and
  Math.random in its internal points. Its deterministic entry point therefore
  needs seeded randomness before byte-for-byte reproducibility can be claimed.
- KREATIVE src/api/imageAnalyzer.js estimates relief from image cues. Treat those
  outputs as uncertain priors, not measured facial depth.
- LEGION core/bridges/blender_bridge.mjs provides a subprocess execution bridge.
  Its generated example adds an armature modifier but no weight calculation;
  do not interpret that example as a finished automatic rig.
- LEGION core/studio_3d/mesh_topology.mjs serializes triangle geometry; its index
  accessor is fixed at UNSIGNED_SHORT despite supporting Uint32Array input.
  Validate/fix that before routing high-index meshes through this serializer.
- NOISIA src/api/spatialPerceptionEngine.js maps normalized depth to a fixed
  0.30–6.00 distance range. That mapping alone does not calibrate metric geometry
  from character reference images.

Next useful integration: an importer and synchronized reference/model cameras
in a local KREATIVE checkout, followed by silhouette comparisons. Keep Blender
as the authored geometry source. No upstream repository was modified here.
