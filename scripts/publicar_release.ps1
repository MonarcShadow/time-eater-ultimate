# publicar_release.ps1
# Publica una versión del mod para que Hedge Mod Manager la detecte como actualización.
#
# Cómo funciona (verificado en el código de HMM 7.15 y HMM 8):
#   mod.ini -> UpdateServer = https://raw.githubusercontent.com/<repo>/hmm-update/
#   HMM 7.15 pide <UpdateServer>mod_version.ini y después <UpdateServer>mod_files.txt,
#            y descarga cada archivo como <UpdateServer><ruta relativa> (necesita carpetas reales).
#   HMM 8    pide <UpdateServer>update_manifest.json (y si falla, el mismo par mod_version.ini/mod_files.txt).
#   Por eso el contenido actualizable vive en la rama huérfana "hmm-update" (se reescribe en cada versión,
#   sin historial), servida por raw.githubusercontent.com. Además se crea una GitHub Release con el .zip
#   para la primera instalación y con los archivos de la raíz del mod como assets sueltos (compatibilidad
#   con instalaciones cuyo UpdateServer todavía apunte a releases/latest/download/).
#
# Uso:
#   .\scripts\publicar_release.ps1 -Version 0.1.2 -Notas "Qué cambió"
#   .\scripts\publicar_release.ps1 -Version 0.1.2 -Notas "..." -SoloPreparar   # arma build\ sin publicar
#
# Requisitos: gh (GitHub CLI) con sesión iniciada; cambios commiteados.

param(
    [Parameter(Mandatory = $true)][string]$Version,
    [string]$Notas = "",
    [string]$Repo = "MonarcShadow/time-eater-ultimate",
    [string]$RamaUpdate = "hmm-update",
    [switch]$SoloPreparar,
    [switch]$Forzar
)

$ErrorActionPreference = "Stop"
$raiz       = Split-Path $PSScriptRoot -Parent
$modDir     = Join-Path $raiz "mod"
$tag        = "v$Version"
$buildDir   = Join-Path $raiz "build\$tag"
$updDir     = Join-Path $buildDir "hmm-update"
$assetDir   = Join-Path $buildDir "release-assets"
$zipName    = "TimeEaterUltimate-$Version.zip"
$serverUrl  = "https://raw.githubusercontent.com/$Repo/$RamaUpdate/"
$remoteUrl  = "https://github.com/$Repo.git"
$utf8       = New-Object System.Text.UTF8Encoding($false)
$notasTexto = if ($Notas) { $Notas } else { "Versión $Version" }

function Write-Utf8([string]$path, [string]$text) { [IO.File]::WriteAllText($path, $text, $utf8) }

# --- 0. Comprobaciones ---------------------------------------------------------
if (-not (Test-Path (Join-Path $modDir "mod.ini"))) { throw "No existe mod\mod.ini" }
if ($Version -notmatch '^\d+\.\d+\.\d+$') { throw "La versión debe ser X.Y.Z (ej. 0.1.2)" }

