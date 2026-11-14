# Copia el mod construido (mod\ del repositorio) a la carpeta de mods del juego que usa Hedge Mod Manager,
# para probar ajustes (por ejemplo GIRO_CAMARA_PLANEO) sin publicar una release.
# Uso: scripts\probar_en_juego.ps1 [-Juego "<carpeta de Sonic Generations>"]
param(
    [string]$Juego = "D:\SteamLibrary\steamapps\common\Sonic Generations"
)
$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $PSScriptRoot
$origen = Join-Path $raiz "mod"
$destino = Join-Path $Juego "mods\TimeEaterUltimate"

if (-not (Test-Path -LiteralPath (Join-Path $Juego "SonicGenerations.exe"))) {
    throw "No se encontró SonicGenerations.exe en '$Juego'. Indica la carpeta del juego con -Juego."
}
if (-not (Test-Path -LiteralPath (Join-Path $destino "mod.ini"))) {
    throw "El mod no está instalado en '$destino'. Instálalo primero desde Hedge Mod Manager."
}

$n = 0
Get-ChildItem -LiteralPath $origen -Recurse -File | ForEach-Object {
    $rel = $_.FullName.Substring($origen.Length).TrimStart('\')
    $dst = Join-Path $destino $rel
    $dir = Split-Path -Parent $dst
    if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
    if (-not (Test-Path -LiteralPath $dst) -or (Get-FileHash -LiteralPath $dst).Hash -ne (Get-FileHash -LiteralPath $_.FullName).Hash) {
        Copy-Item -LiteralPath $_.FullName -Destination $dst -Force
        Write-Host "  copiado: $rel"
        $n++
    }
}
Write-Host "Listo: $n archivo(s) actualizados en $destino"
Write-Host "Inicia el juego desde Hedge Mod Manager. (Una actualización de HMM volverá a dejar la versión publicada.)"
