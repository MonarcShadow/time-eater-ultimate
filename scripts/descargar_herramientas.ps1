# descargar_herramientas.ps1
# Descarga la toolchain de modding de Sonic Generations (2011) desde sus repos oficiales en GitHub.
# Documentación: bóveda Obsidian "D:\bobedas\mod sonic generation" -> wiki/herramientas/toolchain-sonic-generations.md
#
# Uso:  powershell -ExecutionPolicy Bypass -File .\scripts\descargar_herramientas.ps1 [-Destino <carpeta>] [-SinBlender]

param(
    [string]$Destino = (Join-Path (Split-Path $PSScriptRoot -Parent) "herramientas"),
    [switch]$SinBlender
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"   # Invoke-WebRequest es mucho más rápido sin barra de progreso
$headers = @{ "User-Agent" = "sg-modding-tools-downloader" }

function Get-Release([string]$repo, [string]$tag) {
    if ($tag) { $url = "https://api.github.com/repos/$repo/releases/tags/$tag" }
    else {
        # /releases/latest ignora pre-releases; tomamos la primera de la lista (incluye nightlies/pre-releases)
        $list = Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/repos/$repo/releases?per_page=5"
        return $list | Select-Object -First 1
    }
    Invoke-RestMethod -Headers $headers -Uri $url
}

function Save-ReleaseAssets([string]$nombre, [string]$repo, [string]$tag, [string]$filtro = '\.(zip|7z|exe)$') {
    $dir = Join-Path $Destino $nombre
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    try {
        $rel = Get-Release $repo $tag
    } catch {
        Write-Warning "[$nombre] No se pudo leer la release de $repo : $($_.Exception.Message)"
        return
    }
    Write-Host "[$nombre] $repo -> $($rel.tag_name) ($($rel.published_at))" -ForegroundColor Cyan
    $assets = $rel.assets | Where-Object { $_.name -match $filtro }
    if (-not $assets) { Write-Warning "[$nombre] La release no tiene assets que coincidan con '$filtro'."; return }
    foreach ($a in $assets) {
        $out = Join-Path $dir $a.name
        Write-Host "    descargando $($a.name)"
        Invoke-WebRequest -Headers $headers -Uri $a.browser_download_url -OutFile $out
        if ($a.name -match '\.zip$') {
            Expand-Archive -Path $out -DestinationPath (Join-Path $dir ([IO.Path]::GetFileNameWithoutExtension($a.name))) -Force
        } elseif ($a.name -match '\.7z$') {
            Write-Warning "    $($a.name) es .7z: descomprímelo a mano con 7-Zip (no está instalado en PATH)."
        }
    }
}

New-Item -ItemType Directory -Force -Path $Destino | Out-Null

# 1. SonicGLvl + Hedgehog Converter + Havok Converter + GI Atlas Converter (todo en libgens-sonicglvl, solo nightly)
Save-ReleaseAssets "libgens-sonicglvl" "DarioSamo/libgens-sonicglvl" "nightly"

# 2. HedgeArcPack (dentro de las releases de HedgeLib, pre-release)
Save-ReleaseAssets "HedgeArcPack" "Radfordhound/HedgeLib" $null

# 3. Model Converter (soporta --gens)
Save-ReleaseAssets "ModelConverter" "blueskythlikesclouds/ModelConverter" $null

# 4. HedgeGI (solo nightly)
Save-ReleaseAssets "HedgeGI" "blueskythlikesclouds/HedgeGI" "nightly"

# 5. SonicAudioTools (opcional, música/sonido .csb/.acb)
Save-ReleaseAssets "SonicAudioTools" "blueskythlikesclouds/SonicAudioTools" $null

# 6. PackCpk: no tiene releases, está como binario en SkythTools/Common (master)
$pc = Join-Path $Destino "SkythTools-Common"
New-Item -ItemType Directory -Force -Path $pc | Out-Null
try {
    $files = Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/repos/blueskythlikesclouds/SkythTools/contents/Common?ref=master"
    Write-Host "[PackCpk] SkythTools/Common ($($files.Count) archivos)" -ForegroundColor Cyan
    foreach ($f in $files | Where-Object { $_.type -eq "file" }) {
        Invoke-WebRequest -Headers $headers -Uri $f.download_url -OutFile (Join-Path $pc $f.name)
    }
} catch { Write-Warning "[PackCpk] No se pudo descargar SkythTools/Common: $($_.Exception.Message)" }

# 7. Ini de tags de colisión para Havok Converter (se copia junto a HavokConverter.exe a mano)
try {
    $gist = Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/gists/8e4896b807d49cd86ff2b643d34c7aa2"
    foreach ($p in $gist.files.PSObject.Properties) {
        $p.Value.content | Set-Content -Encoding utf8 -Path (Join-Path $Destino $p.Value.filename)
        Write-Host "[HavokConverter ini] guardado $($p.Value.filename) -> cópialo junto a HavokConverter.exe" -ForegroundColor Cyan
    }
} catch { Write-Warning "[HavokConverter ini] No se pudo descargar el gist: $($_.Exception.Message)" }

# 8. Blender portable (4.5 LTS; HEIO requiere 4.2+). Se descomprime en herramientas\Blender
if (-not $SinBlender) {
    $blenderVer = "4.5.15"
    $blenderZip = Join-Path $Destino "blender-$blenderVer-windows-x64.zip"
    $blenderDir = Join-Path $Destino "Blender"
    if (Test-Path (Join-Path $blenderDir "blender-$blenderVer-windows-x64\blender.exe")) {
        Write-Host "[Blender] $blenderVer ya está descomprimido" -ForegroundColor Cyan
    } else {
        Write-Host "[Blender] descargando $blenderVer portable (~400 MB)..." -ForegroundColor Cyan
        Invoke-WebRequest -Headers $headers -Uri "https://download.blender.org/release/Blender4.5/blender-$blenderVer-windows-x64.zip" -OutFile $blenderZip
        Expand-Archive -Path $blenderZip -DestinationPath $blenderDir -Force
        Remove-Item $blenderZip
    }
}

# 9. HEIO (addon de Blender para formatos Hedgehog Engine) - se instala desde Blender: Preferencias > Get Extensions > Install from Disk
Save-ReleaseAssets "HEIO" "hedge-dev/HedgehogEngineBlenderIO" $null '\.zip$'

Write-Host ""
Write-Host "Listo. Herramientas en: $Destino" -ForegroundColor Green
