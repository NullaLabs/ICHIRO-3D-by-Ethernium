# Experimento de anchura por banda — v0.1

Fecha: 2026-10-28. Resultado: **rechazado; no aplicar al canon**.

## Hipótesis

Los perfiles de anchura mostraban un máximo de silueta más ancha en la fuente
que en las referencias cerca del 70 % de altura desde arriba, en frente y
espalda. Se probó si una compresión suave del eje Y en torno al 30 % de altura
desde abajo podía resolver esa diferencia sin afectar la forma restante.

`tools/project_width_band_exploration.py` crea una copia de la malla en memoria,
aplica una curva simétrica de compresión y proyecta ocho azimuts por BVH/CPU.
No edita el objeto maestro ni guarda una escena. Cada manifiesto conserva el
hash de `Ichiro_Chibi_HighDetail_Working.blend` y los parámetros exactos.

## Resultado medido

Los IoU se calcularon con el mismo scorer, máscaras, cámaras, encuadre y ocho
vistas; solo cambió la copia geométrica. MAE es el error medio absoluto de
anchura por altura normalizada, promediado en las cuatro placas grandes.

| Variante | Compresión máxima | IoU medio 4 placas | IoU medio 8 ángulos | MAE anchura/altura |
|---|---:|---:|---:|---:|
| Fuente | 0 % | 0,5335 | 0,6732 | 0,0202 |
| Banda v01-05 | 5 % | 0,5325 | 0,6713 | 0,0205 |
| Banda v01-10 | 10 % | 0,5310 | 0,6692 | 0,0209 |
| Banda v01-15 | 15 % | 0,5293 | 0,6676 | 0,0214 |

El ajuste empeora con cada aumento de compresión. Aunque una scanline aislada
sugería exceso de ancho, esa operación cambia otros contornos conectados en la
misma altura. La métrica por fila no identifica por sí sola qué pieza anatómica
o de vestuario debe moverse; cámara y máscara también influyen.

## Decisión

- Se descarta la banda de compresión como corrección del personaje.
- No se guarda ningún candidato `.blend`; las variantes fueron copias de memoria
  y `source_scene_saved` es `false`.
- La fuente conserva el SHA-256 `e08c086e2d8fad1be6f593647444455b4c3df034b97f4c3e262e7dd53f9a5024`.
- No escalar ni deformar el maestro a partir de un IoU o una scanline aislada.
- El siguiente cambio de forma se delimita con una máscara revisada visualmente,
  corresponde a una región de Ichiro y se valida de nuevo en los ocho ángulos.

## Reproducción

Desde `Ichiro_Chibi/`:

```powershell
blender --background --factory-startup Ichiro_Chibi_HighDetail_Working.blend --threads 4 --python-exit-code 1 --python tools/project_width_band_exploration.py -- --out renders/width_candidate_05 --center-from-bottom 0.30 --falloff 0.09 --strength 0.05
python tools/score_reference_fit.py --renders renders/width_candidate_05 --projection-prefix candidate_ --output-dir renders/width_candidate_05_comparison --segmenter auto
```

Cambiar `--strength` a `0.10` o `0.15` reproduce las otras pruebas. Cada corrida
crea solo proyecciones PGM y un manifiesto; no altera ni guarda la escena fuente.
