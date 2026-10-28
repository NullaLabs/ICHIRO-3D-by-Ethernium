# Bloque siguiente — Topología de cabeza y manos

## Decisión

La fuente `ICH_CHIBI_HIGHDETAIL_SOURCE__READONLY` queda congelada como
superficie visual de proyección y referencia 360. No se remeshea, booleaniza
ni usa como base de rig. Conserva muy bien el diseño, pero es una concha de
alta densidad con bordes abiertos e islas de geometría, no topología de
producción.

El `BODY_RETOPO_CANDIDATE` queda como guía de volumen; no se usará como cara,
manos, ropa final ni personaje final.

## Entregable inmediato

Crear `HEAD_HANDS_TOPOLOGY_PASS01` con módulos temporales no destructivos
sobre la fuente de alta densidad:

1. Cabeza: cráneo, mandíbula, dos ojos esféricos, 3–4 loops concéntricos por
   párpado, 5–7 anillos de boca, labios y cavidad oral con dientes y lengua.
2. Mano izquierda y derecha: palma, pulgar y cuatro dedos; tres zonas de
   flexión por dedo, separación física entre dedos y loops de nudillos.
3. Validación clay y wireframe en los ocho ángulos, contra todas las imágenes
   de `references/`.

No unir al cuerpo, riggear ni hornear hasta aprobar este bloque.

## Presupuesto de topología de héroe

Objetivo previo a LOD: 70–95k quads (140–190k triángulos), compuesto por:

- Cabeza: 18–24k quads.
- Cuerpo y ropa: 32–42k quads.
- Manos: 5–7k quads en total.
- Cabello: 10–16k quads; mechones fusionados mediante transiciones modeladas,
  no placas flotantes.
- Botas y accesorios integrados: 8–12k quads.

La entrega final será un solo objeto de malla. Piel, ropa y accesorios podrán
usar varias ranuras de material; ojos, dientes y lengua podrán ser componentes
topológicamente separados dentro de ese objeto único.

## Gates de aprobación

- Silueta coherente en frontal, trasera, ambos perfiles y cuatro 3/4.
- Cero caras internas, non-manifold, vértices sueltos o bordes abiertos
  involuntarios.
- Ojos completos, párpados funcionales, boca con volumen y dedos articulables.
- Sólo después: UV, bake normal/AO/curvature, rig de 62 huesos y correctivos.

La proporción no se altera: cabeza dominante (aprox. 42–45% de la altura hasta
el mentón), torso compacto, piernas cortas, botas grandes y manos a media
altura de muslo.
