# Guías de herramientas — Time Eater Ultimate

Una guía por programa de `herramientas\`. Todas las rutas son relativas a `D:\modding\time-eater-ultimate`.
Si falta alguna herramienta, ejecuta `PREPARAR_ENTORNO.bat` (doble clic) y se descarga sola.

## Flujo de trabajo de un nivel (de dónde sale cada cosa)

```
 Juego (bb.cpk, bb2.cpk)
   │  PackCpk ───────────────► archivos originales\ (bb, bb2, bb3)
   │  HedgeArcPack ──────────► abrir/crear .ar.00 y .pfd
   ▼
 Blender (+ HEIO + Time Eater Tools)
   ├─ modelo visual (FBX) ──► Hedgehog Converter ──► terreno  (Packed\<id>\)
   ├─ modelo de colisión ───► Havok Converter ─────► .phy.hkx (#<id>.ar.00)
   ├─ objetos sueltos/cielo ► ModelConverter ──────► .model
   └─ splines (rieles, 2D) ─► BlenderToXML ────────► .path.xml
   ▼
 SonicGLvl ──► objetos (anillos, resortes, portales) = set data
 HedgeGI ────► iluminación precalculada (GI) y light field
 texconv / SonicLightTools / KwasTools ──► texturas, luces, animaciones de material
   ▼
 HedgeArcPack (empaquetar) ──► mod\disk\... ──► Hedge Mod Manager ──► jugar
```

## Índice

| # | Programa | Para qué sirve | Guía |
|---|---|---|---|
| 1 | PackCpk | Extraer los CPK grandes del juego | [01-packcpk.md](01-packcpk.md) |
| 2 | HedgeArcPack | Abrir y crear archivos `.ar` / `.pfd` | [02-hedgearcpack.md](02-hedgearcpack.md) |
| 3 | SonicGLvl | Editor de niveles: colocar objetos | [03-sonicglvl.md](03-sonicglvl.md) |
| 4 | Hedgehog Converter | Modelo 3D → terreno del juego | [04-hedgehog-converter.md](04-hedgehog-converter.md) |
| 5 | Havok Converter | Modelo 3D → colisión | [05-havok-converter.md](05-havok-converter.md) |
| 6 | GI Atlas Converter | Importar texturas de iluminación (método antiguo) | [06-gi-atlas-converter.md](06-gi-atlas-converter.md) |
| 7 | HedgeGI | Hornear iluminación global y light field | [07-hedgegi.md](07-hedgegi.md) |
| 8 | ModelConverter | FBX → `.model` (objetos, cielo) | [08-modelconverter.md](08-modelconverter.md) |
| 9 | modelfbx / terrain2fbx | Sacar modelos del juego a FBX | [09-modelfbx-terrain2fbx.md](09-modelfbx-terrain2fbx.md) |
| 10 | Blender + HEIO + Time Eater Tools | Modelar el nivel | [10-blender.md](10-blender.md) |
| 11 | BlenderToXML (splines) | Rieles, caminos 2D y quickstep | [11-blendertoxml-splines.md](11-blendertoxml-splines.md) |
| 12 | texconv / texdiag | Texturas PNG ↔ DDS | [12-texconv.md](12-texconv.md) |
| 13 | SonicLightTools | Editar luces `.light` | [13-soniclighttools.md](13-soniclighttools.md) |
| 14 | KwasTools (he_anim_tool) | Animaciones de material, UV y cámara | [14-kwastools.md](14-kwastools.md) |
| 15 | fcoEditor | Textos y subtítulos | [15-fcoeditor.md](15-fcoeditor.md) |
| 16 | SonicAudioTools | Música y sonidos | [16-sonicaudiotools.md](16-sonicaudiotools.md) |
| 17 | aria2 (descargar.ps1) | Descargas grandes | [17-aria2-descargas.md](17-aria2-descargas.md) |

## Reglas generales

- **Nunca edites `archivos originales\`**: es la copia limpia del juego. Copia lo que necesites a una carpeta de trabajo o a `mod\`.
- **Nombres sin puntos ni espacios** en objetos, materiales y texturas (`Material.001` cuelga el juego). El panel *Time Eater* de Blender los corrige.
- **Escala**: 1 unidad de Blender = 1 metro. Sonic mide 0.5 × 0.5 × 1.0 m (botón *Añadir referencia Sonic*).
- Documentación de fondo (formatos, IDs, tags de colisión, portales del hub): bóveda Obsidian `D:\bobedas\mod sonic generation`.
- Marcado **(sin probar)**: pasos tomados de la documentación que todavía no hemos comprobado en este proyecto.
