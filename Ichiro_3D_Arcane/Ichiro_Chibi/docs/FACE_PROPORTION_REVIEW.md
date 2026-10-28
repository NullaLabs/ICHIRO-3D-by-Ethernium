# Comparación preliminar de proporciones faciales

Esta revisión detecta si conviene transferir los landmarks canónicos a la malla
high-detail. No es calibración de cámara ni diagnóstico definitivo de escultura.

## Resultado de la lectura manual v01

| Proporción | Referencia frontal | Render fuente | Diferencia relativa |
|---|---:|---:|---:|
| Separación entre centros oculares / distancia centro ocular–mentón | 0.599 | 0.905 | +51.0% |
| Centro ocular–nariz / centro ocular–mentón | 0.442 | 0.491 | +11.0% |
| Nariz–mentón / centro ocular–mentón | 0.559 | 0.511 | −8.7% |

La primera proporción sugiere que la colocación ocular del render fuente podría
ser demasiado ancha respecto al tercio inferior. Los puntos son aproximados; la
referencia canónica y el render usan encuadres distintos. Por lo tanto el valor
solo activa una revisión artística y bloquea la proyección automática, no
autoriza mover los ojos ni redimensionar el rostro.

## Reproducción

- Coordenadas aproximadas del render: `references/source_face_landmarks_estimate_v01.json`.
- Coordenadas canónicas de referencia: `references/canonical_face_landmarks_v01.json`.
- Ejecutar `python tools/compare_face_proportions.py` para regenerar
  `docs/FACE_PROPORTION_COMPARISON_V01.json`.
- `tools/render_source_face_landmarks_estimate.py` crea
  `renders/source_face_landmarks_estimate_v01.png` para revisar los puntos.

## Decisión

Antes de construir otra tira de párpado: registrar cámara y encuadre con varias
correspondencias confiables, medir error de reproyección y comparar proporciones
de frente y perfiles. Si persiste el desajuste, corregir la forma del rostro en
una capa de escultura reversible y volver a evaluar contra todas las vistas.
