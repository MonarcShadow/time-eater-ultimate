# PackCpk (SkythTools)

**Qué es:** extrae y empaqueta los archivos `.cpk` del juego (`disk\bb.cpk`, `bb2.cpk`, `bb3.cpk`), que contienen casi todos los datos de Sonic Generations.

**Ruta:** `herramientas\SkythTools-Common\PackCpk.exe`

## Cuándo se usa

Solo para obtener la copia limpia del juego en `archivos originales\`. **Ya está hecho** y `PREPARAR_ENTORNO.bat` lo repite solo si falta. Los mods de HMM **no** necesitan reempaquetar el CPK: los archivos sueltos en `mod\disk\bb\...` reemplazan a los del CPK.

## Uso

PackCpk recibe **un solo argumento**:

- un archivo `.cpk` → lo extrae en una carpeta con el mismo nombre, **junto al .cpk**;
- una carpeta → la empaqueta en un `.cpk`.

La forma más simple: **arrastra el `.cpk` sobre `PackCpk.exe`**.

> ⚠️ Como extrae junto al `.cpk`, no lo arrastres desde la carpeta del juego (llenarías la instalación de Steam). Copia o crea un enlace duro del `.cpk` en otra carpeta y arrástralo desde ahí (así lo hace `scripts\preparar_entorno.ps1`).

> ⚠️ Necesita una consola propia. Desde PowerShell lánzalo con `Start-Process`; si no, falla con *"Controlador no válido"*.

```powershell
Start-Process herramientas\SkythTools-Common\PackCpk.exe -ArgumentList '"D:\ruta\bb2.cpk"' -Wait
```

## Qué hay en cada CPK

| CPK | Contenido principal |
|---|---|
| `bb` | Escenarios de la Era 1-2 (ghz, cpz, ssz…), `#SystemCommon` (definiciones de objetos) |
| `bb2` | Hub `pam000` (White Space), resto de escenarios, interfaz por idioma |
| `bb3` | Datos varios (66 MB) |

Índice completo de archivos: bóveda → *formatos-de-archivo* y los *SCHG File Index* en `raw/niveles`.
