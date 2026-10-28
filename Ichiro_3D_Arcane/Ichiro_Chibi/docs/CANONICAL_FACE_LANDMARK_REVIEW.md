# Revisión de landmarks faciales canónicos — v01

Fuente: `references/ichiro_chibi_front.png` (384 × 472 px). Se anotaron puntos
de comisuras y márgenes oculares, punta nasal, esquinas de la boca y mentón.
La lámina `renders/canonical_face_landmarks_v01.png` muestra cada punto con
índice, confianza y estado de visibilidad.

Las coordenadas son estimaciones manuales de lectura, no una medición aprobada.
El flequillo ocluye parcialmente la esquina externa del ojo a la izquierda de
la imagen. Los valores `visibility` y `confidence` mantienen esa incertidumbre
explícita. No convertir coordenadas de píxel directamente en coordenadas XYZ.

## Criterio de uso

1. Revisar/corregir puntos sobre la referencia y otras vistas disponibles.
2. Registrar una cámara equivalente al render de la malla, con al menos dos
   correspondencias estables y comprobar error de reproyección en las restantes.
3. Mantener separados los landmarks observados, inferidos y ocluidos.
4. Proyectar a superficie solo después de comparar el primer impacto con una
   región facial etiquetada; nunca aceptar una intersección con pelo por ser el
   primer impacto del rayo.
5. Construir loops en una copia independiente y revisar frente, perfiles y 3/4.

El script `tools/render_canonical_face_landmarks.py` genera la lámina con Pillow.
No modifica la malla ni la sesión Blender. El packet de landmarks es una guía
de revisión y no declara la cara, los ojos o el rig aprobados.
