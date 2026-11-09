# Script: create_append_ar.ps1
# Crea los archivos append (+Nombre.ar.00) a partir de los archivos en la carpeta 'work',
# moviéndolos a la ubicación especificada en el archivo de configuración.

# --- Configuración ---
$modRootFolder = "C:\Users\carlo\Documents\repositorios\time-eater-ultimate\SG_Time_Eater_Ultimate"
$artoolsPath = "D:\modding\sonic_generation\Artools"
$ar0packExe = Join-Path $artoolsPath "ar0pack.exe"

# Archivo de texto que lista los archivos a incluir en los append archives
$appendListFile = Join-Path (Split-Path $MyInvocation.MyCommand.Definition -Parent) "append_archives_to_create.txt"

# Carpeta base de salida para los append archives generados (la carpeta 'disk' dentro de tu mod)
$modDiskOutputFolder = Join-Path $modRootFolder "disk"

# --- Lógica del Script ---

if (-not (Test-Path $ar0packExe)) {
    Write-Error "Error: ar0pack.exe no encontrado en '$ar0packExe'. Ajusta la ruta."
    exit 1
}
if (-not (Test-Path $appendListFile)) {
    Write-Error "Error: El archivo '$appendListFile' no fue encontrado. Créalo con la lista de archivos para los append archives."
    exit 1
}

Write-Host "Iniciando la creación de append archives a partir de la carpeta 'work'..."

# Un hash table para organizar los archivos por el nombre y la ruta de destino del append archive.
$appendFilesGrouped = @{}

# Leer el archivo de lista de append archives
Get-Content $appendListFile | ForEach-Object {
    $line = $_.Trim()
    if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith("#")) {
        return
    }

    $parts = $line -split '\|'
    if ($parts.Length -ne 4) { # Ahora esperamos 4 partes en lugar de 5
        Write-Warning "Formato de línea inválido en '$appendListFile': '$line'. Se esperaban 4 partes (Nombre|Destino|Interna|WorkPath). Saltando."
        return
    }

    $appendBaseName = $parts[0]           # Ej: Sonic
    $relativePathToDisk = $parts[1]       # Ej: bb3/
    $internalSubfolder = $parts[2]        # Ej: sonic
    $relativePathInWork = $parts[3]       # Ej: sonic\chr_sonic_body01_dif_HD.dds

    # Crear una clave única para agrupar archivos que irán al mismo append archive final (que siempre será .ar.00)
    $groupKey = "$appendBaseName`_$relativePathToDisk"

    if (-not $appendFilesGrouped.ContainsKey($groupKey)) {
        $appendFilesGrouped[$groupKey] = @{
            BaseName = $appendBaseName
            RelativeDestPath = $relativePathToDisk
            Files = @()
        }
    }
    $appendFilesGrouped[$groupKey].Files += @{
        InternalSubfolder = $internalSubfolder
        RelativePathInWork = $relativePathInWork
    }
}

