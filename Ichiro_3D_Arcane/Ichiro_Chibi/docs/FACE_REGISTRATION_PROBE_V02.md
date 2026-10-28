# Registro 2D de landmarks canónicos — probe v02

Se ajustó una transformación afín 2D de cinco anclas (centros oculares, nariz,
centro de boca y mentón) desde `ichiro_chibi_front.png` hacia
`renders/skin_review_source.png`. La cámara de este último es ortográfica,
768², escala 0.32, objetivo Z=0.285 y frontal +X. La cámara de la referencia
canónica no está disponible; esto es registro de imagen, no calibración de cámara.

## Resultado

- RMS de los cinco anclajes: 8.55 px en el render fuente (3.64% de la separación
  ocular estimada). Error máximo: 15.57 px en el centro de boca.
- La proyección de 12 puntos canónicos contra la máscara cálida encuentra 7
  impactos candidatos y 5 sin soporte. No se obtuvo un estado fiable de piel
  para todos los puntos.
- La lámina `renders/face_registration_probe_v02.png` permite inspeccionar los
  puntos. Verde = impacto candidato pendiente de juicio; rojo = la máscara no
  tiene candidato. Ninguno está aprobado como geometría.

La imagen muestra que el ajuste sirve para guiar una revisión aproximada de los
ojos, nariz y mentón. Los puntos altos del ojo derecho y los puntos ocluidos del
flequillo no tienen soporte semántico. La esquina izquierda de la boca acusa el
mayor desvío, señal de que un ajuste afín global no conserva todos los rasgos.

## Reproducción

Con Blender 5.2:

```powershell
blender --background --factory-startup --python-exit-code 1 --python tools/register_canonical_face_to_source.py
```

Después generar la lámina:

```powershell
python tools/render_face_registration_probe.py
```

El informe JSON registra los hashes, transformación, residuales, impactos y
limitaciones. El script no guarda ni modifica una escena Blender.

## Puerta de producción

No generar párpados a partir de este probe. Primero hay que marcar la región de
piel en la referencia/render, resolver oclusiones, reducir el error local del
contorno ocular y comprobar las vistas laterales. El ajuste solo produce
coordenadas candidatas 2D; no reemplaza landmarks artísticos ni verifica
superficie, anatomía, contacto o deformación.
