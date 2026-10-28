# Diagnóstico segmentado de contornos oculares — v02

> Histórico, superado para evaluar el ojo derecho por `EYE_BROW_SEPARATION_V03.md`:
> el punto superior canónico de v02 estaba sobre la ceja, no sobre el párpado.

Esta versión desglosa los mismos trazos estimados por cantos, arco superior e
inferior. Un delta vertical negativo indica que el contorno canónico registrado
queda por encima del borde visible trazado en el render fuente.

| Región | Cantos RMS | Arco superior RMS / delta Y | Arco inferior RMS / delta Y |
|---|---:|---:|---:|
| Ojo derecho visible | 5.70 px | 24.56 px / −23.32 px | 5.38 px / +3.97 px |
| Ojo izquierdo parcial | 19.10 px | 39.42 px / −33.67 px | 8.02 px / −6.11 px |

El patrón del ojo derecho es claro en esta comparación: cantos e inferior se
alinean razonablemente, mientras el arco superior no. No escalar ni trasladar
todo el ojo para compensar. Primero corregir/revisar los puntos superiores y
separarlos de la ceja en ambas imágenes. El ojo izquierdo tiene menor confianza
por oclusión de cabello.

El resultado depende de trazos manuales sobre un render y de una transformación
afín 2D. No determina qué fuente es correcta, ni equivale a anatomía o
topología aprobadas. Usarlo como guía de revisión y no como orden de deformación.

Regenerar: `python tools/compare_eye_contours.py`. Datos completos:
`docs/EYE_CONTOUR_ALIGNMENT_V02.json` y superposición
`renders/eye_contour_alignment_v02.png`.
