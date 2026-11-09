# HedgeGI (Skyth)

**Qué es:** horneador de **iluminación global** (GI) y **light field** para escenarios del Hedgehog Engine. La GI son las luces y sombras suaves precalculadas sobre el terreno; el light field es la luz que reciben Sonic y los objetos según dónde estén.

**Ruta:** `herramientas\HedgeGI\HedgeGI.exe` (programa con ventana, nightly 2026-01-01)

## Requisitos

- CPU x64 con AVX.
- Para el *denoiser*: OptiX solo con GPU NVIDIA; con AMD o Intel usa **OIDN**.

## Flujo general (sin probar en este proyecto)

1. Termina antes el terreno ([Hedgehog Converter](04-hedgehog-converter.md)), la luz (`.light`, ver [SonicLightTools](13-soniclighttools.md)) y el cielo.
2. Abre HedgeGI y carga el escenario (la carpeta del escenario con su `Packed\<id>\` y el `#<id>`).
3. Revisa la vista previa: la luz direccional, el color del cielo y el entorno.
4. Ajusta la calidad (resolución de las texturas de GI, número de muestras). Empieza con calidad baja para probar: hornear en alta puede tardar horas.
5. Hornea la **GI** y el **Light Field**.
6. Empaqueta el resultado en el escenario (genera/actualiza `Stage-Add.pfd` y los archivos de light field).
7. Prueba en el juego.

## Consejos

- Cambiar la luz o el terreno obliga a volver a hornear.
- Guarda una copia del `Packed\<id>\` antes de empaquetar.
- Para el White Space "corrompido" quizá no haga falta re-hornear: con cambiar texturas, luz y cielo se logra mucho.
