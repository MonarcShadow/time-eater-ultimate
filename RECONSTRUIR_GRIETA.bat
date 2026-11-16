@echo off
rem Doble clic: reconstruye "Grieta del Tiempo" (lee niveles\grieta_del_tiempo\ajustes.conf) y copia el mod
rem al juego. Despues, en el juego, salir al White Space y volver a entrar al nivel.
title Time Eater Ultimate - Reconstruir Grieta del Tiempo
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\construir_nivel.ps1" -Nivel grieta_del_tiempo
if errorlevel 1 (
    echo.
    echo *** La construccion fallo: no se copio nada al juego. ***
    echo.
    pause
    exit /b 1
)
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\probar_en_juego.ps1"
echo.
pause
