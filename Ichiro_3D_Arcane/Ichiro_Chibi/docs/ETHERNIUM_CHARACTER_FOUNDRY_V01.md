# Ethernium Character Foundry — arquitectura v0.1

Fecha: 2026-10-28  
Alcance inicial: Ichiro Chibi; luego personajes nuevos desde un paquete de referencias.  
Estado: diseño del sistema; no es aprobación de la geometría actual.

## Decisión de diseño

Adoptar el patrón **reglas + parámetros nombrados + build reproducible + revisión + diff**, inspirado en generadores procedurales. No copiar la idea de que una semilla pueda cambiar cualquier cosa. En Ichiro, la identidad visual es dato bloqueado; una semilla solo puede variar módulos secundarios que el artista haya habilitado explícitamente.

El sistema tendrá dos salidas distintas:

1. **Canon build**: parámetros, landmarks y selección de módulos fijados por referencia; misma entrada produce la misma geometría y los mismos informes.
2. **Exploration builds**: variaciones etiquetadas, con semilla y diff de parámetros; nunca reemplazan el canon ni se mezclan con él sin revisión.

Geometry Nodes sirve para módulos paramétricos editables y repetibles. Blender Python sirve para construir escenas, medir, generar informes, comparar y guardar derivados. La escultura manual sigue siendo la vía de autoría para planos faciales, anatomía, pliegues y silueta con intención.

## Qué tomamos de la conversación pegada

| Idea del artículo | Aplicación aquí | Límite |
|---|---|---|
| Reglas antes que piezas puestas a mano | Cada módulo declara inputs, dependencias y salidas | No forzar una forma artística ambigua a una ecuación pobre |
| Parámetros nombrados | Proporciones, offsets, radios, espesores, cámara y tolerancias viven en un manifiesto | Los valores deben medirse de las referencias; no inventar constantes universales |
| Semilla reproducible | Solo accesorios o variación de diseño opcional; guardar seed y versión | El pelo canónico, los rasgos faciales y la silueta de Ichiro no se aleatorizan |
| Script y escena como producto | Guardar fuente del generador, parámetros, hashes, versión Blender, informe y escena derivada | El `.blend` generado no sustituye el código fuente ni el archivo maestro |
| Censo además de render | Métricas de malla, conectividad, escala, distancias e intersecciones junto a hoja visual | Ningún censo numérico prueba parecido, expresión o gusto artístico |
| Ciclo generar → medir → criticar → parche pequeño | Un cambio delimitado por pase, diff explícito y retorno a la misma batería de vistas | No aceptar el texto del modelo como prueba de que el cambio ocurrió |
| Fijar versión/API | Registrar Blender exacto y comprobar enum/propiedades presentes en runtime | La API y las versiones siguen cambiando; pin no significa compatibilidad eterna |

El artículo sobre Opus y Blender reporta resultados de un benchmark propio; no hemos reproducido sus cifras. Sus recomendaciones prácticas —fijar versión, usar asserts, revisar geometría invisible al render y parchear parámetros acotados— coinciden con los problemas que encontramos en los pases de párpado. En Blender 5.0 hubo cambios de API documentados oficialmente, por lo que cada build debe declarar y consultar su versión real.

## Arquitectura propuesta

### A. `character_spec.json` — fuente de verdad por personaje

Campos: identificador y versión; lista ordenada de referencias con vista/autoridad; sistema de coordenadas y unidades; landmarks con visibilidad/confianza; dimensiones normalizadas medidas; parámetros aprobados; módulos activos; semilla opcional; versión de Blender; tolerancias propias del proyecto.

Cada valor debe llevar `source`, `status` (`measured`, `artist_set`, `inferred`, `pending`) y, si viene de imagen, referencia y landmarks que lo sustentan. No se permite que un `pending` controle una operación destructiva.

### B. Generadores por módulo

- **Paramétrico/no destructivo**: mechones repetibles, correas, hebillas, bolsillos, placas, costuras, componentes mecánicos, marcadores y cámaras. Inputs visibles en Geometry Nodes o en el spec.
- **Forma orgánica**: volumen de cráneo/cara, dedos y manos. Se controla por plantilla de topología, landmarks y escultura; scripts solo preparan medición, snapping limitado, capas y reportes.
- **Variantes**: módulos secundarios aislados. Semilla estable, parámetros serializados y nombre de build `explore_<seed>`.
- **Bake/entrega**: conversión de instancias y evaluación solo en una copia de export; se conserva la fuente paramétrica.

Los generadores deben ser idempotentes: ejecutar dos veces con el mismo spec reemplaza únicamente su colección de salida y no duplica objetos ni toca fuentes bloqueadas.

### C. Gates automáticos y revisión artística

