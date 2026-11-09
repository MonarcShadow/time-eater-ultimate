# construir_nivel_prueba.ps1 — construye el nivel de prueba "solo un camino" y lo instala en mod\ en el slot
# del Death Egg Robot (bde, Sonic clásico). Todo automático:
#   1. Blender (headless) genera la escena y exporta FBX visual, FBX de colisión, textura y path.xml (camino 2D)
#   2. Hedgehog Converter: FBX visual -> terreno (Packed\bde: bde.ar.00, Stage.pfd, Stage-Add.pfd)
#   3. Se añade la luz Direct01.light del escenario original al bde.ar
#   4. Havok Converter: FBX de colisión -> teu_camino_col.phy.hkx
#   5. Se arma #bde.ar.00: XML propios (niveles\prueba_camino\escenario_bde) + parámetros del original + path + colisión
#   6. Se copia a mod\disk\bb\
# Uso: powershell -ExecutionPolicy Bypass -File scripts\construir_nivel_prueba.ps1
$ErrorActionPreference = "Stop"
$raiz   = Split-Path $PSScriptRoot -Parent
$nivel  = Join-Path $raiz "niveles\prueba_camino"
$build  = Join-Path $raiz "build\nivel_prueba"
$orig   = Join-Path $raiz "archivos originales\bb"
$herr   = Join-Path $raiz "herramientas"
$modBb  = Join-Path $raiz "mod\disk\bb"
$slot   = "bde"
. (Join-Path $PSScriptRoot "lib\conversores.ps1")
$hap = (Get-ChildItem (Join-Path $herr "HedgeArcPack") -Recurse -Filter HedgeArcPack.exe | Select-Object -First 1).FullName

function Paso([string]$t) { Write-Host "== $t" -ForegroundColor Cyan }
function Extraer([string]$ar, [string]$dest) {
    if (Test-Path $dest) { Remove-Item -LiteralPath $dest -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    & $hap -E $ar $dest | Out-Null
}
function Empaquetar([string]$carpeta, [string]$destinoAr) {
    New-Item -ItemType Directory -Force -Path (Split-Path $destinoAr -Parent) | Out-Null
    & $hap -P $carpeta $destinoAr -T=gens | Out-Null
    if (-not (Test-Path "$destinoAr.00")) { throw "HedgeArcPack no generó $destinoAr.00" }
}

if (Test-Path $build) { Remove-Item -LiteralPath $build -Recurse -Force }
New-Item -ItemType Directory -Force -Path $build | Out-Null

# 1. Blender ---------------------------------------------------------------------------------
Paso "1. Blender: escena y exportación"
$cfg = Join-Path $herr "blender-config"
$env:TEU_HERRAMIENTAS = $herr
$env:BLENDER_USER_RESOURCES = $cfg; $env:BLENDER_USER_CONFIG = "$cfg\config"; $env:BLENDER_USER_SCRIPTS = "$cfg\scripts"
$env:BLENDER_USER_EXTENSIONS = "$cfg\extensions"; $env:BLENDER_USER_DATAFILES = "$cfg\datafiles"
$blender = Get-Content (Join-Path $cfg "blender_exe.txt")
$salidaBl = Join-Path $build "blender"
$ErrorActionPreference = "Continue"   # Blender escribe avisos en stderr; en PS 5.1 eso no debe cortar el script
$log = & $blender --background --factory-startup --python (Join-Path $nivel "crear_escena.py") -- $salidaBl 2>&1 | ForEach-Object { "$_" }
$ErrorActionPreference = "Stop"
if (-not ($log -match "TEU_ESCENA_OK")) { $log | Select-Object -Last 30; throw "Blender no terminó la escena" }
Copy-Item (Join-Path $salidaBl "prueba_camino.blend") $nivel -Force   # la escena queda en el repo para editarla

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
# la carpeta de salida se llama como el escenario: renombrar el .ar generado
Get-ChildItem $terreno -Filter "*.ar*" | Where-Object { $_.BaseName -notlike "$slot*" } | ForEach-Object {
    Rename-Item $_.FullName ($_.Name -replace '^[^.]+', $slot) }

# 3. Luz del escenario original ----------------------------------------------------------------
Paso "3. Luz Direct01 del escenario original"
$extTerreno = Join-Path $build "ext_terreno"
Extraer (Join-Path $terreno "$slot.ar.00") $extTerreno
$extOrigPacked = Join-Path $build "ext_orig_packed"
Extraer (Join-Path $orig "Packed\$slot\$slot.ar.00") $extOrigPacked
Copy-Item (Join-Path $extOrigPacked "Direct01.light") $extTerreno
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

# 5. Archivo #bde --------------------------------------------------------------------------------
Paso "5. Archivo #$slot"
$extOrigHash = Join-Path $build "ext_orig_hash"
Extraer (Join-Path $orig "#$slot.ar.00") $extOrigHash
$hash = Join-Path $build "hash_$slot"
New-Item -ItemType Directory -Force -Path $hash | Out-Null
foreach ($f in "SceneEffect.prm.xml", "Terrain.prm.xml", "StageAct.prm.xml", "BossRivalSetting.prm.xml", "BossDeathEgg.lua") {
    Copy-Item -LiteralPath (Join-Path $extOrigHash $f) $hash }
Get-ChildItem -LiteralPath (Join-Path $nivel "escenario_$slot") -File | ForEach-Object { Copy-Item -LiteralPath $_.FullName $hash }
Copy-Item (Join-Path $salidaBl "$slot.path.xml"), $hkx $hash
Empaquetar $hash (Join-Path $build "#$slot.ar")

# 6. Instalar en mod\ ------------------------------------------------------------------------------
Paso "6. Copiar a mod\disk\bb"
$modPacked = Join-Path $modBb "Packed\$slot"
if (Test-Path $modPacked) { Remove-Item -LiteralPath $modPacked -Recurse -Force }
New-Item -ItemType Directory -Force -Path $modPacked | Out-Null
Copy-Item -LiteralPath (Join-Path $build "#$slot.ar.00"), (Join-Path $build "#$slot.arl") $modBb -Force
Get-ChildItem $packedFinal -File | ForEach-Object { Copy-Item $_.FullName $modPacked -Force }
Get-ChildItem $modBb -Recurse -File | ForEach-Object { "  {0}  {1:N0} bytes" -f $_.FullName.Substring($raiz.Length + 1), $_.Length }
Write-Host "Nivel de prueba instalado en mod\ (slot $slot)" -ForegroundColor Green