# Procesar cada grupo de append archives
foreach ($groupKey in $appendFilesGrouped.Keys) {
    $groupInfo = $appendFilesGrouped[$groupKey]

    $appendBaseName = $groupInfo.BaseName
    $relativePathToDisk = $groupInfo.RelativeDestPath
    $filesToProcess = $groupInfo.Files

    Write-Host "`nProcesando append archive: +$appendBaseName.ar.00 para '$relativePathToDisk'..."

    # Rutas para el append archive final deseado (+Nombre.ar.00, siempre .00)
    $outputAppendARPath = Join-Path $modDiskOutputFolder "$relativePathToDisk`+$appendBaseName.ar.00"
    $outputAppendARLPath = $outputAppendARPath -replace '\.ar\.00$', '.arl'

    # Carpeta temporal para empaquetar
    $tempPackDirName = "$appendBaseName`_pack_temp" # Nombre único para cada grupo
    $tempPackDirPath = Join-Path $modRootFolder $tempPackDirName

    # 1. Limpiar previos
    Write-Host "  - Limpiando carpeta temporal y archivos previos..."
    Remove-Item -Path $tempPackDirPath -Recurse -ErrorAction SilentlyContinue
    Remove-Item -Path $outputAppendARPath -ErrorAction SilentlyContinue
    Remove-Item -Path $outputAppendARLPath -ErrorAction SilentlyContinue

    # 2. Copiar archivos desde 'work' a la carpeta temporal con su estructura interna
    Write-Host "  - Copiando archivos de 'work' a la carpeta temporal '$tempPackDirPath'..."
    foreach ($fileInfo in $filesToProcess) {
        $sourceFilePath = Join-Path $modRootFolder "work\$($fileInfo.RelativePathInWork)"
        # La ruta de destino en la temporal incluye la 'SubcarpetaInternaEnElAppend'
        $destinationFilePath = Join-Path $tempPackDirPath "$($fileInfo.InternalSubfolder)\$((Split-Path $fileInfo.RelativePathInWork -Leaf))"

        if (Test-Path $sourceFilePath) {
            # Asegurarse de que la carpeta de destino exista
            $destDir = Split-Path $destinationFilePath -Parent
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            Copy-Item -Path $sourceFilePath -Destination $destinationFilePath -Force
            Write-Host "    - Copiado '$($fileInfo.RelativePathInWork)' a '$destinationFilePath'"
        } else {
            Write-Warning "    - Archivo no encontrado en work: '$($fileInfo.RelativePathInWork)'. Saltando."
        }
    }

    # 3. Empaquetar la carpeta temporal usando ar0pack.exe
    if ((Test-Path $tempPackDirPath) -and ((Get-ChildItem -Path $tempPackDirPath).Count -gt 0)) {
        Write-Host "  - Verificando contenido de la carpeta temporal ANTES de empaquetar ($tempPackDirPath):"
        Get-ChildItem -Path $tempPackDirPath -Recurse | Select-Object FullName
        
        Write-Host "  - Empaquetando la carpeta temporal con ar0pack.exe..."
        
        # Definimos las rutas de los archivos de log
        $ar0packOutputLog = Join-Path $PSScriptRoot "ar0pack_output.log"
        $ar0packErrorsLog = Join-Path $PSScriptRoot "ar0pack_errors.log"

        # Limpiar logs anteriores
        Remove-Item $ar0packOutputLog -ErrorAction SilentlyContinue
        Remove-Item $ar0packErrorsLog -ErrorAction SilentlyContinue

        Write-Host "  - Ejecutando ar0pack.exe. El directorio de trabajo serÃ¡: '$tempPackDirPath'"
        
        # Argumentos para ar0pack.exe: la subcarpeta interna a empaquetar y el nombre de salida deseado.
        # Asumimos que $filesToProcess tiene al menos un elemento
        $ar0packInputFolder = "$($filesToProcess[0].InternalSubfolder)" # Esto será "sonic"
        $ar0packOutputFilenameDesired = "+$appendBaseName.ar.00" # Esto será "+Sonic.ar.00"

        # Construye el comando CMD completo como una ÚNICA CADENA para cmd.exe /C
        # cd /d cambia el directorio. & encadena comandos.
        # Pasamos la carpeta a empaquetar y el nombre deseado para el archivo de salida a ar0pack.exe
        $cmdCommandString = "cd /d `"$tempPackDirPath`" & `"$ar0packExe`" `"$ar0packInputFolder`" `"$ar0packOutputFilenameDesired`" > `"$ar0packOutputLog`" 2> `"$ar0packErrorsLog`""
        $cmdArgs = "/C `"$cmdCommandString`""
        
        Write-Host "  - Comando CMD completo a ejecutar: cmd.exe $cmdArgs"

        # Ahora usamos Start-Process con cmd.exe como el FilePath
        # Usamos -NoNewWindow y -Wait para un comportamiento controlado
        $process = Start-Process -FilePath "cmd.exe" -ArgumentList $cmdArgs -NoNewWindow -Wait -PassThru
        $ar0packActualExitCode = $process.ExitCode # Esto debería dar el exit code de cmd.exe

        Write-Host "  - ar0pack.exe ejecutado (vÃa cmd.exe). Revisando logs para salida."
        Write-Host "    CÃ³digo de salida de CMD.exe (que ejecutÃ³ ar0pack.exe): $($ar0packActualExitCode)"

        # --- Corrección de los errores de Test-Path aquí (la sintaxis corregida) ---
        if ((Test-Path $ar0packOutputLog) -and ((Get-Item $ar0packOutputLog).Length -gt 0)) {
            Write-Host "  - Contenido de ar0pack_output.log:"
            Get-Content $ar0packOutputLog
        } else {
            Write-Host "  - El archivo ar0pack_output.log está vacío o no se creó."
        }
        
        if ((Test-Path $ar0packErrorsLog) -and ((Get-Item $ar0packErrorsLog).Length -gt 0)) {
            Write-Host "  - Contenido de ar0pack_errors.log:"
            Get-Content $ar0packErrorsLog
        } else {
            Write-Host "  - El archivo ar0pack_errors.log está vacío o no se creó."
        }
        # --- FIN DE LAS CORRECCIONES DE Test-Path ---

        # ESTE ES EL CAMBIO CLAVE FINAL:
        # Los archivos generados por ar0pack.exe (cuando se le pasa una carpeta) probablemente
        # se llamarán con el nombre de la subcarpeta que empaquetó (ej. 'sonic.ar.00').
        # Si el usuario quiere un nombre diferente (ej. '+Sonic.ar.00'), necesitamos renombrarlo.
        $actualGeneratedARName = "$($filesToProcess[0].InternalSubfolder).ar.00"
        $actualGeneratedARLName = "$($filesToProcess[0].InternalSubfolder).arl"

        $generatedARInTemp = Join-Path $tempPackDirPath $actualGeneratedARName
        $generatedARLInTemp = Join-Path $tempPackDirPath $actualGeneratedARLName

        # 4. Mover y RENOMBRAR los archivos generados a la ubicación final
        if (Test-Path $generatedARInTemp) {
            # Asegurarse de que la carpeta de destino exista (ej. disk/bb3/)
            $destinationFolderForAR = Split-Path $outputAppendARPath -Parent
            New-Item -ItemType Directory -Path $destinationFolderForAR -Force | Out-Null

            Write-Host "  - Archivo .ar generado encontrado: '$generatedARInTemp'."
            Write-Host "  - Renombrando a: '$outputAppendARPath'."

            # Renombrar el .ar.00 generado temporalmente al nombre final deseado
            Rename-Item -Path $generatedARInTemp -NewName ($outputAppendARPath | Split-Path -Leaf) -Force -ErrorAction Stop

            # Renombrar el .arl generado temporalmente al nombre final deseado
            Rename-Item -Path $generatedARLInTemp -NewName ($outputAppendARLPath | Split-Path -Leaf) -Force -ErrorAction Stop

            # Mover los archivos ya renombrados a su destino final
            Move-Item -Path (Join-Path $tempPackDirPath ($outputAppendARPath | Split-Path -Leaf)) -Destination $outputAppendARPath -Force -ErrorAction Stop
            Move-Item -Path (Join-Path $tempPackDirPath ($outputAppendARLPath | Split-Path -Leaf)) -Destination $outputAppendARLPath -Force -ErrorAction Stop

            Write-Host "  - Append archive '$outputAppendARPath' generado y movido."
        } else {
            Write-Error "Error: No se encontró el archivo .ar generado por ar0pack.exe: '$generatedARInTemp'. Verifica si la carpeta temporal tenía contenido y si ar0pack.exe funcionó."
        }
    } else {
        Write-Warning "La carpeta temporal '$tempPackDirPath' está vacía o no existe. No se creará append archive para '$appendBaseName'."
    }

    # 5. Limpiar carpeta temporal
    Write-Host "  - Limpiando carpeta temporal '$tempPackDirPath'..."
    Remove-Item -Path $tempPackDirPath -Recurse -ErrorAction SilentlyContinue
}

Write-Host "`nTodos los append archives procesados."
Write-Host "¡IMPORTANTE! Ahora ejecuta el script 'smart_generate_mod_files_txt.ps1' para actualizar mod_files.txt."