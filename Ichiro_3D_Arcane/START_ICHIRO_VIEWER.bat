@echo off
title ETHERNIUM SOVEREIGN // ICHIRO 3D ARCANE WEB VIEWER
echo ===============================================================================
echo   ETHERNIUM SOVEREIGN // KPR-2390 ICHIRO ARCANE 2.3D WEB VIEWER
echo   Local-First Three.js GPU Engine ^| Cyberpunk Glassmorphic HUD
echo ===============================================================================
echo.
echo Iniciando servidor local en http://localhost:8080/viewer/ ...
start "" http://localhost:8080/viewer/
py -m http.server 8080
pause
