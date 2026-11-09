# SonicAudioTools (Skyth)

**Qué es:** herramientas para los formatos de audio CRIWARE. En Sonic Generations la música y los sonidos están en `Sound\*.csb` (+ un `.cpk` con el mismo nombre para el audio en streaming).

**Ruta:** `herramientas\SonicAudioTools\` (necesitan .NET Framework 4, incluido en Windows)

## Programas

| Programa | Uso |
|---|---|
| **CsbEditor.exe** | El que usa Generations. Arrastra un `.csb` → extrae una carpeta con los audios. Arrastra la carpeta → vuelve a crear el `.csb` (y el `.cpk` si hay streaming) |
| CsbBuilder.exe | Editor con ventana para crear/editar CSB desde cero (avanzado) |
| AcbEditor.exe | Igual que CsbEditor pero para `.acb`/`.awb` (juegos posteriores) |
| AcbInjector.exe, ACBFinder.exe | Inyectar/buscar audio en ACB (otros juegos) |

## Reemplazar música (sin probar)

1. Copia el `.csb` y su `.cpk` de la carpeta `Sound\` del juego a una carpeta de trabajo (no edites los del juego).
2. Arrástralo sobre **CsbEditor.exe** → carpeta con subcarpetas `Synth\…` y los audios (`.adx` / `.aax`).
3. Reemplaza el audio respetando **el mismo nombre y formato** (ADX). Convertir WAV → ADX necesita un codificador aparte (p. ej. VGAudio), **no incluido**: avisa cuando haga falta y lo añadimos a las herramientas.
4. Arrastra la carpeta sobre CsbEditor.exe para reconstruir.
5. Pon el `.csb` (y `.cpk`) en `mod\Sound\`… **(ruta en el mod por confirmar)**.

Referencia: el Unleashed Project reemplaza la música del hub en `Sound\SNG18_PAM\Synth\` (archivos `EMBB052_PAM00A_wav.aax`…); ver `archivos originales\referencias\unleashed_project\extraido\…\Sound\`.
