# Herramientas prioritarias y prueba Shrinkwrap

## Resultado implementado

setup_shrinkwrap_review.py crea una escena separada con Shrinkwrap nativo,
NEAREST_SURFACEPOINT, offset 0.0008, grupo INFERRED_DEPTH_REVIEW y máscara de
piel como target. No aplica el modificador; precede al wireframe de revisión.
96 vértices conservados, sin caras degeneradas/invertidas. Desplazamiento máximo
0.0043604; vértices 87 y 88 superan 0.004. No aprobado como ajuste anatómico.
La máscara incompleta sigue siendo el cuello de botella, no la ausencia de
Shrinkwrap. Resultado local: Ichiro_Chibi_Shrinkwrap_Review.blend.

## Inventario y decisión

- Blender 5.2 y Python disponibles: suficientes para seguir sin instalar nada.
- Encontrados LoopTools, PolyQuilt_Fork, qremeshify, Ucupaint y VRM en carpetas
  de extensiones. Presencia de archivos no prueba activación ni compatibilidad.
- blender_mcp_addon.py en scripts/addons contiene solo bl_info y funciones
  register/unregister que imprimen texto. No implementa socket, servidor ni
  ejecución de comandos. No confundir su nombre con un MCP funcional.
- No hay herramienta Blender MCP expuesta en este chat; búsqueda del catálogo
  de plugins por Blender sin resultados. Se puede evaluar configuración externa,
  sin afirmar que ya exista conexión.

Prioridad 1: control de sesión y retopología interactiva. Revisar/instalar un
puente funcional solo con autorización; limitarlo a localhost y revisar datos
que transmite. ahujasid/mcp-for-blender ofrece control y observación, no habilidad
artística automática: https://github.com/ahujasid/mcp-for-blender

Prioridad 2: RetopoFlow compatible con 5.2 para curvas, patches y relax. El
changelog declara compatibilidad desde 4.1.9. Confirmar paquete y condiciones de
distribución concretas antes de descargar/instalar; no asumir que toda versión
es gratuita: https://docs.retopoflow.com/v4/changelist.html

Prioridad 3: probar lo instalado (LoopTools/PolyQuilt) en escena desechable antes
de añadir alternativas. No activar extensiones incompatibles en la sesión viva.

Ucupaint es candidato para acabado posterior; remalladores para superficies
secundarias. Rigify y herramientas de pesos después de anatomía/topología.
No hace falta ahora entrenar modelos, adquirir servicios de generación ni
instalar grandes dependencias. La forma y el flujo de deformación necesitan
criterio artístico y pruebas; el número de scripts no mide progreso del personaje.

Una skill futura útil reuniría guardado, selección de target, ajuste de cámaras,
validación visual y controles de deformación. No sustituye dichas operaciones.
No se instaló ni activó ninguna herramienta en esta evaluación.
