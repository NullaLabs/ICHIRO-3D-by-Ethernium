# Historial de comparación de proporciones faciales

Esta revisión detecta si conviene transferir los landmarks canónicos a la malla
high-detail. No es calibración de cámara ni diagnóstico definitivo de escultura.

## v01 — resultado invalidado

| Proporción | Referencia frontal | Render fuente | Diferencia relativa |
|---|---:|---:|---:|
| Separación entre centros oculares / distancia centro ocular–mentón | 0.599 | 0.905 | +51.0% |
| Centro ocular–nariz / centro ocular–mentón | 0.442 | 0.491 | +11.0% |
| Nariz–mentón / centro ocular–mentón | 0.559 | 0.511 | −8.7% |

La lectura de v01 puso nariz y mentón demasiado abajo en la referencia. La
estimación de +51% para la separación ocular quedó invalidada y no debe usarse
para cambiar la malla.

## Reproducción

- Coordenadas aproximadas del render: `references/source_face_landmarks_estimate_v01.json`.
- Coordenadas canónicas históricas: `references/canonical_face_landmarks_v01.json`.
- El informe histórico es `docs/FACE_PROPORTION_COMPARISON_V01.json`.
- `tools/render_source_face_landmarks_estimate.py` crea
  `renders/source_face_landmarks_estimate_v01.png` para revisar los puntos.

## v02 — corrección sobre cuadrícula de píxeles

La nariz, esquinas de boca y mentón se volvieron a leer sobre una cuadrícula de
20 px y un recorte ampliado. La relación separación ocular/centro-ocular–mentón
queda en 0.923 en la referencia y 0.905 en el render; diferencia aproximada
−1.9%. La alarma de discrepancia amplia desaparece. Esto no equivale a una
calibración de cámara ni valida la geometría completa.

- Landmarks corregidos: `references/canonical_face_landmarks_v02.json`.
- Lámina: `renders/canonical_face_landmarks_v02.png`.
- Herramienta: `tools/render_canonical_face_landmarks_v02.py`.
- Regenerar métricas: `python tools/compare_face_proportions.py`, que escribe
  `docs/FACE_PROPORTION_COMPARISON_V02.json`.

## Decisión

El resultado v02 ya no respalda el supuesto de ojos demasiado separados. Antes
de transferir landmarks a XYZ o construir una nueva tira, todavía hay que
registrar cámara y encuadre, medir error de reproyección y validar impactos
contra la región facial en vistas y perfiles. No ajustar la escultura a partir
de la falsa alarma v01.
