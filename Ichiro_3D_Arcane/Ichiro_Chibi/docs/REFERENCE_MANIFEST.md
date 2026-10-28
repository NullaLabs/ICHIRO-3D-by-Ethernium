# Ichiro Chibi — reference manifest

> **Topología de entrega:** ver `SINGLE_CHARACTER_CONTRACT.md`. El resultado
> final es una malla única; las capas de trabajo no modifican ese requisito.

## Canonical reconstruction evidence

These images are the only visual authority for the first Ichiro Chibi build.
They are copied into this workspace so the build remains reproducible.

| Asset | Role in reconstruction | Authority |
| --- | --- | --- |
| `references/ichiro_chibi_front.png` | Primary width, face, chest-core, boot and frontal hair silhouette | Locked silhouette anchor |
| `references/ichiro_chibi_back.png` | Back hair mass, jacket hem, belt and heel silhouette | Locked silhouette anchor |
| `references/ichiro_chibi_left.png` | Shaved temple, ear/hoop, facial projection and side depth | Locked depth anchor |
| `references/ichiro_chibi_right.png` | Fringe mass, nose/chin and opposite side depth | Locked depth anchor |
| `references/ichiro_chibi_8view_turnaround.png` | Intermediate-angle consistency and pose language | Validation reference |
| `references/ichiro_chibi_kimi_pipeline_board.png` | Kimi's proposed stages, component breakdown and material reference | Process reference only |

## Character invariants

- Chibi build: oversized head, compact torso, short limbs and enlarged boots.
- Asymmetric teal-black hairstyle: long front fringe, shaved patterned temple and gold hoop.
- Cropped light camouflage jacket over a bright orange-red chest core.
- Dark armored gauntlets, cargo trousers, black boots with orange-red accents.
- No blades in the first reconstruction pass. Weapons begin after body, costume and hair pass silhouette review.

## Validation order

1. Front/back silhouette.
2. Left/right head depth, hair and jacket profile.
3. Eight-angle continuity.
4. Separate-mesh intersections and material boundaries.
5. High-frequency sculpt and texture work.

## Non-destructive rule

The working scene must retain the reference empties, the locked base collection and separate costume, hair and detail collections. No destructive remesh, joined mesh or applied modifier is allowed before visual approval of the previous validation stage.
