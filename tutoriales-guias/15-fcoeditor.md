# fcoEditor (brianuuu)

**Qué es:** editor de los archivos `.fco` de **textos y subtítulos** de Sonic Generations (diálogos de Omochao, mensajes, nombres en pantalla). También edita los subtítulos de escenas `.cap` y genera texturas de fuente para caracteres nuevos.

**Ruta:** `herramientas\fcoEditor\fcoEditor.v3.0\fcoEditor\fcoEditor.exe` (programa con ventana)
Manual original: `READ ME (fcoEditor).txt` en la misma carpeta.

## Uso básico

1. Abre el `.fco` (o arrástralo sobre el exe). Los `.fco` están en las carpetas de idioma, p. ej. `archivos originales\bb2\Languages\Spanish\` dentro de los `.ar` (extráelos con [HedgeArcPack](02-hedgearcpack.md)).
2. Usa **Find** para buscar un texto (distingue mayúsculas) o haz doble clic en un subtítulo.
3. Edita el texto y pulsa **Apply Changes** (si no, no se guarda el cambio).
4. `File > Save` / `Save As`.
5. Reempaqueta el `.ar` del idioma y ponlo en `mod\disk\bb2\Languages\<idioma>\`.

## Detalles

- Botones especiales: escríbelos entre dos barras invertidas, `\A\`, `\Start\`, `\LT\`… (lista en `fcoDatabase.txt`).
- Los caracteres soportados están en `fcoDatabase.txt`; si usas uno que no existe, la barra de estado avisa. Para añadirlo: *Font Texture Generator*.
- ⚠️ Borrar o mover grupos/subtítulos cambia los `SerifuID` (los usa Omochao). Mejor editar el texto existente que reordenar.
- Edita **todos los idiomas** que quieras soportar: cada uno tiene su propio `.fco`.
