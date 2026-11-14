@echo off
rem Doble clic: copia el mod construido (carpeta mod\) a la carpeta de mods del juego,
rem para probar cambios sin publicar una release. Despues, iniciar el juego desde HMM.
title Time Eater Ultimate - Probar en el juego
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\probar_en_juego.ps1" %*
echo.
pause
