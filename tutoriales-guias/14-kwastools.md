# KwasTools — he_anim_tool (ThisKwasior)

**Qué es:** convierte las animaciones del Hedgehog Engine (`*-anim`) a XML editable y de vuelta. Sirve para animar materiales: texturas que se desplazan (agua, cintas), colores que cambian, parpadeos.

**Ruta:** `herramientas\KwasTools\KwasTools-win64-20260627\bin\he_anim_tool.exe`

## Formatos

| Formato | Qué anima |
|---|---|
| `.uv-anim` | Desplazamiento de UV (texturas que se mueven) |
| `.mat-anim` | Parámetros del material (color, brillo…) |
| `.cam-anim` | Cámaras |
| `.vis-anim` | Visibilidad |
| `.morph-anim`, `.pt-anim`, `.lit-anim` | Morphs, patrones de textura, luces |

## Uso

Arrastra el archivo sobre `he_anim_tool.exe`, o:

```powershell
$kt = "herramientas\KwasTools\KwasTools-win64-20260627\bin\he_anim_tool.exe"
& $kt "trabajo\pam000\pam_etc_km1_bossgate02.mat-anim"   # → pam_etc_km1_bossgate02.xml al lado (comprobado)
# editar el XML…
& $kt "trabajo\pam000\pam_etc_km1_bossgate02.xml"        # → .mat-anim
```

## Ideas para el proyecto

- `pam_etc_km1_bossgate02.mat-anim` anima el material de las puertas de jefe del hub: buen punto de partida para portales "inestables".
- En `archivos originales\referencias\unleashed_project\analisis\up_pam000\` hay ejemplos de `.uv-anim` y `.mat-anim` del hub del Unleashed Project (la fuente de la plaza, `blbgate_dial.mat-anim`…).

KwasTools trae además `cri_utf_tool`, `cri_afs_tool` y `cri_awb_tool` (formatos de audio CRIWARE); para el audio de Generations usa mejor [SonicAudioTools](16-sonicaudiotools.md).
