# Script para actualizar automáticamente la versión del mod (0.0.X)
# Incrementar el tercer número (parche) si los primeros dos son los mismos que en el último registro.
# Respeta los cambios manuales en el primer o segundo número.
# Autor: Gemini-AI
# Fecha: 2025-07-15

# --- Configuración ---
# Ruta a la carpeta raíz de tu mod (donde están mod.ini y mod_version.ini)
# EJEMPLO: $modRootFolder = "C:\Users\TuUsuario\Documentos\GitHub\SonicGenerationsTimeEaterMod\SG_Time_Eater_Ultimate"
$modRootFolder = "C:\Users\carlo\Documents\repositorios\time-eater-ultimate\SG_Time_Eater_Ultimate" # <--- ¡CAMBIA ESTO A LA RUTA REAL DE TU MOD!

# Rutas a los archivos INI
$modIniFile = Join-Path $modRootFolder "mod.ini"
$modVersionFile = Join-Path $modRootFolder "mod_version.ini"

# Ruta para almacenar la última versión conocida del commit anterior (dentro de .git/hooks)
# Esto DEBE estar en la carpeta .git/ para que persista con el repositorio pero no se comitee.
$lastKnownVersionFile = Join-Path $PSScriptRoot "last_mod_version.txt"
# --- Lógica del Script ---

Write-Host "Iniciando script de actualización de versión..."

# --- 1. Leer la versión actual de mod_version.ini ---
if (-not (Test-Path $modVersionFile)) {
    Write-Error "Error: No se encontró el archivo mod_version.ini en '$modVersionFile'."
    exit 1
}

$modVersionContent = Get-Content $modVersionFile -Raw
$currentVersionString = ""

if ($modVersionContent -match "(?m)^VersionString=""(.+?)""") {
    $currentVersionString = $Matches[1]
    Write-Host "  Versión actual leída de mod_version.ini: $currentVersionString"
} else {
    Write-Error "Error: No se pudo encontrar 'VersionString' en mod_version.ini."
    exit 1
}

# --- 2. Leer la última versión registrada del commit anterior ---
$lastKnownVersion = ""
if (Test-Path $lastKnownVersionFile) {
    $lastKnownVersion = Get-Content $lastKnownVersionFile -Raw
    Write-Host "  Última versión registrada de commit anterior: $lastKnownVersion"
} else {
    Write-Warning "Advertencia: Archivo de última versión '$lastKnownVersionFile' no encontrado. Asumiendo primer commit o reseteo."
}

# --- 3. Parsear versiones y determinar la nueva versión ---
$currentParts = $currentVersionString -split '\.'
$lastKnownParts = $lastKnownVersion -split '\.'

$newMajor = $currentParts[0]
$newMinor = $currentParts[1]
$newPatch = $currentParts[2]

# Comprobar si la versión mayor y menor son las mismas que en la última versión registrada
# Y si la última versión registrada tiene 3 partes (es válida)
if ($lastKnownParts.Length -eq 3 -and
    $currentParts[0] -eq $lastKnownParts[0] -and
    $currentParts[1] -eq $lastKnownParts[1]) {
    # Si mayor y menor son iguales, incrementar el parche
    $newPatch = [int]$currentParts[2] + 1
    Write-Host "  Incrementando el número de parche. Nueva versión: $($newMajor).$($newMinor).$($newPatch)"
} else {
    # Si mayor o menor han cambiado, o es el primer commit, mantener la versión actual como está
    # y la usaremos como base para futuros incrementos de parche.
    Write-Host "  Detectado cambio manual en la versión mayor/menor o primer commit. Manteniendo la versión actual: $($currentVersionString)"
}

$newVersion = "$($newMajor).$($newMinor).$($newPatch)"

# --- 4. Actualizar mod.ini ---
if (-not (Test-Path $modIniFile)) {
    Write-Error "Error: No se encontró el archivo mod.ini en '$modIniFile'."
    exit 1
}

$modIniContent = Get-Content $modIniFile -Raw
if ($modIniContent -match "(?m)^Version=""(.+?)""") {
    $updatedModIniContent = $modIniContent -replace "(?m)^Version="".+?""", "Version=`"$newVersion`""
    Set-Content -Path $modIniFile -Value $updatedModIniContent -Encoding UTF8 -NoNewline
    Write-Host "mod.ini actualizado con Version=""$newVersion"""
} else {
    Write-Warning "Advertencia: No se encontró 'Version' en mod.ini. Por favor, añádela manualmente."
}

# --- 5. Actualizar mod_version.ini ---
if ($modVersionContent -match "(?m)^VersionString="".+?""") {
    $updatedModVersionContent = $modVersionContent -replace "(?m)^VersionString="".+?""", "VersionString=`"$newVersion`""
    Set-Content -Path $modVersionFile -Value $updatedModVersionContent -Encoding UTF8 -NoNewline
    Write-Host "mod_version.ini actualizado con VersionString=""$newVersion"""
} else {
    Write-Warning "Advertencia: No se encontró 'VersionString' en mod_version.ini. Por favor, añádela manualmente."
}

# --- 6. Guardar la nueva versión como la "última conocida" para el próximo commit ---
$newVersion | Set-Content -Path $lastKnownVersionFile -Encoding UTF8 -NoNewline
Write-Host "Versión '$newVersion' guardada para el próximo seguimiento."

Write-Host "Script de actualización de versión completado."