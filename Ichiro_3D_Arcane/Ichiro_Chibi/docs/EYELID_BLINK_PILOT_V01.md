# Piloto de párpado: control de cierre y exportación para juego

Fecha: 2026-11-05. Estado: prueba técnica aislada; NO integrada en la cabeza.
El diseño y la fuente manifold de Ichiro permanecen intactos.

## Entrega

- `exports/eyelid_blink_pilot_v01/Ichiro_Eye_R_Blink_Pilot.blend`: escena pequeña,
  autónoma y editable. Objeto activo `EYE_R_GAME_BLINK_PILOT`; shape key `Blink_R`
  entre 0 y 1. No contiene keyframes ni animaciones.
- `exports/eyelid_blink_pilot_v01/Ichiro_Eye_R_Blink_Pilot.glb`: versión triangulada
  con morph target `Blink_R` y soporte ocular de diagnóstico.
- `renders/eyelid_blink_pilot_v01/`: estados estáticos, referencia del ojo actual,
  traza de contorno, métricas, prueba de reimportación y hashes de artefactos.

La letra R identifica el lado DERECHO DE LA IMAGEN desde una cámara en +X,
no una convención de huesos anatómicos. Esa nomenclatura debe resolverse al
integrar el rig completo.

## Construcción

El contorno se trazó sobre un render del modelo actual, a 1024 px, cámara
ortográfica con escala 0,10 y centro `(0,0.035,0.268)`. No se transfirieron
ciegamente los landmarks antiguos de otra imagen o cámara.

El párpado editable tiene **120 vértices, 96 quads y cinco anillos** de 24
vértices. Los anillos se expanden siguiendo las normales exteriores del
contorno 2D, a distancias de 0, 12, 30, 60 y 100 px. Sus vértices se proyectan
sobre la fuente con un pequeño desplazamiento de revisión en +X.

El cierre usa una curva compartida para pares superior/inferior. Se conservan
los dos extremos del ojo y el anillo exterior. La profundidad del cierre se
ajusta contra una superficie ocular de prueba derivada del modelo. Esta
superficie NO es todavía un globo ocular completo ni tiene iris funcional.

El archivo conserva una versión editable en quads, oculta por defecto. La
versión para juego usa **192 triángulos con diagonales fijas**, sobre los mismos
120 vértices y el mismo morph. La triangulación automática de los quads produjo
una inversión proyectada junto a un extremo al acercarse al cierre; la diagonal
fija elegida elimina ese defecto en las posiciones comprobadas. No dejar que
una exportación posterior decida arbitrariamente esas diagonales.

Las versiones editable, de juego y de wireframe son objetos de trabajo
separados. Sus sliders no están conectados por drivers: usar el del objeto de
juego para previsualizar. La receta los sincroniza al renderizar evidencia.

## Verificación ejecutada

Se comprobaron **21 posiciones**, desde 0 hasta 1 en incrementos de 0,05:

- Cero triángulos con orientación proyectada invertida en la versión de juego.
- Cero penetraciones detectadas contra **427 muestras** de la superficie ocular
  por posición: vértices, puntos medios y centros de caras.
- Separación máxima entre los pares de borde al cierre completo: **0**.
- Desplazamiento de los extremos del ojo y del anillo exterior: **0**.
- Área mínima de cara siempre positiva; mínimo observado aproximadamente
  `9.9843e-7` unidades cuadradas.

La comprobación de contacto es por muestras y proyección en +X. No es una
certificación exhaustiva de auto-intersecciones ni de colisiones continuas.
El cierre de una abertura implica contacto intencional entre bordes opuestos.

La receta se ejecutó completa en un nuevo proceso Blender 5.2 con factory
startup. Después se reimportó el GLB en otra escena vacía:

- Un morph `Blink_R`, con peso inicial 0, conservado.
- 120 correspondencias únicas entre los vértices exportados y la referencia.
- Error máximo neutral y de cierre: **0** en esa reimportación.
- Cero acciones de animación.

Esto prueba el transporte del morph mediante GLB en Blender; todavía no se
probó en Unreal o Unity ni hay esqueleto enlazado.

## Reproducir

Desde `Ichiro_Chibi/`, con la fuente reparada disponible mediante Git LFS:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python tools/build_eyelid_blink_pilot_v01.py -- --out E:/WORKSPACE/Ichiro/nuevo_piloto_ojo
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python tools/verify_eyelid_glb_roundtrip.py -- --dir E:/WORKSPACE/Ichiro/nuevo_piloto_ojo
```

El constructor exige una salida sin escena previa. Sólo limpia la copia de
trabajo en memoria para entregar un `.blend` pequeño; nunca guarda sobre la
escena fuente.

## Pendiente antes de integrarlo en producción

El parche tiene bordes abiertos intencionales para su futura unión a la cara.
No es una pieza imprimible ni reemplaza por sí solo la cabeza manifold.
Todavía faltan la apertura real en la malla facial de juego, continuidad de los
loops hacia mejilla/ceja/nariz, globo e iris funcionales, espesor del borde,
UV/materiales y pruebas con mirada y expresiones. Los materiales mostrados son
de diagnóstico: no representan un cambio de diseño de Ichiro.

Siguiente decisión: integrar la zona orbital conservando la forma original y
validar la unión antes de replicar el método en el ojo parcialmente oculto.
Mantener Astra para esa decisión geométrica; usar Sol 6.1 cuando la operación a
replicar tenga entradas, límites y criterios de aceptación definidos.
