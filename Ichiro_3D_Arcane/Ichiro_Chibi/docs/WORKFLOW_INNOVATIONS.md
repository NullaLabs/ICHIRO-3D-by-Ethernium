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

## WF-003d — suavizado y remuestreo por longitud de arco

Modo -- --smooth en generador y renderizador. Tres pasadas de corner cutting
con extremos fijos, seguidas de muestreo uniforme por longitud de arco, conservan
21 columnas y 40 quads. Es una propuesta de forma; no conserva exactamente los
landmarks interiores ni acredita fidelidad canónica.

La guía reduce su giro máximo de 77.08 a 37.03 grados. Tras proyectar sobre la
máscara, el giro vuelve a 67.59 grados; la banda anterior medía 79.20 grados
en su fila interior. Esto demuestra una mejora parcial, no una solución: los
huecos/discontinuidades de la máscara afectan al resultado y deben revisarse.
Distancia máxima 0.00385785 bajo límite 0.004, área mínima 8.867e-7.

Se guardan escena derivada local Ichiro_Chibi_Smooth_Lid_Strip_Review.blend,
SMOOTH_LID_STRIP_REVIEW.json y tres renders. Frontal inspeccionado: contorno
algo más suave, esquina superior aún demasiado marcada. Pendiente superficie
de apoyo revisada y anatomía completa. No añadir rig basándose en estas métricas.

## WF-003e — conservación del contorno frontal al ajustar profundidad

Modo -- --depth en ambos scripts. Conserva YZ de la guía y toma X del soporte
más cercano. Comprueba de nuevo que el candidato está a menos de 0.004 de la
máscara antes del desplazamiento de visualización +0.0008 en X. La distancia
reportada excluye ese desplazamiento. No equivale a contacto sobre la superficie:
el candidato puede quedar flotando sobre un hueco de la máscara.

Resultado: 40 quads, giro máximo de fila interior 50.93 grados frente a 67.59
en la proyección libre suavizada. Área mínima 8.759e-6, distancia máxima de
soporte 0.00384750. Inspección frontal y perfil: mejor distribución inferior y
lateral, pero parte del arco superior queda tapada por la geometría oscura del
ojo. No aprobado como párpado; falta resolver contacto, margen y soporte real.

Escena local Ichiro_Chibi_Depth_Lid_Strip_Review.blend; informe
DEPTH_LID_STRIP_REVIEW.json y renders depth_strip_* versionados junto al código.
La mejora es experimental y no acredita fidelidad ni comportamiento de rig.

## WF-003f — contacto frontal acotado con comparación reversible

refine_strip_contact.py lee la variante depth y ajusta X al primer impacto
frontal sobre la fuente completa, más 0.0008 para visualizar. Solo acepta
correcciones absolutas <=0.004. Esto comprueba cercanía y visibilidad, NO identidad
semántica de piel. No garantiza excluir accesorios próximos.

Resultado: 59/63 vértices ajustados; 33,54,55,62 conservados al superar el límite.
Se verifican normales y áreas de caras antes de guardar. La forma anterior queda
en shape key Before_Contact_Review (valor 1 restaura la variante depth; 0 muestra
el ajuste). Render frontal inspeccionado: arco superior más visible. Persisten
incertidumbres de superficie y anatomía, sin espesor ni globo validado.

Escena local Ichiro_Chibi_Contact_Lid_Strip_Review.blend. Código, informe
STRIP_CONTACT_REVIEW.json y renders contact_strip_* versionados. Ejecutar el
generador con --python-exit-code 1 y el renderizador con -- --contact.

## WF-004 — contorno periocular cerrado con incertidumbre explícita

build_closed_eye_review.py construye tres anillos de 32 vértices (64 quads).
El landmark 1 conserva su píxel estimado pero infiere profundidad entre 0 y 2.
Dos pasadas de corner cutting y remuestreo distribuyen las columnas. Es una
hipótesis autorada, no reconstrucción exacta de las imágenes canónicas.

