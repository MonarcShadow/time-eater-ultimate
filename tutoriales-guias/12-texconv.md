# texconv y texdiag (Microsoft DirectXTex)

**Qué es:** convierten texturas entre PNG y **DDS**, el formato que usa el juego. `texdiag` muestra información de un DDS (formato, tamaño, mipmaps).

**Ruta:** `herramientas\texconv\texconv.exe` y `herramientas\texconv\texdiag.exe` (línea de comandos)

## 1. Ver qué formato tiene una textura original

```powershell
herramientas\texconv\texdiag.exe info "ruta\pam_etc_km1_base01_dif.dds"
```
Fíjate en `format` (p. ej. `BC1_UNORM` = DXT1) y `mipLevels`. **Respeta el mismo formato y tamaño** al reemplazarla.

## 2. DDS → PNG (para editar)

```powershell
herramientas\texconv\texconv.exe -ft png -o "trabajo\png" "ruta\textura.dds"
```

Edita el PNG en el programa que prefieras (GIMP, Paint.NET, Krita…).

## 3. PNG → DDS (para el juego)

```powershell
# DXT1 (sin transparencia), con todos los mipmaps
herramientas\texconv\texconv.exe -f BC1_UNORM -m 0 -ft dds -y -o "trabajo\dds" "trabajo\png\textura.png"

# DXT5 (con transparencia)
herramientas\texconv\texconv.exe -f BC3_UNORM -m 0 -ft dds -y -o "trabajo\dds" "trabajo\png\textura.png"
```

| Opción | Significado |
|---|---|
| `-f` | Formato: `BC1_UNORM` = DXT1, `BC3_UNORM` = DXT5, `R8G8B8A8_UNORM` = sin comprimir |
| `-m 0` | Generar todos los mipmaps (`-m 1` = ninguno) |
| `-y` | Sobrescribir sin preguntar |
| `-o` | Carpeta de salida (**debe existir**; si no, falla con "no puede encontrar la ruta") |
| `-w 256 -h 256` | Cambiar tamaño (usa potencias de 2) |

## Ejemplo del proyecto: White Space "corrompido"

La textura base del hub es `pam_etc_km1_base01_dif.dds` (256 × 256, `BC1_UNORM` = DXT1, 9 mipmaps; comprobado con texdiag, y la ida y vuelta PNG → DDS con estos comandos funciona). Pasarla a PNG, recolorearla, volver a DDS con `BC1_UNORM -m 0` y empaquetarla en `mod\disk\bb2\+pam000.ar.00` (append, ver [HedgeArcPack](02-hedgearcpack.md)).
