# Separación de ceja y párpado — corrección v03

La inspección de la cuadrícula mostró que el landmark superior del ojo derecho
en v02 (`[228,96]`) estaba sobre el trazo de ceja. Se movió al borde ocular
visible (`[226,101]`) y se anotó la ceja como curva aparte. El contorno izquierdo
se marcó parcial, con extremos ocluidos de menor confianza. La lámina
`renders/canonical_eye_brow_regions_v03.png` distingue ambas regiones.

Con los mismos cinco anclajes 2D, la comparación con el render fuente cambia:

| Región | RMS v02 | RMS v03 | Arco superior RMS v02 → v03 |
|---|---:|---:|---:|
| Ojo derecho visible | 16.10 px | 5.45 px | 24.56 → 5.39 px |
| Ojo izquierdo parcial | 26.84 px | 15.10 px | 39.42 → 14.76 px |

La reducción indica que la discrepancia superior anterior era principalmente
un landmark mal clasificado, no evidencia de que hubiera que bajar la ceja o
mover el ojo. El ojo izquierdo sigue sin calibrarse porque el pelo tapa su
esquina y parte del arco.

## Límite antes de construir

El contorno derecho ya se alinea visualmente, pero la máscara cálida solo ofrece
candidato de textura para 7/20 muestras del contorno. En anillos expandidos al
12% del centro ocular, 7/10 son candidatos, 3/10 no tienen clasificación de
piel; el BVH sí encuentra superficie fuente. Falta una región facial/eyelid
etiquetada por imagen o muestreo UV exacto en el punto de impacto. Aún no es
seguro producir una banda de párpado riggeable.

Reproducir:

```powershell
blender --background --factory-startup --python-exit-code 1 --python tools/register_canonical_face_to_source.py
python tools/compare_eye_contours.py
python tools/render_canonical_face_regions_v03.py
python tools/render_face_registration_probe.py
```

## Revisión 3D de las curvas

Los impactos `full_hit` del informe v03 se dibujaron como cuatro curvas de
revisión sobre la superficie de la malla fuente: contorno derecho, segmento
ocular izquierdo visible, ceja derecha y segmento visible de ceja izquierda.
La vista frontal confirma la alineación del contorno derecho con el párpado;
las dos vistas oblicuas mantienen el trazo sobre la superficie. El flequillo
oculta parte del ojo y ceja izquierdos, por lo que esos trazos siguen abiertos.

En la sesión viva de Blender se crearon en la colección
`CANONICAL_EYE_BROW_GUIDES_V03__REVIEW_ONLY`, con `hide_render=True`. No son
párpados ni loops listos para rig: son guías delgadas y reversibles. La carga
de la colección guardada desde otro `.blend` fue rechazada por el modo seguro
del MCP; se reconstruyeron en la sesión a partir de los impactos 3D publicados
en el JSON, sin tocar ni guardar el archivo principal. Para repetir, ejecutar
`tools/build_eye_brow_surface_guides_v03.py` en una copia derivada del blend.
Se omitió el render por lotes en segundo plano porque EEVEE agotó memoria al
crear buffers de la malla densa; la revisión visual se hizo en el viewport del
Blender abierto.

El cálculo y las curvas permanecen como diagnóstico; no se modificó la malla
fuente ni se aprobó todavía una banda ocular riggeable.
