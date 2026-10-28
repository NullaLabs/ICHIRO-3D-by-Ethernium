# Ichiro Chibi — contrato de malla única

## Resultado exigido

El asset final será `ICH_CHIBI_FINAL_SINGLE_MESH`: una sola malla de personaje,
con topología continua, sin objetos de vestuario flotando dentro del cuerpo y
sin interpenetraciones utilizadas para simular unión. Puede conservar varios
material slots (piel, pelo, tela, metal, emisivo), pero no varios objetos de
geometría.

## Por qué no se colapsa al principio

Una malla única no significa modelar todo como una masa desde el primer minuto.
Las placas, cabello, chaqueta y anatomía se construyen como capas revisables
para medir cada silueta contra las referencias. Tras aprobar cada módulo, sus
uniones se reconstruyen como superficies continuas y se retopologiza una única
vez. Un `Join` temprano sólo convierte intersecciones en un problema difícil de
arreglar.

## Gates obligatorios

1. `ICH_CHIBI_VISUAL_HULL__LOCKED`: una malla única de evidencia volumétrica;
   no se edita.
2. Módulos temporales: sólo para diseño y evaluación 360; ninguno se exporta.
3. `ICH_CHIBI_HIGH_SINGLE_SURFACE`: fusión de superficie real, comprobada sin
   caras interiores, bordes abiertos ni non-manifold.
4. `ICH_CHIBI_FINAL_SINGLE_MESH`: retopología de producción, UV, material
   slots y mapas baked. Es el único objeto autorizado para rig/export final.

## Definición de terminado

- Una sola malla de producción y una sola armature cuando llegue el rig.
- Siluetas y detalles verificables frente a las seis referencias suministradas.
- Sin modifiers destructivos aplicados antes de tener una copia bloqueada y una
  revisión visual aprobada.
