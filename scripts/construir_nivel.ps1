# construir_nivel.ps1 — construye un nivel de niveles\<Nivel> y lo instala en mod\ en el slot de su nivel.json.
#   1. Blender (headless, niveles\comun\crear_camino.py): escena + FBX visual, FBX de colisión, textura y path.xml
#   2. Hedgehog Converter: FBX visual -> terreno (Packed\<slot>: <slot>.ar.00, Stage.pfd, Stage-Add.pfd)
#   3. Se añade la luz del escenario original (campo "luz") al <slot>.ar
#   4. Havok Converter: FBX de colisión -> teu_camino_col.phy.hkx
#   5. #<slot>.ar.00 = XML propios (niveles\<Nivel>\escenario_<slot>) + "archivos_base" del original + path + colisión
#   6. Copia a mod\disk\<cpk>\
# Uso: powershell -ExecutionPolicy Bypass -File scripts\construir_nivel.ps1 -Nivel prueba_moderno
param([Parameter(Mandatory)][string]$Nivel)
$ErrorActionPreference = "Stop"
$raiz  = Split-Path $PSScriptRoot -Parent
$dirNivel = Join-Path $raiz "niveles\$Nivel"
$cfg   = Get-Content (Join-Path $dirNivel "nivel.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$slot  = $cfg.slot
$build = Join-Path $raiz "build\niveles\$Nivel"
$orig  = Join-Path $raiz "archivos originales\$($cfg.cpk)"
$herr  = Join-Path $raiz "herramientas"
$modDisk = Join-Path $raiz "mod\disk\$($cfg.cpk)"
. (Join-Path $PSScriptRoot "lib\conversores.ps1")
$hap = (Get-ChildItem (Join-Path $herr "HedgeArcPack") -Recurse -Filter HedgeArcPack.exe | Select-Object -First 1).FullName

function Paso([string]$t) { Write-Host "== $t" -ForegroundColor Cyan }
function Extraer([string]$ar, [string]$dest) {
    if (Test-Path -LiteralPath $dest) { Remove-Item -LiteralPath $dest -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    & $hap -E $ar $dest | Out-Null
}
function Empaquetar([string]$carpeta, [string]$destinoAr) {
    New-Item -ItemType Directory -Force -Path (Split-Path $destinoAr -Parent) | Out-Null
    & $hap -P $carpeta $destinoAr -T=gens | Out-Null
    if (-not (Test-Path -LiteralPath "$destinoAr.00")) { throw "HedgeArcPack no generó $destinoAr.00" }
}

Write-Host "Nivel '$Nivel' -> slot $slot ($($cfg.descripcion))" -ForegroundColor Yellow
if (Test-Path $build) { Remove-Item -LiteralPath $build -Recurse -Force }
New-Item -ItemType Directory -Force -Path $build | Out-Null

# 1. Blender ---------------------------------------------------------------------------------
Paso "1. Blender: escena y exportación"
$bcfg = Join-Path $herr "blender-config"
$env:TEU_HERRAMIENTAS = $herr
$env:BLENDER_USER_RESOURCES = $bcfg; $env:BLENDER_USER_CONFIG = "$bcfg\config"; $env:BLENDER_USER_SCRIPTS = "$bcfg\scripts"
$env:BLENDER_USER_EXTENSIONS = "$bcfg\extensions"; $env:BLENDER_USER_DATAFILES = "$bcfg\datafiles"
$blender = Get-Content (Join-Path $bcfg "blender_exe.txt")
$salidaBl = Join-Path $build "blender"
$ErrorActionPreference = "Continue"   # Blender escribe avisos en stderr; en PS 5.1 eso no debe cortar el script
$log = & $blender --background --factory-startup --python (Join-Path $raiz "niveles\comun\crear_camino.py") -- $dirNivel $salidaBl 2>&1 | ForEach-Object { "$_" }
$ErrorActionPreference = "Stop"
if (-not ($log -match "TEU_ESCENA_OK")) { $log | Select-Object -Last 30; throw "Blender no terminó la escena" }
Copy-Item (Join-Path $salidaBl "$($cfg.nombre).blend") $dirNivel -Force   # la escena queda en el repo para editarla

# 2. Hedgehog Converter -------------------------------------------------------------------------
Paso "2. Hedgehog Converter: terreno"
$terreno = Join-Path $build "terreno"
New-Item -ItemType Directory -Force -Path $terreno | Out-Null
$r = Invoke-ConversorGui "HedgehogConverter.exe" "HedgehogConverter.ini" ([ordered]@{
    model_source_paths = (ConvertTo-RutaQt "$salidaBl\teu_camino.fbx"); texture_source_path = (ConvertTo-RutaQt $salidaBl)
    terrain_output_path = (ConvertTo-RutaQt $terreno); game_engine = 0; merge_existing = "false"
    generate_materials = "true"; copy_and_convert_textures = "true"; force_tags_layers = "true"
    remove_material_tags = "true"; remove_model_tags = "true"; use_model_groups = "true"; convert_lights = "true"
    position_x = 0; position_y = 0; position_z = 0; scale_x = 100; scale_y = 100; scale_z = 100
    rotation_x = 0; rotation_y = 0; rotation_z = 0; group_cell_size = 75
}) "HCWindow.centralwidget.groupBox.te_progress" $null 300
if (-not ($r.Log -match "Conversion complete")) { $r.Log; throw "Hedgehog Converter no terminó" }
# el .ar se llama como la carpeta de salida: renombrarlo al slot
Get-ChildItem $terreno -Filter "*.ar*" | Where-Object { $_.BaseName -notlike "$slot*" } | ForEach-Object {
    Rename-Item $_.FullName ($_.Name -replace '^[^.]+', $slot) }

# 3. Luz del escenario original ----------------------------------------------------------------
Paso "3. Luz $($cfg.luz) del escenario original"
$extTerreno = Join-Path $build "ext_terreno"
Extraer (Join-Path $terreno "$slot.ar.00") $extTerreno
$extOrigPacked = Join-Path $build "ext_orig_packed"
Extraer (Join-Path $orig "Packed\$slot\$slot.ar.00") $extOrigPacked
$luz = Join-Path $extOrigPacked "$($cfg.luz).light"
if (-not (Test-Path -LiteralPath $luz)) { throw "No existe $($cfg.luz).light en Packed\$slot del juego" }
Copy-Item -LiteralPath $luz $extTerreno
$packedFinal = Join-Path $build "Packed\$slot"
Empaquetar $extTerreno (Join-Path $packedFinal "$slot.ar")
Copy-Item (Join-Path $terreno "Stage.pfd"), (Join-Path $terreno "Stage-Add.pfd") $packedFinal

# 4. Havok Converter ---------------------------------------------------------------------------
Paso "4. Havok Converter: colisión"
$hkx = Join-Path $build "teu_camino_col.phy.hkx"
$iniHavok = Join-Path $BinLibgens "HavokConverter.ini"
$tags = ([regex]::Match([IO.File]::ReadAllText($iniHavok), '(?m)^property_tags=(.*)$')).Groups[1].Value.TrimEnd("`r")
if (-not $tags) { throw "HavokConverter.ini no tiene property_tags (vuelve a ejecutar descargar_herramientas.ps1)" }
$r = Invoke-ConversorGui "HavokConverter.exe" "HavokConverter.ini" ([ordered]@{
    model_source_paths = (ConvertTo-RutaQt "$salidaBl\teu_camino_col.fbx"); output_file = (ConvertTo-RutaQt $hkx); mode = 0
    position_x = 0; position_y = 0; position_z = 0; scale_x = 100; scale_y = 100; scale_z = 100
    rotation_x = 0; rotation_y = 0; rotation_z = 0; property_tags = $tags
}) $null $hkx 300
if (-not (Test-Path $hkx)) { throw "Havok Converter no generó $hkx" }

# 5. Archivo #<slot> --------------------------------------------------------------------------------
Paso "5. Archivo #$slot"
$extOrigHash = Join-Path $build "ext_orig_hash"
Extraer (Join-Path $orig "#$slot.ar.00") $extOrigHash
$hash = Join-Path $build "hash_$slot"
New-Item -ItemType Directory -Force -Path $hash | Out-Null
foreach ($f in $cfg.archivos_base) { Copy-Item -LiteralPath (Join-Path $extOrigHash $f) $hash }
Get-ChildItem -LiteralPath (Join-Path $dirNivel "escenario_$slot") -File | ForEach-Object { Copy-Item -LiteralPath $_.FullName $hash }
$path = Join-Path $salidaBl "$slot.path.xml"
if (Test-Path -LiteralPath $path) { Copy-Item -LiteralPath $path $hash }
Copy-Item -LiteralPath $hkx $hash
Empaquetar $hash (Join-Path $build "#$slot.ar")

# 6. Instalar en mod\ ------------------------------------------------------------------------------
Paso "6. Copiar a mod\disk\$($cfg.cpk)"
$modPacked = Join-Path $modDisk "Packed\$slot"
if (Test-Path -LiteralPath $modPacked) { Remove-Item -LiteralPath $modPacked -Recurse -Force }
New-Item -ItemType Directory -Force -Path $modPacked | Out-Null
Copy-Item -LiteralPath (Join-Path $build "#$slot.ar.00"), (Join-Path $build "#$slot.arl") $modDisk -Force
Get-ChildItem $packedFinal -File | ForEach-Object { Copy-Item $_.FullName $modPacked -Force }
Get-ChildItem -LiteralPath $modDisk -Recurse -File | Where-Object { $_.Name -like "*$slot*" -or $_.DirectoryName -like "*\$slot" } |
    ForEach-Object { "  {0}  {1:N0} bytes" -f $_.FullName.Substring($raiz.Length + 1), $_.Length }
Write-Host "Nivel '$Nivel' instalado en mod\ (slot $slot)" -ForegroundColor Green
