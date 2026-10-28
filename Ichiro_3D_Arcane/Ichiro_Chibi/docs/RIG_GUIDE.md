# Rig guide — Ichiro Chibi

`blend/Ichiro_Chibi_RigGuide.blend` contains `RIG_ICH_CHIBI_GUIDE__UNBOUND`.
It is a 62-bone structural guide, not an animation and not a bound final rig.

Included controls/joints:

- Root, pelvis, spine, chest, neck, head and jaw.
- Left/right eye, upper lid, lower lid and brow.
- Upper and lower lip guides.
- Clavicle, upper arm, forearm, hand, thigh, shin and foot per side.
- Thumb, index, middle, ring and pinky, each with three phalange chains per
  hand.

Before skinning, manually rebuild the final face and hands over the high source,
then bind only `ICH_CHIBI_FINAL_SINGLE_MESH`. Do not bind the protected source
or the voxel body candidate.
