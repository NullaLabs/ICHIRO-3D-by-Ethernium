# Decisión de autoría del rig — Blender y Unreal Engine 5.8

Fecha: 2026-10-28. Objetivo: producir primero Ichiro Chibi fiel y deformable;
la animación no es el entregable actual.

## Decisión

Mantener Blender como fuente de autoría para escultura, retopología, UV,
correctivos faciales, pesos y pruebas de poses. Exportar a Unreal Engine 5.8
cuando la geometría y el rig superen sus gates, para integración, evaluación de
Control Rig y revisión de materiales/iluminación en destino. No riggear ahora la
malla high-detail original en UE.

## Razones

- La malla original preserva la apariencia como referencia, pero todavía no es
  topología de deformación: sus islas, bordes y densidad no forman loops útiles
  de hombros, dedos, párpados ni boca.
- UE 5.8 admite creación de huesos, pintura de pesos y Control Rig dentro del
  editor; técnicamente es posible riggear allí. Eso no aporta herramientas de
  retopología y escultura que resuelvan las limitaciones actuales de esta malla.
- Mantener pesos, shape keys/correctivos y geometría en una sola fuente editable
  reduce bifurcaciones. La importación de FBX puede llevar malla esquelética y
  pesos, y UE puede crear su Control Rig desde el esqueleto importado.

## Flujo propuesto

1. En Blender: malla final retopologizada, una pieza de entrega con componentes
   topológicos separados permitidos para ojos/dientes/lengua, materiales/UV y
   correctivos para párpados, boca, mandíbula y manos.
2. Probar poses extremas en Blender: cierre ocular, cierre/apertura oral,
   mandíbula, sonrisa, puño, oposición del pulgar y articulaciones de los dedos.
3. Congelar revisión y exportar FBX de prueba con armature y skin weights.
   Conservar blend maestro; export no reemplaza la fuente.
4. En UE 5.8: importar como Skeletal Mesh, validar escala, ejes, pesos, morph
   targets/materiales y crear Control Rig para la necesidad de integración.
5. Retornar a Blender para corregir geometría, pesos o correctivos; reimportar
   una versión identificada. UE puede ser autoridad del Control Rig de destino,
   pero Blender permanece autoridad de la malla fuente.

## Cuándo convendría riggear enteramente en Unreal

Si el objetivo cambiara a un personaje exclusivamente para UE y la geometría ya
estuviera terminada, UE 5.8 sería una opción válida: Skeleton Editing documenta
creación de huesos y pintura de pesos, y Control Rig permite rigging dentro del
editor. Para este proyecto no se gana nada empezando ahí antes de completar la
topología facial, manos y cuerpo.

## Gates de exportación

- Identidad y siluetas aprobadas en todas las vistas canónicas.
- Topología deformable revisada, sin bordes abiertos accidentales ni colisiones.
- Pesos normalizados y probados en poses de estrés; correctivos faciales probados.
- FBX reimportado en una escena de prueba y comparado contra el maestro.

## Fuentes oficiales consultadas

- Epic, [Skeleton Editing in Unreal Engine 5.8](https://dev.epicgames.com/documentation/en-us/unreal-engine/skeleton-editing-in-unreal-engine): huesos y pesos pueden editarse en el editor, con Control Rig/Sequencer.
- Epic, [Rigging with Control Rig in Unreal Engine 5.8](https://dev.epicgames.com/documentation/en-us/unreal-engine/rigging-with-control-rig-in-unreal-engine): construcción y uso de rigs en UE.
- Epic, [FBX Skeletal Mesh Pipeline](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-skeletal-mesh-pipeline-in-unreal-engine): flujo de intercambio de meshes esqueléticas.
- Epic, [Interchange Import Reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/interchange-import-reference-in-unreal-engine): opciones de geometría, pesos y esqueleto al importar.

Esta decisión no certifica que el personaje esté listo para rig ni exportación.