**Gate de entrada**: archivos presentes, hashes, resolución, vista correcta, lectura JSON, escala/unidades y versión Blender.  
**Gate geométrico**: coordenadas finitas, caras degeneradas, aristas frontera/manifold según módulo, objetos sueltos, dimensiones, distancia a fuente, penetraciones y winding. No imponer `manifold=0` a pelo, ropa abierta u ojos si el contrato de esa pieza permite superficies abiertas.  
**Gate de proyección**: etiqueta de región, oclusión, máxima distancia y confianza; rayos ambiguos se bloquean, no se rellenan por extrapolación.  
**Gate visual**: hoja ortográfica de ocho vistas con idénticas cámaras, escala, iluminación clay y máscara de silueta; overlay contra referencias; panel de close-ups para ojos, boca y manos.  
**Gate de deformación**: solo después de retopo. Pruebas estáticas de cierre ocular/oral, mandíbula, puño, oposición de pulgar y flexión de articulaciones; revisar penetración, pliegues y pérdida de volumen. Son poses de diagnóstico, no animación como entrega.

Automatización puede marcar `PASS`, `REVIEW` o `BLOCKED`; no puede marcar `CANON_APPROVED`. Esa aprobación requiere comparación visual y decisión de dirección artística.

### D. Ciclo por pase

1. Elegir una pregunta visual concreta, por ejemplo “¿coincide la silueta de la cabeza en frente y perfiles?”
2. Congelar spec y referencias; registrar hashes y versión de Blender.
3. Producir un derivado aislado en una colección/archivo nuevo.
4. Correr auditoría numérica ligera antes de renderizar. La hoja se hace con proxy o evaluación controlada para no pedir a EEVEE que almacene buffers de la malla densa completa si ya agotó memoria.
5. Revisar la hoja de vistas. La IA propone una lista breve de discrepancias; el artista la corrige.
6. Aplicar un patch limitado a parámetros aprobados; devolver diff y métricas antes/después.
7. Conservar pase aprobado y sus fuentes. Archivar rechazos como diagnóstico, nunca tratarlos como progreso del personaje.

### E. Contrato de scripts Blender

Todo script declara `blender_version_min/max` probado, unidades, entradas, salidas, hash del spec y política de escritura. Evitar depender de selección/contexto y operadores para manipular geometría; preferir `bpy.data`, `bmesh` y `mathutils`. Consultar enums desde RNA en tiempo de ejecución. En CLI, fallos Python deben dar código no cero (`--python-exit-code`). No usar una escena de usuario como entorno de prueba destructiva.

La ejecución headless debe ser por lotes pequeños: abrir fuente una vez, medir, cerrar; solo renderizar proxies cuando la escena de héroe exceda memoria. Toda salida lleva log, status, warnings y manifiesto de versiones. No afirmar “validado” si solo abrió o guardó.

## Aplicación inmediata a Ichiro

El pase ocular v03 mostró una mejora diagnóstica local, pero no generó párpado riggeable. Se conserva como prueba de registro y se deja de extender esa rama. Antes de tocar geometría facial:

1. Auditar de una vez todos los archivos de referencia y los blends derivados; deduplicar pruebas por hash y etiquetar maestro, evidencia, candidato y rechazado.
2. Sacar una hoja base coherente del modelo y las referencias completas: frontal, posterior, dos perfiles, cuatro 3/4 y close-up frontal de cara/manos. Congelar cámaras/escala e informar si la vista canónica no corresponde a ortográfica.
3. Medir proporciones de la fuente y referencias con landmarks revisados; declarar incertidumbre por perspectiva/oclusión.
4. Elegir **una** ruta para la cara: retopo manual guiada sobre el sculpt con RetopoFlow o herramientas nativas; candidato automático solo para comparación. No adquirir/instalar addons ni dependencias sin consultar al usuario.
5. Crear primero topología facial de baja resolución con loops de ojos y labios. Probar cierres/expresiones diagnósticas antes de subdividir. Esculpir volúmenes en capas revisables y comparar desde todos los ángulos.
6. Si el pase no supera referencias visuales, corregir la plantilla/topología o forma; no añadir otro documento de proyección local.

## Stack candidato, sin instalación en este pase

- Blender MCP: autoría/revisión interactiva en la escena; manipular solo una colección aislada. No usarlo como único verificador de scripts.
- Python de Blender en segundo plano: builds reproducibles, auditoría y hojas de vista de proxies.
- Geometry Nodes: módulos repetibles, sliders y variantes secundarias; no malla facial final por sí solos.
- RetopoFlow o Poly Build nativo: aceleración de retopo guiada. Verificar compatibilidad/licencia antes de instalar.
- QuadriFlow/Instant Meshes: benchmark de candidatos no deformables; no asumir flujo de loops facial.
- KREATIVE/LEGION: posible consumidor de paquetes de revisión y ejecuciones con hash/versiones; integrar solo tras definir el contrato, no duplicar el generador.

## Fuentes consultadas

