# Mapa de componentes geométricos — v0.1

Fecha: 2026-10-28. Estado: diagnóstico reproducible; ninguna isla está
clasificada como anatomía aprobada.

## Hallazgo

`Ichiro_Chibi_HEAD_HANDS_Topology_Workspace.blend` contiene el maestro visual
como un único objeto Blender, pero sus 773.535 vértices se dividen en 181 islas
conectadas. La malla tiene 1.495.680 caras triangulares, 2.269.034 aristas y un
solo material con atlas 4K. Por eso «un objeto» no significa una superficie
continua: un raycast sobre el objeto completo puede tocar pelo, ceja, piel,
ropa, guante o una pieza decorativa. Un nombre de objeto o un índice de
material no basta para decidir el destino de una proyección.

## Herramienta

`tools/build_component_map_review.py` etiqueta una copia en memoria con un color
plano determinista por isla, calcula sus límites y tamaños, y genera cinco
vistas ortográficas más `component_map_manifest.json`. Usa union-find sobre las
aristas, por lo que no necesita listas de adyacencia por vértice. La escena se
abre con Blender 5.2; el maestro no se edita y no se guarda ningún `.blend`.

Reproducir desde `Ichiro_Chibi/`:

```powershell
blender --background --factory-startup Ichiro_Chibi_HEAD_HANDS_Topology_Workspace.blend `
  --python tools/build_component_map_review.py -- `
  --out renders/component_map_review_v01 --resolution 768
```

La indexación compartida vive en `tools/component_islands.py`; el mapa y los
diagnósticos de proyección usan el mismo orden determinista de IDs.

La evidencia del pase está en `renders/component_map_review_v01/`. Los IDs se
ordenan por número de vértices descendente y luego por índice raíz; el JSON
incluye color, caja, centro y cantidad de caras/vértices para cada ID.

## Cómo interpretar el mapa

- Los colores son claves de diagnóstico, no materiales finales ni clases de
  pelo, piel, ojo, ropa o mano.
- Un componente que cae en la región de la cara sigue sin ser necesariamente
  piel: puede contener una parte de ceja, párpado o decoración conectada.
- El mapa sustituye temporalmente el atlas por colores planos; sirve para
  encontrar islas y límites, no para evaluar la semejanza visual.
- El archivo fuente conserva el SHA-256
  `d906a5b55041a8047a3b38d8e346cf41f9fa6cd7f08ccc3f121c2b8c41fb5b86`.
  El manifiesto registra `source_scene_saved: false`.

## Próxima decisión de modelado

Antes de proyectar loops faciales o digitales, la herramienta debe aceptar una
selección explícita de componente/s y mostrarla sobre las vistas originales.
La clasificación puede combinar los límites 3D con landmarks/UV del atlas,
pero toda región sigue requiriendo revisión visual. Después se crean a mano
las superficies de ojos, párpados, boca y dedos sobre esos objetivos. No se
aplica QuadriFlow, voxel remesh ni un raycast indiscriminado como topología
final.

## Prueba de soporte de párpados

`tools/classify_eyelid_projection_support.py` asocia ahora cada muestra de
raycast con el ID de la isla alcanzada. En el contorno A, 128 muestras se
reparten entre los IDs 9 (20), 49 (103) y 54 (5); en el contorno B, las 128
muestras caen en el ID 27. El estimador de color UV marca 39/128 como posibles
colores de piel en A y 23/128 en B. Son pistas, no etiquetas anatómicas: el
atlas es compartido y el centro UV no describe necesariamente una cara
completa.

El informe es `docs/EYELID_SUPPORT_CLASSIFICATION.json`. No se debe crear el
parche A como una banda continua hasta clasificar y revisar sus tres islas. El
contorno B tiene soporte geométrico consistente en una isla, pero aún hay que
confirmar que esa isla es piel y revisar el contacto con el globo ocular.