La proyección frontal admite desplazamientos X <=0.004. Los puntos rechazados
conservan profundidad inferida y pertenecen al grupo INFERRED_DEPTH_REVIEW.
Resultado final: 29/96 pendientes de contacto aceptado. El informe conserva
estado por vértice; no confundir contorno cerrado con aprobación anatómica.

Comprobaciones: 64 aristas de frontera (dos bucles), sin aristas de más de dos
caras, caras sin área casi nula y normales frontales positivas. Frontal y perfil
positivo inspeccionados: el contorno rodea el ojo, pero el tramo superior muestra
separación y quiebros pendientes de ajuste. No hay espesor ni cierre ocular.

Escena local Ichiro_Chibi_Closed_Eye_Review.blend. Renderizador: -- --closed.
Código, CLOSED_EYE_REVIEW.json y renders closed_eye_* versionados. La escena
fuente y los experimentos anteriores permanecen preservados.

## WF-004b — regularización de profundidad con puntos fijos

relax_closed_eye_depth.py ajusta solo X de los 29 vértices inferidos mediante
40 iteraciones de promedio de vecinos, paso 0.5 y desplazamiento acotado a 0.004.
Los 67 restantes quedan exactamente fijos (assert). Normales y áreas verificadas.
Máximo movimiento observado 0.00333401; energía de Laplaciano cuadrado sobre
puntos libres pasa de 1.44786e-5 a 2.19528e-10. Esta energía mide suavidad,
no fidelidad ni contacto. La proyección/contacto no se ha revalidado.

Perfil positivo inspeccionado: persiste separación superior. No aprobar como
anatomía final. La forma anterior se conserva en Before_Depth_Regularization.
Escena local Ichiro_Chibi_Closed_Eye_Relax_Review.blend, informe
CLOSED_EYE_RELAX_REVIEW.json. Renderizador admite -- --relax. Scripts,
informe y renders quedan versionados; no se modifica la sesión abierta.

Cada bloque debe producir una mejora verificable; no añadir capas de servicios
antes de tener un caso geométrico útil. La reconstrucción artística sigue pendiente.

## WF-005 — rechazo de la tira ocular por contacto flotante

La tira 96v/64q relajada se importó en una colección independiente de la sesión
Blender abierta para inspección con MCP, conservando intacta la malla de origen.
La inspección cercana desde frente, perfil y tres cuartos mostró separación
respecto al volumen del párpado y tramos flotantes causados por profundidades
inferidas. Se rechazó para producción y se ocultó; no se fusionó ni se guardó
sobre el archivo de trabajo del usuario. La escena abierta permanece modificada
en memoria, y antes de MCP existe la copia de recuperación en E:/WORKSPACE.

Decisión del flujo: una mejora de suavidad numérica no acredita contacto
anatómico. La próxima construcción facial requiere validar superficie y silueta
por vistas antes de aceptar una malla; los vértices inferidos quedan señalados
como incertidumbre, nunca cubiertos por un Shrinkwrap sin soporte suficiente.

## WF-006 — clasificar soporte antes de generar otra malla facial

tools/classify_eyelid_projection_support.py repite las 256 muestras previstas
para dos parches y registra el primer impacto en la fuente completa: polígono,
material, normal, posición y color UV aproximado. En esta fuente, todas las
256 muestras alcanzan alguna superficie, pero solo 62 superan el heurístico de
color cálido. Como solo hay una ranura de material y el cabello puede ocluir la
piel, ese dato no identifica piel de forma fiable. El resultado bloquea la
generación automática; no pretende resolver la semántica ni corrige landmarks.

El informe docs/EYELID_SUPPORT_CLASSIFICATION.json conserva cada muestra y los
hashes de entrada/herramienta. Ejecutar con Blender 5.2 en modo background y el
script tools/classify_eyelid_projection_support.py. La siguiente mejora debe
ser una región de cara etiquetada manualmente contra las referencias, con
segmentación/landmarks revisables; no relajar más la tira actual.