$tags = @()
if (-not $SoloPreparar) {
    $tags = gh release list -R $Repo --limit 200 --json tagName --jq ".[].tagName"
    if ($tags -contains $tag) { throw "La release $tag ya existe en GitHub." }
    if (-not $Forzar) {
        Push-Location $raiz
        $sucio = git status --porcelain
        Pop-Location
        if ($sucio) { throw "Hay cambios sin commitear. Haz commit primero (o usa -Forzar):`n$($sucio -join "`n")" }
    }
}

# --- 1. Versión y UpdateServer en mod.ini (y commit + push) --------------------
$iniPath = Join-Path $modDir "mod.ini"
$ini = [IO.File]::ReadAllText($iniPath)
$ini = [regex]::Replace($ini, '(?m)^Version=".*"', "Version=`"$Version`"")
$ini = [regex]::Replace($ini, '(?m)^Date=".*"', "Date=`"$(Get-Date -Format yyyy-MM-dd)`"")
$ini = [regex]::Replace($ini, '(?m)^UpdateServer=".*"', "UpdateServer=`"$serverUrl`"")
Write-Utf8 $iniPath $ini

if (-not $SoloPreparar) {
    Push-Location $raiz
    git add mod/mod.ini
    git diff --cached --quiet
    if ($LASTEXITCODE -ne 0) { git commit -m "Versión $Version" --quiet }
    git push origin HEAD:main --quiet
    $pushOk = $LASTEXITCODE
    Pop-Location
    if ($pushOk -ne 0) { throw "git push de main falló" }
}

# --- 2. Contenido de la rama hmm-update ---------------------------------------
if (Test-Path $buildDir) { Remove-Item $buildDir -Recurse -Force }
New-Item -ItemType Directory -Force -Path $updDir, $assetDir | Out-Null
Copy-Item (Join-Path $modDir "*") $updDir -Recurse

$archivos = Get-ChildItem $modDir -Recurse -File | Sort-Object FullName
$entradas = foreach ($f in $archivos) {
    [pscustomobject]@{
        Path = $f.FullName.Substring($modDir.Length + 1).Replace('\', '/')
        Sha  = (Get-FileHash $f.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        Size = $f.Length
        Full = $f.FullName
    }
}
$totalBytes = ($entradas | Measure-Object Size -Sum).Sum

# Archivos de la versión anterior que ya no existen -> borrar
$borrados = @()
try {
    $prev = Invoke-RestMethod -Uri "$($serverUrl)update_manifest.json" -Headers @{ "Cache-Control" = "no-cache" }
    foreach ($pf in $prev.files) {
        if ($pf.size -ge 0 -and -not ($entradas | Where-Object { $_.Path -ieq $pf.path })) { $borrados += $pf.path }
    }
} catch { }   # primera publicación en la rama: no hay manifiesto previo

# mod_version.ini (HMM 7.15 / GMI)
$tamano = if ($totalBytes -ge 1MB) { "{0:N2} MB" -f ($totalBytes / 1MB) } else { "{0:N1} KB" -f ($totalBytes / 1KB) }
$tieneChangelog = [bool]($entradas | Where-Object { $_.Path -eq "changelog.md" })
$verIni = "[Main]`nVersionString=`"$Version`"`nDownloadSizeString=`"$tamano`"`n"
if ($tieneChangelog) { $verIni += "Markdown=`"changelog.md`"`n" }
$verIni += "`n[Changelog]`nStringCount=1`nString0=`"$($notasTexto -replace '"', "'")`"`n"
Write-Utf8 (Join-Path $updDir "mod_version.ini") $verIni

# mod_files.txt (primero borrados, luego archivos; una línea "comando ruta")
$lineas = @()
$lineas += $borrados | ForEach-Object { "delete $_" }
$lineas += $entradas | ForEach-Object { "add $($_.Path)" }
Write-Utf8 (Join-Path $updDir "mod_files.txt") ($lineas -join "`n")

# update_manifest.json (HMM 8; rutas relativas a basePath = rama hmm-update)
$files = New-Object System.Collections.ArrayList
foreach ($e in $entradas) { [void]$files.Add([ordered]@{ path = $e.Path; sha256 = $e.Sha; size = $e.Size }) }
foreach ($b in $borrados) { [void]$files.Add([ordered]@{ path = $b; size = -1 }) }
$manifest = [ordered]@{
    manifestVersion = 1
    modVersion      = $Version
    basePath        = $serverUrl
    changelogPath   = $(if ($tieneChangelog) { "$($serverUrl)changelog.md" } else { $null })
    files           = $files
}
Write-Utf8 (Join-Path $updDir "update_manifest.json") ($manifest | ConvertTo-Json -Depth 6)

# --- 3. Assets de la release ---------------------------------------------------
$zipTmp = Join-Path $buildDir "zip\TimeEaterUltimate"
New-Item -ItemType Directory -Force -Path $zipTmp | Out-Null
Copy-Item (Join-Path $modDir "*") $zipTmp -Recurse
Compress-Archive -Path $zipTmp -DestinationPath (Join-Path $assetDir $zipName) -Force
Remove-Item (Join-Path $buildDir "zip") -Recurse -Force
# Compatibilidad con UpdateServer = releases/latest/download/ (solo sirve para archivos de la raíz del mod)
foreach ($n in "mod_version.ini", "mod_files.txt", "update_manifest.json") { Copy-Item (Join-Path $updDir $n) $assetDir }
$anidados = @($entradas | Where-Object { $_.Path -like "*/*" })
foreach ($e in $entradas | Where-Object { $_.Path -notlike "*/*" }) { Copy-Item $e.Full (Join-Path $assetDir $e.Path) }

Write-Host "Preparado $tag en $buildDir ($($entradas.Count) archivos, $tamano; $($borrados.Count) a borrar)" -ForegroundColor Green
if ($SoloPreparar) { return }

# --- 4. Publicar la rama hmm-update (huérfana, se sobrescribe) ----------------
Push-Location $updDir
git init --quiet
git config core.autocrlf false   # nunca convertir saltos de línea (hay archivos binarios .ar/.pfd)
git checkout --quiet --orphan $RamaUpdate
git add -A
git -c user.name="$(git -C $raiz config user.name)" -c user.email="$(git -C $raiz config user.email)" commit --quiet -m "Contenido de actualización HMM $Version"
git push --force --quiet $remoteUrl "HEAD:refs/heads/$RamaUpdate"
$pushOk = $LASTEXITCODE
Pop-Location
if ($pushOk -ne 0) { throw "git push de la rama $RamaUpdate falló" }

# --- 5. GitHub Release -------------------------------------------------------------
$notasFinal = $notasTexto + "`n`n**Instalar:** descarga ``$zipName`` y arrástralo a Hedge Mod Manager. Las siguientes versiones se instalan desde HMM buscando actualizaciones."
$lista = Get-ChildItem $assetDir -File | ForEach-Object { $_.FullName }
gh release create $tag @lista -R $Repo --target main --title "Time Eater Ultimate $Version" --notes $notasFinal --latest
if ($LASTEXITCODE -ne 0) { throw "gh release create falló" }
Write-Host "Publicada: https://github.com/$Repo/releases/tag/$tag" -ForegroundColor Green
Write-Host "raw.githubusercontent.com puede tardar ~5 min en servir la nueva versión (caché)." -ForegroundColor Yellow
