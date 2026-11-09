# configurar_blender.ps1
# Prepara una configuración de Blender AISLADA dentro de herramientas\blender-config, usando el Blender de Steam:
#   - instala las extensiones HEIO (Hedgehog Engine I/O) y Time Eater Tools (scripts\blender\time_eater_tools)
#   - guarda preferencias (directorio temporal dentro del mod) y un archivo de inicio en metros
# Nada se escribe en %APPDATA%: Blender lee las variables BLENDER_USER_*.
# Después, abre Blender siempre con scripts\abrir_blender.bat
#
# Uso: powershell -ExecutionPolicy Bypass -File .\scripts\configurar_blender.ps1 [-BlenderExe <ruta a blender.exe>]

param([string]$BlenderExe = "")

$ErrorActionPreference = "Stop"
$raiz   = Split-Path $PSScriptRoot -Parent
$herr   = Join-Path $raiz "herramientas"
$cfg    = Join-Path $herr "blender-config"

# --- Localizar Blender de Steam -------------------------------------------------
if (-not $BlenderExe) {
    $librerias = @("C:\Program Files (x86)\Steam")
    $vdf = "C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf"
    if (Test-Path $vdf) {
        $librerias += (Select-String -Path $vdf -Pattern '"path"\s+"([^"]+)"').Matches | ForEach-Object { $_.Groups[1].Value -replace '\\\\', '\' }
    }
    foreach ($l in $librerias | Select-Object -Unique) {
        $c = Join-Path $l "steamapps\common\Blender\blender.exe"
        if (Test-Path $c) { $BlenderExe = $c; break }
    }
}
if (-not $BlenderExe -or -not (Test-Path $BlenderExe)) { throw "No se encontró Blender de Steam. Usa -BlenderExe <ruta>" }
Write-Host "Blender: $BlenderExe" -ForegroundColor Cyan

# --- Configuración aislada ---------------------------------------------------------
foreach ($d in "config", "scripts", "extensions", "datafiles", "temp") { New-Item -ItemType Directory -Force -Path (Join-Path $cfg $d) | Out-Null }
[IO.File]::WriteAllText((Join-Path $cfg "blender_exe.txt"), $BlenderExe, (New-Object Text.UTF8Encoding($false)))
$env:TEU_HERRAMIENTAS        = $herr
$env:BLENDER_USER_RESOURCES  = $cfg
$env:BLENDER_USER_CONFIG     = Join-Path $cfg "config"
$env:BLENDER_USER_SCRIPTS    = Join-Path $cfg "scripts"
$env:BLENDER_USER_EXTENSIONS = Join-Path $cfg "extensions"
$env:BLENDER_USER_DATAFILES  = Join-Path $cfg "datafiles"

# --- Empaquetar Time Eater Tools ------------------------------------------------------
$addonSrc = Join-Path $PSScriptRoot "blender\time_eater_tools"
$addonZip = Join-Path $cfg "time_eater_tools.zip"
if (Test-Path $addonZip) { Remove-Item $addonZip }
Compress-Archive -Path (Join-Path $addonSrc "*") -DestinationPath $addonZip

$heioZip = Get-ChildItem (Join-Path $herr "HEIO") -Filter "hedgehog_engine_io-*.zip" | Sort-Object Name | Select-Object -Last 1
if (-not $heioZip) { throw "No está el zip de HEIO en herramientas\HEIO. Ejecuta scripts\descargar_herramientas.ps1" }

# --- Instalar extensiones (repositorio local "user_default") ------------------------------
foreach ($zip in $heioZip.FullName, $addonZip) {
    Write-Host "Instalando $(Split-Path $zip -Leaf)..." -ForegroundColor Cyan
    & $BlenderExe --command extension install-file -r user_default -e $zip
    if ($LASTEXITCODE -ne 0) { throw "Falló la instalación de $zip" }
}

# --- Preferencias y archivo de inicio --------------------------------------------------
$temp = (Join-Path $cfg "temp") -replace '\\', '/'
$py = @"
import bpy, addon_utils
prefs = bpy.context.preferences
prefs.filepaths.temporary_directory = r'$temp'
for mod in ('bl_ext.user_default.hedgehog_engine_io', 'bl_ext.user_default.time_eater_tools'):
    addon_utils.enable(mod, default_set=True, persistent=True)
bpy.ops.wm.save_userpref()
for sc in bpy.data.scenes:
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 1.0
    sc.unit_settings.length_unit = 'METERS'
bpy.ops.wm.save_homefile()
print('TEU_OK', sorted(a.module for a in prefs.addons if a.module.startswith('bl_ext')))
"@
$pyFile = Join-Path $cfg "temp\teu_setup.py"
[IO.File]::WriteAllText($pyFile, $py, (New-Object Text.UTF8Encoding($false)))
& $BlenderExe --background --python $pyFile
if ($LASTEXITCODE -ne 0) { throw "Falló la configuración de preferencias" }
Remove-Item $pyFile

Write-Host ""
Write-Host "Listo. Abre Blender con: scripts\abrir_blender.bat" -ForegroundColor Green
