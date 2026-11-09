# HedgeArcPack (HedgeLib)

**Qué es:** abre y crea los paquetes del Hedgehog Engine: `.ar.00` / `.arl` (Generations y Unleashed), `.pfd` y `.pac` de otros juegos. Es la herramienta que más vas a usar.

**Ruta:** `herramientas\HedgeArcPack\HedgeArcPack.exe`

## Uso rápido (arrastrar y soltar)

- Arrastra un `.ar.00` sobre el exe → crea una carpeta con su contenido al lado.
- Arrastra una carpeta sobre el exe → la empaqueta (si no sabe el tipo, pregunta: responde `gens`).

## Uso por línea de comandos

```
HedgeArcPack input [output] [modo] [flags]

-E           Extraer el archivo "input" en la carpeta "output"
-P           Empaquetar la carpeta "input" en "output" (crea .ar.00, .ar.01… si hace falta)
-T=gens      Tipo .ar de Unleashed/Generations   (también: -T=pfd para .pfd)
-?           Ayuda
```

Ejemplos (PowerShell, desde la raíz del repo):

```powershell
$hap = "herramientas\HedgeArcPack\HedgeArcPack.exe"

# Extraer el archivo # del hub para ver set data y Terrain.stg.xml
& $hap -E "archivos originales\bb2\#pam000.ar.00" "trabajo\#pam000"

# Volver a empaquetar después de editar (crea #pam000.ar.00 + #pam000.arl)
New-Item -ItemType Directory -Force "mod\disk\bb2" | Out-Null
& $hap -P "trabajo\#pam000" "mod\disk\bb2\#pam000.ar" -T=gens

# Empaquetar un .pfd de terreno (regenera también el .pfi)  (sin probar)
& $hap -P "trabajo\Stage" "mod\disk\bb2\Packed\pam000\Stage.pfd" -T=pfd
```

> ⚠️ Al empaquetar, **la carpeta de destino debe existir**; si no, falla con *"An internal error has occurred"*. Comprobado: extraer y volver a empaquetar `#pam001` funciona.

## Archivos de un escenario (ejemplo `ghz200`)

| Archivo | Contiene |
|---|---|
| `#ghz200.ar.00` + `.arl` | Set data (objetos), `Terrain.stg.xml`, `Stage.stg.xml`, colisión `.phy.hkx`, splines `.path.xml` |
| `Packed\ghz200\ghz200.ar.00…` | Texturas, materiales, modelos, cielo, luz |
| `Packed\ghz200\Stage.pfd` / `Stage-Add.pfd` | Geometría del terreno / GI horneada |

## Archivos "append" (`+nombre.ar.00`)

Un `+pam000.ar.00` en `mod\disk\bb2\` **añade o reemplaza solo los archivos que contiene**, sin copiar el paquete entero. Es lo que usa el mod *Dark Mode* (una sola textura). Úsalo siempre que cambies pocos archivos.

## Ojo

- Para Generations solo soporta datos **sin comprimir** (los del juego lo están, no hay problema).
- El `.arl` se regenera al empaquetar; cópialo junto al `.ar.00`.
