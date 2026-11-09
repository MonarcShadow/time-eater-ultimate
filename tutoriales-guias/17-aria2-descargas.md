# aria2 y scripts de descarga

**Qué es:** gestor de descargas portable (aria2 1.37.0) para archivos grandes del proyecto (mods de referencia, recursos). Reanuda descargas cortadas y sigue descargando aunque cierres la terminal. Tu Free Download Manager queda aparte, solo para ti.

**Ruta:** `herramientas\aria2\…\aria2c.exe` — se usa a través de los scripts:

## Descargar

```powershell
powershell -ExecutionPolicy Bypass -File scripts\descargar.ps1 -Url "<enlace>"
powershell -ExecutionPolicy Bypass -File scripts\descargar.ps1 -Url "<enlace>" -Nombre "archivo.zip"
```

- Guarda en `descargas\` (fuera de git). Después mueve el archivo a su sitio (p. ej. `archivos originales\referencias\…`).
- Enlaces de **Google Drive** (`drive.google.com/file/d/…`): se convierten solos al enlace directo, incluso los que muestran el aviso de "no se pudo analizar en busca de virus".
- 8 conexiones en paralelo y reintentos infinitos.
- Si se corta (apagaste el PC, sin internet), **vuelve a ejecutar el mismo comando**: continúa donde quedó.

## Ver el estado

```powershell
powershell -ExecutionPolicy Bypass -File scripts\estado_descargas.ps1
```

Muestra cada descarga con su progreso, `TERMINADA -> ruta` o `ERROR`. Los registros están en `descargas\.logs\`.

## Uso directo de aria2 (avanzado)

```powershell
herramientas\aria2\aria2-1.37.0-win-64bit-build1\aria2-1.37.0-win-64bit-build1\aria2c.exe -c -x8 -s8 --dir=descargas "<enlace>"
```
