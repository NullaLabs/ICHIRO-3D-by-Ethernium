# Ichiro Chibi: conservar diseño, reparar conectividad, preparar rig de juego

Fecha: 2026-11-05.

## Dirección del usuario y estado

El usuario prefiere el aspecto original. Quedan descartadas como dirección de
producción las correcciones estéticas de nariz y cresta. Sus experimentos se
conservan como historial; la nueva escena parte de la fuente ORIGINAL y no
contiene esas shape keys. La prioridad es rig y uso en juego; impresión es una
copia derivada con requisitos propios.

Entrega: `exports/rig_connectivity_v01/Ichiro_Chibi_Rig_Connectivity_v01.blend`.
Objeto activo: `ICH_CHIBI_CONNECTIVITY_CANDIDATE_v01`.
La fuente enlazada permanece protegida y oculta. La candidata está reparada a
nivel manifold de aristas y vértices; todavía NO tiene topología de deformación,
rig funcional ni certificación para impresión.

## Trabajo ejecutado en Blender MCP

1. Desactivar todas las correcciones estéticas y copiar la fuente original.
2. Soldar vértices a distancia `1e-6`, con altura del personaje de una unidad.
3. Inspeccionar los defectos residuales; aislar la corona de caras alrededor de
   aristas abiertas o compartidas por más de dos caras.
4. Reemplazar 1.199 caras defectuosas y vecinas por 541 triángulos, repartidos en
   82 parches pequeños. Cada contorno debe ser simple; el script se detiene si
   una extensión supera `0.008` unidades. Máxima extensión observada: `0.00705314`.
5. Transferir UV de cada triángulo nuevo usando la cara fuente más cercana a su
   centro, para evitar mezclar directamente coordenadas de islas del atlas.
   Puede haber extrapolación local: se comprueba mediante renders.
6. Recalcular orientación y validar manifold antes de escribir la malla.

El relleno automático inicial dejó dos contornos abiertos y NO se aplicó a la
malla persistente. El procedimiento final ordena explícitamente cada contorno,
crea su cara y triangula. Todos los parches pasaron la comprobación final.

## Resultados medidos

| Medida | Fuente | Soldadura | Reparación final |
| --- | ---: | ---: | ---: |
| Vértices | 773.535 | 747.752 | 747.423 |
| Caras triangulares | 1.495.680 | 1.495.516 | 1.494.858 |
| Aristas de borde | 51.028 | 164 | 0 |
| Aristas con más de dos caras | 0 | 164 | 0 |
| Vértices no manifold | No medido | No medido | 0 |

La soldadura conectó las 181 islas previas en una sola componente.
La reparación final no presenta caras de área inferior a `1e-12`.
Volumen firmado positivo: `0.03974281073848724` unidades cúbicas.
Distancia máxima medida entre los centros de los 541 triángulos nuevos y la
fuente: `0.00044497` unidades. Esto NO es una distancia Hausdorff global.
No se ejecutó comprobación de auto-intersecciones ni de espesor imprimible.

## Conservación del aspecto

Se renderizaron original y reparado desde las mismas ocho cámaras ortográficas
a 512 × 512, con el mismo material y configuración. En las ocho vistas:

- IoU de silueta = 1.0; cero píxeles diferentes en las máscaras alfa a umbral 127.
- Diferencia RGB media dentro del personaje entre 0,043 y 0,075 sobre 255.
- La mayor fracción de píxeles del personaje con diferencia superior a 10 en
  algún canal es 0,110 %. Son diferencias localizadas de sombreado/UV.

Se revisaron también frontal facial a 768 px y el mosaico completo. La igualdad
de máscara a 512 px no prueba igualdad geométrica exacta ni ausencia de defectos
a otra resolución. Se conserva el diseño; el siguiente pase debe mantenerlo.

Evidencia: `renders/rig_connectivity_v01/appearance_comparison.json`,
`geometry_audit.json`, `original_vs_repaired_face.png` y
`repaired_eight_views.png`.

## Reproducción

Desde `Ichiro_Chibi/`:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python tools/build_rig_connectivity_v01.py -- --out E:/WORKSPACE/Ichiro/nueva_conectividad
python tools/package_rig_connectivity_v01.py E:/WORKSPACE/Ichiro/nueva_conectividad
```

Se ejecutó la receta completa en un proceso nuevo con factory startup; terminó
correctamente y reprodujo los recuentos de la reparación de la sesión MCP.
El constructor se niega a sobrescribir una escena de salida existente.

## Próximo trabajo: topología de deformación

Esta malla de 1,49 millones de triángulos es una fuente de proyección y baking.
La malla para juego necesita loops funcionales, densidad adecuada y pruebas
estáticas de deformación. Priorizar párpados/boca, hombros/codos, cadera/rodillas,
muñecas/manos/dedos. Conservar silueta mediante proyección controlada y comparar
renders; el rig no debe usarse para disimular una topología defectuosa.

Un personaje de juego puede ser un único asset con varias superficies para
ojos, boca y accesorios. No es necesario soldar el globo ocular al párpado.
La copia imprimible sí requerirá evaluar volumen cerrado, intersecciones,
espesores y soportes a escala física, además de las comprobaciones manifold.

Modelo siguiente: mantener Astra para definir la primera región de retopología
y sus pruebas de deformación. Sol 6.1 será apropiado para automatizar una receta
ya definida y ejecutar sus verificaciones.
