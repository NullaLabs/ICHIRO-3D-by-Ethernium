# Alineación de contornos oculares — v01

> Versión histórica superada por `EYE_BROW_SEPARATION_V03.md`. V01 y v02
> usaban un landmark superior que estaba anotado en la ceja.

Se trazó a mano el borde visible de ambos ojos en `skin_review_source.png`,
guiándose por cuadrícula de 10 px. Cada trazo corresponde por orden a los diez
puntos del contorno canónico v02, ya transferidos por la afinidad 2D de cinco
anclas.

| Lado | RMS entre trazos | Error relativo al espacio ocular | Desvío medio del arco superior |
|---|---:|---:|---:|
| Izquierdo de imagen, parcial bajo flequillo | 26.84 px | 11.42% | −33.67 px |
| Derecho de imagen | 16.10 px | 6.85% | −23.32 px |

El signo negativo indica que el contorno canónico transformado aparece por
encima del borde ocular trazado en el render fuente. En la superposición
`renders/eye_contour_alignment_v01.png`, verde es el trazo visible fuente y
rojo/cian son los contornos canónicos registrados.

Estos valores describen una diferencia entre dos imágenes y una máscara por
color incompleta. Las trazas no son límites anatómicos certificados; podrían
reflejar error de cámara/registro, distinta forma de liner o puntos manuales.
No mover el ojo ni generar parches con base en este reporte. La tarea siguiente
es revisar y corregir los landmarks oculares sobre ambas vistas, luego
comprobarlos en perfiles y delimitar piel antes de hacer retopología.

Regenerar con `python tools/compare_eye_contours.py`. Datos: `references/source_eye_contours_estimate_v01.json` y `docs/FACE_REGISTRATION_PROBE_V02.json`.
