@echo off
rem Doble clic: descarga y configura todo el entorno de modding de Time Eater Ultimate
rem (herramientas, Blender aislado, archivos del juego y mods de referencia).
rem Se puede ejecutar las veces que haga falta: salta lo que ya esta listo.
title Time Eater Ultimate - Preparar entorno
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\preparar_entorno.ps1" %*
echo.
pause