- Blender MCP oficial: advertencia de que el servidor ejecuta código generado sin protecciones. https://www.blender.org/lab/mcp-server/
- Blender Python API 5.0, cambios de compatibilidad: https://developer.blender.org/docs/release_notes/5.0/python_api/
- Manual Blender Geometry Nodes 5.2: https://docs.blender.org/manual/en/latest/editors/geometry_node.html
- Blender Studio, retopología limpia para workflow estilizado: https://studio.blender.org/training/stylized-character-workflow/chapter/5d384edea5b8f5c2c32c8507/
- Blender Studio, retopología y por qué ayuda a rig/deformación: https://studio.blender.org/training/realistic-human-research/retopology/
- Blender 5.2, límites del remesh automático para topología deformable: https://docs.blender.org/manual/en/5.2/modeling/meshes/retopology.html
- Blender API, ray casting con `BVHTree`: https://docs.blender.org/api/current/mathutils.bvhtree.html
- OpenCV, GrabCut con inicialización rectangular y retoques: https://docs.opencv.org/4.x/d8/d83/tutorial_py_grabcut.html
- Blender Studio, curso de rig facial y ribbon guides/shape keys: https://studio.blender.org/training/facial-rigging/
- RetopoFlow docs: snapping sobre fuente y workflow 4.x: https://docs.retopoflow.com/
- Artículo compartido y benchmark auto-reportado: https://teapawt.net/0xCodio/article/2109275834984915150
- Ejemplo comunitario reproducible de pipeline de personaje asistido por IA con pasos humanos: https://github.com/ChilyerStudiosLLC/blender-character-pipeline
- CharacterGen, generación multi-vista de personaje desde imagen (paper/proyecto): https://arxiv.org/abs/2402.17214

## Primer componente implementado: inventario de activos

`tools/inventory_character_assets.py` recorre solo `Ichiro_Chibi/`, calcula SHA-256 en streaming y escribe `docs/ASSET_INVENTORY.json`. No modifica los archivos inventariados. Clasifica por ruta/nombre como sugerencia y conserva una nota de que la clase no equivale a aprobación. Agrupa duplicados exactos y excluye el propio informe para que una reejecución no se vuelva entrada de sí misma.

Primera ejecución: 167 archivos y una pareja de PNG idénticos (`eye_contour_alignment_v01.png` y `v02.png`). La alerta de ruta fue aparente: el `.blend` del repo y el maestro de `E:\WORKSPACE\Ichiro_Chibi\blend` tienen el mismo SHA-256. El repo quedó como raíz operativa de los generadores; sus categorías heurísticas requieren confirmación humana.

Reproducir desde `Ichiro_Chibi/`:

```powershell
python tools/inventory_character_assets.py
```

## Segundo componente implementado: bloque de silueta v02

`tools/build_calibrated_visual_hull.py` produce un OBJ volumétrico reproducible
con proporción preservada, altura/unidades declaradas y eje frontal `+X`.
V02 corrige escala, aspecto y winding; audita conectividad antes de aceptar el
blockout. Resultado y límites: `docs/VISUAL_HULL_BLOCKOUT_V02.md` y
`exports/visual_hull_v02/visual_hull_report_v02.json`. Se usa solo como soporte
de proporción; no reemplaza el sculpt de alta densidad ni es topología de rig.

## Tercer componente implementado: comparación 360 de referencias

`tools/project_reference_silhouettes.py` proyecta la fuente bloqueada contra un
BVH en CPU en ocho azimuts, sin renderizar ni guardar la escena fuente.
`tools/score_reference_fit.py` compara las cuatro placas grandes y los ocho
recortes de `ichiro_chibi_8view_turnaround.png`; genera máscaras, overlays,
perfiles de anchura por altura, contact sheets y un informe versionado. Usa GrabCut determinista en las cuatro
placas grandes si OpenCV ya está disponible; usa el modelo simple de borde en
los paneles de baja resolución o como fallback. No se instaló ninguna
dependencia. Puede recibir máscaras PNG corregidas por el artista y registra su
hash sin volver a segmentarlas. `docs/REFERENCE_CATALOG.md` registra las seis imágenes, los
landmarks auxiliares y el procedimiento.

La segmentación automática puede retener sombras y sus scores dependen de la
cámara y el encuadre. Por eso los resultados son localizadores de discrepancias
y material para revisión visual, no una calificación de canon. El siguiente
pase añadirá máscaras corregibles y calibración de cámara antes de autorizar
cualquier corrección de escultura. El cálculo utiliza `BVHTree` documentado por Blender;
evita el fallo repetido del render EEVEE headless con el controlador OpenGL de
este equipo.

Evidencia de este pase: `renders/reference_fit_v02_cpu/comparison/` y
`renders/reference_fit_v02_cpu/projections/projection_manifest.json`. El archivo
maestro mantiene su hash en el manifiesto y `source_scene_saved` es `false`.

La primera corrección paramétrica de pelvis por perfil se probó en copias en
memoria y empeoró las cuatro placas y los ocho ángulos al 5 %, 10 % y 15 % de
compresión. Quedó rechazada y documentada en
`docs/WIDTH_BAND_EXPERIMENT_V01.md`; el siguiente morph debe estar delimitado
por una región de referencia revisada, no por una curva global de anchura.

## Criterio de éxito del sistema

Para el mismo spec/version/seed, el build produce hashes y métricas repetibles. Un cambio afecta solo el módulo declarado. Cada pase muestra evidencia visual y auditoría numérica asociadas. Los proyectos futuros reutilizan herramientas y contratos, pero no transfieren identidad ni proporciones de Ichiro a otros personajes. El personaje solo progresa cuando supera una puerta visual/técnica; más código, polígonos o renders no cuentan por sí solos.
