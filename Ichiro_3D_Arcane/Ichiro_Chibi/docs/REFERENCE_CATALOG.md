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

`tools/score_reference_fit.py` compara esas máscaras con las cuatro placas grandes y con los ocho paneles recortados de la hoja. `--segmenter auto` utiliza GrabCut de OpenCV en las cuatro imágenes de alta resolución, inicializado con un rectángulo encontrado por el modelo del fondo; fija la semilla aleatoria en 0 y registra la versión de OpenCV. Para los paneles pequeños usa el modelo de fondo por medianas de bordes, ya que GrabCut recortó partes de varios perfiles a baja resolución. Si OpenCV no está disponible, `auto` cae al modelo de fondo para todas las vistas; `--segmenter border` permite fijar ese modo. OpenCV es opcional y no se instaló en este pase. Además de IoU, calcula anchura de silueta por 49 alturas normalizadas para las cuatro placas grandes. El gráfico `reference_fit_width_profiles.png` superpone referencia y fuente sin asignar nombres anatómicos automáticos a cada franja. El informe incluye hash de la fuente y del manifiesto de proyección, así como cualquier transformación experimental. Requiere NumPy y Pillow en el Python anfitrión; el script de proyección usa la API incluida en Blender 5.2.

Para corregir una máscara con trazos manuales, `--manual-masks-dir` acepta PNGs escala de grises, blanco = personaje y negro = fondo. Deben conservar el tamaño exacto de la placa o recorte. Los nombres son `ortho_front.png`, `ortho_back.png`, `ortho_left.png`, `ortho_right.png` y `turnaround_<vista>.png`; solo los archivos presentes sustituyen el segmentador automático. El informe guarda hash, tamaño y área de cada override usado. Esto permite corregir flecos/sombras en cualquier editor de imagen sin instalar una herramienta y mantener la revisión reproducible.

El modelo de fondo de los ocho paneles usa umbral RGB residual 24. El GrabCut de las cuatro placas grandes elimina más sombra de suelo y hace que sus IoU y relaciones ancho/alto cambien poco o nada con ese umbral. Las máscaras todavía dependen de la inicialización automática y de cámaras que no se han calibrado. Los scores sirven para localizar diferencias, nunca como puertas automáticas ni aprobación de parecido.

### Baseline visual del archivo fuente

Resultados de `renders/reference_fit_v02_cpu/comparison/reference_fit_report.json`:

| Grupo | Vista | IoU | Lectura |
|---|---:|---:|---|
| Placas grandes | Frente | 0,560 | GrabCut, diagnóstico provisional |
| Placas grandes | Espalda | 0,539 | GrabCut, diagnóstico provisional |
| Placas grandes | Perfil izquierdo | 0,520 | GrabCut, diagnóstico provisional |
| Placas grandes | Perfil derecho | 0,515 | GrabCut, diagnóstico provisional |
| Hoja 8 vistas | Ocho ángulos | 0,640–0,708 | Secundario; la baja resolución limita la precisión |

Con GrabCut, las razones de bbox ancho/alto de la fuente y referencia son muy cercanas: frente 0,485/0,493; espalda 0,485/0,482; perfil izquierdo 0,427/0,428; perfil derecho 0,427/0,429. La medición inicial que mostraba una discrepancia frontal de 16–17 % estaba sesgada por la sombra de suelo. No hay evidencia de que se deba ensanchar la fuente. Los IoU restantes miden diferencias locales de contorno y todavía mezclan perspectiva y encuadre.

## Reproducción

Desde `Ichiro_Chibi/`, con Blender 5.2 disponible:

```powershell
blender --background --factory-startup Ichiro_Chibi_HighDetail_Working.blend --threads 4 --python-exit-code 1 --python tools/project_reference_silhouettes.py -- --out renders/reference_fit_v02_cpu/projections --resolution 384
python tools/score_reference_fit.py --renders renders/reference_fit_v02_cpu/projections --output-dir renders/reference_fit_v02_cpu/comparison --segmenter auto
```

El segundo comando rehace el informe, perfiles de anchura, máscaras de referencia, overlays, recortes del turnaround y hojas de contacto. Para una salida sin OpenCV, usar `--segmenter border`; el informe registra método y versiones para que las salidas no se confundan. `--threshold` controla el modelo de fondo de los paneles pequeños. Para aplicar una carpeta de máscaras corregidas, añade `--manual-masks-dir <carpeta>`. Se debe revisar la hoja y las curvas, no elegir ajustes por maximizar IoU.

## Siguiente mejora del comparador

La forma de hacer la segmentación reproducible y menos sesgada es guardar máscaras revisadas manualmente para las cuatro placas, con un overlay de corrección y versión/hash de la imagen. El modelo de fondo automático seguirá siendo una propuesta inicial. Después se calibra la cámara de cada placa y se compara ancho por regiones (cabeza, torso, piernas, botas) además del IoU global. No se instalará otro addon ni dependencia para este cambio.

## Referencias técnicas

- Blender API, `BVHTree`: https://docs.blender.org/api/current/mathutils.bvhtree.html
- OpenCV, segmentación GrabCut y retoque manual de errores: https://docs.opencv.org/4.x/d8/d83/tutorial_py_grabcut.html
- Manual Blender 5.2, límites de remesh automático en retopología: https://docs.blender.org/manual/en/5.2/modeling/meshes/retopology.html
- Blender Studio, flujo de personaje estilizado y edge flow: https://studio.blender.org/training/stylized-character-workflow/
- ModelSheetTo3D, investigación e implementación oficial: https://onlinelibrary.wiley.com/doi/10.1111/cgf.70323 y https://github.com/hjyoon02/ModelSheetTo3D

ModelSheetTo3D sirve como referencia para alinear hojas de modelo con geometría, no como dependencia inmediata: su README documenta un entorno Conda con PyTorch 2.6/CUDA 12.6, Blender 4.3.2 y RTX 4090. Para Ichiro conviene reutilizar sus ideas de correspondencia entre vistas sin incorporar ese entorno pesado; no produce por sí solo la topología facial/anatómica lista para rig.
