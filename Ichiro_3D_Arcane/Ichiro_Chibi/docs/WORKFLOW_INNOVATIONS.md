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

Cada bloque debe producir una mejora verificable; no añadir capas de servicios
antes de tener un caso geométrico útil. La reconstrucción artística sigue pendiente.
