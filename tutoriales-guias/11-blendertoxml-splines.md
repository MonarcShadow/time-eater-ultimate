# BlenderToXML (exportador de splines, zatsick160)

**Qué es:** script que convierte curvas de Blender en el XML de caminos (`.path.xml`) del juego: rieles para grindar, caminos de las secciones 2D, carriles de quickstep, etc.

**Ruta:** `herramientas\blender-scripts\BlenderToXML.py` (licencia GPL-3). **No se usa directamente**: lo llama el botón *Exportar splines* de Time Eater Tools.

## Pasos

1. En Blender crea una curva y conviértela a tipo **Poly** (el script solo acepta *Poly spline*).
2. Ponle el nombre con el **sufijo** del tipo de camino:

| Sufijo | Tipo |
|---|---|
| `@SV` | *Side View*: camino de una sección 2D |
| `@GR` | *Grind Rail*: riel para grindar (no necesita colisión) |
| `@QS` | *Quickstep*: necesita el modo "Forward" y una entrada en `Stage.stg.xml` |
| `@DP` | *Dash Path*: Sonic sigue la curva a alta velocidad sin salirse |

Ejemplo: `Riel01@GR`. No puede haber dos curvas con el mismo nombre.

En SonicGLvl hay que colocar **Changers** tocando la curva (Forward para quickstep, 3D, 2D, Dash para `@DP`). Si un changer no funciona, gíralo 180°.

3. Selecciona las curvas → panel **Time Eater** → *Exportar splines* → elige el `.path.xml`.
4. Copia el XML dentro del `#<id>.ar.00` del escenario (con [HedgeArcPack](02-hedgearcpack.md)) y decláralo en `Stage.stg.xml`:
   ```xml
   <Path>
     <Container>nombre_del_path</Container>
     <IsAutoLoad>true</IsAutoLoad>
   </Path>
   ```
   Los caminos guía (2D) se registran con `<Guide><Name>…</Name><ID>…</ID></Guide>` dentro de ese `<Path>`.

El script invierte Y y la intercambia con Z (Blender usa Z arriba; el juego, Y). No hace falta rotar nada a mano.

Más detalle: bóveda → *splines*.
