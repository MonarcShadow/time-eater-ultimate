# publicar_release.ps1
# Publica una versión del mod como GitHub Release, lista para que Hedge Mod Manager la detecte como actualización.
#
# Cómo funciona:
#   mod.ini -> UpdateServer = https://github.com/<repo>/releases/latest/download/
#   HMM 7 pide <UpdateServer>/HedgeModManager.xml   (una URL absoluta por archivo)
#   HMM 8 pide <UpdateServer>/update_manifest.json  (una URL absoluta por archivo + sha256 + tamaño)
#   Ambos manifiestos se suben como assets de la release; cada archivo del mod se sube como asset "plano"
#   (los assets de GitHub no admiten carpetas) y el manifiesto indica en qué ruta va dentro del mod.
#   También se sube un .zip con el mod completo para instalarlo por primera vez (arrastrar a HMM).
#
# Uso:
#   .\scripts\publicar_release.ps1 -Version 0.1.1 -Notas "Qué cambió"
#   .\scripts\publicar_release.ps1 -Version 0.1.1 -Notas "..." -SoloPreparar   # arma build\ sin publicar
#
# Requisitos: gh (GitHub CLI) con sesión iniciada; cambios commiteados y pusheados a main.

param(
    [Parameter(Mandatory = $true)][string]$Version,
    [string]$Notas = "",
    [string]$Repo = "MonarcShadow/time-eater-ultimate",
    [switch]$SoloPreparar,
    [switch]$Forzar
)

$ErrorActionPreference = "Stop"
$raiz     = Split-Path $PSScriptRoot -Parent
$modDir   = Join-Path $raiz "mod"
$tag      = "v$Version"
$buildDir = Join-Path $raiz "build\$tag"
$assetDir = Join-Path $buildDir "assets"
$zipName  = "TimeEaterUltimate-$Version.zip"
$baseUrl  = "https://github.com/$Repo/releases/download/$tag"
$utf8     = New-Object System.Text.UTF8Encoding($false)

function Write-Utf8([string]$path, [string]$text) { [IO.File]::WriteAllText($path, $text, $utf8) }

# --- 0. Comprobaciones ---------------------------------------------------------
if (-not (Test-Path (Join-Path $modDir "mod.ini"))) { throw "No existe mod\mod.ini" }
if ($Version -notmatch '^\d+\.\d+\.\d+$') { throw "La versión debe ser X.Y.Z (ej. 0.1.1)" }

if (-not $SoloPreparar) {
    gh release view $tag -R $Repo *> $null
    if ($LASTEXITCODE -eq 0) { throw "La release $tag ya existe en GitHub." }
}

