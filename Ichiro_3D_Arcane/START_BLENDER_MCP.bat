@echo off
title ETHERNIUM SOVEREIGN // BLENDER 5.2 MCP DAEMON
echo ===============================================================================
echo   ETHERNIUM SOVEREIGN // ICHIRO BLENDER 5.2 MCP DAEMON
echo   TCP Socket Bridge: 127.0.0.1:9876
echo ===============================================================================
echo.
echo Lanzando Blender 5.2 en modo MCP Daemon con la escena maestra...
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" "e:\DESCARGAS\Web3\My web3 Projects\KPR\KPR Art Portfolio\KPR (My art)\KPR Ai Portfolio\Ichiro\Ichiro_3D_Arcane\blend\Ichiro_2390_Arcane_Master.blend" -b --factory-startup -P "e:\DESCARGAS\Web3\My web3 Projects\KPR\KPR Art Portfolio\KPR (My art)\KPR Ai Portfolio\Ichiro\Ichiro_3D_Arcane\mcp\blender_mcp_addon.py" -- --mcp-daemon
pause
