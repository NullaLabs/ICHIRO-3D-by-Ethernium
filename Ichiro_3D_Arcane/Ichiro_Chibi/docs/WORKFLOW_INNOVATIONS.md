# Registro de mejoras del workflow Ethernium

Cada mejora se guarda con implementación, evidencia, límites y commit. Una
propuesta no se etiqueta implementada; un test geométrico no aprueba identidad.
Se mantienen las referencias y escenas fuente. No instalar herramientas o
modelos sin la autorización solicitada por el usuario.

## WF-001 — control geométrico portable de parches frontales

Estado: implementado; validación sobre fixtures y packet real registrada en Git.
Problema: contar quads y aristas manifold dejaba pasar párpados invertidos y
saltos de profundidad procedentes de una proyección global.

Implementación: tools/validate_review_packet.py, Python estándar, sin Blender
ni GPU. Consume el contrato ya exportado para KREATIVE; revisa índices, finitud,
normales, degeneración, conectividad por arista y discontinuidad de profundidad.
Escribe hash del packet y del validador. Código de salida 2 significa revisión
bloqueada, no fallo del ejecutor. 0 solo indica que esas comprobaciones pasan.

Reproducir desde Ichiro_Chibi:

```powershell
python tools/test_review_gate.py
python tools/validate_review_packet.py exports/ethernium_review_packet.json --output docs/REVIEW_GATE_REPORT.json
```

El packet actual debe quedar bloqueado. Esta regresión captura el defecto real
antes de integrarlo con LEGION. No usar este gate de orientación frontal para
una cabeza completa: sus caras posteriores deben mirar en otras direcciones.
No verifica ajuste a imagen, auto-intersecciones, skinning ni expresiones.
No altera el archivo Blender ni resuelve por sí mismo la proyección.

## WF-002 — experimento de máscara regional asistida por textura

Implementado en tools/probe_skin_projection.py. Se ejecuta con Blender
--background --factory-startup --python y genera una escena nueva
Ichiro_Chibi_Skin_Projection_Experiment.blend sin editar la sesión abierta.
La máscara usa posición y color de textura muestreado en el centro UV de cada
cara. Guarda correspondencia a polígonos fuente y UVs para inspección visual.
No es segmentación semántica ni proyección aprobada.

Resultado real: 46.893 caras candidatas; 69 rayos con candidato, 15 con candidato
ocluido y 172 sin candidato, de 256 muestras. Los puntos no resueltos quedan
explícitos: no se rellenan ni interpolan. SKIN_PROJECTION_PROBE.json conserva
los resultados y hashes de entrada/script. Los umbrales son hipótesis específicas
de esta textura y no se extrapolan a otros personajes.

Conclusión: el color solo no resuelve la región periocular. Se necesita máscara
revisada y contornos anatómicos; este experimento no reemplaza los párpados.
La escena derivada se regenera con el script y los assets fuente versionados.
El informe se guarda en Git; el blend derivado permanece local.

## Próximas mejoras propuestas, todavía no implementadas

- WF-002b: revisión de máscara de piel y selección anatómica de impactos.
- WF-003: landmarks con confianza y cámaras por referencia; comparación de silueta.
- WF-004: ajuste de plantilla anatómica y pruebas de deformación reproducibles.
- WF-005: consumidor de packets en KREATIVE y trabajos versionados en LEGION.

## WF-002b — revisión visual y landmarks explícitos (parcial)

render_skin_mask_review.py produce dos renders con la misma cámara, fuente y
máscara aislada. Inspección visual: se excluye pelo, pero también márgenes oscuros
del ojo; quedan falsos positivos en iris rojo, trazos del cabello y arete. No usar
el filtro como clasificación semántica aprobada.

references/eyelid_landmarks_review.json fija 16 estimaciones de contorno exterior
de piel en coordenadas de imagen. La cámara ortográfica queda documentada para
reproyectar píxeles a rayos reproducibles. No son landmarks canónicos aprobados
ni el borde interno del párpado. build_eyelid_landmark_review.py proyecta sin
rellenar huecos y crea marcadores editables en una nueva escena local.

