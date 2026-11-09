# ModelConverter (Skyth)

**Qué es:** convierte un modelo FBX en un `.model` del juego, con sus materiales. Se usa para **objetos sueltos** (decoración, objetos de `ObjectPhysics`, NPCs) y para el **cielo**. El terreno grande del nivel va con [Hedgehog Converter](04-hedgehog-converter.md).

**Ruta:** `herramientas\ModelConverter\ModelConverter.exe`

## Uso rápido

Arrastra el `.fbx` sobre **`ModelConverter-Generations.bat`** (en la misma carpeta). Crea el `.model` junto al FBX.

> Usa siempre la variante **Generations** (`--gens`). Las otras `.bat` son para Forces, Frontiers, Lost World, Unleashed o la versión *Raytracing* de Generations (un mod aparte).

## Línea de comandos

```powershell
herramientas\ModelConverter\ModelConverter.exe --gens origen.fbx destino.model
```

## Exportar el FBX desde Blender

Usa *Time Eater Tools → Exportar FBX* (aplica *FBX Units Scale* y desactiva *Add Leaf Bones*, que es lo que pide ModelConverter).

## Dónde va el resultado

| Uso | Destino |
|---|---|
| Cielo | `Packed\<id>\<id>.ar.00` + `<Sky><Model>nombre</Model></Sky>` en `Terrain.stg.xml` |
| Objeto de un escenario | `<id>_cmn.ar.00` o el `.ar` del escenario; registrar en `StageObject.sto.xml` y en `ObjectProduction.phy.xml` |
| Objeto del hub | `bb2\pam000.ar.00` (como hace el Unleashed Project) |

Detalles de objetos nuevos: bóveda → *objetos-set-data*.
