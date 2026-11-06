# Ichiro Chibi: revisión de forma y primera corrección reversible

Fecha: 2026-11-05. Estado: candidata para revisión artística, no canon aprobado.

## Entrega

- Escena: `exports/form_review_v01/Ichiro_Chibi_Form_Review_v01.blend` (Git LFS).
- Evidencia: `renders/form_review_v01/`, ocho cámaras ortográficas fijas, antes/después frontal y perfiles, manos, referencias y manifiesto SHA-256.
- Reproducción: `tools/build_form_review_v01.py`; empaquetado: `tools/package_form_review_v01.py`.
- Fuente original intacta: workspace SHA-256 `d906a5b55041a8047a3b38d8e346cf41f9fa6cd7f08ccc3f121c2b8c41fb5b86`.

Se abrió Blender mediante MCP y se conservó la sesión inicial vacía en
`E:/WORKSPACE/Ichiro/review_2026-11-05/session_before_review.blend` antes de abrir el personaje.
La escena de revisión conserva el objeto fuente enlazado y oculto; la candidata
es una copia local con una shape key que permite alternar el cambio entre 0 y 1.

## Diagnóstico visual

Se examinaron las cuatro placas individuales, el turnaround de ocho ángulos y
la lámina de proceso Kimi. Esta última orienta el diseño, pero no demuestra que
existan los rigs, UVs o topologías que representa. Las cámaras de las imágenes
no están calibradas; no se declara una reconstrucción exacta ni una puntuación
numérica de fidelidad.

Tres prioridades observadas:

1. **Rostro.** La nariz presenta una punta/puente prominentes y angulosos; las
   cejas son relieves gruesos. Se ven discontinuidades de sombreado y superficies
   oculares talladas en el modelo visible. Los globos de prueba ocultos de otro
   pase no constituyen una solución integrada. Párpados, boca y cavidad oral
   necesitan construcción funcional independiente de esta corrección.
2. **Cabello.** La cresta frontal tiene masas redondeadas y estrías anchas; las
   referencias muestran mechones y puntas más definidos. Corregir por mechón,
   conservando flequillo asimétrico, lateral rapado y lectura posterior.
3. **Manos.** Los puños contienen separaciones superficiales de dedos; esta
   observación no prueba que puedan abrirse ni deformarse. Hace falta revisar
   la estructura digital y construir dedos articulables antes de aprobar rig.

Las irregularidades de chaqueta observadas con textura se revisaron también en
clay. No se aplicó un suavizado global: parte de la lectura viene del material y
las facetas son parte del lenguaje visual de las referencias.

## Primera intervención

Shape key `REVIEW_Nose_Projection_Reduction` sobre `ICH_CHIBI_FORM_CANDIDATE_v01`.
Se reduce suavemente la proyección nasal en X y ligeramente la anchura local en
Y. Campo compacto centrado en `(y,z)=(-0.015,0.226)`, radios `(0.034,0.038)`,
desplazamiento X máximo `-0.007`, contracción lateral `0.08`, transición smoothstep
en X entre `0.09` y `0.11`. Fuera de esa región el desplazamiento es cero.
Los parámetros son una hipótesis artística, no medidas anatómicas deducidas de
cámaras calibradas. La corrección produce un perfil menos saliente; conserva
limitaciones de expresión y topología y requiere revisión posterior.

## Verificación ejecutada

- Basis idéntica vértice por vértice a la fuente enlazada.
- 4.001 vértices con desplazamiento mayor que `1e-9` (4.018 visitados por el campo).
- Desplazamiento máximo `0.006997311422677403` unidades de escena.
- 7.803 triángulos afectados: cero inversiones respecto a sus normales iniciales;
  cero productos cruzados de área menores que `1e-12`.
- No se ejecutó prueba de auto-intersecciones; no se declara geometría final.
- Se revisaron visualmente frontal, perfiles, textura frontal y ocho vistas clay.
- Reproducción completa en un proceso nuevo de Blender 5.2 con `--factory-startup`:
  terminó correctamente. Los PNG frontal inicial, frontal corregido y perfil
  izquierdo corregido coinciden píxel a píxel con la ejecución MCP.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python tools/build_form_review_v01.py -- --out E:/WORKSPACE/Ichiro/nueva_revision
python tools/package_form_review_v01.py E:/WORKSPACE/Ichiro/nueva_revision
```

Ejecutar desde `Ichiro_Chibi/`. El constructor requiere una carpeta de salida
sin un archivo de revisión previo. El empaquetador actualiza la evidencia v01;
sus métricas de validación están identificadas como mediciones registradas de
esta sesión, no como resultados recalculados para cualquier entrada.

## Siguiente decisión

Priorizar forma y anatomía antes del benchmark N-view/Remi/SNN del plan anterior.
El próximo ajuste artístico es separar y definir los mechones de la cresta
frontal, con comparación en frontal, perfiles y tres cuartos. No confundir un
remallado más regular con una mejora de diseño. Automatizar solamente lo que
demuestre utilidad sobre el personaje.

Modelo recomendado al terminar este bloque: **mantener Astra**, por las
decisiones visuales y las referencias aún sin calibrar. Cambiar a **Sol 6.1**
cuando estén definidos el componente, los límites de edición y los criterios
de aceptación de una implementación concreta.
