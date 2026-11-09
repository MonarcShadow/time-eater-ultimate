# SonicLightTools (SWS90)

**Qué es:** herramientas para leer y editar los archivos de luz `.light` del escenario: posición y color de la luz direccional (el "sol") y de las luces omni (puntuales).

**Ruta:** `herramientas\SonicLightTools\` (necesitan .NET Framework 4, incluido en Windows)

## Programas

| Programa | Uso |
|---|---|
| **SonicLightXml.exe** | Arrastra un `.light` → crea `.light.xml` editable. Arrastra el `.light.xml` → vuelve a crear el `.light`. **El más práctico.** |
| **SonicLightEditor.exe** | Editor con ventana: dirección X/Y/Z y color RGB (direccional); posición, color y rango interior/exterior (omni) |
| **SonicLightReader.exe** | Arrastra un `.light` (o una carpeta) → muestra sus datos |
| SonicLightToForces.exe / SonicLightNormalizer.exe | Multiplican/dividen el color por 10 000 para pasar luces a/desde Sonic Forces. **No los necesitamos** |

## Ejemplo: teñir la luz del White Space

1. Extrae `archivos originales\bb2\Packed\pam000\pam000.ar.00` con [HedgeArcPack](02-hedgearcpack.md) (o usa la carpeta ya extraída).
2. Busca la luz que usa el hub: `pam000_Direct01.light` (es la que nombra `Terrain.stg.xml` en `<Light><DataName>`).
3. Arrástrala sobre **SonicLightXml.exe** → `pam000_Direct01.light.xml`.
4. Cambia el color (por ejemplo, morado/rojo para el hub "corrompido") y guarda.
5. Arrastra el `.light.xml` sobre SonicLightXml.exe → nuevo `.light`.
6. Empaquétalo en un append `mod\disk\bb2\Packed\pam000\+pam000.ar.00` **(sin probar: confirmar que el append funciona dentro de Packed)** o en el `pam000.ar` completo.

> El Unleashed Project hizo lo mismo de otra forma: puso una luz nueva `light.light` y cambió `<DataName>` en `Terrain.stg.xml`.

Si cambias mucho la luz, la GI horneada puede no coincidir; ver [HedgeGI](07-hedgegi.md).
