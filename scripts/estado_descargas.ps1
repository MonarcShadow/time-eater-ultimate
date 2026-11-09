# Muestra el estado de las descargas lanzadas con scripts\descargar.ps1 (lee descargas\.logs\*.log)
param([string]$Carpeta)
if (-not $Carpeta) { $Carpeta = Join-Path (Split-Path $MyInvocation.MyCommand.Path -Parent | Split-Path -Parent) "descargas" }
$logs = Get-ChildItem (Join-Path $Carpeta ".logs") -Filter *.log -ErrorAction SilentlyContinue
if (-not $logs) { Write-Host "No hay descargas registradas en $Carpeta"; return }
$activas = @(Get-CimInstance Win32_Process -Filter "Name='aria2c.exe'" | ForEach-Object { $_.CommandLine })
foreach ($l in $logs | Sort-Object LastWriteTime) {
    $nombre = $l.BaseName
    $texto = Get-Content $l.FullName -Raw -ErrorAction SilentlyContinue
    $enCurso = [bool]($activas | Where-Object { $_ -like "*$nombre*" -or $_ -like "*$($l.FullName)*" })
    $prog = [regex]::Matches("$texto", '\[#\w+ ([^\]]+)\]') | Select-Object -Last 1
    if ($texto -match '(?m)^\w+\|OK\s*\|[^|]*\|(.+)$') { $estado = "TERMINADA -> $($Matches[1].Trim())" }
    elseif ($texto -match '(?m)^\w+\|(ERR|RM)\s*\|') { $estado = "ERROR (ver $($l.FullName))" }
    elseif ($prog) { $estado = $prog.Groups[1].Value + $(if ($enCurso) { "" } else { "  [detenida: relanza descargar.ps1 con la misma URL para reanudar]" }) }
    else { $estado = if ($enCurso) { "iniciando..." } else { "sin datos" } }
    "{0,-50} {1}" -f $nombre, $estado
}
