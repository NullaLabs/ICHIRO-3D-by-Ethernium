# ICHIRO CHIBI — estado de producción

## Activo maestro actual

`blend/Ichiro_Chibi_HighDetail_Working.blend` contiene la fuente visual de
alta densidad. Su revisión giratoria está en
`renders/highdetail_turntable/ichiro_chibi_highdetail_turntable_contact_sheet.png`.
Esta fuente es la referencia de forma y detalle: no debe convertirse en la
malla final mediante un remesh automático.

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
