# Script: extract_game_archives.ps1
# Desempaqueta archivos .ar.00/.ar.01 del juego a la estructura de tu REPOSITORIO (fuera de la carpeta del mod).
# Los contenidos de cada AR se moverán a una subcarpeta con el nombre del AR dentro de disk/bbX.

# --- Configuración ---
# La ruta a la raíz de tu REPOSITORIO (time-eater-ultimate), no a la carpeta del mod.
$repoRootFolder = "C:\Users\carlo\Documents\repositorios\time-eater-ultimate" 
$artoolsPath = "D:\modding\sonic_generation\Artools"
$ar0unpackExe = Join-Path $artoolsPath "ar0unpack.exe"

# Archivo de texto que lista los archivos AR a extraer
$archivesListFile = Join-Path (Split-Path $MyInvocation.MyCommand.Definition -Parent) "archives_to_extract.txt"

# Carpeta base de destino en la raíz del repositorio para los contenidos extraídos
$repoDiskFolder = Join-Path $repoRootFolder "disk"

# --- Lógica del Script ---

if (-not (Test-Path $ar0unpackExe)) {
    Write-Error "Error: ar0unpack.exe no encontrado en '$ar0unpackExe'. Ajusta la ruta."
    exit 1
}
if (-not (Test-Path $archivesListFile)) {
    Write-Error "Error: El archivo '$archivesListFile' no fue encontrado. Créalo con las rutas de los archivos AR a extraer."
    exit 1
}

Write-Host "Iniciando la extracción de archivos AR del juego a la carpeta 'disk' del repositorio..."

# Asegurarse de que la carpeta 'disk' en la raíz del repositorio exista
New-Item -ItemType Directory -Path $repoDiskFolder -Force | Out-Null


Get-Content $archivesListFile | ForEach-Object {
    $line = $_.Trim()
    if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith("#")) {
        # Ignorar líneas vacías o comentarios
        return
    }

    $parts = $line -split '\|'
    if ($parts.Length -ne 2) {
        Write-Warning "Formato de línea inválido en '$archivesListFile': '$line'. Saltando."
        return
    }

    $sourceARPath = $parts[0]
    # relativeDestPath ahora es la subcarpeta bbX (ej: "bb3\") donde se moverá la carpeta del AR
    $relativeDestPath = $parts[1]

    if (-not (Test-Path $sourceARPath)) {
        Write-Warning "Archivo AR de origen no encontrado: '$sourceARPath'. Saltando."
        return
    }

    # Determinar el nombre de la carpeta que ar0unpack.exe crea
    # ar0unpack.exe crea una carpeta con el nombre del AR sin la extensión completa (.ar.00)
    $sourceARFileName = Split-Path $sourceARPath -Leaf # Ej: Sonic.ar.00
    $nameWithout00 = [System.IO.Path]::GetFileNameWithoutExtension($sourceARFileName) # Ej: Sonic.ar
    $extractedFolderName = [System.IO.Path]::GetFileNameWithoutExtension($nameWithout00) # Ej: Sonic

    # Carpeta donde ar0unpack.exe creará el contenido extraído (junto al AR original)
    $extractedFolderInSource = Join-Path (Split-Path $sourceARPath -Parent) $extractedFolderName

    Write-Host "`nDesempaquetando '$sourceARFileName' de '$sourceARPath'..."
    Invoke-Expression "& `"$ar0unpackExe`" `"$sourceARPath`""

    # Mover el contenido desempaquetado a la carpeta de destino en el REPOSITORIO
    if (Test-Path $extractedFolderInSource) {
        # La carpeta de destino final para el contenido extraído (ej: repoRoot/disk/bb3/Sonic/)
        $finalDestinationFolder = Join-Path $repoDiskFolder "$relativeDestPath\$extractedFolderName"
        New-Item -ItemType Directory -Path $finalDestinationFolder -Force | Out-Null # Asegurarse de que exista

        Write-Host "Moviendo contenido de '$extractedFolderInSource' a '$finalDestinationFolder'..."
        
        # Mover los contenidos (archivos y subcarpetas) de la carpeta extraída a la carpeta final de destino
        Get-ChildItem -Path $extractedFolderInSource -Force | ForEach-Object {
            Move-Item -Path $_.FullName -Destination $finalDestinationFolder -Force
        }
        Remove-Item -Path $extractedFolderInSource -Recurse -Force # Eliminar la carpeta vacía en el origen

        Write-Host "Extracción y movimiento de '$sourceARFileName' a '$finalDestinationFolder' completado."
    } else {
        Write-Error "Error: No se encontró la carpeta extraída en '$extractedFolderInSource'. ¿ar0unpack.exe funcionó correctamente?"
        Write-Error "Asegúrate de que el AR de origen no está dañado o que la herramienta tiene permisos."
    }
}

Write-Host "`nProceso de extracción de archivos AR completado."
Write-Host "Los contenidos ahora están en la carpeta 'disk' de la raíz de tu repositorio (ej: '$repoRootFolder\disk\bb3\Sonic\')."
Write-Host "¡Ahora puedes mover manualmente los archivos que necesites de ahí a tu carpeta 'work' para trabajar con ellos!"