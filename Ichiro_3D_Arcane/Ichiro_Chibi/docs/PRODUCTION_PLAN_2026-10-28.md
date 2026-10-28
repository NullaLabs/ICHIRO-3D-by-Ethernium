# Ichiro Chibi: producción y retopología verificables

Investigación: 2026-10-28. Objetivo: personaje fiel y preparado para rig.
Estado: forma y anatomía aún no aprobadas; no es un asset AAA terminado.
Este documento sustituye promesas absolutas y umbrales no calibrados del mega plan.

## Métodos evaluados

| Método | Decisión | Límite |
|---|---|---|
| RetopoFlow | Candidato para loops guiados sobre escultura | Verificar paquete exacto compatible con Blender 5.2 antes de instalar |
| Instant Meshes | Benchmark para regiones amplias menos deformables | Sus campos no expresan por sí mismos anatomía facial |
| QuadriFlow | Remallado candidato para regiones secundarias | Cuadrangulación no certifica flujo apto para expresiones |
| UniRig | Investigación posterior de esqueleto/pesos | No construye la anatomía que falta en cara y manos |
| Plantilla anatómica propia ajustada por regiones | Ruta principal propuesta | Landmarks y evaluación artística necesarios; aún por implementar |

Fuentes primarias:
- https://github.com/CGCookie/retopoflow : código GPL-3.0; activos no-code con condiciones diferentes.
- https://docs.retopoflow.com/v4/changelist.html : curvas, relax y patches; consultar versión concreta.
- https://github.com/wjakob/instant-meshes : remallado por campos; consultar LICENSE.txt.
- https://github.com/hjwdzh/QuadriFlow : cuadrangulación automática.
- https://github.com/VAST-AI-Research/UniRig : investigación de rigging automático.

Son decisiones de ingeniería, no benchmarks realizados sobre Ichiro.
Instant Meshes (remallador) es distinto de InstantMesh (reconstrucción generativa).
No se instaló herramienta ni se descargó modelo en este bloque.

## Orden de trabajo y aceptación

1. **Referencias y forma.** Usar las seis referencias: vistas, turnaround y lámina
   de proceso. Esta última no prueba que sus rigs o UV existan. Ajustar cámaras
   y marcar landmarks visibles, ocluidos e inferidos. Resolver diferencias de
   perspectiva y pose antes de exigir coincidencia. Revisar cráneo, mandíbula,
   cabello, cuello, torso, manos y calzado con renders neutros de varios ángulos.
2. **Escultura.** Derivados separados para piel, pelo, prendas y accesorios.
   Grandes volúmenes antes de costuras. Copia anterior y procedencia conservadas.
   La malla high-detail es una referencia falible, no canon geométrico definitivo.
3. **Cara y manos.** Párpados con borde y espesor interior alrededor del globo;
   labios, comisuras, cavidad oral y mandíbula. Dientes/lengua cuando se requieran.
   Dedos separados, base de pulgar, membranas interdigitales y loops articulares.
   Evitar concentrar polos en pliegues. No existe un número universal de loops.
4. **Cuerpo.** Flujo que preserve hombros, codos, caderas, rodillas y muñecas.
   Automatización regional con límites protegidos. Densidad según silueta y
   deformación; quads no equivalen automáticamente a buena topología.
5. **Validación para rig.** Probar parpadeo, cierre labial, apertura de mandíbula,
   sonrisa, puño y oposición del pulgar; revisar penetración, separación y pérdida
   de volumen. Son pruebas técnicas, no animación como entrega. No declarar
   rig-ready sin pesos y deformaciones probados.
6. **UV y acabado.** Densidad según cámara de entrega, pruebas de bake, cage,
   costuras y normales antes de texturizar. Mantener proporciones Chibi y pintura
   estilizada; Arcane no justifica convertirlo en humano adulto.
7. **Entrega.** Maestro editable, export probado en destino, hashes, versiones,
   dependencias y renders. Después comenzar Ichiro canónico.

## Innovación reproducible propuesta

Separar conectividad anatómica de ajuste geométrico: plantilla con landmarks,
restricciones de silueta por cámara, penalización de distorsión y desplazamiento
limitado. Oclusiones con menor confianza. Proyección regional que rechace pelo,
ropa y saltos de profundidad: ante ambigüedad marcar revisión, no primer impacto.
La IA puede proponer landmarks, máscaras y alertas como hipótesis revisables.
Esta ruta no requiere entrenar un modelo gigante.

Blender mantiene la autoría. KREATIVE puede consumir el review packet para
comparación sincronizada; LEGION ejecutar trabajos con manifiesto, hash, logs
y semilla cuando aplique. Ver tools/ETHERNIUM_REVIEW_PACKET.md para límites
concretos ya hallados en sus módulos. La integración todavía no está operativa.

## Primer bloque ejecutado

tools/audit_eyelid_geometry.py ejecutado sobre Pass02 con Blender 5.2.
Ambos parches tienen 96 quads, pero A alcanza una arista 23.19 veces la mediana
y B 5.61 veces. Hay 30 y 14 aristas con salto X superior a tres veces la mediana.
El winding del generador estaba invertido y queda corregido en código; el blend
auditado se conserva. Invertir normales no resuelve el mal ajuste geométrico.
No integrar esos parches en un rig de producción.

El auditor no verifica auto-intersecciones, ajuste anatómico, modificadores ni
deformación. El informe no aprueba calidad. Siguiente entrega: aislar piel facial
y reconstruir contornos con profundidad revisada, render frontal/perfiles y
nueva auditoría. No repetir proyección global sobre pelo.
