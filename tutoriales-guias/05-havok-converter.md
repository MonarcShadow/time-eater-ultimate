# Havok Converter (libgens-sonicglvl)

**Qué es:** convierte un modelo 3D en la **colisión** del escenario (`.phy.hkx`): lo que Sonic pisa y qué tipo de superficie es (hierba, agua, daño…).

**Ruta:** `herramientas\libgens-sonicglvl\libgens-sonicglvl\bin\HavokConverter.exe` (programa con ventana)
Junto a él está `HavokConverter.ini`, que trae la lista de **tags de superficie** (lo descarga el script de herramientas; no lo borres).

## Preparar la colisión en Blender

- Usa un **modelo aparte**, más simple que el visual (menos polígonos, sin detalles pequeños).
- El tipo de superficie se pone **en el nombre del objeto/malla** con `@TAG`, por ejemplo `suelo@GRASS`, `agua@SHALLOWWATER`.
- Exporta a FBX con *Time Eater Tools → Exportar FBX*.

### Tags disponibles (del .ini)

| Tag | Efecto |
|---|---|
| `NORMAL` | Normal |
| `GRASS`, `DIRT`, `ROCK`, `WOOD`, `METAL`, `GLASS` | Sonido/partículas de esa superficie |
| `SAND` | Arena (en Generations suena a concreto) |
| `SNOW` | ⚠️ **Cuelga Generations**, no usar |
| `ICE` | Hielo (limitado en la versión final) |
| `DEEPWATER` / `SHALLOWWATER` / `NODEADWATER` | Agua profunda / poco profunda / sin muerte |
| `DEAD` | Muerte al tocar |
| `DAMAGE` | Hace daño |
| `NOEFFECT` | Sin efectos |
| `OIL`, `PINBALLGLASS`, `WRONGWAY`, `LAVA`, `POISON` | Solo Generations |
| `CAMERA` | La cámara no atraviesa esta colisión |

Más detalle: bóveda → *tags-de-colision*.

## Pasos

1. Abre Havok Converter.
2. **Source 3D model files**: el FBX de colisión.
3. **Output file**: nombre terminado en `.phy.hkx`, por ejemplo `teu_colision.phy.hkx`.
4. Pulsa **Convert**.
5. Extrae el `#<id>.ar.00` del escenario con [HedgeArcPack](02-hedgearcpack.md), copia dentro el `.phy.hkx` y en `Terrain.stg.xml` pon el nombre **sin extensión**:
   ```xml
   <Terrain>
     <RigidBodyContainer>teu_colision</RigidBodyContainer>
     <IsCollisionRender>false</IsCollisionRender>
   </Terrain>
   ```
6. Reempaqueta el `#`. Compruébalo en SonicGLvl (*View* → colisión) o en el juego.

## Versiones incluidas

`HavokConverter_Unleashed.exe` y `HavokConverter_LostWorld.exe` son para otros juegos; para este proyecto usa siempre `HavokConverter.exe`.
