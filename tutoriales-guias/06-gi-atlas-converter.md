# GI Atlas Converter (libgens-sonicglvl)

**Qué es:** importa texturas de **iluminación global** (lightmaps y shadowmaps renderizadas fuera, p. ej. en 3ds Max/V-Ray) al formato de atlas del escenario (`gi-texture`, `Stage-Add.pfd`).

**Ruta:** `herramientas\libgens-sonicglvl\libgens-sonicglvl\bin\GIAtlasConverter.exe` (programa con ventana)

## ¿Lo necesitamos?

Probablemente **no**: [HedgeGI](07-hedgegi.md) hornea la GI directamente sobre el escenario y la empaqueta. GI Atlas Converter es el camino antiguo, útil solo si renderizas los mapas de luz en otro programa.

## Campos principales (sin probar)

Según su configuración (`GIAtlasConverter.ini`, que el programa crea en la carpeta desde donde se abre):

| Campo | Para qué |
|---|---|
| Game engine | Generations |
| Source GI directory | carpeta con las texturas de luz/sombra renderizadas |
| Terrain directory | la carpeta `Packed\<id>\` del escenario |
| Octree cell size, Quality size multiplier, Max texture size / Max atlas texture size | resolución y tamaño de los atlas (por defecto 75, 16, 1024, 2048) |
| Override lightmap / shadowmap | forzar un color o sombra fija en vez de la textura |

## Atajo sin GI

Si el nivel solo usa luz direccional y no quieres GI, puedes **borrar `Stage-Add.pfd`** del `Packed\<id>\` (ahí se guarda la GI) y el nivel pesa bastante menos. Se verá más plano.
