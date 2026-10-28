# Blender MCP instalado y verificado — 2026-10-28

Instalación autorizada por el usuario. Alcance: Blender y Codex; sin modificar
Antigravity ni instalar RetopoFlow u otras herramientas.

## Componentes

- Servidor publicado PyPI mcp-for-blender==2.2.6, Python 3.12 en
  E:/WORKSPACE/ichiro-blender-mcp-env. Dependencias en MCP_RUNTIME_REQUIREMENTS.txt.
- Fuente inspeccionada: https://github.com/ahujasid/mcp-for-blender
  revisión 8782963ba87a4c90482198bd7c7e17219ac3a0f7.
- Addon de esa revisión copiado como ichiro_mcp_runtime.py en scripts/addons
  de Blender 5.2, habilitado en preferencias y en la sesión abierta.
  SHA256: 6c2917c157c26d7549adcbd480243db2154a9b06bc580664f090530c8ef3801f.
- El antiguo blender_mcp_addon.py de registro vacío no fue eliminado.

El checkout GitHub instalado como paquete falló por ausencia de blender_mcp.config.
Se sustituyó únicamente el servidor por la distribución publicada 2.2.6, que
pasó las comprobaciones. No repetir instalación del paquete desde ese checkout.

## Configuración local de Codex

Entrada blender_ichiro registrada mediante codex mcp add. Ejecutable absoluto:
E:/WORKSPACE/ichiro-blender-mcp-env/Scripts/mcp-for-blender.exe.

Variables: DISABLE_TELEMETRY=true, BLENDER_MCP_SAFE_MODE=1,
BLENDER_HOST=127.0.0.1, BLENDER_PORT=9876.

Listener confirmado en 127.0.0.1:9876 del proceso Blender abierto. No se modificó
el firewall. Consentimiento de telemetría false; todas las integraciones
polyhaven/sketchfab/polypizza/tripo/hunyuan3d/hyper3d/meshy reportan off.
Safe mode pertenece al servidor MCP; no autentica el socket local del addon.

## Verificación

tools/verify_blender_mcp.py usa el SDK MCP: initialize, list_tools,
get_addon_status y execute_blender_code con consulta bpy de solo lectura.
Resultado: protocolo 15 actualizado, Blender 5.2.0 LTS, 10 objetos en la escena
abierta, sin errores. Evidencia: MCP_CONNECTION_CHECK.json.
El test detecta también errores devueltos como texto aunque isError sea false.

```powershell
& E:/WORKSPACE/ichiro-blender-mcp-env/Scripts/python.exe tools/verify_blender_mcp.py
```

El servidor está configurado en Codex, pero esta sesión no ha incorporado sus
herramientas a la lista nativa. Si no aparecen tras recargar la conexión MCP,
reiniciar Codex permite cargar la configuración; no es necesario cerrar Blender.
La conexión al Blender vivo ya fue comprobada con el cliente MCP de prueba.

## Recuperación

- Escena viva respaldada antes de activar el addon, usando save_as_mainfile
  con copy=True: E:/WORKSPACE/Ichiro_Chibi/before_mcp_activation.blend.
  El archivo original no fue sobrescrito. Vista 3D restaurada al terminar.
- Configuración previa de Codex y userpref.blend respaldados localmente en
  E:/WORKSPACE/mcp-for-blender-ichiro. No subir esos backups personales a Git.
- Para retirar conexión de Codex: codex mcp remove blender_ichiro.
  Para detener servidor: panel MCP for Blender, Stop. Desactivar addon en
  preferencias impide su activación futura. No borrar ni restaurar preferencias
  completas sin revisar cambios posteriores.

No se instaló generador de modelos ni se enviaron assets a servicios de generación.
La instalación mejora control/observación; no convierte automáticamente el
personaje en anatomía o topología aprobadas.
