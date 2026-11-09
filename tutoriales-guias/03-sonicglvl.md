# SonicGLvl (libgens-sonicglvl)

**Qué es:** el editor de niveles. Muestra el escenario en 3D y permite colocar, mover y editar los **objetos** (set data): anillos, resortes, enemigos, cámaras, el punto de inicio y, en el hub, los portales (`StageGate`).

**Ruta:** `herramientas\libgens-sonicglvl\libgens-sonicglvl\bin\SonicGLvl.exe`

> Es la rama 0.9 (nightly). Su autor la describe como experimental: sirve bien para **editar objetos**; el terreno, la colisión y la GI se hacen con las otras herramientas.

## Primer uso (sin probar en detalle)

1. Ábrelo y configura la ruta del juego / del escenario cuando lo pida.
2. Abre un escenario extraído (por ejemplo una copia de `#ghz200` + `Packed\ghz200`). SonicGLvl guarda una caché en `libgens-sonicglvl\cache\`.
3. Navega con el ratón por la vista 3D; selecciona objetos con clic.

## Tareas típicas

### Empezar un nivel propio desde un escenario existente (guía de HedgeDocs)
1. Abre el escenario que vas a reemplazar (p. ej. `ghz200`).
2. `Ctrl+A` y `Supr`: borra todos los objetos.
3. Coloca un objeto **SonicSpawn**, pon `Active = true`.
4. `File > Save Stage Data`.

### Editar un objeto
Selecciónalo y cambia sus propiedades en el panel. Las más comunes:

| Propiedad | Efecto |
|---|---|
| `Range` | Distancia a la que el objeto existe/se dibuja. Si un objeto interactúa con otro fuera de rango, el juego se cuelga |
| `SetObjectID` | ID para enlazar objetos; no lo cambies a mano |
| `IsCastShadow` | Proyecta sombra |

Lista de objetos y propiedades: bóveda → *objetos-set-data*.

### Portales del hub (pam000)
- `StageGate` = caja invisible con `StageID` (0, 2, … 16). Al entrar abre el menú de ese escenario.
- `StageName` = cartel con anillos rojos, mismo `StageID`.
- Para enlazar nuestro nivel basta con reemplazar el escenario de ese ID y, si se quiere, mover ambos objetos.

### Ver la colisión
Menú **View** → mostrar la malla de colisión, para comprobar el `.phy.hkx` de Havok Converter.

## Archivos que modifica

`setdata_*.set.xml` dentro del `#<id>.ar.00` (base, design, effect, sound…). Si prefieres, puedes extraer el `#` con HedgeArcPack y editar esos XML a mano: son texto.

## Problemas conocidos

- Si se cierra al cargar, borra la caché del escenario en `libgens-sonicglvl\cache\`.
- Necesita DirectX 9 (`d3dx9_43.dll`); `PREPARAR_ENTORNO.bat` lo comprueba.
