# descargar_herramientas.ps1
# Descarga la toolchain de modding de Sonic Generations (2011) desde sus repos oficiales en GitHub.
# Documentación: bóveda Obsidian "D:\bobedas\mod sonic generation" -> wiki/herramientas/toolchain-sonic-generations.md
#
# Uso:  powershell -ExecutionPolicy Bypass -File .\scripts\descargar_herramientas.ps1 [-Destino <carpeta>] [-ConBlenderPortable]
# Blender se usa desde Steam; -ConBlenderPortable descarga además una copia portable 4.5 LTS.

param(
    [string]$Destino = (Join-Path (Split-Path $PSScriptRoot -Parent) "herramientas"),
    [switch]$ConBlenderPortable
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"   # Invoke-WebRequest es mucho más rápido sin barra de progreso
$headers = @{ "User-Agent" = "sg-modding-tools-downloader" }

function Invoke-Descarga([string]$url, [string]$out) {
    # GitHub devuelve a veces 502/504 pasajeros: hasta 3 intentos
    for ($i = 1; $i -le 3; $i++) {
        try { Invoke-WebRequest -Headers $headers -Uri $url -OutFile $out; return }
        catch {
            if ($i -eq 3) { throw }
            Write-Warning "    intento $i falló ($($_.Exception.Message)); reintentando..."
            Start-Sleep -Seconds (5 * $i)
        }
    }
}

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
    # Marca de versión: si ya está descargada esta misma release, no se repite
    $marca = Join-Path $dir ".tag"
    $clave = "$($rel.tag_name) $($rel.published_at)"
    if ((Test-Path $marca) -and ((Get-Content $marca -Raw).Trim() -eq $clave)) {
        Write-Host "[$nombre] $($rel.tag_name) ya está al día" -ForegroundColor DarkGray
        return
    }
    Write-Host "[$nombre] $repo -> $($rel.tag_name) ($($rel.published_at))" -ForegroundColor Cyan
    $assets = $rel.assets | Where-Object { $_.name -match $filtro }
    if (-not $assets) { Write-Warning "[$nombre] La release no tiene assets que coincidan con '$filtro'."; return }
    foreach ($a in $assets) {
        $out = Join-Path $dir $a.name
        Write-Host "    descargando $($a.name)"
        try { Invoke-Descarga $a.browser_download_url $out }
        catch { Write-Warning "[$nombre] Falló la descarga de $($a.name): $($_.Exception.Message)"; return }
        if ($a.name -match '\.zip$') {
            Expand-Archive -Path $out -DestinationPath (Join-Path $dir ([IO.Path]::GetFileNameWithoutExtension($a.name))) -Force
        } elseif ($a.name -match '\.7z$') {
            # El tar de Windows (bsdtar) lee .7z; el de Git Bash no
            & "$env:SystemRoot\System32\tar.exe" -xf $out -C $dir
            if ($LASTEXITCODE -eq 0) { Remove-Item $out } else { Write-Warning "    No se pudo descomprimir $($a.name)"; return }
        }
    }
    Set-Content -Path $marca -Value $clave
}

New-Item -ItemType Directory -Force -Path $Destino | Out-Null

# 1. SonicGLvl + Hedgehog Converter + Havok Converter + GI Atlas Converter (todo en libgens-sonicglvl, solo nightly)
Save-ReleaseAssets "libgens-sonicglvl" "DarioSamo/libgens-sonicglvl" "nightly"

# 2. HedgeArcPack (dentro de las releases de HedgeLib, pre-release)
Save-ReleaseAssets "HedgeArcPack" "Radfordhound/HedgeLib" $null

# 3. Model Converter (soporta --gens)
Save-ReleaseAssets "ModelConverter" "blueskythlikesclouds/ModelConverter" $null 'x64\.7z$'

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
        Invoke-Descarga $f.download_url (Join-Path $pc $f.name)
    }
} catch { Write-Warning "[PackCpk] No se pudo descargar SkythTools/Common: $($_.Exception.Message)" }

# 7. Ini de tags de colisión para Havok Converter (se copia junto a HavokConverter.exe a mano)
try {
    $gist = Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/gists/8e4896b807d49cd86ff2b643d34c7aa2"
    foreach ($p in $gist.files.PSObject.Properties) {
        $p.Value.content | Set-Content -Encoding utf8 -Path (Join-Path $Destino $p.Value.filename)
        $bin = Join-Path $Destino "libgens-sonicglvl\libgens-sonicglvl\bin"
        if (Test-Path $bin) { Copy-Item (Join-Path $Destino $p.Value.filename) $bin -Force }
        Write-Host "[HavokConverter ini] $($p.Value.filename) copiado junto a HavokConverter.exe" -ForegroundColor Cyan
    }
} catch { Write-Warning "[HavokConverter ini] No se pudo descargar el gist: $($_.Exception.Message)" }

# 7b. Herramientas adicionales (las que usan otros mods de niveles, ver wiki/herramientas/toolchain)
# KwasTools: he_anim_tool convierte .uv-anim/.mat-anim/.cam-anim a XML y de vuelta
Save-ReleaseAssets "KwasTools" "ThisKwasior/KwasTools" $null '\.zip$'
# fcoEditor: textos/subtítulos .fco/.fte
Save-ReleaseAssets "fcoEditor" "brianuuu/fcoEditor" $null '\.(zip|7z|exe)$'
# texconv/texdiag (DirectXTex): convertir PNG <-> DDS (DXT1/DXT5 con mipmaps) para retexturizar
Save-ReleaseAssets "texconv" "microsoft/DirectXTex" $null '^(texconv|texdiag)\.exe$'

function Save-RepoFolder([string]$nombre, [string]$repo, [string]$ruta, [string]$filtro = '.') {
    $dir = Join-Path $Destino $nombre
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    try {
        $items = Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/repos/$repo/contents/$ruta"
        foreach ($f in @($items) | Where-Object { $_.type -eq "file" -and $_.name -match $filtro }) {
            Invoke-Descarga $f.download_url (Join-Path $dir $f.name)
        }
        Write-Host "[$nombre] $repo/$ruta descargado" -ForegroundColor Cyan
    } catch { Write-Warning "[$nombre] No se pudo descargar $repo/$ruta : $($_.Exception.Message)" }
}
# SonicLightTools: leer/editar color y posición de archivos .light (no tiene releases; binarios en /bin)
Save-RepoFolder "SonicLightTools" "SWS90/SonicLightTools" "bin" '\.(exe|config)$'
# Exportador de splines para Blender (GPL-3.0, zatsick160). El addon time_eater_tools lo carga desde aquí.
Save-RepoFolder "blender-scripts" "zatsick160/SonicGenerationsBlender" "BlenderToXML.py"
Save-RepoFolder "blender-scripts" "zatsick160/SonicGenerationsBlender" "LICENSE"

# 8. Blender portable (4.5 LTS; HEIO requiere 4.2+). Se descomprime en herramientas\Blender
if ($ConBlenderPortable) {
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
