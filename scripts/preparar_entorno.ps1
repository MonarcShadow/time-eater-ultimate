# preparar_entorno.ps1 — deja el entorno de modding completo en un PC recién formateado.
# Lo lanza PREPARAR_ENTORNO.bat (doble clic). Se puede repetir: salta lo que ya está hecho.
#
#  1. Revisa requisitos del sistema (Visual C++, DirectX 9, Blender y Sonic Generations de Steam).
#     Lo que falte fuera de la carpeta del mod solo se instala si respondes S.
#  2. Descarga la toolchain en herramientas\            (descargar_herramientas.ps1)
#  3. Configura Blender aislado en herramientas\blender-config (configurar_blender.ps1)
#  4. Extrae bb, bb2 y bb3 del juego en "archivos originales\"
#  5. (Opcional) Descarga y extrae los mods de referencia (Dark Mode, Unleashed Project 2,5 GB)
#
# Parámetros: -Todo (responde S a todo), -SinReferencias, -SinJuego
param([switch]$Todo, [switch]$SinReferencias, [switch]$SinJuego)

$ErrorActionPreference = "Stop"
$raiz  = Split-Path $PSScriptRoot -Parent
$herr  = Join-Path $raiz "herramientas"
$orig  = Join-Path $raiz "archivos originales"
$refs  = Join-Path $orig "referencias"
$ps    = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$avisos = New-Object System.Collections.Generic.List[string]

