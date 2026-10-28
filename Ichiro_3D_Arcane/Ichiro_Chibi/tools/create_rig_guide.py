"""Create a non-animated rig guide for Ichiro Chibi's protected high source.

This establishes the required joint/control inventory.  It intentionally does
not bind weights: binding happens only after the final clean single mesh exists.
"""
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
INFILE=ROOT/'Ichiro_Chibi_HighDetail_Working.blend'
OUTFILE=ROOT/'exports'/'Ichiro_Chibi_RigGuide_UNBOUND.blend'
OUTFILE.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(INFILE))
src=bpy.data.objects.get('ICH_CHIBI_HIGHDETAIL_SOURCE__READONLY')
if not src: raise RuntimeError('High source missing')

bpy.ops.object.armature_add(enter_editmode=True, location=(0,0,0))
rig=bpy.context.object; rig.name='RIG_ICH_CHIBI_GUIDE__UNBOUND'
rig.data.name='ARM_ICH_CHIBI_GUIDE__UNBOUND'; rig.show_in_front=True
eb=rig.data.edit_bones
eb.remove(eb[0])
def bone(name,head,tail,parent=None):
    b=eb.new(name); b.head=head; b.tail=tail
    if parent: b.parent=eb.get(parent)
    return b

# Central deformation chain, Z is character vertical in the protected source.
bone('root',(0,0,-.50),(0,0,-.39))
bone('pelvis',(0,0,-.39),(0,0,-.20),'root')
bone('spine_01',(0,0,-.20),(0,0,-.04),'pelvis')
bone('spine_02',(0,0,-.04),(0,0,.10),'spine_01')
bone('chest',(0,0,.10),(0,0,.20),'spine_02')
bone('neck',(0,0,.20),(0,0,.28),'chest')
bone('head',(0,0,.28),(0,0,.47),'neck')
bone('jaw',(0,-.12,.29),(0,-.20,.28),'head')

# Provisional guide coordinates use a legacy front=-Y frame. The whole guide
# is rotated to the source convention (+X front, Y lateral, Z up) below.
for side,x in (('L',-.072),('R',.072)):
    bone(f'eye.{side}',(x,-.175,.350),(x,-.235,.350),'head')
    bone(f'lid_upper.{side}',(x,-.180,.380),(x,-.225,.380),'head')
    bone(f'lid_lower.{side}',(x,-.180,.325),(x,-.225,.325),'head')
    bone(f'brow.{side}',(x,-.165,.415),(x,-.215,.415),'head')
bone('lip_upper',(0,-.185,.275),(0,-.245,.275),'head')
bone('lip_lower',(0,-.185,.250),(0,-.245,.250),'jaw')

# Limb and digit inventory; correct manual retopo creates deformation loops at each.
for side,sgn in (('L',-1),('R',1)):
    x=sgn*.15
    bone(f'clavicle.{side}',(0,0,.14),(x,0,.15),'chest')
    bone(f'upper_arm.{side}',(x,0,.15),(sgn*.22,0,.02),f'clavicle.{side}')
    bone(f'forearm.{side}',(sgn*.22,0,.02),(sgn*.25,-.01,-.10),f'upper_arm.{side}')
    bone(f'hand.{side}',(sgn*.25,-.01,-.10),(sgn*.30,-.02,-.10),f'forearm.{side}')
    for digit,lateral_offset in (('thumb',.045),('index',.025),('middle',.005),('ring',-.015),('pinky',-.035)):
        p=f'hand.{side}'
        for n in range(1,4):
            finger_x=sgn*(.30+lateral_offset)
            z0=-.10-.025*(n-1); z1=z0-.025
            name=f'{digit}_{n}.{side}'
            bone(name,(finger_x,-.02,z0),(finger_x,-.02,z1),p); p=name
    bone(f'thigh.{side}',(sgn*.07,0,-.22),(sgn*.10,0,-.36),'pelvis')
    bone(f'shin.{side}',(sgn*.10,0,-.36),(sgn*.10,-.01,-.47),f'thigh.{side}')
    bone(f'foot.{side}',(sgn*.10,-.01,-.47),(sgn*.10,-.12,-.50),f'shin.{side}')

for guide_bone in eb:
    guide_bone.head=Vector((-guide_bone.head.y,guide_bone.head.x,guide_bone.head.z))
    guide_bone.tail=Vector((-guide_bone.tail.y,guide_bone.tail.x,guide_bone.tail.z))
bpy.ops.object.mode_set(mode='OBJECT')
rig['status']='UNBOUND GUIDE — bind only after final manual face/hand topology passes validation.'
rig['bones_required']='eyes, lids, jaw, lips, brows, hands and 5x3 finger chains included'
bpy.context.scene['character_front_axis']='+X; lateral=Y; up=Z'
bpy.context.scene['rig_stage']='Guide created; no animation and no automatic weights.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUTFILE))
print(f'SAVED {OUTFILE}; bones={len(rig.data.bones)}')
