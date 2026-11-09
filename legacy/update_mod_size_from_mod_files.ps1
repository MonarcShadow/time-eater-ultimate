# Script para actualizar DownloadSizeString en mod_version.ini
# Calcula el tamaño total de los archivos listados en mod_files.txt
# Autor: Gemini-AI
# Fecha: 2025-07-15

# --- Configuración ---
# Ruta a la carpeta raíz de tu mod (donde está mod_files.txt y mod_version.ini)
# EJEMPLO: $modRootFolder = "C:\Users\TuUsuario\Documentos\GitHub\SonicGenerationsTimeEaterMod\SG_Time_Eater_Ultimate"
$modRootFolder = "C:\Users\carlo\Documents\repositorios\time-eater-ultimate\SG_Time_Eater_Ultimate" # <--- ¡VERIFICA ESTA RUTA!

# Ruta al archivo mod_files.txt
$modFilesTxt = Join-Path $modRootFolder "mod_files.txt"

# Ruta al archivo mod_version.ini
$modVersionIni = Join-Path $modRootFolder "mod_version.ini"

# --- Lógica del Script ---

Write-Host "Iniciando script para actualizar DownloadSizeString desde mod_files.txt..."

# Verificar si los archivos existen
if (-not (Test-Path $modFilesTxt)) {
    Write-Error "Error: No se encontró mod_files.txt en '$modFilesTxt'."
    exit 1
}
if (-not (Test-Path $modVersionIni)) {
    Write-Error "Error: No se encontró mod_version.ini en '$modVersionIni'."
    exit 1
}

Write-Host "Calculando el tamaño de los archivos especificados en '$modFilesTxt'..."

$totalSizeBytes = 0
$filesProcessedCount = 0

# Leer el mod_files.txt línea por línea
$modFilesContent = Get-Content $modFilesTxt -Encoding UTF8

foreach ($line in $modFilesContent) {
    $trimmedLine = $line.Trim()
    # Solo procesar líneas que empiezan con 'add ' (ignorando 'delete' y comentarios)
    if ($trimmedLine -match "^add\s+[`"']?(.+?)[`"']?$") {
        $relativePath = $Matches[1].Trim()
        $relativePath = $relativePath.TrimStart('"').TrimEnd('"') # Quita comillas si las tiene

        $fullPath = Join-Path $modRootFolder $relativePath

        if (Test-Path $fullPath -PathType Leaf) {
            $fileInfo = Get-Item $fullPath
            $fileSize = $fileInfo.Length # El tamaño en bytes
            $totalSizeBytes += $fileSize
            $filesProcessedCount++

            # Para depuración: Mostrar el tamaño individual
            # [double]$sizeMB = $fileSize / 1MB
            # Write-Host "  Añadido: $relativePath - $($sizeMB.ToString("N2")) MB"
        } else {
            Write-Warning "Advertencia: Archivo no encontrado (ignorado en el cálculo de tamaño): '$relativePath'"
        }
    }
}

if ($filesProcessedCount -eq 0) {
    Write-Warning "Advertencia: No se encontraron archivos 'add' válidos en mod_files.txt para calcular el tamaño. Se establecerá DownloadSizeString en '0 MB'."
    $downloadSizeString = "0 MB"
} else {
    # Convertir a Megabytes (usando 1MB = 1024*1024 bytes para más precisión)
    # y asegurarse de que la división sea de punto flotante.
    [double]$totalSizeMB = $totalSizeBytes / 1MB
    # Formatear a dos decimales y usar coma como separador decimal si es necesario
    $downloadSizeString = "$($totalSizeMB.ToString("N2", [System.Globalization.CultureInfo]::CurrentCulture)) MB"
    Write-Host "`nTamaño total calculado para la descarga: $downloadSizeString"
}

# Leer el contenido de mod_version.ini
$modVersionContent = Get-Content $modVersionIni -Raw

# Actualizar la línea DownloadSizeString
if ($modVersionContent -match "(?m)^DownloadSizeString="".*?""") {
    $updatedModVersionContent = $modVersionContent -replace "(?m)^DownloadSizeString="".*?""", "DownloadSizeString=`"$downloadSizeString`""
    Set-Content -Path $modVersionIni -Value $updatedModVersionContent -Encoding UTF8 -NoNewline
    Write-Host "mod_version.ini actualizado con DownloadSizeString=""$downloadSizeString"""
} else {
    Write-Warning "Advertencia: No se encontró 'DownloadSizeString' en mod_version.ini. Por favor, añádela manualmente."
}

Write-Host "Script completado."