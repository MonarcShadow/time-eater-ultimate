# modelfbx y terrain2fbx (conversores inversos)

Sirven para **sacar modelos del juego a FBX** y abrirlos en Blender como referencia (por ejemplo, para copiar la escala o la forma de algo del White Space).

> Alternativa más cómoda: el addon **HEIO** de Blender importa `.model` y `.terrain-model` directamente (ver [10-blender.md](10-blender.md)).

## modelfbx

**Ruta:** `herramientas\libgens-sonicglvl\libgens-sonicglvl\bin\modelfbx.exe` (y `modelfbx_2012.exe`, versión con FBX 2012)

Convierte `.model` (con esqueleto `.skl.hkx` y animación `.anm.hkx` opcionales) a FBX:

```powershell
modelfbx.exe modelo.model [esqueleto.skl.hkx] [animacion.anm.hkx] salida.fbx
```

Ejemplo incluido (`modelfbx-convert-example.bat`): convierte todas las animaciones de Sonic:
```bat
for %%f in (Sonic/*.anm.hkx) do modelfbx Sonic/chr_Sonic_HD.model Sonic/chr_Sonic_HD.skl.hkx Sonic/%%f Sonic/%%f.fbx
```

## terrain2fbx

**Ruta:** `herramientas\SkythTools-Common\terrain2fbx.exe` (y `terrain2fbx-png.exe`, que además convierte las texturas a PNG)

Convierte piezas de terreno (`.terrain-model`) a FBX. Uso: arrastra el archivo (o la carpeta extraída del `.pfd` del escenario) sobre el exe **(sin probar)**.

Necesita Visual C++ 2010 x86; `PREPARAR_ENTORNO.bat` lo comprueba.
