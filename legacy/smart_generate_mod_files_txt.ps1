# Script para generar mod_files.txt de forma inteligente, manejando 'add' y 'delete'.
# Compara los archivos presentes en el sistema de archivos con los que ya están en mod_files.txt.
# Autor: Gemini-AI
# Fecha: 2025-07-15

# --- Configuración (¡IMPORTANTE: Ajusta 'modRootFolder' a la ruta REAL de tu mod!) ---
# Ruta a la carpeta raíz de tu mod (donde están mod_files.txt y las carpetas de contenido)
# EJEMPLO: $modRootFolder = "C:\Users\TuUsuario\Documentos\GitHub\SonicGenerationsTimeEaterMod\SG_Time_Eater_Ultimate"
$modRootFolder = "C:\Users\carlo\Documents\repositorios\time-eater-ultimate\SG_Time_Eater_Ultimate" # <--- ¡CAMBIA ESTO A LA RUTA REAL DE TU MOD!

# Nombres de las subcarpetas dentro de $modRootFolder que contienen los archivos del mod
$modContentFolders = @("disk", "movie", "sound") # <--- Ajusta esta lista si tienes más carpetas de contenido

# Ruta al archivo mod_files.txt
$modFilesTxt = Join-Path $modRootFolder "mod_files.txt"

# Archivos de metadatos/control que deben ser incluidos explícitamente en mod_files.txt
# y que no están en las carpetas de contenido (ej. mod.ini, config.json en la raíz del mod)
$explicitlyIncludedFiles = @("mod.ini") # Puedes añadir otros como "config.json" si los usas

# --- Lógica del Script ---

Write-Host "Iniciando script para generar mod_files.txt de forma inteligente..."

# Verificar si la carpeta raíz del mod existe
if (-not (Test-Path $modRootFolder -PathType Container)) {
    Write-Error "Error: No se encontró la carpeta raíz del mod en '$modRootFolder'."
    exit 1
}

# 1. Obtener la lista actual de archivos y sus rutas relativas en el sistema de archivos
Write-Host "Escaneando archivos actuales en las carpetas de contenido..."
$currentFilesInSystem = New-Object System.Collections.Generic.HashSet[string] # Usamos HashSet para búsquedas eficientes

foreach ($folderName in $modContentFolders) {
    $currentFolderPath = Join-Path $modRootFolder $folderName
    if (Test-Path $currentFolderPath -PathType Container) {
        $files = Get-ChildItem -Path $currentFolderPath -Recurse -File -ErrorAction SilentlyContinue
        foreach ($file in $files) {
            $relativePath = $file.FullName.Replace($modRootFolder + "\", "")
            $relativePath = $relativePath.Replace("\", "/") # <--- AÑADE ESTA LÍNEA
            [void]$currentFilesInSystem.Add($relativePath)
        }
    }
}

# Añadir archivos explícitamente incluidos al HashSet si existen
foreach ($fileName in $explicitlyIncludedFiles) {
    $fullPath = Join-Path $modRootFolder $fileName
    if (Test-Path $fullPath -PathType Leaf) {
        [void]$currentFilesInSystem.Add($fileName)
    }
}

# 2. Leer el mod_files.txt existente para ver qué archivos se gestionaban previamente
Write-Host "Leyendo el mod_files.txt existente para identificar archivos previos..."
$filesInExistingModFiles = New-Object System.Collections.Generic.HashSet[string]
$existingLines = @()

if (Test-Path $modFilesTxt) {
    $existingLines = Get-Content $modFilesTxt -Encoding UTF8
    foreach ($line in $existingLines) {
        $trimmedLine = $line.Trim()
        if ($trimmedLine -match "^(add|delete)\s+[`"']?(.+?)[`"']?$") { # Captura add/delete y la ruta
            $action = $Matches[1]
            $filePath = $Matches[2].Trim()
            $filePath = $filePath.TrimStart('"').TrimEnd('"') # Quita comillas si las tiene
            [void]$filesInExistingModFiles.Add($filePath)
        }
    }
} else {
    Write-Warning "Advertencia: mod_files.txt no encontrado. Se creará uno nuevo."
}

# 3. Determinar qué líneas deben ir en el nuevo mod_files.txt
$outputLines = New-Object System.Collections.Generic.List[string]

# Añadir un encabezado al archivo mod_files.txt
#$outputLines.Add("; Este archivo fue generado automáticamente por un script de PowerShell.")
#$outputLines.Add("; ¡No edites este archivo manualmente a menos que sepas lo que haces!")
#$outputLines.Add("; Los comentarios con ';' son ignorados por Hedgehog Engine Mod Manager.")
#$outputLines.Add("")

# Añadir líneas 'delete' para archivos que ya no están en el sistema de archivos pero estaban en el mod_files.txt
$deletedFilesCount = 0
foreach ($filePath in $filesInExistingModFiles) {
    if (-not $currentFilesInSystem.Contains($filePath)) {
        # Si el archivo NO está en el sistema actual pero HEMM lo conocía, debe ser eliminado.
        $outputLines.Add("delete $filePath")
        $deletedFilesCount++
    }
}
if ($deletedFilesCount -gt 0) {
    #$outputLines.Add("") # Añadir línea en blanco si hay deletes
    Write-Host "  Añadidas $deletedFilesCount líneas 'delete' por archivos que ya no existen."
}


# Añadir líneas 'add' para todos los archivos presentes en el sistema de archivos
$addedFilesCount = 0
foreach ($filePath in $currentFilesInSystem) {
    $outputLines.Add("add $filePath")
    $addedFilesCount++
}
Write-Host "  Añadidas $addedFilesCount líneas 'add' por archivos presentes en el sistema."

# 4. Escribir el nuevo contenido en mod_files.txt
Set-Content -Path $modFilesTxt -Value ($outputLines -join "`n") -Encoding UTF8 -NoNewline

Write-Host "mod_files.txt generado y actualizado con $(($outputLines.Count) - 4) entradas."
Write-Host "Script completado."