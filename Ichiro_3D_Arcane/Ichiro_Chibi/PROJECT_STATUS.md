# ICHIRO CHIBI — estado de producción

## Activo maestro actual

`Ichiro_Chibi_HighDetail_Working.blend` en esta carpeta contiene la fuente
visual de alta densidad. Las seis referencias, guías y generadores usan rutas
relativas al proyecto. Su hoja giratoria se regenera con
`tools/render_highdetail_turntable.py` y `tools/make_turntable_contact_sheet.py`;
el ángulo 0° parte de la cara frontal `+X`. La hoja antigua en
`renders/ichiro_chibi_highdetail_turntable_contact_sheet.png` precede ese ajuste
de orientación y queda como evidencia histórica. Esta fuente es la referencia
de forma y detalle: no debe convertirse en la malla final mediante un remesh
automático.

La copia previa al replanteamiento de workflow está en
`Ichiro_Chibi_HEAD_HANDS_Topology_Workspace_PRE_FOUNDRY_RECOVERY_2026-10-28.blend`.
`exports/visual_hull_v02/` contiene un bloque de silueta independiente; el OBJ
no sustituye la fuente de alta densidad ni cuenta como forma aprobada.

## Qué está aprobado para la siguiente fase

- Usar todas las imágenes de `references/`, no solamente las cuatro vistas
  ortográficas.
- Retopología manual de producción guiada por la fuente de alta densidad y la
  validación en 8 ángulos.
- Conservar ojos, cavidad/labios de la boca y dedos separados en componentes
  topológicos dentro del único objeto de malla final, según
  `docs/RIGGABLE_ANATOMY_CONTRACT.md`.
- Aplicar rig y pesos sólo después de aprobar la topología final.

## Activos de exploración (no finales)

- `Ichiro_Chibi_VisualHull_LOCKED.obj`: volumen de calibración de silueta.
- `Ichiro_Chibi_Retopology_BodyCandidate.blend`: prueba cerrada de volumen;
  no tiene la calidad facial, ocular, oral ni de manos necesaria.
- `Ichiro_Chibi_RigGuide.blend`: guía ósea sin pesos ni animación.

## Reproducibilidad

Los scripts de `tools/` documentan la construcción de la envolvente 360, la
auditoría, la guía de rig y el render de revisión. No se versionan entornos
virtuales, cachés ni el clon de Hunyuan: son dependencias regenerables, no
activos del personaje.

## Comparación de referencias CPU — 2026-10-28

`tools/project_reference_silhouettes.py` produce proyecciones para ocho ángulos
sin renderizar y sin guardar la escena fuente. `tools/score_reference_fit.py`
compara las cuatro placas individuales y los ocho paneles del turnaround; se
documenta cada imagen en `docs/REFERENCE_CATALOG.md`. El informe incluye perfiles
de anchura en 49 alturas por placa (`reference_fit_width_profiles.png`) para
mostrar dónde aparece cada diferencia de silueta. Puede recibir máscaras
revisadas en PNG y registra sus hashes.

Con la máscara GrabCut, el IoU actual es 0,515–0,560 en las cuatro placas y
0,640–0,708 en la hoja de ocho vistas. Las proporciones ancho/alto de la fuente
y las placas grandes coinciden casi exactamente; la medición inicial estaba
sesgada por la sombra de suelo. Los IoU sirven para localizar diferencias con
los overlays, no para aprobar parecido. La fuente maestra permanece intacta.
El siguiente paso técnico es calibrar cámaras y revisar máscaras antes de usar
cualquier medición para esculpir.

Una hipótesis de estrechamiento de cadera/pantalón se simuló en copias en
memoria al 5 %, 10 % y 15 % y empeoró las métricas en las cuatro placas y ocho
vistas. Se descartó; no se modificó la forma maestra. Ver
`docs/WIDTH_BAND_EXPERIMENT_V01.md`.

El maestro también se auditó por islas conectadas: un solo objeto contiene
181 islas y un único material/atlas 4K. El mapa por componentes v0.1 expone
estos grupos en cinco vistas sin tocar ni guardar la fuente. Ningún ID se
considera semánticamente clasificado todavía. Ver
`docs/COMPONENT_MAP_REVIEW_V01.md` y `renders/component_map_review_v01/`.

## Auditoría de blockout 360 — V02

El candidato de silueta está aislado en `exports/visual_hull_v02/`; gate geométrico PASS, pero revisión artística pendiente. Mide 0.525 × 0.575 × 1.000 m frente a la fuente (0.420 × 0.490 × 1.000 m), diferencia que se debe resolver con calibración de vistas y cámaras, no escalando el maestro. Detalle: `docs/VISUAL_HULL_BLOCKOUT_V02.md`. El inventario automatizado más reciente registra 177 archivos y 1 grupo de duplicados exactos; sus categorías son sugerencias por nombre/ruta, no aprobación.