function Titulo([string]$t) { Write-Host ""; Write-Host "=== $t ===" -ForegroundColor Yellow }
function Preguntar([string]$p) {
    if ($Todo) { return $true }
    return ((Read-Host "$p (S/N)") -match '^[sSyY]')
}
function Ejecutar-Script([string]$nombre, [string[]]$argumentos = @()) {
    & $ps -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot $nombre) @argumentos
    if ($LASTEXITCODE -ne 0) { throw "$nombre terminó con código $LASTEXITCODE" }
}
function Get-LibreriasSteam {
    $libs = @("C:\Program Files (x86)\Steam")
    $vdf = "C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf"
    if (Test-Path $vdf) {
        $libs += (Select-String -Path $vdf -Pattern '"path"\s+"([^"]+)"').Matches | ForEach-Object { $_.Groups[1].Value -replace '\\\\', '\' }
    }
    $libs | Select-Object -Unique
}
function Find-SteamApp([string]$carpeta, [string]$archivo) {
    foreach ($l in Get-LibreriasSteam) {
        $c = Join-Path $l "steamapps\common\$carpeta"
        if (Test-Path (Join-Path $c $archivo)) { return $c }
    }
    return $null
}

# ---------------------------------------------------------------------------------
Titulo "1. Requisitos del sistema"
$sys32 = "$env:SystemRoot\System32"; $wow = "$env:SystemRoot\SysWOW64"
$requisitos = @(
    @{ Nombre = "Visual C++ 2015-2022 x64"; Ok = (Test-Path "$sys32\vcruntime140_1.dll") -and (Test-Path "$sys32\msvcp140.dll"); Winget = "Microsoft.VCRedist.2015+.x64"; Para = "HedgeArcPack, texconv" },
    @{ Nombre = "Visual C++ 2015-2022 x86"; Ok = (Test-Path "$wow\vcruntime140.dll") -and (Test-Path "$wow\msvcp140.dll"); Winget = "Microsoft.VCRedist.2015+.x86"; Para = "SonicGLvl, Hedgehog/Havok Converter" },
    @{ Nombre = "Visual C++ 2010 x86";      Ok = (Test-Path "$wow\msvcr100.dll") -and (Test-Path "$wow\msvcp100.dll"); Winget = "Microsoft.VCRedist.2010.x86"; Para = "terrain2fbx" },
    @{ Nombre = "DirectX 9 (d3dx9_43)";     Ok = (Test-Path "$wow\d3dx9_43.dll") -and (Test-Path "$sys32\d3dx9_43.dll"); Winget = "Microsoft.DirectX"; Para = "SonicGLvl (visor 3D)" }
)
$faltan = @()
foreach ($r in $requisitos) {
    if ($r.Ok) { Write-Host ("  OK     {0}" -f $r.Nombre) -ForegroundColor Green }
    else { Write-Host ("  FALTA  {0}  (lo usa: {1})" -f $r.Nombre, $r.Para) -ForegroundColor Red; $faltan += $r }
}
if ($faltan) {
    Write-Host "  Estos runtimes se instalan en Windows (fuera de la carpeta del mod)." -ForegroundColor DarkYellow
    if ((Get-Command winget -ErrorAction SilentlyContinue) -and (Preguntar "  ¿Instalarlos ahora con winget?")) {
        foreach ($r in $faltan) {
            Write-Host "  winget install $($r.Winget)" -ForegroundColor Cyan
            winget install --id $r.Winget -e --accept-package-agreements --accept-source-agreements
        }
    } else {
        foreach ($r in $faltan) { $avisos.Add("Instalar $($r.Nombre): winget install --id $($r.Winget) -e") }
    }
}

$juego   = Find-SteamApp "Sonic Generations" "SonicGenerations.exe"
$blender = Find-SteamApp "Blender" "blender.exe"
if ($juego)   { Write-Host "  OK     Sonic Generations: $juego" -ForegroundColor Green } else { Write-Host "  FALTA  Sonic Generations (Steam)" -ForegroundColor Red; $avisos.Add("Instalar Sonic Generations desde Steam y volver a ejecutar PREPARAR_ENTORNO.bat") }
if ($blender) { Write-Host "  OK     Blender (Steam): $blender" -ForegroundColor Green } else { Write-Host "  FALTA  Blender (Steam)" -ForegroundColor Red; $avisos.Add("Instalar Blender desde Steam y volver a ejecutar PREPARAR_ENTORNO.bat") }
$candidatosHmm = @("D:\HedgeModManager.exe")
if ($juego) { $candidatosHmm += Join-Path $juego "HedgeModManager.exe" }
$hmm = $candidatosHmm | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($hmm) { Write-Host "  OK     Hedge Mod Manager: $hmm" -ForegroundColor Green } else { Write-Host "  FALTA  Hedge Mod Manager" -ForegroundColor Red }
if (-not $hmm) { $avisos.Add("Descargar Hedge Mod Manager 7.15: https://github.com/thesupersonic16/HedgeModManager/releases") }

# ---------------------------------------------------------------------------------
Titulo "2. Herramientas de modding"
Ejecutar-Script "descargar_herramientas.ps1"

# ---------------------------------------------------------------------------------
Titulo "3. Blender aislado (HEIO + Time Eater Tools)"
if ($blender) { Ejecutar-Script "configurar_blender.ps1" @("-BlenderExe", (Join-Path $blender "blender.exe")) }
else { Write-Host "  Omitido: falta Blender." -ForegroundColor DarkYellow }

# ---------------------------------------------------------------------------------
Titulo "4. Archivos originales del juego"
$packcpk = Get-ChildItem $herr -Recurse -Filter PackCpk.exe -ErrorAction SilentlyContinue | Select-Object -First 1
if ($SinJuego) { Write-Host "  Omitido (-SinJuego)." }
elseif (-not $juego) { Write-Host "  Omitido: falta el juego." -ForegroundColor DarkYellow }
elseif (-not $packcpk) { $avisos.Add("No se encontró PackCpk.exe; revisa el paso 2") }
else {
    New-Item -ItemType Directory -Force -Path $orig | Out-Null
    foreach ($cpk in "bb", "bb2", "bb3") {
        $destino = Join-Path $orig $cpk
        if ((Test-Path $destino) -and (Get-ChildItem $destino -Recurse -File | Select-Object -First 1)) { Write-Host "  [$cpk] ya extraído"; continue }
        Write-Host "  [$cpk] extrayendo (puede tardar varios minutos)..." -ForegroundColor Cyan
        # PackCpk extrae junto al .cpk: se trabaja con un enlace duro (o una copia) para no escribir en la carpeta del juego
        $enlace = Join-Path $orig "$cpk.cpk"
        $origen = Join-Path $juego "disk\$cpk.cpk"
        if (-not (Test-Path $enlace)) {
            try { New-Item -ItemType HardLink -Path $enlace -Target $origen | Out-Null }
            catch { Copy-Item $origen $enlace }
        }
        # PackCpk necesita una consola propia
        Start-Process -FilePath $packcpk.FullName -ArgumentList "`"$enlace`"" -WorkingDirectory $orig -Wait -WindowStyle Minimized
        Remove-Item $enlace -Force
        $n = (Get-ChildItem $destino -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
        if ($n -gt 0) { Write-Host "  [$cpk] $n archivos" -ForegroundColor Green } else { $avisos.Add("La extracción de $cpk.cpk no produjo archivos") }
    }
}

# ---------------------------------------------------------------------------------
Titulo "5. Mods de referencia"
$aria = Get-ChildItem (Join-Path $herr "aria2") -Recurse -Filter aria2c.exe -ErrorAction SilentlyContinue | Select-Object -First 1
$hedgearc = Get-ChildItem $herr -Recurse -Filter HedgeArcPack.exe -ErrorAction SilentlyContinue | Select-Object -First 1
function Descargar-Aria([string]$url, [string]$dir, [string]$nombre) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    & $aria.FullName -c -x8 -s8 -k1M --max-tries=0 --retry-wait=10 --file-allocation=prealloc --enable-color=false `
        --summary-interval=0 --console-log-level=warn --auto-file-renaming=false --allow-overwrite=false --dir="$dir" --out="$nombre" $url
    if ($LASTEXITCODE -ne 0) { throw "aria2 falló ($LASTEXITCODE) descargando $nombre" }
}
function Url-GoogleDrive([string]$id) {
    $pag = Invoke-WebRequest -UseBasicParsing "https://drive.google.com/uc?export=download&id=$id"
    $accion = [regex]::Match($pag.Content, 'action="([^"]+)"').Groups[1].Value
    if (-not $accion) { return "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t" }
    $campos = [regex]::Matches($pag.Content, '<input type="hidden" name="([^"]+)" value="([^"]*)"') |
        ForEach-Object { "$($_.Groups[1].Value)=$([uri]::EscapeDataString($_.Groups[2].Value))" }
    return $accion + "?" + ($campos -join "&")
}

if ($SinReferencias) { Write-Host "  Omitido (-SinReferencias)." }
elseif (-not $aria) { $avisos.Add("No se encontró aria2c.exe; revisa el paso 2") }
else {
    # Dark Mode for Hub World (GameBanana 650721): recoloreado del hub con una sola textura
    $dm = Join-Path $refs "dark_mode_hub"
    if (-not (Test-Path (Join-Path $dm "dark_mode.zip"))) {
        Write-Host "  [Dark Mode] descargando..." -ForegroundColor Cyan
        Descargar-Aria "https://gamebanana.com/dl/1617021" $dm "dark_mode.zip"
        Set-Content (Join-Path $dm "url.txt") "https://gamebanana.com/dl/1617021" -Encoding ascii
    }
    if (-not (Test-Path (Join-Path $dm "contenido"))) { Expand-Archive (Join-Path $dm "dark_mode.zip") (Join-Path $dm "contenido") -Force }
    if ($hedgearc -and -not (Test-Path (Join-Path $dm "ext_black"))) {
        $ar = Get-ChildItem (Join-Path $dm "contenido") -Recurse -Filter "+pam000.ar.00" | Where-Object { $_.FullName -match 'black' } | Select-Object -First 1
        if ($ar) { & $hedgearc.FullName $ar.FullName (Join-Path $dm "ext_black") | Out-Null }
    }
    Write-Host "  [Dark Mode] listo" -ForegroundColor Green

    # Unleashed Project 1.0 (Team Unleashed, 2013): hub rehecho completo. 2,5 GB comprimido, 3,3 GB extraído
    $up = Join-Path $refs "unleashed_project"
    $upExt = Join-Path $up "extraido"
    if (Test-Path (Join-Path $upExt "Unleashed Project Final")) {
        Write-Host "  [Unleashed Project] ya extraído"
    } elseif (Preguntar "  ¿Descargar el Unleashed Project (2,5 GB, unos 6 GB libres en total)?") {
        $z = Join-Path $up "sonic_generations_unleashed_project_1.0-r2.7z"
        if (-not (Test-Path $z) -or (Test-Path "$z.aria2")) {
            Write-Host "  [Unleashed Project] descargando de Google Drive..." -ForegroundColor Cyan
            Descargar-Aria (Url-GoogleDrive "1ErRoQp04-V6ZoPX0-3vi3m7QP6Y86MhE") $up (Split-Path $z -Leaf)
        }
        Write-Host "  [Unleashed Project] extrayendo..." -ForegroundColor Cyan
        New-Item -ItemType Directory -Force -Path $upExt | Out-Null
        & "$env:SystemRoot\System32\tar.exe" -xf $z -C $upExt
        if ($LASTEXITCODE -ne 0) { throw "tar no pudo extraer $z" }
        if (Preguntar "  ¿Borrar el .7z para liberar 2,5 GB?") { Remove-Item $z }
    }

    # Desempaquetar los archivos del hub para compararlos (ver bóveda: white-space-pam000)
    $mod = Join-Path $upExt "Unleashed Project Final\mods\UnleashedProjectMod"
    $an = Join-Path $up "analisis"
    if ($hedgearc -and (Test-Path $mod)) {
        $pares = @(
            @("up_#pam000",        "$mod\#pam000.ar.00"),
            @("up_pam000",         "$mod\pam000.ar.00"),
            @("up_Packed_pam000",  "$mod\Packed\pam000\pam000.ar.00"),
            @("up_#Application",   "$mod\#Application.ar.00"),
            @("up_#SystemCommon",  "$mod\#SystemCommon.ar.00"),
            @("orig_#pam000",      "$orig\bb2\#pam000.ar.00"),
            @("orig_pam000",       "$orig\bb2\pam000.ar.00")
        )
        foreach ($p in $pares) {
            $out = Join-Path $an $p[0]
            if ((Test-Path $out) -or -not (Test-Path $p[1])) { continue }
            New-Item -ItemType Directory -Force -Path $out | Out-Null
            & $hedgearc.FullName $p[1] $out | Out-Null
        }
        Write-Host "  [Unleashed Project] análisis en $an" -ForegroundColor Green
    }
}

# ---------------------------------------------------------------------------------
Titulo "Verificación"
$esperados = [ordered]@{
    "SonicGLvl"          = "SonicGLvl.exe";      "Hedgehog Converter" = "HedgehogConverter.exe"
    "Havok Converter"    = "HavokConverter.exe"; "Havok ini"          = "HavokConverter.ini"
    "GI Atlas Converter" = "GIAtlasConverter.exe"; "HedgeArcPack"     = "HedgeArcPack.exe"
    "PackCpk"            = "PackCpk.exe";        "ModelConverter"     = "ModelConverter.exe"
    "HedgeGI"            = "HedgeGI.exe";        "SonicAudioTools"    = "AcbEditor.exe"
    "SonicLightTools"    = "SonicLightEditor.exe"; "texconv"          = "texconv.exe"
    "KwasTools"          = "he_anim_tool.exe";   "fcoEditor"          = "fcoEditor.exe"
    "aria2"              = "aria2c.exe";         "BlenderToXML"       = "BlenderToXML.py"
    "Blender config"     = "userpref.blend"
}
$todos = Get-ChildItem $herr -Recurse -File -ErrorAction SilentlyContinue
foreach ($k in $esperados.Keys) {
    $ok = [bool]($todos | Where-Object Name -eq $esperados[$k] | Select-Object -First 1)
    Write-Host ("  {0,-6} {1}" -f $(if ($ok) { "OK" } else { "FALTA" }), $k) -ForegroundColor $(if ($ok) { "Green" } else { "Red" })
    if (-not $ok) { $avisos.Add("Falta $k; vuelve a ejecutar PREPARAR_ENTORNO.bat (GitHub a veces da error 504)") }
}
foreach ($c in "bb", "bb2", "bb3") {
    $ok = Test-Path (Join-Path $orig $c)
    Write-Host ("  {0,-6} archivos originales\{1}" -f $(if ($ok) { "OK" } else { "FALTA" }), $c) -ForegroundColor $(if ($ok) { "Green" } else { "Red" })
}

Write-Host ""
if ($avisos.Count) {
    Write-Host "Pendiente:" -ForegroundColor Yellow
    $avisos | Select-Object -Unique | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
} else {
    Write-Host "Entorno listo. Abre Blender con scripts\abrir_blender.bat" -ForegroundColor Green
}
