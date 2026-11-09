# Time Eater Ultimate

Mod para **Sonic Generations (2011, Steam)**: un nivel nuevo y un White Space rediseñado, inspirados en la batalla final contra el Time Eater.

## Instalar

1. Descarga `TimeEaterUltimate-X.Y.Z.zip` de la [última release](https://github.com/MonarcShadow/time-eater-ultimate/releases/latest).
2. Arrástralo a Hedge Mod Manager y actívalo.
3. Las siguientes versiones se instalan desde HMM con *Check for updates*.

## Estructura del repositorio

| Carpeta | Contenido | En git |
|---|---|---|
| `mod/` | El mod tal como lo carga HMM (`mod.ini`, `disk/...`) | Sí |
| `scripts/` | `descargar_herramientas.ps1`, `publicar_release.ps1` | Sí |
| `herramientas/` | Toolchain descargada (SonicGLvl, Hedgehog/Havok Converter, HedgeArcPack, PackCpk, Blender…) | No |
| `archivos originales/` | Datos extraídos del juego (`bb`, `bb2`, `bb3`) | No (copyright de SEGA) |
| `legacy/` | Primer intento (cambio de textura de prueba, 2025) | Sí, salvo `legacy/disk` |
| `build/` | Salida de las releases | No |

## Publicar una versión

```powershell
.\scripts\publicar_release.ps1 -Version 0.2.0 -Notas "Qué cambió"
```

El script sube la versión en `mod/mod.ini`, hace commit y push, y crea la GitHub Release. La release incluye cada archivo del mod, un zip y los manifiestos de actualización de HMM 7 (`HedgeModManager.xml`) y HMM 8 (`update_manifest.json`).