Resultado: 11 candidatos, 3 sin impacto y 2 ocluidos. Ver
EYELID_LANDMARK_REVIEW.json. La revisión de profundidad y contraste con las
referencias canónicas sigue pendiente. No hay párpados nuevos ni rig final.
Se versionan scripts, coordenadas, informes y renders; las escenas derivadas
se regeneran a partir de la fuente y quedan guardadas localmente.

## WF-003a — banda periocular inferior editable

build_lower_lid_strip.py crea 27 vértices y 16 quads a partir de landmarks 7,6,5
del ojo visible (SCREEN_RIGHT). Interpola una guía y proyecta cada punto contra
la máscara regional con distancia máxima 0.004 unidades de modelo. Si no existe
impacto dentro de ese radio, aborta. Distancia máxima observada: 0.00239511.
Verifica normales hacia +X antes de guardar una escena nueva.

render_landmark_depth_review.py genera frontal y ambos perfiles; con -- --strip
muestra la banda. Inspección frontal: sigue la piel bajo el margen oscuro del ojo.
El perfil positivo permite revisar profundidad; el negativo queda ocluido por
cabello. No se ha validado aún contra todos los dibujos canónicos.

Es una banda parcial de piel, no un párpado completo: faltan canto, margen,
espesor, contacto con globo y pruebas de parpadeo. La interpolación es una
hipótesis de forma local, no profundidad medida de las referencias. Maestro
fuente y sesión abierta permanecen intactos. La escena derivada se conserva
localmente; script, informe y renders se versionan para reproducirla.

## WF-003b — extensión lateral con dirección de expansión local

El generador admite -- --outer. Amplía la guía hasta el landmark 4 y orienta
las filas exteriores según la perpendicular a la tangente en el plano YZ,
en lugar de desplazarlas siempre hacia abajo. Resultado: 39 vértices, 24 quads,
distancia máxima de proyección 0.00376475, límite conservado en 0.004.
Normales comprobadas; frontal y perfil positivo inspeccionados visualmente.

Intentar incluir el landmark 3 produjo un punto sin soporte y abortó antes de
guardar. La versión conservada termina en 4: no se elevó el umbral para forzar
el encaje. Falta completar margen superior y comisuras con una máscara revisada.
La banda sigue siendo piel periocular, sin espesor, contacto ocular ni rig.

Comando reproducible desde Ichiro_Chibi (usar la ruta local de Blender):
```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --python-exit-code 1 --python tools/build_lower_lid_strip.py -- --outer
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --python-exit-code 1 --python tools/render_landmark_depth_review.py -- --outer
```
--python-exit-code 1 evita confundir una excepción Python con ejecución correcta
del proceso Blender. Escena local: Ichiro_Chibi_Outer_Lid_Strip_Review.blend.

## WF-003c — ancho variable para explorar el arco superior

Los dos scripts anteriores admiten -- --upper. La guía continúa por 3 y 2;
el ancho se reduce progresivamente a la mitad al aproximarse al arco superior.
Se mantiene el límite de proyección 0.004. Se añadió rechazo de caras con área
inferior a 1e-10 unidades cuadradas de modelo, además de normales invertidas.

Ejecución real: 63 vértices, 40 quads, distancia máxima 0.00334550, área mínima
6.431e-7. Escena local: Ichiro_Chibi_Upper_Lid_Strip_Review.blend. Informe:
UPPER_LID_STRIP_REVIEW.json. Renders frontal y perfil positivo inspeccionados.

La esquina externa es demasiado angular y algunas filas superiores quedan
muy próximas: la prueba numérica NO aprueba el diseño. Conservar como candidato;
corregir recorrido y distribución antes de espesor o rig. El arco interior sigue
incompleto. Este bloque no acredita fidelidad a todas las referencias canónicas.

Cada bloque debe producir una mejora verificable; no añadir capas de servicios
antes de tener un caso geométrico útil. La reconstrucción artística sigue pendiente.
