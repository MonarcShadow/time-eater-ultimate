@echo off
rem Abre el Blender de Steam con una configuración aislada dentro de herramientas\blender-config
rem (addons, preferencias, archivo de inicio y temporales no tocan %APPDATA%).
rem Primero ejecuta una vez: powershell -ExecutionPolicy Bypass -File scripts\configurar_blender.ps1
setlocal
for %%I in ("%~dp0..") do set "RAIZ=%%~fI"
set "TEU_HERRAMIENTAS=%RAIZ%\herramientas"
set "BLENDER_USER_RESOURCES=%TEU_HERRAMIENTAS%\blender-config"
set "BLENDER_USER_CONFIG=%BLENDER_USER_RESOURCES%\config"
set "BLENDER_USER_SCRIPTS=%BLENDER_USER_RESOURCES%\scripts"
set "BLENDER_USER_EXTENSIONS=%BLENDER_USER_RESOURCES%\extensions"
set "BLENDER_USER_DATAFILES=%BLENDER_USER_RESOURCES%\datafiles"

set "BLENDER_EXE="
if exist "%BLENDER_USER_RESOURCES%\blender_exe.txt" set /p BLENDER_EXE=<"%BLENDER_USER_RESOURCES%\blender_exe.txt"
if not defined BLENDER_EXE set "BLENDER_EXE=D:\SteamLibrary\steamapps\common\Blender\blender.exe"
if not exist "%BLENDER_EXE%" (
    echo No se encontro Blender en "%BLENDER_EXE%". Ejecuta scripts\configurar_blender.ps1
    pause
    exit /b 1
)
start "" "%BLENDER_EXE%" %*
