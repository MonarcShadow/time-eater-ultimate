# Blender + HEIO + Time Eater Tools

**Qué es:** Blender (de Steam) es donde se modela el nivel, la colisión, los objetos y las splines. Está configurado **aislado** en `herramientas\blender-config`: tu Blender normal no cambia.

## Abrir

Doble clic en **`scripts\abrir_blender.bat`**.
Si lo abres desde Steam verás tu Blender normal, **sin** los addons del mod.

## Addons incluidos

### HEIO (Hedgehog Engine I/O) 1.0.8
Importa y exporta formatos del juego: `File > Import / Export` → opciones de Hedgehog Engine (`.model`, `.terrain-model`, materiales…).
Útil para **traer modelos del juego como referencia**. Para Generations la precisión de materiales está marcada como incompleta, así que el camino principal de exportación sigue siendo FBX → Hedgehog Converter / ModelConverter.

### Time Eater Tools (nuestro)
Barra lateral con **N** → pestaña **Time Eater**:

| Botón | Qué hace |
|---|---|
| Configurar escena | Unidades métricas, escala 1.0, metros |
| Añadir referencia de Sonic | Caja `REF_Sonic` de 0.5 × 0.5 × 1.0 m en la colección *Referencias* (no se exporta) |
| Corregir nombres con puntos | Cambia `.` por `_` en materiales e imágenes (`Material.001` → `Material_001`) |
| Exportar FBX (Hedgehog/Havok) | FBX de lo seleccionado con los ajustes que piden los conversores |
| Exportar splines (path.xml) | Las curvas *Poly* seleccionadas a `.path.xml` (ver [11-blendertoxml-splines.md](11-blendertoxml-splines.md)) |

La sección **Revisión** del panel avisa si la escena no está en metros / escala 1.0, si hay materiales con punto o curvas que no son *Poly*; si todo está bien muestra *"Sin problemas detectados"*.

## Flujo recomendado

1. Abrir con `abrir_blender.bat` → *Configurar escena* → *Añadir referencia Sonic*.
2. Modelar el nivel visual en una colección y la colisión (simplificada, con `@TAG` en los nombres) en otra.
3. *Corregir nombres*.
4. Seleccionar lo visual → *Exportar FBX* → [Hedgehog Converter](04-hedgehog-converter.md).
5. Seleccionar la colisión → *Exportar FBX* → [Havok Converter](05-havok-converter.md).
6. Curvas → *Exportar splines*.

## Si algo falla

Reconfigura con `scripts\configurar_blender.ps1` (o `PREPARAR_ENTORNO.bat`): reinstala HEIO y Time Eater Tools.
