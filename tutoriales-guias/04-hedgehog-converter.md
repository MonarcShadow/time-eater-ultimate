# Hedgehog Converter (libgens-sonicglvl)

**Qué es:** convierte el modelo visual del nivel (FBX, OBJ, DAE o glTF hecho en Blender) en **terreno** del juego: `.terrain-model`, grupos de terreno, materiales y texturas dentro de `Packed\<id>\`.

**Ruta:** `herramientas\libgens-sonicglvl\libgens-sonicglvl\bin\HedgehogConverter.exe` (programa con ventana)

## Antes de convertir (en Blender)

- Escala en metros. Exporta con **Time Eater Tools → Exportar FBX** (ya usa *Apply Scalings: FBX Units Scale*; sin eso el nivel sale 100 veces más grande).
- Nombres de materiales/texturas sin puntos.
- Transparencias: prefijo de capa en el nombre del material, `@LYR(punch)` (recorte) o `@LYR(trans)` (translúcido).

## Pasos

1. Crea la carpeta destino del escenario dentro del mod, por ejemplo:
   `mod\disk\bb\Packed\ghz200\`
2. Abre Hedgehog Converter y rellena:

| Campo | Valor |
|---|---|
| **Game Engine** | Generations |
| **Source 3D model files** | tu `.fbx` |
| **Source textures directory** | carpeta de las texturas PNG/DDS del modelo |
| **Terrain output directory** | la carpeta `Packed\ghz200\` del paso 1 |
| **Merge with existing files** | **desactivado** para un nivel nuevo |
| **Generate materials** | activado |
| **Copy and convert textures** | activado |
| **Force tags from Source 3D models' material names as submesh layer** | activado |
| **Groups / Cell size** | por defecto (los grupos dividen el terreno para cargarlo por partes) |

3. Pulsa **Convert**.

> ⚠️ Con *Merge with existing files* activado puedes perder cambios: la guía de HedgeDocs lo llama "irreversible". Trabaja sobre copias.

## Lo que NO genera

- El archivo `#ghz200.ar.00` (set data, colisión, configuración): cópialo de `archivos originales\bb\` y edítalo.
- La colisión → [Havok Converter](05-havok-converter.md).
- La iluminación → [HedgeGI](07-hedgegi.md).

Si arrancas el nivel solo con terreno, Sonic cae al vacío: falta la colisión.

## Cielo (opcional)

El cielo es un `.model` (de [ModelConverter](08-modelconverter.md) o de otro escenario) dentro de `Packed\<id>\<id>.ar.00`, y se declara en `Terrain.stg.xml` del `#`:
```xml
<Sky><Model>nombre_del_cielo</Model></Sky>
```
