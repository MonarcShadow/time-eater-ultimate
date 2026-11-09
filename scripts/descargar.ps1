# Descarga un archivo grande con aria2 (herramientas\aria2) a la carpeta descargas\ del repo.
# El proceso queda independiente de la terminal (se crea vía WMI), así que sigue aunque se cierre Claude Code.
# Reanuda descargas cortadas (-c). Resuelve enlaces de Google Drive (aviso de "no se pudo escanear").
#
# Uso:  powershell -ExecutionPolicy Bypass -File .\scripts\descargar.ps1 -Url <url> [-Nombre archivo.ext] [-Carpeta <dir>]
# Estado: .\scripts\estado_descargas.ps1
param(
    [Parameter(Mandatory)][string]$Url,
    [string]$Nombre,
    [string]$Carpeta
)
$ErrorActionPreference = "Stop"
$raiz = Split-Path $PSScriptRoot -Parent
if (-not $Carpeta) { $Carpeta = Join-Path $raiz "descargas" }
$aria = Get-ChildItem (Join-Path $raiz "herramientas\aria2") -Recurse -Filter aria2c.exe | Select-Object -First 1
if (-not $aria) { throw "No está aria2c.exe; ejecuta scripts\descargar_herramientas.ps1" }

# Google Drive: convertir el enlace de vista en el enlace directo con confirmación
if ($Url -match 'drive\.google\.com/(?:file/d/|.*[?&]id=)([\w-]+)') {
    $id = $Matches[1]
    $pag = Invoke-WebRequest -UseBasicParsing "https://drive.google.com/uc?export=download&id=$id"
    $accion = [regex]::Match($pag.Content, 'action="([^"]+)"').Groups[1].Value
    if ($accion) {
        $campos = [regex]::Matches($pag.Content, '<input type="hidden" name="([^"]+)" value="([^"]*)"') |
            ForEach-Object { "$($_.Groups[1].Value)=$([uri]::EscapeDataString($_.Groups[2].Value))" }
        $Url = $accion + "?" + ($campos -join "&")
        if (-not $Nombre) { $Nombre = [regex]::Match($pag.Content, '<a href="[^"]*">([^<]+)</a> \(').Groups[1].Value }
    } else {
        $Url = "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t"
    }
}

New-Item -ItemType Directory -Force -Path $Carpeta, (Join-Path $Carpeta ".logs") | Out-Null
$etiqueta = if ($Nombre) { $Nombre } else { [IO.Path]::GetFileName(([uri]$Url).AbsolutePath) }
if (-not $etiqueta) { $etiqueta = "descarga-" + (Get-Date -Format yyyyMMdd-HHmmss) }
$log = Join-Path $Carpeta ".logs\$etiqueta.log"

$args_ = @("-c", "-x8", "-s8", "-k1M", "--max-tries=0", "--retry-wait=10", "--file-allocation=prealloc", "--enable-color=false",
           "--summary-interval=5", "--console-log-level=warn", "--show-console-readout=false",
           "--auto-file-renaming=false", "--allow-overwrite=false", "--dir=`"$Carpeta`"")
if ($Nombre) { $args_ += "--out=`"$Nombre`"" }
$args_ += "`"$Url`""
$cmd = "cmd.exe /c `"`"$($aria.FullName)`" $($args_ -join ' ') > `"$log`" 2>&1`""

# WMI crea el proceso fuera del árbol de la terminal: no muere al cerrarla
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd; CurrentDirectory = $Carpeta }
if ($r.ReturnValue -ne 0) { throw "No se pudo lanzar aria2 (código $($r.ReturnValue))" }
Write-Host "Descargando '$etiqueta' en $Carpeta (PID $($r.ProcessId))"
Write-Host "Log: $log"