if (-not $SoloPreparar -and -not $Forzar) {
    Push-Location $raiz
    $sucio = git status --porcelain
    Pop-Location
    if ($sucio) { throw "Hay cambios sin commitear. Haz commit primero (o usa -Forzar):`n$($sucio -join "`n")" }
}

# --- 1. Escribir la versión en mod.ini (y commit + push de ese cambio) ---------
$iniPath = Join-Path $modDir "mod.ini"
$ini = [IO.File]::ReadAllText($iniPath)
$ini = [regex]::Replace($ini, '(?m)^Version=".*"', "Version=`"$Version`"")
$ini = [regex]::Replace($ini, '(?m)^Date=".*"', "Date=`"$(Get-Date -Format yyyy-MM-dd)`"")
Write-Utf8 $iniPath $ini

if (-not $SoloPreparar) {
    Push-Location $raiz
    git add mod/mod.ini
    git diff --cached --quiet
    if ($LASTEXITCODE -ne 0) { git commit -m "Versión $Version" --quiet }
    git push origin HEAD:main --quiet
    $pushOk = $LASTEXITCODE
    Pop-Location
    if ($pushOk -ne 0) { throw "git push falló" }
}

# --- 2. Preparar build\vX.Y.Z ---------------------------------------------------
if (Test-Path $buildDir) { Remove-Item $buildDir -Recurse -Force }
New-Item -ItemType Directory -Force -Path $assetDir | Out-Null

$archivos = Get-ChildItem $modDir -Recurse -File | Sort-Object FullName
$entradas = New-Object System.Collections.ArrayList
$i = 0
$totalBytes = 0
foreach ($f in $archivos) {
    $i++
    $rel = $f.FullName.Substring($modDir.Length + 1).Replace('\', '/')
    # Nombre de asset plano, único y seguro para GitHub: f001__disk__bb2__x.ar.00
    $seguro = ($rel -replace '/', '__') -replace '[^A-Za-z0-9._-]', '_'
    $asset = "f{0:D3}__{1}" -f $i, $seguro
    Copy-Item $f.FullName (Join-Path $assetDir $asset)
    $sha = (Get-FileHash $f.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $totalBytes += $f.Length
    [void]$entradas.Add([pscustomobject]@{ Path = $rel; Asset = $asset; Url = "$baseUrl/$asset"; Sha = $sha; Size = $f.Length })
}

# Archivos que estaban en la release anterior y ya no existen -> borrar (solo HMM 8 lo soporta)
$borrados = New-Object System.Collections.ArrayList
try {
    $prev = Join-Path $buildDir "prev_manifest.json"
    gh release download -R $Repo --pattern "update_manifest.json" --output $prev 2>$null
    if ($LASTEXITCODE -eq 0 -and (Test-Path $prev)) {
        $pm = Get-Content $prev -Raw | ConvertFrom-Json
        foreach ($pf in $pm.files) {
            if ($pf.size -ge 0 -and -not ($entradas | Where-Object { $_.Path -ieq $pf.path })) { [void]$borrados.Add($pf.path) }
        }
        Remove-Item $prev
    }
} catch { }
$global:LASTEXITCODE = 0   # no tener release previa no es un error

# --- 3. HedgeModManager.xml (HMM 7) --------------------------------------------
$tamano = if ($totalBytes -ge 1MB) { "{0:N2} MB" -f ($totalBytes / 1MB) } else { "{0:N1} KB" -f ($totalBytes / 1KB) }
$notasXml = [Security.SecurityElement]::Escape($(if ($Notas) { $Notas } else { "Versión $Version" }))
$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine('<?xml version="1.0" encoding="utf-8"?>')
[void]$sb.AppendLine('<HedgeModManagerUpdate>')
[void]$sb.AppendLine("  <UpdateInfo version=`"$Version`" downloadSize=`"$tamano`">$notasXml</UpdateInfo>")
[void]$sb.AppendLine('  <UpdateFiles>')
foreach ($e in $entradas) {
    [void]$sb.AppendLine('    <UpdateFile>')
    [void]$sb.AppendLine("      <FilePath>$([Security.SecurityElement]::Escape($e.Path))</FilePath>")
    [void]$sb.AppendLine("      <URL>$($e.Url)</URL>")
    [void]$sb.AppendLine('    </UpdateFile>')
}
[void]$sb.AppendLine('  </UpdateFiles>')
[void]$sb.AppendLine('</HedgeModManagerUpdate>')
Write-Utf8 (Join-Path $assetDir "HedgeModManager.xml") $sb.ToString()

# --- 4. update_manifest.json (HMM 8) -------------------------------------------
$files = New-Object System.Collections.ArrayList
foreach ($e in $entradas) {
    [void]$files.Add([ordered]@{ path = $e.Path; downloadPaths = @($e.Url); sha256 = $e.Sha; size = $e.Size })
}
foreach ($b in $borrados) { [void]$files.Add([ordered]@{ path = $b; size = -1 }) }
$changelogAsset = ($entradas | Where-Object { $_.Path -eq "changelog.md" } | Select-Object -First 1)
$manifest = [ordered]@{
    manifestVersion = 1
    modVersion      = $Version
    basePath        = "$baseUrl/"
    changelogPath   = $(if ($changelogAsset) { $changelogAsset.Url } else { $null })
    files           = $files
}
Write-Utf8 (Join-Path $assetDir "update_manifest.json") ($manifest | ConvertTo-Json -Depth 6)

# --- 5. Zip para instalación inicial -------------------------------------------
$zipTmp = Join-Path $buildDir "zip\TimeEaterUltimate"
New-Item -ItemType Directory -Force -Path $zipTmp | Out-Null
Copy-Item (Join-Path $modDir "*") $zipTmp -Recurse
Compress-Archive -Path $zipTmp -DestinationPath (Join-Path $assetDir $zipName) -Force
Remove-Item (Join-Path $buildDir "zip") -Recurse -Force

Write-Host "Preparado $tag en $assetDir ($($entradas.Count) archivos del mod, $tamano; $($borrados.Count) a borrar)" -ForegroundColor Green
if ($SoloPreparar) { return }

# --- 6. Publicar ---------------------------------------------------------------
$notasFinal = if ($Notas) { $Notas } else { "Versión $Version" }
$notasFinal += "`n`n**Instalar:** descarga ``$zipName`` y arrástralo a Hedge Mod Manager. Las siguientes versiones se instalan desde HMM con *Check for updates*."
$lista = Get-ChildItem $assetDir -File | ForEach-Object { $_.FullName }
gh release create $tag @lista -R $Repo --target main --title "Time Eater Ultimate $Version" --notes $notasFinal --latest
if ($LASTEXITCODE -ne 0) { throw "gh release create falló" }
Write-Host "Publicada: https://github.com/$Repo/releases/tag/$tag" -ForegroundColor Green
