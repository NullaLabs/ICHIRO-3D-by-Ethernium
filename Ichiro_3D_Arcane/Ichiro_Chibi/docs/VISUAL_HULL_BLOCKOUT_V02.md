# Envolvente de silueta v02 — bloque de proporción

## Qué se corrigió

El generador anterior apuntaba a `E:/WORKSPACE`, estiraba cada recorte a una
cuadrícula fija, emitía altura sobre Y y usaba tamaño de voxel fijo `0.025`.
Con 120 muestras verticales eso representa 3 m, aunque el personaje fuente mide
1 m. La malla también salía con winding invertido. Esos defectos hacían que el
resultado dependiera de la ubicación local, deformara proporciones, no
coincidiera con los ejes del personaje y fallara una comprobación que el render
no muestra.

`tools/build_calibrated_visual_hull.py` ahora:

- deriva raíces desde la ubicación del script y acepta `--output-dir` y
  `--target-height-m`;
- preserva la relación de aspecto de cada máscara al ajustarla al lienzo;
- usa la convención observada en la fuente: frente `+X`, anchura `Y`, altura `Z`;
- calcula el paso de voxel como altura objetivo / 120;
- guarda hashes SHA-256 de las cuatro imágenes geométricas;
- comprueba incidencias de aristas, componentes, vértices sueltos, caras
  degeneradas y volumen firmado; bloquea el build si la superficie cerrada no
  tiene winding exterior.

Reproducir desde cualquier carpeta:

```powershell
python tools/build_calibrated_visual_hull.py
```

Salida: `exports/visual_hull_v02/`.

## Resultado medido

- Cuadrícula: 80 × 120 × 80; paso: 0.008333 m.
- Dimensiones importadas en Blender 5.2: X 0.525 m (profundidad), Y 0.575 m
  (anchura), Z 1.000 m (altura).
- La fuente `Ichiro_Chibi_HighDetail_Working.blend` mide X 0.420 × Y 0.490 ×
  Z 1.000 m. El bloque resulta +25% en profundidad y +17.3% en anchura. No se
  debe escalar la escultura maestra para igualarlo: la unión de cuatro siluetas
  sin calibración de cámara puede inflar el volumen; revisar primero las
  referencias y las cámaras ortográficas.
- 39,924 vértices y 39,922 quads; 1 componente; aristas frontera 0;
  aristas no manifold 0; vértices sueltos 0; caras degeneradas 0;
  volumen firmado +0.12147 m³; gate del bloque: `PASS`.
- El test de auto-intersecciones no está implementado.

La revisión de cinco direcciones en Blender confirmó que el archivo queda en
Z-up y el frente mira `+X`. También mostró claramente el límite artístico:
esta envolvente une masas, suaviza separaciones entre brazos/piernas y presenta
escalones de voxel. Es útil para bloquear volumen y revisar proporciones; no es
escultura AAA, retopología, rostro, manos, pelo ni malla riggeable. No sustituye
ni modifica `Ichiro_Chibi_HighDetail_Working.blend`.

En la sesión Blender abierta se importó a la colección
`ICH_CHIBI_VISUAL_HULL_BLOCKOUT_V02__CANDIDATE`, oculta del viewport y del
render después de inspeccionarla. La sesión principal sigue sin guardar; su
copia de rescate previa está en
`Ichiro_Chibi_HEAD_HANDS_Topology_Workspace_PRE_FOUNDRY_RECOVERY_2026-10-28.blend`.
Para recrear la importación se usa `tools/import_visual_hull_blockout_v02.py`.
Hay un archivo local de revisión independiente en
`exports/visual_hull_v02/Ichiro_Chibi_VISUAL_HULL_V02_REVIEW.blend`; no se
incluye como fuente reproducible porque el OBJ y el importador bastan para
reconstruir la colección candidata.

## Fuente y alcance

Se usan frente, espalda y ambos perfiles como restricciones de silueta. El
turnaround de ocho vistas y la lámina de proceso siguen como evidencia de
revisión, no como restricciones geométricas. El cálculo no registra perspectiva
ni pose entre vistas; las cuatro imágenes ortográficas requieren revisión
artística antes de tratar cualquier proporción como canon. El hull puede
sobreestimar el volumen al unir las siluetas opuestas; por eso no se usó para
deformar automáticamente la escultura fuente.

El SHA-256 del `.blend` maestro en el repo coincide con el de la copia en
`E:/WORKSPACE/Ichiro_Chibi/blend/`; la primera alerta de inventario era un
desacuerdo de layout, no dos fuentes distintas. Los scripts productivos del
repo se están normalizando a rutas relativas a este proyecto.
