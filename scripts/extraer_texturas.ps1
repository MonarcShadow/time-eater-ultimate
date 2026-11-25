# extraer_texturas.ps1 — saca de los archivos originales del juego las texturas que pide niveles\<Nivel>\texturas.json
# y las deja como PNG de 512 px en build\texturas_originales\tex\<nombre>.png (fuera de git: las texturas de Sega solo
# viajan dentro del mod construido). Solo extrae lo que falta. Sin "archivos originales\" no hace nada (el nivel usa
# entonces sus cuadriculados propios). Lo llama construir_nivel.ps1.
# Uso: powershell -ExecutionPolicy Bypass -File scripts\extraer_texturas.ps1 -Nivel grieta_del_tiempo
param([Parameter(Mandatory)][string]$Nivel)
$ErrorActionPreference = "Stop"
$raiz = Split-Path $PSScriptRoot -Parent
$json = Join-Path $raiz "niveles\$Nivel\texturas.json"
if (-not (Test-Path -LiteralPath $json)) { return }
$cfg = Get-Content -LiteralPath $json -Raw -Encoding UTF8 | ConvertFrom-Json
$orig = Join-Path $raiz "archivos originales"
$dest = Join-Path $raiz "build\texturas_originales"
$ext = Join-Path $dest "ext"; $tex = Join-Path $dest "tex"
New-Item -ItemType Directory -Force -Path $ext, $tex | Out-Null
$herr = Join-Path $raiz "herramientas"
$hap = (Get-ChildItem (Join-Path $herr "HedgeArcPack") -Recurse -Filter HedgeArcPack.exe | Select-Object -First 1).FullName
$texconv = Join-Path $herr "texconv\texconv.exe"
$hechas = 0; $faltan = 0
foreach ($m in $cfg.materiales.PSObject.Properties) {
    foreach ($clave in "suelo", "pared") {
        $ref = $m.Value.$clave
        if (-not $ref) { continue }
        $zona, $nombre = $ref.Split("/")
        $png = Join-Path $tex "$nombre.png"
        if (Test-Path -LiteralPath $png) { continue }
        $carpeta = Join-Path $ext $zona
        $dds = Join-Path $carpeta "$nombre.dds"
        if (-not (Test-Path -LiteralPath $dds)) {
            $ar = Join-Path $orig $cfg.archivos.$zona
            if (-not (Test-Path -LiteralPath $ar)) { $faltan++; continue }
            New-Item -ItemType Directory -Force -Path $carpeta | Out-Null
            & $hap -E $ar $carpeta | Out-Null
        }
        if (-not (Test-Path -LiteralPath $dds)) { Write-Host "   TEU_AVISO textura $ref no está en $zona"; $faltan++; continue }
        & $texconv -nologo -y -ft png -f R8G8B8A8_UNORM -m 1 -w 512 -h 512 -o $tex $dds | Out-Null
        $hechas++
    }
}
Write-Host "   texturas originales: $hechas nuevas, $faltan sin original, $((Get-ChildItem $tex -Filter *.png).Count) en total"
