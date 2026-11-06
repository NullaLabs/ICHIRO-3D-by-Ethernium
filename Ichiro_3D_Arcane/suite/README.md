# Suite foundation

The `suite` folder contains reusable, character-independent contracts and stage definitions. Its first operation creates a reference package without requiring Blender or third-party Python packages.

## Initialize a character case

Run from the repository root. Repeat `--reference` for every source image:

```powershell
python Ichiro_3D_Arcane/suite/init_character_project.py `
  --character-id new-character `
  --name "New Character" `
  --profile stylized_humanoid `
  --output Ichiro_3D_Arcane/characters/new_character `
  --reference "front|whole_character|primary_canon|authored_art|unknown|C:/art/front.png"
```

Reference columns are `view|region|authority|origin|projection|path`. Use `unknown` when an attribute is not established. The command checks the input files, copies them byte-for-byte into a new package, verifies SHA-256, writes `character_spec.json`, and refuses to overwrite an existing package. It does not calibrate cameras, infer missing views, start Blender, or modify the model.

For a contact sheet, add one `--subview "parent_id|id|view|x0|y0|x1|y1"` per panel. Parent IDs are assigned by the order of `--reference` arguments (`reference_01`, `reference_02`, …). Crop coordinates use normalized `[0,1]` XYXY values measured from the source image's top-left; a subview inherits source hash and provenance from its parent. It never pretends a panel label is a calibrated camera angle.

Validate the package and all copied file hashes before starting an expensive stage:

```powershell
python Ichiro_3D_Arcane/suite/validate_character_project.py `
  Ichiro_3D_Arcane/characters/new_character/character_spec.json
```

`review` is a valid package whose unknown camera, view, provenance or authority fields need human review. `failed` means a structural or hash error blocks the next worker.

Extract declared panel crops for a multiview worker:

```powershell
python Ichiro_3D_Arcane/suite/extract_spec_subviews.py `
  Ichiro_3D_Arcane/characters/ichiro_chibi/character_spec.json `
  --out Ichiro_3D_Arcane/characters/ichiro_chibi/derived/turnaround_v02
```

Each crop is linked to its parent image hash, normalized and pixel crop rectangle, label, dimensions, resolution class, and output hash in `subview_manifest.json`. Crops stay derived review assets and do not become primary canon by extraction. Crops under 128 px on the short side are flagged for coarse view continuity only, never face, retopology or texture detail.

For Ichiro Chibi, the first package is [here](../characters/ichiro_chibi/character_spec.json). `character_spec.schema.json` is the data contract; `stage_registry.json` records which pipeline stages are implemented, partial, candidate-only, or still unverified.
