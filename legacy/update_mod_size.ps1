# Script para actualizar DownloadSizeString en mod_version.ini
# Autor: Gemini-AI
# Fecha: 2025-07-15
$OutputEncoding = [System.Text.Encoding]::UTF8
# --- Configuración (¡IMPORTANTE: Ajusta 'modRootFolder' a la ruta REAL de tu mod!) ---
# Ruta a la carpeta raíz de tu mod (donde está mod_version.ini, mod.ini y las carpetas de contenido como disk/, movie/, sound/)
# EJEMPLO: $modRootFolder = "C:\Users\TuUsuario\Documentos\GitHub\SonicGenerationsTimeEaterMod\SG_Time_Eater_Ultimate"
$modRootFolder = "C:\Users\carlo\Documents\repositorios\time-eater-ultimate\SG_Time_Eater_Ultimate" # <--- ¡CAMBIA ESTO A LA RUTA REAL DE TU MOD!

# Nombres de las subcarpetas dentro de $modRootFolder que contienen los archivos del mod
# Estas deben coincidir con tus carpetas de contenido como 'disk', 'movie', 'sound', etc.
$modContentFolders = @("disk", "movie", "sound") # <--- Ajusta esta lista si tienes más carpetas de contenido

# Ruta al archivo mod_version.ini (no necesita ajuste si $modRootFolder es correcto)
$modVersionFile = Join-Path $modRootFolder "mod_version.ini"

# --- Lógica del Script ---

Write-Host "Iniciando script para actualizar DownloadSizeString..."

# Verificar si el archivo mod_version.ini existe
if (-not (Test-Path $modVersionFile)) {
    Write-Error "Error: No se encontró el archivo mod_version.ini en '$modVersionFile'."
    exit 1
}

Write-Host "Calculando el tamaño de los archivos del mod en '$modRootFolder'..."

$totalSizeKB = 0

# Iterar sobre cada carpeta de contenido especificada
foreach ($folderName in $modContentFolders) {
    $currentFolderPath = Join-Path $modRootFolder $folderName
    if (Test-Path $currentFolderPath -PathType Container) {
        Write-Host "  Procesando carpeta: '$currentFolderPath'"
        # Obtener todos los archivos en la carpeta actual y sus subcarpetas
        # -Recurse para incluir subcarpetas
        # -File para asegurarse de que solo se procesen archivos
        # -ErrorAction SilentlyContinue para ignorar errores si no hay permisos o archivos extraños
        $files = Get-ChildItem -Path $currentFolderPath -Recurse -File -ErrorAction SilentlyContinue
        foreach ($file in $files) {
            $totalSizeKB += ($file.Length / 1KB) # Sumar el tamaño de cada archivo en Kilobytes
        }
    } else {
        Write-Warning "Advertencia: La carpeta '$folderName' no existe en '$modRootFolder'. Se omitirá de la suma."
    }
}

# Calcular el tamaño del mod.ini si existe en la raíz del mod y debe ser parte del paquete de descarga
$modIniFile = Join-Path $modRootFolder "mod.ini"
if (Test-Path $modIniFile -PathType Leaf) {
    $totalSizeKB += ((Get-Item $modIniFile).Length / 1KB)
    Write-Host "  Incluyendo tamaño de mod.ini."
} else {
    Write-Warning "Advertencia: mod.ini no encontrado en la raíz del mod. No se incluirá en el cálculo del tamaño."
}


# Convertir el tamaño total a un formato legible (KB o MB)
$formattedSize = ""
if ($totalSizeKB -lt 1024) { # Si es menor a 1 MB, mostrar en KB
    $formattedSize = "{0:N0} KB" -f $totalSizeKB
} else { # Si es 1 MB o más, mostrar en MB con dos decimales
    $formattedSize = "{0:N2} MB" -f ($totalSizeKB / 1MB)
}

Write-Host ""
Write-Host "Tamaño total calculado para la descarga: $formattedSize"

# Leer el contenido actual de mod_version.ini
$modVersionContent = Get-Content $modVersionFile -Raw

# Actualizar la línea DownloadSizeString usando una expresión regular
# (?m)^ indica que ^ coincide con el inicio de cada línea (multilínea)
# "[^""]*" coincide con cualquier carácter que no sea comilla, cero o más veces.
if ($modVersionContent -match "(?m)^DownloadSizeString=""[^""]*""") {
    $updatedContent = $modVersionContent -replace "(?m)^DownloadSizeString=""[^""]*""", "DownloadSizeString=`"$formattedSize`""
    Set-Content -Path $modVersionFile -Value $updatedContent -Encoding UTF8 -NoNewline
    Write-Host "mod_version.ini actualizado con DownloadSizeString=""$formattedSize"""
} else {
    Write-Warning "Advertencia: No se encontró la línea 'DownloadSizeString' en mod_version.ini. Asegúrate de que exista y tenga el formato correcto."
}

Write-Host "Script completado."