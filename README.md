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
| `scripts/` | Preparar entorno, descargas, Blender y publicación de releases | Sí |
| `tutoriales-guias/` | Una guía por herramienta (empieza por `00-indice.md`) | Sí |
| `herramientas/` | Toolchain descargada (SonicGLvl, Hedgehog/Havok Converter, HedgeArcPack, PackCpk, Blender…) | No |
| `archivos originales/` | Datos extraídos del juego (`bb`, `bb2`, `bb3`) | No (copyright de SEGA) |
| `legacy/` | Primer intento (cambio de textura de prueba, 2025) | Sí, salvo `legacy/disk` |
| `build/` | Salida de las releases | No |

## Preparar el entorno (una vez, o después de formatear)

Requisitos previos: Git (para clonar el repo) y, desde Steam, **Sonic Generations** y **Blender**.

```
git clone https://github.com/MonarcShadow/time-eater-ultimate.git D:\modding\time-eater-ultimate
```

Luego **doble clic en `PREPARAR_ENTORNO.bat`**. Hace todo y se puede repetir (salta lo que ya está):

1. Revisa los runtimes de Windows (Visual C++ 2010/2015+, DirectX 9); si falta alguno, ofrece instalarlo con winget.
2. Descarga la toolchain en `herramientas\` (`scripts\descargar_herramientas.ps1`).
3. Configura Blender aislado en `herramientas\blender-config` (`scripts\configurar_blender.ps1`).
4. Extrae `bb`, `bb2` y `bb3` del juego en `archivos originales\`.
5. Descarga los mods de referencia (Dark Mode y, si dices que sí, el Unleashed Project de 2,5 GB) y desempaqueta su hub para compararlo.

Opciones: `PREPARAR_ENTORNO.bat -Todo` (sin preguntas), `-SinReferencias`, `-SinJuego`.

Para descargas grandes sueltas: `scripts\descargar.ps1 -Url <url>` (aria2, a `descargas\`) y `scripts\estado_descargas.ps1`.

Luego abre Blender siempre con `scripts\abrir_blender.bat`: carga HEIO y el addon **Time Eater Tools** (panel N > Time Eater), y no toca la configuración global de Blender (`%APPDATA%`).

## Publicar una versión

```powershell
.\scripts\publicar_release.ps1 -Version 0.2.0 -Notas "Qué cambió"
```

El script sube la versión en `mod/mod.ini`, hace commit y push, y crea la GitHub Release. La release incluye cada archivo del mod, un zip y los manifiestos de actualización de HMM 7 (`HedgeModManager.xml`) y HMM 8 (`update_manifest.json`).
