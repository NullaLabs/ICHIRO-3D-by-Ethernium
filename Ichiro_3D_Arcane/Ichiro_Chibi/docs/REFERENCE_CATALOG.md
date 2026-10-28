# Catálogo de referencias — Ichiro Chibi

Estado: seis imágenes visuales indexadas; sus roles son distintos. Las láminas generadas no se interpretan como datos 3D calibrados.

## Jerarquía y uso

| Archivo | Uso dentro del flujo | Confianza / límite |
|---|---|---|
| `references/ichiro_chibi_front.png` | Silueta frontal y lectura de cara, pecho, manos y proporción | Placa principal. La cámara y la sombra de suelo no tienen calibración publicada. |
| `references/ichiro_chibi_back.png` | Volumen posterior, pelo, chaqueta, cinturón y pantalón | Placa principal con las mismas limitaciones de cámara. |
| `references/ichiro_chibi_left.png` | Perfil izquierdo: frente de cara, cráneo, nariz, pecho, manos y calzado | Placa principal. |
| `references/ichiro_chibi_right.png` | Perfil opuesto: profundidad del pelo, mandíbula, torso, equipo y calzado | Placa principal. |
| `references/ichiro_chibi_8view_turnaround.png` | Ocho ángulos del mismo diseño; revisión secundaria de continuidad y volumen entre perfiles y 3/4 | Menor resolución, encuadres por panel y cámara sin calibrar. Sus IoU sirven solo como evidencia auxiliar. |
| `references/ichiro_chibi_kimi_pipeline_board.png` | Referencia de intención visual y temas de producción: topología, cara, mapas, ropa y materiales | Collage de estudio. No proporciona malla, UV, mapas ni topología fuente verificables. |

Las cuatro placas individuales son las restricciones de silueta con mayor peso. La hoja de ocho ángulos amplía la revisión a la rotación; el collage de proceso informa decisiones de acabado, pero no sustituye archivos de producción. La forma del modelo solo cambia después de cotejar estas fuentes y revisar el overlay visualmente.

## Landmarks y trazos faciales

- `canonical_face_landmarks_v01.json` a `v03.json`: anotaciones 2D manuales sobre `ichiro_chibi_front.png`. La v03 es la revisión más reciente de márgenes oculares; indica explícitamente que el ojo izquierdo está parcialmente oculto por el flequillo. No son landmarks 3D ni anatomía aprobada.
- `source_face_landmarks_estimate_v01.json` y `v02.json`, `source_eye_contours_estimate_v01.json` y `eyelid_landmarks_review.json`: estimaciones sobre renders de la fuente actual. Se usan para registro y diagnóstico local; no se deben proyectar a la malla como posiciones canónicas.

Toda coordenada de pantalla conserva su referencia, escala, lado de la imagen, visibilidad y confianza. Los puntos o curvas ocluidos permanecen marcados como inciertos y no guían una operación destructiva.

## Comparación 2D implementada

`tools/project_reference_silhouettes.py` proyecta la malla `ICH_CHIBI_HIGHDETAIL_SOURCE__READONLY` mediante rayos ortográficos CPU contra un BVH de Blender. Produce máscaras PGM a ocho azimuts alrededor de Z, con el frente en `+X` y los perfiles en `±Y`. No usa motor de render, materiales, GPU ni add-ons y escribe `source_scene_saved: false` en el manifiesto.

`tools/score_reference_fit.py` compara esas máscaras con las cuatro placas grandes y con los ocho paneles recortados de la hoja. Para las placas, estima el fondo gris degradado usando medianas por fila tomadas en los bordes laterales; para la hoja, usa recortes fijos 4 × 2 con márgenes y excluye la franja de etiquetas. El umbral, las máscaras, los recortes y los overlays quedan guardados junto al informe. Requiere NumPy y Pillow en el Python anfitrión; el script de proyección usa la API incluida en Blender 5.2.

La ejecución actual usa umbral RGB residual 24. La máscara aún recoge parte de la sombra de suelo y es sensible al umbral: en la placa frontal, cambiarlo de 24 a 32 y 40 mueve IoU de 0,432 a 0,514 y 0,558. El aumento no prueba una mejora del modelo: al elevar el umbral se pierden bordes de bajo contraste. Por ello, las puntuaciones son señales para localizar diferencias, nunca puertas automáticas ni aprobación de parecido.

### Baseline visual del archivo fuente

Resultados de `renders/reference_fit_v02_cpu/comparison/reference_fit_report.json`:

| Grupo | Vista | IoU | Lectura |
|---|---:|---:|---|
| Placas grandes | Frente | 0,432 | Diagnóstico provisional |
| Placas grandes | Espalda | 0,421 | Diagnóstico provisional |
| Placas grandes | Perfil izquierdo | 0,518 | Diagnóstico provisional |
| Placas grandes | Perfil derecho | 0,404 | Diagnóstico provisional |
| Hoja 8 vistas | Ocho ángulos | 0,640–0,708 | Secundario; la baja resolución limita la precisión |

En las placas frontales, la relación ancho/alto del bbox medido en la fuente es aproximadamente 16–17 % menor que la de la máscara de referencia. Esa diferencia aún mezcla silueta, sombra, perspectiva y encuadre; se registra como hipótesis para revisión, no como instrucción para ensanchar el personaje. Los perfiles están más cerca en esa métrica simple.

## Reproducción

Desde `Ichiro_Chibi/`, con Blender 5.2 disponible:

```powershell
blender --background --factory-startup Ichiro_Chibi_HighDetail_Working.blend --threads 4 --python-exit-code 1 --python tools/project_reference_silhouettes.py -- --out renders/reference_fit_v02_cpu/projections --resolution 384
python tools/score_reference_fit.py --renders renders/reference_fit_v02_cpu/projections --output-dir renders/reference_fit_v02_cpu/comparison
```

El segundo comando rehace el informe, máscaras de referencia, overlays, recortes del turnaround y hojas de contacto. `--threshold` permite probar otro residual sin cambiar la malla ni la escena. Se debe revisar la hoja y no escoger el umbral que produzca el IoU más alto.

## Siguiente mejora del comparador

La forma de hacer la segmentación reproducible y menos sesgada es guardar máscaras revisadas manualmente para las cuatro placas, con un overlay de corrección y versión/hash de la imagen. El modelo de fondo automático seguirá siendo una propuesta inicial. Después se calibra la cámara de cada placa y se compara ancho por regiones (cabeza, torso, piernas, botas) además del IoU global. No se instalará otro addon ni dependencia para este cambio.

## Referencias técnicas

- Blender API, `BVHTree`: https://docs.blender.org/api/current/mathutils.bvhtree.html
- Manual Blender 5.2, límites de remesh automático en retopología: https://docs.blender.org/manual/en/5.2/modeling/meshes/retopology.html
- Blender Studio, flujo de personaje estilizado y edge flow: https://studio.blender.org/training/stylized-character-workflow/
- ModelSheetTo3D, investigación de alineación entre hoja de diseño y reconstrucción 3D: https://onlinelibrary.wiley.com/doi/10.1111/cgf.70323
