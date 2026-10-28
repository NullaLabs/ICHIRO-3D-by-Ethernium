# Ichiro Chibi — contrato de anatomía riggeable

La entrega `ICH_CHIBI_FINAL_SINGLE_MESH` será un único objeto de malla, pero
contendrá componentes topológicamente separados dentro de ese objeto cuando lo
requiera la deformación o el shading (por ejemplo globos oculares). No se usarán
objetos flotantes como sustituto de anatomía.

## Cara

- Dos globos oculares completos, con superficie esférica limpia y orientación
  independiente para controles `eye.L` / `eye.R`.
- Párpado superior e inferior con loops concéntricos que cierran al ojo y
  permiten parpadeo, squash y mirada extrema.
- Boca con borde labial, cavidad oral, interior oscuro, lengua y dientes cuando
  sean visibles; loops radiales para sonrisa, fonemas y compresión Chibi.
- Ceja y puente nasal integrados a la lectura de la cara; no depender de textura
  para expresar el volumen.

## Manos

- Palma, pulgar y cuatro dedos identificables por mano, cada uno con al menos
  tres zonas de flexión legibles para los huesos digitales.
- Webbing/espacio entre dedos suficiente para que no colapsen en puño.
- Guante/placas con holgura visual o weights de correctivo; no pegar placas a
  los nudillos como geometría rígida sin articulación.

## Retopología por regiones

1. Cuerpo, chaqueta, pantalón y botas: candidato automático como guía de
   densidad, después corrección manual.
2. Cabeza, ojos, párpados, boca y orejas: retopología manual dirigida por
   expresiones; nunca aceptar voxel/QuadriFlow como topología final.
3. Manos y dedos: retopología manual dirigida por articulaciones; nunca
   fusionar dedos por proximidad.

## Gate antes de rig

- Una sola malla de producción; un armature separado.
- Sin bordes abiertos no intencionales ni non-manifold en la piel/cuerpo.
- Prueba de parpadeo, mirada, `A/E/I/O/U`, sonrisa, puño y dedos extendidos.

## Resultado de la prueba automática (Pass 01)

`ICH_CHIBI_RETOPO_BODY__QF30K__NOT_FACE_OR_HANDS` es una cáscara cerrada de
13.864 vértices y 13.868 caras, con cero bordes abiertos y cero aristas
non-manifold. QuadriFlow no pudo resolver el flujo de la fuente abierta, por lo
que la fase voxel creó la topología cerrada de partida. Se acepta sólo como
referencia de volumen/densidad corporal: **no** se acepta para rostro, ojos,
párpados, boca, manos, dedos, ropa o baking final.
