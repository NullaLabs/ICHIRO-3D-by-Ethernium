# Siguiente fase: reconstrucción multivista + Remi + SNN LIF

Fecha: 2026-11-05  
Estado: plan de ejecución aprobado; no altera ni sustituye el maestro.

## Objetivo

Demostrar con una prueba reversible si una fusión real de las ocho vistas y una
candidata de topología por región mejoran el ajuste geométrico sin perder detalle
ni crear la falsa impresión de que una malla automática ya está lista para rig.
Remi es una herramienta de reparación, remallado, retopología guiada, UV y bake;
el criterio de forma seguirá siendo Ichiro, medido contra las referencias.

## Evidencia que ya existe

- `references/ichiro_chibi_8view_turnaround.png` y las placas individuales de
  frente, espalda, izquierda y derecha.
- `tools/score_reference_fit.py` ya calcula las cuatro vistas canónicas y ocho
  recortes del turnaround. El reporte actual usa centrado por caja y escala por
  altura; incluye IoU, perfiles de ancho y metadatos de recorte. No equivale a
  una calibración fiable de cámara para toda imagen futura.
- `tools/build_calibrated_visual_hull.py` crea el bloque v02 con cuatro placas,
  no ocho. Su reporte registra una malla cerrada de 39.924 vértices y 39.922
  quads; la prueba de auto-intersecciones aún no se ejecutó. El bloque no es el
  maestro ni topología de producción.
- Remi 2.0 quedó instalado y habilitado en el perfil Blender 5.2. La instancia
  interactiva anterior debe reiniciarse antes de usar su panel.
- La SNN de 50M no participa todavía en el reconstructor de este repo. La
  propuesta inicial es un planificador LIF compacto, medido contra una política
  heurística; no usar 50M hasta que los datos demuestren que hace falta.

## Experimento geométrico

1. **Congelar la referencia.** Registrar hashes de las cuatro placas, turnaround,
   escena fuente y parámetros de cámara. Toda prueba sale de una copia con nombre
   `*_REVIEW_*`; no sobrescribir `ICH_CHIBI_HIGHDETAIL_SOURCE__READONLY`.
2. **Crear máscaras y calibración por imagen.** Para cada imagen registrar tipo
   de cámara (ortográfica, perspectiva o desconocida), yaw/pitch, escala,
   landmarks, región visible, oclusión y confianza. Las ocho direcciones del
   turnaround son cámaras canónicas; fotografías, detalles y vistas generadas
   entran como evidencia suplementaria con confianza separada.
3. **Comparar geometría 4-vistas vs 8-vistas.** Extender el visual hull para
   consumir N cámaras y generar primero `N=4` y `N=8` con idéntico volumen,
   resolución y máscara. Medir por vista IoU, Chamfer de contorno y deriva de
   landmark; medir además voxels discrepantes, componentes, manifoldness,
   degenerados y auto-intersecciones. No confundir más densidad con más fidelidad.
4. **Incorporar evidencia adicional gradualmente.** Añadir cada vista extra sólo
   después de asignarle cámara/confianza y comprobar si reduce error fuera de su
   propia imagen. Si contradice las vistas canónicas, se marca como conflicto y
   no se promedia a ciegas.
5. **Mantener geometría observada e inferida separada.** Silueta y landmarks
   observados constriñen la superficie; profundidad estimada, oclusiones y
   superficies generadas se registran como hipótesis, con peso menor y origen
   visible en el manifiesto.

## Benchmark de Remi

- Seleccionar una copia de región amplia y de deformación moderada (pantalón,
  bota o torso), no la cara completa ni la malla fuente entera.
- Ejecutar una única candidata mediante Remi Interactive Instant Meshes con
  orientación guiada. Registrar versión, configuración, tiempo, RAM/VRAM,
  polígonos, advertencias y hash de entrada/salida.
- Proyectar la candidata desde las ocho cámaras y compararla con el maestro y
  máscaras; revisar shading, huecos, componentes, tangentes y densidad de silueta.
- Conservar el resultado sólo como derivado si mantiene forma y reduce coste sin
  artefactos. Un remesh uniforme de voxel no sustituye loops de expresión,
  articulaciones, manos ni dedos.
- Cara, párpados, boca y dedos continúan por retopología manual dirigida sobre
  sculpt; Remi puede servir para preparar superficies, reparar o hacer UV/bake,
  no para aprobar su flujo de deformación.

## SNN LIF: primera integración medible

Representar **8 vistas × 8 regiones = 64 unidades LIF** (cabeza/cabello, torso,
brazos, manos, pelvis/pantalón, piernas, botas y accesorios). Cada entrada
codifica discrepancia de silueta, incertidumbre de cámara, oclusión, confianza de
la referencia y coste estimado del próximo cálculo. La red prioriza la pareja
vista-región que se espera reduzca más el error ponderado por coste.

La SNN **no deforma ni genera la malla**. Controla el orden de evaluación y pide
más evidencia cuando hay conflicto. Medir contra una heurística determinista con
el mismo presupuesto:

- reducción de error ponderado por vista y región tras cada ciclo;
- número de vistas/procesamientos necesarios para alcanzar el umbral;
- selecciones redundantes o de baja confianza;
- tiempo CPU/GPU, pico de VRAM y capacidad de reanudar desde checkpoint.

La SNN pasa a una siguiente fase sólo si mejora consistentemente el resultado o
reduce trabajo con calidad equivalente. El runtime de 50M se audita aparte y no
se conecta a producción hasta certificar lecturas de spikes, sincronización GPU,
memoria y benchmark físico reproducible.

## Puertas de decisión

- **Geometría:** el pase de ocho vistas debe mejorar el error agregado sin
  empeorar de manera oculta un perfil o espalda.
- **Topología:** ninguna candidata se denomina rig-ready hasta validar flujo en
  cara/manos y pruebas estáticas de deformación por articulación.
- **Reproducibilidad:** toda ejecución guarda entrada, hash, cámara, máscara,
  parámetros, herramienta/versión, métricas, logs y resultado separado.
- **Memoria:** reportar pico real de VRAM/RAM por etapa; trocear o apagar modelos
  no se contará como ahorro hasta medirlo.
- **Aprobación artística:** comparar frontal, espalda, ambos perfiles, cuatro
  intermedias y vistas suplementarias; corregir primero silueta y proporción,
  luego volúmenes anatómicos, después detalle.

## Orden de trabajo

1. Reiniciar Blender para cargar Remi 2.0 en la sesión interactiva.
2. Crear paquete de cámaras/máscaras versionado y dejar los métricos actuales
   como baseline 4/8 vistas.
3. Extender el tallado volumétrico a N vistas y producir comparación 4 vs 8.
4. Sólo entonces ejecutar una candidata Remi de una región sobre un archivo
   derivado y medir silueta/topología/coste.
5. Implementar y comparar el planificador LIF de 64 unidades con la heurística.
6. Elegir manualmente qué topología conserva el artista; actualizar informes y
   guardar cada iteración en GitHub.
