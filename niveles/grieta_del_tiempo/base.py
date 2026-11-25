# Herramientas comunes del generador de "Grieta del Tiempo": geometría (Malla), cursor del recorrido, carreteras,
# objetos del set data, plantillas de enemigos, checkpoints, cámara de planeo y estimación del tiempo de juego.
# Lo usan generar.py y cada sección (secciones/sNN_*.py) con "from base import *".
#
# Ejes: Blender X/Y = plano horizontal, Z = arriba. Juego: (x, y, z) = (bx, bz, -by).
# Rumbo θ (Blender, desde +X hacia +Y). Yaw del juego φ = 90° + θ (comprobado: yaw 90 = avanzar hacia +X).
import json
import math
import os
import re
import sys

import bpy

_COMUN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "comun")
if _COMUN not in sys.path:
    sys.path.insert(0, _COMUN)
from plantillas_objetos import PLANTILLAS  # noqa: E402

# ----------------------------------------------------------------------------------------------
# Ajustes editables a mano: ajustes.conf (líneas "NOMBRE = valor", comentarios con #)
# ----------------------------------------------------------------------------------------------
AJUSTES_POR_DEFECTO = {
    "HOMING_ALCANCE_3D": 32.0,     # m; el juego trae 21.1
    "HOMING_ALCANCE_2D": 20.0,     # m; el juego trae 13.5
    "GIRO_CAMARA_RELOJ": 180.0,    # grados; planeo de la sección 11 ("casi ideal" en la prueba de la 0.7.2)
    "GIRO_CAMARA_PLANEO": 135.0,   # grados; planeo final (sección 12)
    "MARGEN_CAMBIO_2D": 40.0,      # m libres de huecos y enemigos a cada lado de un cambio 3D<->2D (~2 s corriendo)
    "INICIO_SECCION": 0.0,         # 0 = salida original; N = checkpoint de la sección N (solo para pruebas)
    "RAMPA_TEJADO_ALTO": 1.2,      # m; cuña en el borde de los tejados de la sección 9
    "RAMPA_TEJADO_ANGULO": 25.0,   # grados de esa cuña (a 45° se salía demasiado alto, 0.7.4)
    "GIMMICKS_NUEVOS": 1.0,        # 1 = JumpPole, Pulley, WallJumpBlock e IronPole; 0 = sin ellos
    "BARRA_GIRO_LARGO": 6.0,       # m; PoleLen de la IronPole3D de la sección 3
    "BARRA_GIRO_ALTO": 3.0,        # m sobre la pista
    "BARRA_GIRO_LADO": 3.0,        # m a la izquierda del eje donde va su extremo (la barra crece hacia la derecha)
    "CAMARA_2D_DISTANCIA": 17.0,   # m; cámara de los tramos 2D (los originales usan 15-20)
    "CAMARA_2D_PITCH": 10.0,       # grados mirando hacia abajo
    "CAMARA_2D_ALTURA": 1.5,       # m por encima de Sonic (TargetOffset_Up)
    "CAMARA_2D_GIRO": 0.0,         # grados de corrección del Yaw si la cámara no queda de lado
    "LOOP_RADIO": 30.0,            # m; loop de la sección 1 (10 hasta la 0.7.10, 15 hasta la 0.7.15)
    "LOOP_MURO_ALTO": 12.0,        # m de la pared invisible entre la entrada y la salida del loop (máx. 0,4 × radio)
    # cámara de los loops = primer loop de ghz200 (ObjCameraPan 122609 + ChangeVolumeCamera 122608)
    "LOOP_CAMARA_ADELANTO": 37.0,  # m de la cámara antes del centro del volumen
    "LOOP_CAMARA_ALTO": 1.0,       # m sobre el suelo de la cámara y del centro del volumen
    "LOOP_CAMARA_DISTANCIA": 10.0,
    "LOOP_CAMARA_FOVY": 45.0,
    "LOOP_CAMARA_VOL_LARGO": 50.0,
    "LOOP_CAMARA_VOL_ANCHO": 8.0,
    "LOOP_CAMARA_VOL_ALTO": 14.0,
    "LOOP_CAMARA_PRIORIDAD": 1.0,
    "LOOP_CAMARA_EASE": 0.6,
    "RIEL_SECRETO_ANGULO": 20.0,   # grados a la izquierda del frente donde empieza el riel secreto (0.7.10: 45)
    "RIEL_SECRETO_ALTO": 14.0,     # m sobre la explanada del inicio del riel secreto (0.7.10: 9,5)
    "RIEL_CAMARA_PITCH": 85.0,     # grados: cámara cenital del riel secreto (euc200 usa 85-89 en el riel de la torre)
    "RIEL_CAMARA_DISTANCIA": 6.0,  # m (euc200: 4-5)
    "LIGHT_DASH_SEPARACION": 1.1,  # m entre anillos de light dash (pla204: 1,13; con 1,5-2 m Sonic no seguía las curvas)
    "LIGHT_DASH_GIRO_MAX": 6.0,    # grados máximos de giro entre dos anillos seguidos (pla204: 5,9)
    "LIGHT_DASH_HUECO": 50.0,      # m del hueco del desafío aéreo de la sección 9 (con 24 se cruzaba con air boost)
    "LIGHT_DASH_REBOTE": 4.0,      # m del primer anillo de la sección 9 sobre el tercer Spinner (rebote del homing)
    "LIGHT_DASH_ESPIRAL_RADIO": 4.0,  # m de radio de la espiral de light dash de la sección 9 (0.7.17)
}


def leer_ajustes(ruta=os.path.join(os.path.dirname(os.path.abspath(__file__)), "ajustes.conf")):
    ajustes = dict(AJUSTES_POR_DEFECTO)
    leidos = set()
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as f:
            for n, linea in enumerate(f, 1):
                linea = linea.split("#", 1)[0].strip()
                if not linea:
                    continue
                if "=" not in linea:
                    print(f"TEU_AVISO ajustes.conf línea {n}: falta '=' ({linea})")
                    continue
                clave, valor = (p.strip() for p in linea.split("=", 1))
                try:
                    ajustes[clave] = float(valor)
                    leidos.add(clave)
                except ValueError:
                    print(f"TEU_AVISO ajustes.conf línea {n}: '{valor}' no es un número")
    for clave in AJUSTES_POR_DEFECTO:
        if clave not in leidos:
            print(f"TEU_AVISO ajustes.conf no define {clave}: se usa {AJUSTES_POR_DEFECTO[clave]:g}")
    return ajustes


AJUSTES = leer_ajustes()

# ----------------------------------------------------------------------------------------------
# Materiales: gris para el recorrido, un color por zona para las "intrusiones", costura morada y blanco
# ----------------------------------------------------------------------------------------------
COLORES = {
    "gris":    ((0.42, 0.42, 0.45), (0.30, 0.30, 0.33)),
    "ghz":     ((0.25, 0.70, 0.25), (0.55, 0.35, 0.15)),   # Green Hill: verde / tierra
    "cpz":     ((0.75, 0.20, 0.70), (0.25, 0.30, 0.55)),   # Chemical Plant: Mega Mack / metal
    "ssz":     ((0.90, 0.90, 0.85), (0.40, 0.75, 0.75)),   # Sky Sanctuary: mármol / turquesa
    "sph":     ((0.10, 0.12, 0.35), (0.85, 0.75, 0.20)),   # Speed Highway: noche / luces
    "cte":     ((0.85, 0.45, 0.15), (0.30, 0.30, 0.30)),   # City Escape: naranja / asfalto
    "ssh":     ((0.20, 0.55, 0.90), (0.85, 0.80, 0.60)),   # Seaside Hill: mar / arena
    "csc":     ((0.85, 0.15, 0.05), (0.20, 0.10, 0.08)),   # Crisis City: lava / ceniza
    "euc":     ((0.55, 0.35, 0.20), (0.80, 0.65, 0.30)),   # Rooftop Run: tejas / oro
    "pla":     ((0.60, 0.90, 0.10), (0.35, 0.35, 0.40)),   # Planet Wisp: lima / fábrica
    "costura": ((0.55, 0.05, 0.85), (0.95, 0.40, 1.00)),   # tejido del Time Eater
    "blanco":  ((0.97, 0.97, 0.97), (0.85, 0.85, 0.88)),   # White Space / color comido
}
# 0.8.0: texturas originales del juego (texturas.json; las extrae scripts/extraer_texturas.ps1 a TEU_TEXTURAS). Cada
# material con textura tiene tres variantes: suelo (caras horizontales), "_pared" (caras verticales) y "_grieta" (suelo
# con grietas moradas propias, en GRIETA_PORCENTAJE % de las caras de suelo). Sin los originales, cuadriculados propios.
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "texturas.json"), encoding="utf-8") as _f:
    TEXTURAS = json.load(_f)["materiales"]
GRIETA_PORCENTAJE = 18
ORDEN_MATS = list(COLORES) + [f"{m}_{v}" for m in TEXTURAS for v in ("pared", "grieta")]
MATS = {}
ZONAS = ("ghz", "cpz", "ssz", "sph", "cte", "ssh", "csc", "euc", "pla")


def _cuadriculado(ca, cb, n=128):
    import numpy as np
    y, x = np.mgrid[0:n, 0:n]
    par = (((x // (n // 8)) + (y // (n // 8))) % 2).astype(bool)
    pix = np.ones((n, n, 4), dtype=np.float32)
    pix[..., :3] = np.where(par[..., None], np.array(ca, dtype=np.float32), np.array(cb, dtype=np.float32))
    return pix


def _grietas(pix, semilla):
    """Grietas moradas propias sobre una textura (0.8.0): ramas que avanzan quebradas, con un núcleo morado brillante y
    un halo que tiñe el fondo (como el tejido del Time Eater). Se repiten sin cortes (todo en módulo n)."""
    import numpy as np
    rng = np.random.default_rng(semilla)
    n = pix.shape[0]
    esc = n / 512
    halo = np.zeros((n, n), dtype=np.float32)
    nucleo = np.zeros((n, n), dtype=np.float32)
    ramas = [(float(rng.uniform(0, n)), float(rng.uniform(0, n)), float(rng.uniform(0, 2 * math.pi)), 3.0 * esc + 1)
             for _ in range(2)]
    total = len(ramas)
    while ramas:
        x, y, ang, grosor = ramas.pop()
        for _ in range(int(n * 0.35)):
            ang += float(rng.normal(0, 0.3))
            x, y = (x + math.cos(ang) * 2) % n, (y + math.sin(ang) * 2) % n
            r = int(grosor * 3)
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    d = math.hypot(dx, dy)
                    yy, xx = int(y + dy) % n, int(x + dx) % n
                    halo[yy, xx] = max(halo[yy, xx], 1 - d / (r + 0.5))
                    if d <= grosor * 0.6:
                        nucleo[yy, xx] = 1.0
            if grosor > 1.2 and total < 7 and rng.random() < 0.02:
                total += 1
                ramas.append((x, y, ang + float(rng.choice((-1, 1))) * float(rng.uniform(0.6, 1.2)), grosor * 0.65))
            if rng.random() < 0.004:
                break
    morado = np.array((0.55, 0.05, 0.85), dtype=np.float32)
    brillo = np.array((0.95, 0.55, 1.0), dtype=np.float32)
    out = pix.copy()
    out[..., :3] = out[..., :3] * (1 - 0.65 * halo[..., None]) + morado * 0.65 * halo[..., None]
    out[..., :3] = np.where(nucleo[..., None] > 0, brillo, out[..., :3])
    return out


def crear_materiales(salida):
    import numpy as np
    carpeta_tex = os.environ.get("TEU_TEXTURAS", "")
    usadas = 0
    for nombre in ORDEN_MATS:
        base_m, _, variante = nombre.partition("_")
        if base_m not in COLORES or nombre in COLORES:
            base_m, variante = nombre, ""
        pix = None
        cfg = TEXTURAS.get(base_m)
        if cfg and carpeta_tex:
            ref = cfg["pared" if variante == "pared" else "suelo"].split("/")[1]
            ruta = os.path.join(carpeta_tex, ref + ".png")
            if os.path.exists(ruta):
                src = bpy.data.images.load(ruta)
                pix = np.array(src.pixels[:], dtype=np.float32).reshape(src.size[1], src.size[0], 4)
                pix[..., 3] = 1.0
                bpy.data.images.remove(src)
                usadas += 1
        if pix is None:
            ca, cb = COLORES[base_m]
            if variante == "pared":
                ca, cb = tuple(c * 0.8 for c in ca), tuple(c * 0.8 for c in cb)
            pix = _cuadriculado(ca, cb)
        if variante == "grieta":
            pix = _grietas(pix, sum(map(ord, base_m)))
        alto, ancho_px = pix.shape[:2]
        img = bpy.data.images.new(f"teu_{nombre}_dif", ancho_px, alto)
        img.pixels = pix.ravel()
        img.filepath_raw = os.path.join(salida, f"teu_{nombre}_dif.png")
        img.file_format = "PNG"
        img.save()
        m = bpy.data.materials.new(f"teu_{nombre}")
        if m.node_tree is None:
            m.use_nodes = True
        t = m.node_tree.nodes.new("ShaderNodeTexImage")
        t.image = img
        m.node_tree.links.new(t.outputs["Color"], m.node_tree.nodes.get("Principled BSDF").inputs["Base Color"])
        MATS[nombre] = m


# ----------------------------------------------------------------------------------------------
# Constructor de geometría: una sola malla con índice de material por cara
# ----------------------------------------------------------------------------------------------
class Malla:
    def __init__(self):
        self.v, self.f, self.mat, self.uv = [], [], [], []

    def cara(self, pts, mat, uvs=None, hacia=None):
        """Cara de 3 o 4 vértices. 'hacia' = punto hacia el que debe mirar la normal (invierte el orden si hace falta)."""
        pts = list(pts)
        if hacia is not None:
            ax, ay, az = (pts[1][k] - pts[0][k] for k in range(3))
            bx, by, bz = (pts[2][k] - pts[0][k] for k in range(3))
            n = (ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx)
            if sum(n[k] * (hacia[k] - pts[0][k]) for k in range(3)) < 0:
                pts.reverse()
        i = len(self.v)
        self.v += pts
        self.f.append(tuple(range(i, i + len(pts))))
        mat, uvs = self._material_y_uv(pts, mat, uvs)
        self.mat.append(ORDEN_MATS.index(mat))
        self.uv.append(uvs)

    @staticmethod
    def _material_y_uv(pts, mat, uvs):
        """0.8.0: con textura original, las caras verticales usan la variante "_pared" y algunas de suelo la "_grieta"
        (elegidas por la posición: siempre las mismas). UV: las dadas (en unidades de 4 m) se escalan a los metros por
        repetición de la textura; sin UV, proyección plana en el plano de la cara (horizontal a lo largo y vertical
        hacia arriba en las paredes), desplazada cerca de 0 (los UV de media precisión pierden detalle lejos de 0)."""
        nx = ny = nz = 0.0
        for a, b in zip(pts, pts[1:] + pts[:1]):           # normal de Newell
            nx += (a[1] - b[1]) * (a[2] + b[2])
            ny += (a[2] - b[2]) * (a[0] + b[0])
            nz += (a[0] - b[0]) * (a[1] + b[1])
        ln = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
        nx, ny, nz = nx / ln, ny / ln, nz / ln
        cfg = TEXTURAS.get(mat)
        metros = cfg["metros"] if cfg else 4.0
        if cfg:
            if abs(nz) < 0.55:
                mat = mat + "_pared"
            else:
                c = [sum(p[k] for p in pts) / len(pts) for k in range(3)]
                h = ((int(math.floor(c[0] / 4)) * 73856093) ^ (int(math.floor(c[1] / 4)) * 19349663)
                     ^ (int(math.floor(c[2])) * 83492791))
                if h % 100 < GRIETA_PORCENTAJE:
                    mat = mat + "_grieta"
        if uvs:
            f = 4.0 / metros
            return mat, [(u * f, v * f) for u, v in uvs]
        if abs(nz) < 0.9:                                   # e1 horizontal dentro del plano, e2 hacia arriba
            e1 = (-ny, nx, 0.0)
        else:
            e1 = tuple(pts[1][k] - pts[0][k] for k in range(3))
        l1 = math.sqrt(sum(c * c for c in e1)) or 1.0
        e1 = tuple(c / l1 for c in e1)
        e2 = (ny * e1[2] - nz * e1[1], nz * e1[0] - nx * e1[2], nx * e1[1] - ny * e1[0])
        if abs(nz) < 0.9 and e2[2] < 0:
            e2 = tuple(-c for c in e2)
        uv = [(sum(p[k] * e1[k] for k in range(3)) / metros, sum(p[k] * e2[k] for k in range(3)) / metros) for p in pts]
        u0, v0 = math.floor(min(u for u, _ in uv)), math.floor(min(v for _, v in uv))
        return mat, [(u - u0, v - v0) for u, v in uv]

    def quad(self, a, b, c, d, mat, uvs=None):
        self.cara([a, b, c, d], mat, uvs)

    def prisma(self, p0, p1, radio, mat, n=10, tapas=True):
        """Cilindro de n lados entre dos puntos cualesquiera (tuberías, columnas, agujas)."""
        d = [p1[k] - p0[k] for k in range(3)]
        largo = math.sqrt(sum(c * c for c in d)) or 1.0
        d = [c / largo for c in d]
        ref = (0.0, 0.0, 1.0) if abs(d[2]) < 0.9 else (1.0, 0.0, 0.0)
        u = [d[1] * ref[2] - d[2] * ref[1], d[2] * ref[0] - d[0] * ref[2], d[0] * ref[1] - d[1] * ref[0]]
        lu = math.sqrt(sum(c * c for c in u))
        u = [c / lu for c in u]
        w = [d[1] * u[2] - d[2] * u[1], d[2] * u[0] - d[0] * u[2], d[0] * u[1] - d[1] * u[0]]

        def anillo(p):
            return [tuple(p[k] + radio * (math.cos(2 * math.pi * j / n) * u[k] + math.sin(2 * math.pi * j / n) * w[k])
                          for k in range(3)) for j in range(n)]
        a, b = anillo(p0), anillo(p1)
        vueltas = max(1.0, round(2 * math.pi * radio / 4))
        for j in range(n):
            k = (j + 1) % n
            medio = tuple((a[j][m] + a[k][m] + b[j][m] + b[k][m]) / 4 for m in range(3))
            eje = tuple((p0[m] + p1[m]) / 2 for m in range(3))
            fuera = tuple(2 * medio[m] - eje[m] for m in range(3))
            u0, u1 = vueltas * j / n, vueltas * (j + 1) / n
            self.cara([a[j], a[k], b[k], b[j]], mat, [(u0, 0), (u1, 0), (u1, largo / 4), (u0, largo / 4)], hacia=fuera)
        if tapas:
            for anillo_, centro, otro in ((a, p0, p1), (b, p1, p0)):
                fuera = tuple(2 * centro[m] - otro[m] for m in range(3))
                for j in range(n):
                    self.cara([tuple(centro), anillo_[j], anillo_[(j + 1) % n]], mat, [(0.5, 0.5), (0, 0), (1, 0)], hacia=fuera)

    def disco(self, centro, radio, normal, mat, n=20, grosor=0.6):
        """Disco (prisma corto) con el eje en la dirección 'normal'."""
        ln = math.sqrt(sum(c * c for c in normal))
        h = [c / ln * grosor / 2 for c in normal]
        self.prisma(tuple(centro[k] - h[k] for k in range(3)), tuple(centro[k] + h[k] for k in range(3)), radio, mat, n)

    def caja(self, centro, tam, rumbo, mat):
        """Caja orientada: centro (x,y,z de la base), tam (largo, ancho, alto), rumbo en radianes."""
        cx, cy, cz = centro
        L, W, H = tam
        c, s = math.cos(rumbo), math.sin(rumbo)

        def p(u, v, w):
            return (cx + u * c - v * s, cy + u * s + v * c, cz + w)
        P = [p(u, v, w) for w in (0, H) for v in (-W / 2, W / 2) for u in (-L / 2, L / 2)]
        # índices: 0..3 abajo (u-,v-),(u+,v-),(u-,v+),(u+,v+); 4..7 arriba
        caras = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (1, 3, 7, 5), (3, 2, 6, 7), (2, 0, 4, 6)]
        for cara in caras:
            pts = [P[k] for k in cara]
            self.quad(*pts, mat)                     # UV planas por cara (0.8.0)

    def objeto(self, nombre, col):
        me = bpy.data.meshes.new(nombre)
        me.from_pydata(self.v, [], self.f)
        for m in ORDEN_MATS:
            me.materials.append(MATS[m])
        for poly, mi in zip(me.polygons, self.mat):
            poly.material_index = mi
        uvl = me.uv_layers.new(name="UVMap")
        for poly, uvs in zip(me.polygons, self.uv):
            for li, uv in zip(poly.loop_indices, uvs):
                uvl.data[li].uv = uv
        me.validate()
        me.update()
        ob = bpy.data.objects.new(nombre, me)
        col.objects.link(ob)
        return ob


SOLIDO = Malla()      # recorrido + decoración sólida (visual y colisión)
SOLO_VISUAL = Malla()  # rieles de grind, costuras, ventanas, agua (sin colisión)
MUERTE = Malla()       # suelos de muerte bajo los huecos (solo colisión, tag DEAD)
DANO = Malla()         # zonas que hacen daño, p. ej. lava (solo colisión, tag DAMAGE)
INVISIBLE = Malla()    # paredes invisibles (solo colisión, tag ROCK; 0.7.16: muro en medio del loop)
ULTIMO_ANCHO = [12.0]  # ancho final de la última carretera (0.7.16: los tramos 2D toman ese ancho)
# Agua para correr encima con el boost (solo colisión). Copia el cuerpo sea02 de ssh200.phy.hkx (material 2 agua
# profunda + swa_col_player 10; tag AGUAHONDA, que construir_nivel.ps1 añade a los del HavokConverter.ini): con panel o
# boost se cruza (prueba de la 0.7.5). Descartadas: sea01 (material 12 + 5) mata aunque se vaya con boost (0.7.4);
# inside02 (material 14 + 23) no mata pero se atraviesa: es agua para nadar dentro (servirá para el tanque de CPZ).
AGUA = {"B": Malla()}
TAGS_AGUA = {"B": "AGUAHONDA"}
GUIAS = []             # (nombre, ID) de las splines guía (tirolinas): se declaran en Stage.stg.xml como <Guide>
OBJETOS = []           # (xml) set data
CURVAS = []            # (nombre, [[puntos riel 1], [puntos riel 2]?])
QUICKSTEPS = []        # nombres de splines @QS (se declaran en Stage.stg.xml como SingleForward)
# Para comprobar el margen alrededor de los cambios 3D<->2D (el homing se corta al cruzar uno, prueba de la 0.7.2).
# Puntos en Blender; sección en la que se colocaron.
CAMBIOS_2D = []        # (x, y, z, sección)
PUNTOS_ENEMIGO = []    # (x, y, z, sección, tipo)
TRAMOS_MUERTE = []     # ((x, y, z) inicio, (x, y, z) fin, sección): bordes de los huecos (a la altura del recorrido)
SID = [910000]
MIN_Z = [0.0]


def nuevo_id():
    SID[0] += 1
    return SID[0]


# ----------------------------------------------------------------------------------------------
# Recorrido: un "cursor" que avanza dejando carretera
# ----------------------------------------------------------------------------------------------
class Cursor:
    def __init__(self):
        self.x, self.y, self.z, self.th = 0.0, 0.0, 0.0, 0.0
        self.pend = 0.0          # pendiente del suelo en el punto actual (radianes, + = cuesta arriba)

    def frame(self, adelante=0.0, lado=0.0, arriba=0.0):
        c, s = math.cos(self.th), math.sin(self.th)
        return (self.x + adelante * c - lado * s, self.y + adelante * s + lado * c, self.z + arriba)

    def avanzar(self, d, dz=0.0):
        self.x += d * math.cos(self.th)
        self.y += d * math.sin(self.th)
        self.z += dz
        registrar_eje(d)


K = Cursor()


# ----------------------------------------------------------------------------------------------
# Secciones, tiempo estimado y control de solapes
# ----------------------------------------------------------------------------------------------
# Velocidades medias (m/s) por tipo de tramo. Calibradas para que la versión de 8 secciones (0.6.x, ~1,5 km)
# dé ~55 s, que es lo que tardó el usuario ("menos de 60 s"). Se recalibran con cada prueba.
VEL = {"rapido": 50.0, "3d": 35.0, "plataformas": 15.0, "2d": 12.0, "grind": 45.0}
RITMO = ["3d"]
SECCIONES = []          # [nombre, segundos, metros]
EJE = []                # (x, y, z, s_total, índice_sección) muestras del eje del recorrido
S_TOTAL = [0.0]
PM_ID = [0]
INICIOS_SECCION = []    # (punto Blender del checkpoint, rumbo) de cada sección, en orden


def registrar_eje(d):
    S_TOTAL[0] += abs(d)
    EJE.append((K.x, K.y, K.z, S_TOTAL[0], len(SECCIONES) - 1))


def ritmo(tipo):
    """Tipo de los tramos que siguen (para la estimación de tiempo): rapido, 3d, plataformas, 2d, grind."""
    RITMO[0] = tipo


def sumar_tiempo(segundos, metros=0.0):
    if SECCIONES:
        SECCIONES[-1][1] += segundos
        SECCIONES[-1][2] += metros


def seccion(nombre, checkpoint=True):
    """Empieza una sección: la anota para el informe de tiempo y pone un checkpoint (PointMarker) 6 m antes,
    sobre el final de la carretera anterior."""
    if SECCIONES and checkpoint:
        punto_control(-6)
    # salida de prueba (ajustes.conf: INICIO_SECCION); la de la sección 1 en la salida original (x 2), no detrás de la
    # pared del inicio (0.7.11)
    INICIOS_SECCION.append((K.frame(-6 if SECCIONES else 2, 0, 0.1), K.th))
    SECCIONES.append([nombre, 0.0, 0.0])
    ritmo("3d")


def informe_tiempo():
    total = 0.0
    for nombre, seg, metros in SECCIONES:
        total += seg
        print(f"TEU_TIEMPO {nombre}: {seg:.0f} s ({metros:.0f} m)")
    print(f"TEU_TIEMPO_TOTAL {total:.0f} s, {sum(s[2] for s in SECCIONES):.0f} m")
    if total < 300:
        print(f"TEU_AVISO tiempo estimado {total:.0f} s < 300 s")
    return total


def comprobar_solapes(dist_h=30.0, dist_v=22.0, separacion=150.0):
    """Avisa si el recorrido pasa cerca de sí mismo (dos puntos del eje a menos de dist_h en horizontal y dist_v en
    vertical, separados más de 'separacion' metros de recorrido)."""
    celdas = {}
    for p in EJE:
        celdas.setdefault((int(p[0] // dist_h), int(p[1] // dist_h)), []).append(p)
    avisos = set()
    for (cx, cy), pts in celdas.items():
        vecinos = [q for dx in (-1, 0, 1) for dy in (-1, 0, 1) for q in celdas.get((cx + dx, cy + dy), [])]
        for p in pts:
            for q in vecinos:
                if q[3] - p[3] > separacion and math.hypot(p[0] - q[0], p[1] - q[1]) < dist_h and abs(p[2] - q[2]) < dist_v:
                    avisos.add((SECCIONES[p[4]][0] if p[4] >= 0 else "?", SECCIONES[q[4]][0] if q[4] >= 0 else "?"))
    for a, b in sorted(avisos):
        print(f"TEU_AVISO solape: '{a}' pasa cerca de '{b}'")
    return len(avisos)


def seccion_actual():
    return SECCIONES[-1][0] if SECCIONES else "?"


def _dist_segmento(p, a, b):
    """Distancia horizontal de p al segmento a-b, y diferencia de altura con el punto más cercano."""
    ax, ay = b[0] - a[0], b[1] - a[1]
    l2 = ax * ax + ay * ay
    t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / l2))
    q = (a[0] + ax * t, a[1] + ay * t, a[2] + (b[2] - a[2]) * t)
    return math.hypot(p[0] - q[0], p[1] - q[1]), abs(p[2] - q[2])


def comprobar_margen_2d(dist_v=25.0):
    """Avisa de enemigos o huecos (suelos de muerte) a menos de MARGEN_CAMBIO_2D m en horizontal de un cambio
    3D<->2D: un homing attack que cruza el cambio de modo se cancela (prueba de la 0.7.2)."""
    margen = AJUSTES["MARGEN_CAMBIO_2D"] - 0.5      # tolerancia: el primer hueco de tramo_2d cae justo en el margen
    n = 0
    for cx, cy, cz, sec in CAMBIOS_2D:
        for ex, ey, ez, sec_e, tipo in PUNTOS_ENEMIGO:
            d = math.hypot(ex - cx, ey - cy)
            if d < margen and abs(ez - cz) < dist_v:
                print(f"TEU_AVISO margen 2D: {tipo} ({sec_e}) a {d:.0f} m de un cambio de modo ({sec})")
                n += 1
        for a, b, sec_m in TRAMOS_MUERTE:
            d, dz = _dist_segmento((cx, cy, cz), a, b)
            if d < margen and dz < dist_v:
                print(f"TEU_AVISO margen 2D: hueco ({sec_m}) a {d:.0f} m de un cambio de modo ({sec})")
                n += 1
    print(f"TEU_MARGEN_2D {len(CAMBIOS_2D)} cambios de modo, margen {margen:g} m, {n} avisos")
    return n


class Tramo:
    """Muestras (x, y, z, rumbo, s) del eje de un tramo de carretera, para colocar objetos sobre él."""

    def __init__(self, muestras):
        self.m = muestras
        self.largo = muestras[-1][4]

    def estado(self, s):
        s = max(0.0, min(self.largo, s))
        for a, b in zip(self.m, self.m[1:]):
            if a[4] <= s <= b[4]:
                t = (s - a[4]) / (b[4] - a[4]) if b[4] > a[4] else 0.0
                return tuple(a[i] + (b[i] - a[i]) * t for i in range(4))
        return self.m[-1][:4]

    def pendiente(self, s):
        """Ángulo de la pendiente en s (radianes, + = cuesta arriba)."""
        a, b = self.estado(max(0.0, s - 1.0)), self.estado(min(self.largo, s + 1.0))
        return math.atan2(b[2] - a[2], math.hypot(b[0] - a[0], b[1] - a[1]))


class en:
    """with en(tramo, s): coloca temporalmente el cursor en el punto s del tramo (sobre la carretera)."""

    def __init__(self, tramo, s):
        self.t, self.s = tramo, s

    def __enter__(self):
        self.guardado = (K.x, K.y, K.z, K.th, K.pend)
        K.x, K.y, K.z, K.th = self.t.estado(self.s)
        K.pend = self.t.pendiente(self.s)
        return K

    def __exit__(self, *exc):
        K.x, K.y, K.z, K.th, K.pend = self.guardado


def carretera(largo, ancho=12.0, dz=0.0, giro_grados=0.0, muros=1.2, mat="gris", mat_muro=None, paso=4.0, grosor=2.0,
              muro_izq=None, muro_der=None, ancho_final=None, muro_solido=False):
    """Tramo de carretera desde el cursor: largo (m), desnivel total dz, giro total (curva suave). Devuelve un Tramo.
    muro_izq / muro_der (altura en m) permiten un muro distinto por lado; izquierda = lado +, derecha = lado −.
    ancho_final (0.7.12): el ancho pasa de 'ancho' a 'ancho_final' a lo largo del tramo (embudo).
    muro_solido (0.7.12): muros como cajas de 1 m de grosor por fuera del borde en lugar de caras dobles (en el mismo
    plano, a gran velocidad se atravesaban)."""
    alturas_muro = {1: muros if muro_izq is None else muro_izq, -1: muros if muro_der is None else muro_der}
    a_fin = ancho if ancho_final is None else ancho_final
    n = max(1, int(math.ceil(largo / paso)))
    giro = math.radians(giro_grados)
    secciones = []
    for i in range(n + 1):
        secciones.append((K.x, K.y, K.z, K.th, i * largo / n))
        if i < n:
            K.th += giro / n / 2
            K.avanzar(largo / n, dz / n)
            K.th += giro / n / 2
    sumar_tiempo(largo / VEL[RITMO[0]], largo)
    mm = mat_muro or mat
    for (x0, y0, z0, t0, s0), (x1, y1, z1, t1, s1) in zip(secciones, secciones[1:]):
        def borde(x, y, z, t, lado, h):
            return (x - lado * math.sin(t), y + lado * math.cos(t), z + h)
        w0 = ancho + (a_fin - ancho) * s0 / largo                                    # ancho en cada extremo
        w1 = ancho + (a_fin - ancho) * s1 / largo
        a, b = borde(x0, y0, z0, t0, -w0 / 2, 0), borde(x1, y1, z1, t1, -w1 / 2, 0)
        c, d = borde(x1, y1, z1, t1, w1 / 2, 0), borde(x0, y0, z0, t0, w0 / 2, 0)
        uvs = [(s0 / 4, -w0 / 8), (s1 / 4, -w1 / 8), (s1 / 4, w1 / 8), (s0 / 4, w0 / 8)]
        SOLIDO.quad(a, b, c, d, mat, uvs)                                            # superficie
        ab, bb = borde(x0, y0, z0, t0, -w0 / 2, -grosor), borde(x1, y1, z1, t1, -w1 / 2, -grosor)
        cb, db = borde(x1, y1, z1, t1, w1 / 2, -grosor), borde(x0, y0, z0, t0, w0 / 2, -grosor)
        SOLIDO.quad(db, cb, bb, ab, mat)                                             # fondo
        SOLIDO.quad(ab, bb, b, a, mat)                                               # lateral izq.
        SOLIDO.quad(c, cb, db, d, mat)                                               # lateral der.
        for signo, alto_muro in alturas_muro.items():
            if not alto_muro:
                continue
            p0, p1 = borde(x0, y0, z0, t0, signo * w0 / 2, 0), borde(x1, y1, z1, t1, signo * w1 / 2, 0)
            if muro_solido:                          # caja de 1 m de grosor por fuera del borde, desde el fondo
                e0, e1 = borde(x0, y0, z0, t0, signo * (w0 / 2 + 0.5), 0), borde(x1, y1, z1, t1, signo * (w1 / 2 + 0.5), 0)
                largo_s = math.hypot(e1[0] - e0[0], e1[1] - e0[1])
                SOLIDO.caja(((e0[0] + e1[0]) / 2, (e0[1] + e1[1]) / 2, min(e0[2], e1[2]) - grosor),
                            (largo_s + 0.3, 1.0, alto_muro + grosor + abs(e1[2] - e0[2])),
                            math.atan2(e1[1] - e0[1], e1[0] - e0[0]), mm)
                continue
            q0, q1 = borde(x0, y0, z0, t0, signo * w0 / 2, alto_muro), borde(x1, y1, z1, t1, signo * w1 / 2, alto_muro)
            SOLIDO.quad(p0, p1, q1, q0, mm)          # dos caras: se ve y colisiona desde ambos lados
            SOLIDO.quad(p1, p0, q0, q1, mm)
    MIN_Z[0] = min(MIN_Z[0], min(sec[2] for sec in secciones) - grosor)
    ULTIMO_ANCHO[0] = a_fin
    return Tramo(secciones)


def fondo_rectangular(largo, ancho, mat, alto_fondo=2.5, alto_lados=1.2, mat_muro=None):
    """Terreno DETRÁS del cursor (inicio del nivel): losa de largo × ancho m y 2 m de grosor, con paredes laterales
    que prolongan las de la carretera (alto_lados) y una pared al fondo (alto_fondo), todas cajas de 1 m de grosor
    por fuera del borde. 0.7.14: rectangular (el semicírculo de la 0.7.13 podía dar problemas de textura). No mueve
    el cursor."""
    mm = mat_muro or mat
    plataforma(-largo, 0, 0, largo, ancho, alto=2.0, mat=mat)
    for signo in (1, -1):                                 # laterales (1 m más largas para cerrar las esquinas)
        x, y, z = K.frame(-largo / 2 - 0.5, signo * (ancho / 2 + 0.5), -2.0)
        SOLIDO.caja((x, y, z), (largo + 1.0, 1.0, alto_lados + 2.0), K.th, mm)
    x, y, z = K.frame(-largo - 0.5, 0, -2.0)              # fondo
    SOLIDO.caja((x, y, z), (1.0, ancho + 2.0, alto_fondo + 2.0), K.th, mm)
    MIN_Z[0] = min(MIN_Z[0], z)


def plataforma(adelante, lado, arriba, largo, ancho, alto=2.0, mat="gris", rumbo=None):
    x, y, z = K.frame(adelante + largo / 2, lado, arriba - alto)
    SOLIDO.caja((x, y, z), (largo, ancho, alto), K.th if rumbo is None else rumbo, mat)
    MIN_Z[0] = min(MIN_Z[0], z)


def decorado(adelante, lado, arriba, tam, mat, rumbo_extra=0.0):
    """Bloque de 'intrusión' de otra zona (sólido)."""
    x, y, z = K.frame(adelante, lado, arriba)
    SOLIDO.caja((x, y, z), tam, K.th + math.radians(rumbo_extra), mat)


def visual(adelante, lado, arriba, tam, mat, rumbo_extra=0.0):
    """Bloque solo visual (sin colisión): costuras, charcos, ventanas, agua."""
    x, y, z = K.frame(adelante, lado, arriba)
    SOLO_VISUAL.caja((x, y, z), tam, K.th + math.radians(rumbo_extra), mat)


def tubo(desde, hasta, radio, mat, solido=True, n=10):
    """Cilindro entre dos puntos dados en el marco del cursor: (adelante, lado, arriba)."""
    (SOLIDO if solido else SOLO_VISUAL).prisma(K.frame(*desde), K.frame(*hasta), radio, mat, n)


def costura(ancho, adelante=0.0):
    """Franja morada del Time Eater cruzando la pista (visual), con dos postes: marca la unión entre dos eras."""
    visual(adelante, 0, 0.03, (1.2, ancho, 0.02), "costura")
    for lado in (-ancho / 2 - 0.5, ancho / 2 + 0.5):
        tubo((adelante, lado, -1), (adelante, lado, 5), 0.35, "costura", solido=False, n=6)


def arco_costura(ancho, adelante=0.0, alto=6.0):
    """Arco morado sobre la pista (sólido): portal entre dos eras."""
    decorado(adelante, 0, alto, (2, ancho, 1), "costura")
    decorado(adelante, -ancho / 2 - 0.5, 0, (2, 1, alto), "costura")
    decorado(adelante, ancho / 2 + 0.5, 0, (2, 1, alto), "costura")


def charco_dano(adelante, lado, largo, ancho, mat="csc"):
    """Mancha que hace daño (lava, Mega Mack): placa visual fina + colisión @DAMAGE un poco más alta."""
    visual(adelante, lado, 0.02, (largo, ancho, 0.04), mat)
    x, y, z = K.frame(adelante, lado, 0.0)
    DANO.caja((x, y, z), (largo * 0.9, ancho * 0.9, 0.12), K.th, "gris")


def cuna(adelante, lado, largo, ancho, alto, mat):
    """Cuña sólida (rampa) que sube de 0 a 'alto' a lo largo de 'largo' hacia adelante. Con largo = alto, 45°."""
    def p(u, v, w):
        return K.frame(adelante + u, lado + v, w)
    a0, b0 = p(0, -ancho / 2, 0), p(0, ancho / 2, 0)
    a1, b1 = p(largo, -ancho / 2, 0), p(largo, ancho / 2, 0)
    a2, b2 = p(largo, -ancho / 2, alto), p(largo, ancho / 2, alto)
    dentro = p(largo * 0.66, 0, alto * 0.33)
    for cara in ([a0, a2, b2, b0], [a1, b1, b2, a2], [a0, b0, b1, a1], [a0, a1, a2], [b0, b2, b1]):
        fuera = tuple(2 * sum(q[k] for q in cara) / len(cara) - dentro[k] for k in range(3))
        SOLIDO.cara(cara, mat, hacia=fuera)


def agua(adelante, largo, ancho=20.0, variante="B", profundidad=12.0):
    """Tramo de agua para cruzar corriendo con el boost: colisión de agua 0,2 m bajo la pista, placa azul visual y suelo
    de muerte debajo (sin boost, Sonic se hunde). Ver AGUA."""
    x, y, z = K.frame(adelante + largo / 2, 0, -0.2)
    AGUA[variante].caja((x, y, z - 0.5), (largo, ancho, 0.5), K.th, "ssh")
    visual(adelante + largo / 2, 0, -0.22, (largo, ancho, 0.04), "ssh")
    suelo_muerte(adelante, largo, ancho=ancho + 20, profundidad=profundidad)


def suelo_muerte(adelante, largo, ancho=30.0, profundidad=15.0):
    x, y, z = K.frame(adelante + largo / 2, 0, -profundidad)
    MUERTE.caja((x, y, z - 1), (largo, ancho, 1.0), K.th, "gris")
    MIN_Z[0] = min(MIN_Z[0], z - 1)
    TRAMOS_MUERTE.append((K.frame(adelante, 0, 0), K.frame(adelante + largo, 0, 0), seccion_actual()))


# ----------------------------------------------------------------------------------------------
# Objetos (XML del set data). Posiciones en el sistema del juego.
# ----------------------------------------------------------------------------------------------
def a_juego(p):
    return (p[0], p[2], -p[1])


def q_yaw(th_extra=0.0):
    phi = math.pi / 2 + K.th + th_extra
    return (math.cos(phi / 2), 0.0, math.sin(phi / 2), 0.0)   # w, x, y, z


def q_superficie(th_extra=0.0):
    """Giro horizontal + inclinación del suelo en el cursor (K.pend), para objetos apoyados en pendientes.
    q = q_Y(yaw) * q_X(alfa): el eje Z local (frente del objeto) pasa a tener componente vertical -sin(alfa).
    Con el frente hacia adelante alfa = -pendiente; con el objeto girado 180° (th_extra = pi), alfa = +pendiente."""
    phi = math.pi / 2 + K.th + th_extra
    alfa = -K.pend * math.cos(th_extra)
    c1, s1, c2, s2 = math.cos(phi / 2), math.sin(phi / 2), math.cos(alfa / 2), math.sin(alfa / 2)
    return (c1 * c2, c1 * s2, s1 * c2, -s1 * s2)


def xyz(tag, p):
    return f"<{tag}><x>{p[0]:.3f}</x><y>{p[1]:.3f}</y><z>{p[2]:.3f}</z></{tag}>"


def rot(q):
    return f"<Rotation><w>{q[0]:.6f}</w><x>{q[1]:.6f}</x><y>{q[2]:.6f}</y><z>{q[3]:.6f}</z></Rotation>"


def obj(tipo, campos, adelante=0.0, lado=0.0, arriba=0.0, q=None, pos=None):
    p = a_juego(pos if pos else K.frame(adelante, lado, arriba))
    q = q or q_yaw()
    sid = nuevo_id()
    OBJETOS.append(f"  <{tipo}>{campos}{xyz('Position', p)}{rot(q)}<SetObjectID>{sid}</SetObjectID></{tipo}>")
    return sid                       # SetObjectID asignado, para enlazar objetos entre sí (p. ej. volumen de cámara -> cámara)


CAMPOS_RING = ("<GroundOffset>0</GroundOffset><InitDisp>false</InitDisp><IsCastShadow>true</IsCastShadow>"
               "<IsLightSpeedDashTarget>false</IsLightSpeedDashTarget><IsReset>false</IsReset><Range>80</Range>"
               "<ResetTime>0</ResetTime><TreasureSearchHideType>0</TreasureSearchHideType>")


CAMPOS_RING_DASH = CAMPOS_RING.replace("<IsLightSpeedDashTarget>false", "<IsLightSpeedDashTarget>true")


def anillos(desde, hasta, cada=2.5, lado=0.0, arriba=0.8, tramo=None, dash=False):
    """Fila de anillos. Con tramo, 'desde'/'hasta' son distancias sobre el tramo (siguen curvas y pendientes).
    dash=True: anillos para el light speed dash (IsLightSpeedDashTarget), siempre a LIGHT_DASH_SEPARACION (0.7.10)."""
    campos = CAMPOS_RING_DASH if dash else CAMPOS_RING
    if dash:
        cada = AJUSTES["LIGHT_DASH_SEPARACION"]
    d = desde
    while d <= hasta + 1e-6:
        if tramo:
            with en(tramo, d):
                obj("Ring", campos, 0, lado, arriba)
        else:
            obj("Ring", campos, d, lado, arriba)
        d += cada


def fila_light_dash(control, fantasmas=None):
    """Fila curva de anillos de light dash (0.7.10), con las medidas de Planet Wisp (pla204): 'control' son puntos
    (adelante, lado, arriba) del cursor; se interpola una curva Catmull-Rom y se remuestrea a LIGHT_DASH_SEPARACION.
    Avisa si dos anillos seguidos giran más de LIGHT_DASH_GIRO_MAX (con giros mayores Sonic sale recto).
    fantasmas (0.7.17): (antes, después), puntos de control fuera de la fila que solo marcan la tangente de los extremos;
    sin ellos, los extremos se prolongan en línea recta."""
    ctl = [K.frame(*c) for c in control]
    # extremos prolongados en línea recta (0.7.17): duplicados, la curva se doblaba de golpe en el primer y el último anillo
    if fantasmas:
        ext = [K.frame(*fantasmas[0])] + ctl + [K.frame(*fantasmas[1])]
    else:
        ext = ([tuple(2 * a - b for a, b in zip(ctl[0], ctl[1]))] + ctl
               + [tuple(2 * a - b for a, b in zip(ctl[-1], ctl[-2]))])
    densos = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for k in range(40):
            t = k / 40
            densos.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                       + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(3)))
    densos.append(ctl[-1])
    sep = AJUSTES["LIGHT_DASH_SEPARACION"]
    puntos, acum = [densos[0]], 0.0                 # remuestreo exacto por longitud de arco (0.7.17)
    for a, b in zip(densos, densos[1:]):
        tramo = math.dist(a, b)
        while acum + tramo >= sep and tramo > 1e-9:
            f = (sep - acum) / tramo
            a = tuple(a[j] + (b[j] - a[j]) * f for j in range(3))
            puntos.append(a)
            tramo, acum = math.dist(a, b), 0.0
        acum += tramo
    giro_max = 0.0
    for a, b, c in zip(puntos, puntos[1:], puntos[2:]):
        u = [b[j] - a[j] for j in range(3)]
        v = [c[j] - b[j] for j in range(3)]
        cos = sum(x * y for x, y in zip(u, v)) / max(1e-9, math.hypot(*u) * math.hypot(*v))
        giro_max = max(giro_max, math.degrees(math.acos(max(-1.0, min(1.0, cos)))))
    if giro_max > AJUSTES["LIGHT_DASH_GIRO_MAX"]:
        print(f"TEU_AVISO light dash ({seccion_actual()}): giro de {giro_max:.1f}° entre anillos (máx. {AJUSTES['LIGHT_DASH_GIRO_MAX']:g})")
    for p in puntos:
        obj("Ring", CAMPOS_RING_DASH, pos=p)
    return puntos


def dash_panel(adelante, lado=0.0, velocidad=100):
    obj("DashPanel", "<GroundOffset>0</GroundOffset><IsCastShadow>true</IsCastShadow><IsChangeCameraWhenChangePath>false</IsChangeCameraWhenChangePath>"
        "<IsChangePath>false</IsChangePath><IsConstantStartVelocity>true</IsConstantStartVelocity><IsInvisible>false</IsInvisible>"
        f"<IsTo3D>false</IsTo3D><IsUseDelayCamera>true</IsUseDelayCamera><OutOfControl>0.5</OutOfControl><Range>100</Range>"
        f"<Speed>{velocidad}</Speed><SpeedMax>60</SpeedMax><SpeedMin>30</SpeedMin>", adelante, lado, 0.0, q=q_superficie())


def resorte_vertical(adelante, lado=0.0, arriba=0.0, velocidad=30, a_3d=False, mantener=5):
    obj("Spring", "<AimDirection>0</AimDirection><BaseRotation>0</BaseRotation><DebugShotTimeLength>2</DebugShotTimeLength>"
        f"<FirstSpeed>{velocidad}</FirstSpeed><GroundOffset>0</GroundOffset><IsBreak>false</IsBreak><IsCastShadow>true</IsCastShadow>"
        "<IsChangeCameraWhenPathChange>true</IsChangeCameraWhenPathChange><IsHomingAttackEnable>false</IsHomingAttackEnable>"
        "<IsLongBase>false</IsLongBase><IsPathChange>false</IsPathChange><IsSideSet>false</IsSideSet>"
        "<IsStartVelocityConstant>true</IsStartVelocityConstant><IsWallWalk>false</IsWallWalk><IsWithBase>false</IsWithBase>"
        f"<IsYawUpdate>false</IsYawUpdate><KeepVelocityDistance>{mantener}</KeepVelocityDistance><MotionType>0</MotionType>"
        "<OutOfControl>0.4</OutOfControl><Range>60</Range><m_IsConstantFrame>false</m_IsConstantFrame>"
        "<m_IsConstantPosition>true</m_IsConstantPosition><m_IsMonkeyHunting>false</m_IsMonkeyHunting>"
        f"<m_IsStopBoost>false</m_IsStopBoost><m_IsTo3D>{'true' if a_3d else 'false'}</m_IsTo3D>"
        "<m_MonkeyTarget><x>0</x><y>0</y><z>0</z></m_MonkeyTarget>",
        adelante, lado, arriba, q=(1.0, 0.0, 0.0, 0.0))


def rampa_salto(adelante, lado=0.0, boost=50, normal=35, angulo=0):
    """JumpBoard. angulo = AngleType del juego: 0 = rampa tendida, 1 = rampa empinada.
    Calibrado en el juego: hueco de 28 m -> 60/60 ángulo 0; hueco de 22 m (a una isla) -> 68/62 ángulo 1 llegaba justo
    al borde, 71,4/65,1 desde la 0.7.17."""
    obj("JumpBoard", f"<AngleType>{angulo}</AngleType><GroundOffset>0</GroundOffset>"
        f"<ImpulseSpeedOnBoost>{boost}</ImpulseSpeedOnBoost><ImpulseSpeedOnNormal>{normal}</ImpulseSpeedOnNormal>"
        "<IsCastShadow>false</IsCastShadow><IsTo3D>false</IsTo3D><LookBack>false</LookBack><OutOfControl>1.5</OutOfControl>"
        "<Range>60</Range><RigidBody>true</RigidBody>", adelante, lado, 0.0,
        q=q_superficie(math.pi))      # el frente del JumpBoard es el contrario al del DashPanel (probado en 0.4.0)


def aro_impulso_inclinado(adelante, lado=0.0, arriba=1.6, velocidad=30, bajada_grados=40.0, mantener=5):
    """DashRing que lanza hacia adelante y hacia ABAJO 'bajada_grados'. Su frente es -Z local (como aro_impulso):
    q = q_Y(yaw + 180°) · q_X(alfa); el frente -Z queda con componente vertical +sin(alfa), así que alfa = -bajada."""
    phi = math.pi / 2 + K.th + math.pi
    alfa = -math.radians(bajada_grados)
    c1, s1, c2, s2 = math.cos(phi / 2), math.sin(phi / 2), math.cos(alfa / 2), math.sin(alfa / 2)
    obj("DashRing", f"<FirstSpeed>{velocidad}</FirstSpeed><GroundOffset>0</GroundOffset><IsCastShadow>true</IsCastShadow>"
        "<IsChangeCameraWhenChangePath>false</IsChangeCameraWhenChangePath><IsChangePath>false</IsChangePath>"
        f"<IsHeadToVelocity>false</IsHeadToVelocity><IsTo3D>false</IsTo3D><KeepVelocityDistance>{mantener}</KeepVelocityDistance>"
        "<OutOfControl>0.5</OutOfControl><Range>60</Range>", adelante, lado, arriba, q=(c1 * c2, c1 * s2, s1 * c2, -s1 * s2))


def aro_impulso(adelante, lado=0.0, arriba=1.6, velocidad=25):
    """DashRing. Su frente es -Z local, como el JumpBoard (probado en 0.5.0: con el giro del DashPanel lanzaba hacia atrás)."""
    obj("DashRing", f"<FirstSpeed>{velocidad}</FirstSpeed><GroundOffset>0</GroundOffset><IsCastShadow>true</IsCastShadow>"
        "<IsChangeCameraWhenChangePath>false</IsChangeCameraWhenChangePath><IsChangePath>false</IsChangePath>"
        "<IsHeadToVelocity>false</IsHeadToVelocity><IsTo3D>false</IsTo3D><KeepVelocityDistance>5</KeepVelocityDistance>"
        "<OutOfControl>0.5</OutOfControl><Range>60</Range>", adelante, lado, arriba, q=q_yaw(math.pi))


# ----------------------------------------------------------------------------------------------
# Enemigos de las 9 zonas (plantillas copiadas de los actos originales: niveles/comun/plantillas_objetos.py)
# ----------------------------------------------------------------------------------------------
# zona -> (tipo de objeto, altura sobre el suelo, archivos de EnemyArchiveTree que necesita)
ENEMIGOS = {
    "ghz": ("EnemyMotora3D", 0.0, ["EnemyMotora"]),
    "cpz": ("EnemyLander3D", 0.0, ["EnemyLander"]),
    "ssz": ("EnemyEggRobo3D", 1.0, ["EnemyEggRobo"]),
    "sph": ("EnemySpinner", 2.5, ["EnemySpinner"]),
    "cte": ("EnemyGunHunter3D", 0.0, ["EnemyGunHunter"]),
    "ssh": ("EnemyPawnLance3D", 0.0, ["EnemyEPawnCommon", "EnemyEPawnSSH"]),
    "csc": ("EnemyTaker3D", 3.0, ["EnemyTaker"]),       # vuelan; a 0 m quedaba hundido (0.7.0), a 2 m algo bajo (0.7.1)
    "euc": ("EnemyEFighter3D", 0.0, ["EnemyEFighter"]),
    "pla": ("EnemyPawnPla3D", 0.0, ["EnemyEPawnCommon", "EnemyEPawnPLA"]),
}
# Si un enemigo cierra el juego, se quita su zona de aquí y se reconstruye: sus apariciones pasan a ser Egg Fighters
# (confirmados en el juego). nivel.json debe listar los archivos de los enemigos activos ("enemigos").
ENEMIGOS_ACTIVOS = set(ENEMIGOS)
CAMPOS_EFIGHTER = (
    "<ActionRange>100</ActionRange><AttackRange>4.5</AttackRange><BarrelID><SetObjectID>0</SetObjectID></BarrelID>"
    "<ChaserManagerID><SetObjectID>0</SetObjectID></ChaserManagerID><GroundOffset>0</GroundOffset><IsAimTarget>false</IsAimTarget>"
    "<IsArrivalEffect>true</IsArrivalEffect><IsCastShadow>true</IsCastShadow><IsDamageFromOnlyPlayer>true</IsDamageFromOnlyPlayer>"
    "<IsPlayFindMotion>true</IsPlayFindMotion><Range>200</Range><SearchType>1</SearchType>"
    "<Target><x>0</x><y>0</y><z>0</z></Target><WayPointA><x>0</x><y>0</y><z>0</z></WayPointA><WayPointB><x>0</x><y>0</y><z>0</z></WayPointB>"
    "<m_AttackMoveSpeedRatio>1</m_AttackMoveSpeedRatio><m_ChargeTime>0.5</m_ChargeTime><m_ChaserModeVelocity>5</m_ChaserModeVelocity>"
    "<m_FindMotionType>1</m_FindMotionType><m_IsAllRangeSearch>false</m_IsAllRangeSearch><m_IsAttack>true</m_IsAttack>"
    "<m_IsChaseAfter>false</m_IsChaseAfter><m_IsChaserMode>false</m_IsChaserMode><m_IsForceSmartTurn>false</m_IsForceSmartTurn>"
    "<m_IsPushBarrelMode>false</m_IsPushBarrelMode><m_IsPushBarrelOnce>false</m_IsPushBarrelOnce><m_IsPushDirRight>true</m_IsPushDirRight>"
    "<m_IsRestrictMove>false</m_IsRestrictMove><m_LostTime>10</m_LostTime><m_MoveSpeedRatio>1</m_MoveSpeedRatio>"
    "<m_PushBarrelSpanTime>2</m_PushBarrelSpanTime><m_SeekSpanTime>3</m_SeekSpanTime><m_TurnAccel>4</m_TurnAccel><m_WaitTime>0.3</m_WaitTime>")
PLANTILLAS.setdefault("EnemyEFighter3D", CAMPOS_EFIGHTER)
ZONAS_USADAS = set()


def enemigo(zona, adelante=0.0, lado=0.0, arriba=None, pos=None):
    """Enemigo de la zona indicada, mirando hacia Sonic. Los puntos de patrulla (WayPointA/B) de la plantilla se
    sustituyen por la posición del enemigo (en los originales eran su propia posición).
    arriba: altura sobre el cursor (por defecto, la de la tabla ENEMIGOS). pos: punto Blender exacto (ignora el resto)."""
    if zona not in ENEMIGOS_ACTIVOS:
        zona = "euc"
    tipo, alto, _ = ENEMIGOS[zona]
    if arriba is not None:
        alto = arriba
    ZONAS_USADAS.add(zona)
    pb = pos if pos else K.frame(adelante, lado, alto)
    PUNTOS_ENEMIGO.append((pb[0], pb[1], pb[2], seccion_actual(), tipo))
    p = a_juego(pb)
    campos = PLANTILLAS[tipo]
    for wp in ("WayPointA", "WayPointB"):
        m = re.search(f"<{wp}><x>([^<]*)</x><y>([^<]*)</y><z>([^<]*)</z></{wp}>", campos)
        if m and any(float(v) != 0.0 for v in m.groups()):
            campos = campos.replace(m.group(0), xyz(wp, p))
    return obj(tipo, campos, adelante, lado, alto, q=q_yaw(math.pi), pos=pos)


def egg_fighter(adelante, lado=0.0):
    """Egg Fighter de Rooftop Run (confirmado en el juego en la 0.6.1)."""
    return enemigo("euc", adelante, lado)


def archivos_enemigos():
    """Archivos de EnemyArchiveTree que necesitan los enemigos colocados (para comprobar nivel.json)."""
    return sorted({a for z in ZONAS_USADAS for a in ENEMIGOS[z][2]})


# ----------------------------------------------------------------------------------------------
# Gimmicks y otros objetos
# ----------------------------------------------------------------------------------------------
def punto_control(adelante=0.0):
    """Checkpoint (PointMarker) atravesando la pista. Campos de ghz200; PointMarkerID correlativo."""
    PM_ID[0] += 1
    campos = re.sub(r"<PointMarkerID>\d+</PointMarkerID>", f"<PointMarkerID>{PM_ID[0]}</PointMarkerID>", PLANTILLAS["PointMarker"])
    return obj("PointMarker", campos, adelante, 0.0, 0.0, q=q_yaw())


def nube(adelante, lado=0.0, arriba=1.0, velocidad=24):
    """Nube de Sky Sanctuary (SszCloud): rebota hacia arriba. Requiere ssz_cmn + SonicSsz (confirmado en el laboratorio)."""
    return obj("SszCloud", "<AimDirection>0</AimDirection><Attenuation>0.5</Attenuation><CatchTime>0.2</CatchTime>"
               f"<FirstSpeed>{velocidad}</FirstSpeed><GroundOffset>0</GroundOffset><IsCastShadow>false</IsCastShadow><IsVisible>true</IsVisible>"
               "<IsYawUpdate>false</IsYawUpdate><KeepVelocityDistance>0</KeepVelocityDistance><LifeTime>0</LifeTime>"
               "<OutOfControl>0</OutOfControl><Range>100</Range><Size>2</Size>", adelante, lado, arriba, q=(1.0, 0.0, 0.0, 0.0))


def plataforma_giratoria(adelante, lado=0.0, arriba=4.0, velocidad=1.2):
    """Plataforma giratoria de Sky Sanctuary (SszRollingFloor). Requiere ssz_cmn (confirmado en el laboratorio)."""
    return obj("SszRollingFloor", "<AttachOffsetX>0</AttachOffsetX><AttachOffsetY>0</AttachOffsetY><AttachOffsetZ>0</AttachOffsetZ>"
               "<AttachTarget /><CameraID_0><SetObjectID>0</SetObjectID></CameraID_0><EnterEaseTime_0>0</EnterEaseTime_0>"
               "<FloorType>0</FloorType><GroundOffset>0</GroundOffset><IsCastShadow>false</IsCastShadow><IsMessageOn>false</IsMessageOn>"
               f"<LeaveEaseTime_0>0</LeaveEaseTime_0><Phase>0</Phase><PoleType>2</PoleType><Range>200</Range><Speed>{velocidad}</Speed>",
               adelante, lado, arriba, q=(1.0, 0.0, 0.0, 0.0))


def cambio_bgm(adelante, cue=0):
    """ChangeBGMCollision cruzando la pista (campos de cte200). Experimento 0.7.2: en el slot de jefe la música solo
    sonaba tras reiniciar; al cruzarlo con IsResetOnFront se intenta forzar el arranque del tema del escenario."""
    return obj("ChangeBGMCollision", "<Collision_Height>30</Collision_Height><Collision_Width>30</Collision_Width>"
               f"<CueIDOnBack>{cue}</CueIDOnBack><CueIDOnFront>{cue}</CueIDOnFront><GroundOffset>0</GroundOffset>"
               "<IsCastShadow>false</IsCastShadow><IsResetOnBack>false</IsResetOnBack><IsResetOnFront>true</IsResetOnFront>"
               "<LerpTimeBack>0.5</LerpTimeBack><LerpTimeFront>0.5</LerpTimeFront><Range>100</Range>",
               adelante, 0.0, 0.0, q=q_yaw())


def grind_dash(pos_blender, velocidad=60, giro=0.0):
    # OutOfControl 0.25 como en cpz200/csc200/pla200: con 2.5 (de ghz200) Sonic no podía saltar en el riel y seguía
    # sin control unos segundos al salir (prueba de la 0.7.1). giro: radianes respecto al rumbo del cursor.
    obj("GrindDashPanel", "<GroundOffset>0</GroundOffset><IsCastShadow>true</IsCastShadow><IsFront>true</IsFront>"
        f"<IsStartVelocityConstant>true</IsStartVelocityConstant><OutOfControl>0.25</OutOfControl><Range>100</Range><Speed>{velocidad}</Speed>",
        pos=pos_blender, q=q_yaw(giro))


def cambio_modo(tipo, adelante, salida=False, ancho=30, alto=40, extra="", arriba=0.0, cambiar_camara=True):
    """Trigger de cambio de modo. Cruzarlo en su dirección activa el modo; un trigger girado 180° (salida)
    se cruza 'por detrás' y devuelve al modo 3D normal."""
    p = K.frame(adelante, 0, arriba)
    if tipo == "ChangeMode_3Dto2D":
        CAMBIOS_2D.append((p[0], p[1], p[2], seccion_actual()))
    pj = a_juego(p)
    destino = (pj[0], pj[1] - 5.0, pj[2])
    q = q_yaw(math.pi if salida else 0.0)
    campos = (f"<Collision_Height>{alto}</Collision_Height><Collision_Width>{ancho:g}</Collision_Width><GroundOffset>0</GroundOffset>"
              f"<IsCastShadow>true</IsCastShadow><Range>100</Range>{xyz('TargetDirection', destino)}"
              f"<m_IsChangeCamera>{'true' if cambiar_camara else 'false'}</m_IsChangeCamera><m_IsEnableFromBack>true</m_IsEnableFromBack>"
              f"<m_IsEnableFromFront>true</m_IsEnableFromFront>{extra}")
    obj(tipo, campos, adelante, 0, arriba, q=q)


def a_2d(adelante, salida=False, arriba=0.0, ancho_camino=0.0):
    """ancho_camino (0.7.16): el activador cubre siempre todo el camino (30 m como mínimo)."""
    cambio_modo("ChangeMode_3Dto2D", adelante, salida, arriba=arriba, ancho=max(30.0, ancho_camino + 4.0),
                extra="<m_IsAutoChange2DPath>true</m_IsAutoChange2DPath><m_IsPadCorrect>true</m_IsPadCorrect><m_PathEaseTime>0.5</m_PathEaseTime>")


def a_quickstep(adelante, salida=False):
    cambio_modo("ChangeMode_3DtoForward", adelante, salida, ancho=40,
                extra="<Template>3</Template><m_CurveCorrectionForce>1</m_CurveCorrectionForce><m_DashPathSideMoveRate>0.6</m_DashPathSideMoveRate>"
                      "<m_IsEnableAirBoost>false</m_IsEnableAirBoost><m_IsGravityControl>false</m_IsGravityControl>"
                      "<m_IsLimitEdge>false</m_IsLimitEdge><m_IsReverseCameraEnable>false</m_IsReverseCameraEnable>"
                      "<m_PathCorrectionForce>1</m_PathCorrectionForce>")


def curva_recta(nombre, desde, hasta, rieles=None, arriba=0.0):
    """Spline recta a lo largo del rumbo actual. rieles=(±m) crea dos rieles (@SV)."""
    puntos = []
    for lado in (rieles if rieles else (0.0,)):
        puntos.append([K.frame(desde, lado, arriba), K.frame(hasta, lado, arriba)])
    CURVAS.append((nombre, puntos))


def riel_grind(nombre, puntos):
    CURVAS.append((nombre, [puntos]))
    for a, b in zip(puntos, puntos[1:]):        # barra visible del riel (sin colisión)
        dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        largo = math.hypot(dx, dy)
        if abs(dz) > largo:                     # tramo muy empinado (loop): cilindro en cualquier dirección
            SOLO_VISUAL.prisma((a[0], a[1], a[2] - 0.2), (b[0], b[1], b[2] - 0.2), 0.09, "costura", n=6, tapas=False)
            continue
        n = max(1, int(largo / 2))
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            # barra fina con la cara superior 0,10 m bajo la spline (Sonic apoya los pies en la spline)
            c = (a[0] + dx * (t0 + t1) / 2, a[1] + dy * (t0 + t1) / 2, a[2] + dz * (t0 + t1) / 2 - 0.25)
            SOLO_VISUAL.caja(c, (largo / n + 0.05, 0.15, 0.15), math.atan2(dy, dx), "costura")


# ----------------------------------------------------------------------------------------------
# Patrones de recorrido reutilizables
# ----------------------------------------------------------------------------------------------
def embudo_2d(ancho_terreno, mat):
    """0.7.17: franja ancha + terreno estrecho + embudo 3D. Devuelve (franja, embudo_hecho). La franja (rieles @SV y
    activador) mide lo que la carretera anterior (0.7.16: con ±1 m, entrando por un borde la cámara pasaba a 2D y Sonic
    seguía en 3D). El terreno 2D vuelve a su ancho (6-8 m; ancho se veía raro, prueba de la 0.7.16) y, para que Sonic
    llegue centrado, un embudo 3D de 30 m con paredes sólidas de 4 m lleva del ancho de la carretera al del terreno,
    como en la sección 1 (probado). El cambio a 2D va entonces al final del embudo (cambio = -1)."""
    franja = ULTIMO_ANCHO[0]
    if franja > ancho_terreno + 0.5:
        carretera(30, ancho=franja, ancho_final=ancho_terreno, muros=4, muro_solido=True, mat=mat)
        return franja, True
    return max(franja, ancho_terreno), False


def tramo_2d(nombre, alturas, mats=("gris", "gris"), largo_plat=9.0, hueco=5.0, ancho=6.0, tubos=None,
             resortes=(), ancho_salida=14, mat_salida="gris", enemigos=None, cambio=-12.0, cambio_ghz=False):
    """Tramo de plataformas en 2D (patrón de la sección 1, probado en el juego). Se llama al final de una carretera
    recta de al menos 20 m: el cambio a 2D va 12 m antes del final; la vuelta a 3D, 8 m dentro de la carretera de
    salida (30 m), que esta función también crea. alturas: altura de cada plataforma respecto al suelo (subidas de
    1,5 m como máximo, o un resorte en 'resortes' = índices de plataforma). Devuelve el Tramo de salida.
    enemigos: zona (o None): un enemigo en el centro de cada plataforma y un Spinner volando sobre cada hueco, para
    poder encadenar homing attacks (pedido en la prueba de la 0.7.1; en 2D están bien así, prueba de la 0.7.11).
    cambio (0.7.12): posición del cambio a 2D respecto al cursor (por defecto 12 m antes del final de la carretera
    anterior). cambio_ghz: trigger con los campos del que hay al pie del último loop de ghz200 (32012), que pasa del
    modo dash a 2D a 2,8 m de la salida del dash.
    Margen (0.7.3): un homing que cruza el cambio de modo se cancela, así que la primera plataforma empieza con una
    pista de MARGEN_CAMBIO_2D - 12 m sin enemigos, la última mide MARGEN - 8 m y no lleva enemigo, y la carretera de
    salida mide 8 + MARGEN m (lo que pongan las secciones encima debe ir más allá; generar.py lo comprueba).
    ancho: de las plataformas (6 m). La franja de la ruta @SV y el activador miden lo que la carretera anterior, con
    un embudo 3D delante si es más ancha (embudo_2d, 0.7.17)."""
    margen = AJUSTES["MARGEN_CAMBIO_2D"]
    franja, con_embudo = embudo_2d(ancho, mats[0])
    if con_embudo:
        cambio = -1.0
    ritmo("2d")
    if cambio_ghz:
        cambio_modo("ChangeMode_3Dto2D", cambio, ancho=10, alto=15,
                    extra="<m_IsAutoChange2DPath>true</m_IsAutoChange2DPath><m_IsPadCorrect>true</m_IsPadCorrect>"
                          "<m_PathEaseTime>1</m_PathEaseTime>", cambiar_camara=False)
    else:
        a_2d(cambio, ancho_camino=franja)
    n = len(alturas)
    entrada = max(0.0, margen + cambio)                       # pista de entrada (parte de la primera plataforma)
    largo_final = max(largo_plat + 3.0, margen - 8.0)       # última plataforma (hasta el cambio de vuelta a 3D)
    huecos_salvavidas = {1, n - 3} if n >= 4 else set()      # el segundo y el penúltimo hueco
    largos = [largo_plat] * n
    largos[0] += entrada
    largos[-1] = largo_final + (entrada if n == 1 else 0.0)
    total = sum(largos) + (n - 1) * hueco
    curva_recta(f"{nombre}@SV", cambio - 5, total + 20, rieles=(-franja / 2, franja / 2))
    camara_2d(cambio, total + 8, min(alturas) - 25, max(alturas) + 30)
    if n > 1:                                               # suelo de muerte solo entre el primer y el último hueco
        suelo_muerte(largos[0], total - largos[0] - largos[-1], profundidad=15 + max(alturas))
    x = 0.0
    for i, h in enumerate(alturas):
        largo = largos[i]
        plataforma(x, 0, h, largo, ancho, alto=3, mat=mats[i % len(mats)])
        anillos(x + 2, x + largo - 2, cada=2.0, arriba=h + 0.8)
        if i in resortes:
            resorte_vertical(x + largo - 1.5, 0, h, velocidad=26)
        if tubos:
            tubo((x + largo - largo_plat / 2, 0, h - 16), (x + largo - largo_plat / 2, 0, h - 3.1), 1.8, tubos)
        if enemigos:
            if i < n - 1:                                   # en el centro de la parte normal de la plataforma
                enemigo(enemigos, x + largo - largo_plat / 2, 0, arriba=h + ENEMIGOS[enemigos][1])
                enemigo("sph", x + largo + hueco / 2, 0, arriba=max(h, alturas[i + 1]) + 4.0)
        if i in huecos_salvavidas and gimmicks_activos():
            # JumpPole de salvavidas (0.7.7): pegado a la cara de la plataforma siguiente, bajo su borde. Si Sonic cae
            # por el hueco lo coge, gira y sale hacia arriba. Un pilar prolonga la cara 3 m hacia abajo como pared.
            x_sig, h_sig = x + largo + hueco, alturas[i + 1]
            plataforma(x_sig, 0, h_sig - 3.0, 2.0, ancho, alto=3.0, mat=mats[(i + 1) % len(mats)])
            barra_acrobacia(x_sig - 1.0, 0, h_sig - 3.5)
        x += largo + hueco
    x -= hueco
    K.avanzar(x, alturas[-1])          # la carretera de salida va a la altura de la última plataforma
    extra = entrada + largo_final - (largo_plat + 3.0)      # pistas planas: se recorren corriendo
    sumar_tiempo((x - extra) / VEL["2d"] + extra / VEL["3d"], x)
    ritmo("3d")
    a_2d(8, salida=True, ancho_camino=franja)
    return carretera(8 + margen, ancho=ancho_salida, mat=mat_salida)


def plataformas_3d(n, largo=18.0, hueco=7.0, ancho=10.0, mats=("gris",), dz=(0.0,), muerte=25.0, enemigos=None):
    """Serie de plataformas flotantes en 3D separadas por huecos que se saltan sin ayuda (7 m a velocidad normal).
    dz: cambio de altura al pasar a cada plataforma (cíclico; ±1,5 m como máximo).
    enemigos: zona o None. Con zona (0.7.12): solo voladores, un Spinner sobre cada hueco y otro sobre la mitad de la
    última plataforma (1 por plataforma). Los de tierra salían despedidos con el homing y destruían al siguiente,
    lo que cortaba la cadena de homing (prueba de la 0.7.11)."""
    ritmo("plataformas")
    total = n * largo + (n - 1) * hueco
    suelo_muerte(-2, total + 4, ancho=40, profundidad=muerte)
    for i in range(n):
        if i:
            if enemigos:                     # Spinner volando sobre el hueco: enlaza el homing entre plataformas
                enemigo("sph", hueco / 2, 0, arriba=max(0.0, dz[i % len(dz)]) + 4.0)   # +4 desde la 0.7.13
            K.avanzar(hueco, dz[i % len(dz)])
            sumar_tiempo(hueco / VEL["plataformas"], hueco)
        t = carretera(largo, ancho=ancho, mat=mats[i % len(mats)], muros=0)
        anillos(4, largo - 4, cada=3, tramo=t)
        if enemigos and i == n - 1:          # Spinner sobre la mitad de la última plataforma
            with en(t, largo / 2):
                enemigo("sph", 0, 0, arriba=4.0)
    ritmo("3d")


def camara_pan(adelante, lado, arriba, distancia=6.0, fovy=45.0):
    """ObjCameraPan fija en un punto que mira a Sonic (CameraPositionMode 1, campos de ghz200). Devuelve su ID."""
    return obj("ObjCameraPan", f"<CameraPositionMode>1</CameraPositionMode><Distance>{distancia:g}</Distance><Ease_Time_Enter>0</Ease_Time_Enter>"
               f"<Ease_Time_Leave>0</Ease_Time_Leave><FaceType>0</FaceType><Fovy>{fovy:g}</Fovy><GroundOffset>0</GroundOffset>"
               "<IsCameraView>false</IsCameraView><IsCastShadow>false</IsCastShadow><IsCollision>false</IsCollision>"
               "<IsControllable>false</IsControllable><OffsetPitch>0</OffsetPitch><OffsetYaw>0</OffsetYaw><Radius>1</Radius>"
               "<Range>10100</Range><Target><SetObjectID>0</SetObjectID></Target><TargetOffset_Front>0</TargetOffset_Front>"
               "<TargetOffset_Right>0</TargetOffset_Right><TargetOffset_Up>0</TargetOffset_Up><TargetOffset_Vel>0</TargetOffset_Vel>"
               "<TargetPositionFix><x>0</x><y>0</y><z>0</z></TargetPositionFix><Target_Type>0</Target_Type>"
               "<VelOffsetXYZ>0</VelOffsetXYZ><ZRot>0</ZRot>", adelante, lado, arriba, q=(1.0, 0.0, 0.0, 0.0))


LOOP_RADIO_REF = 15.0   # radio con el que se probaron los valores LOOP_CAMARA_* (0.7.11-0.7.15)


def camara_loop(adelante, lado_entrada, lado_salida, arriba, radio=None, ancho=10.0):
    """Cámara de un loop como el PRIMER loop de ghz200 (0.7.11, a petición del usuario; la 0.7.10 copiaba el último):
    una ObjCameraPan (122609: CameraPositionMode 1, Distance 10, Fovy 45) en el eje, a ras de suelo y 37 m antes del
    centro de su ChangeVolumeCamera (122608: 50 m en el sentido de la marcha × 8 × 14, Priority 1, Ease 0,6), que está
    a la misma altura que la cámara. Aquí el volumen se centra en el loop ('adelante') y todo sale de ajustes.conf
    (LOOP_CAMARA_*), con los valores de ghz200 por defecto."""
    a = AJUSTES
    # en el eje de llegada, como en ghz200 (centrado entre entrada y salida, el volumen de 8 m dejaba fuera la entrada)
    eje = lado_entrada
    if radio is None:                    # riel de la sección 4: valores tal cual
        z = arriba + a["LOOP_CAMARA_ALTO"]
        id_pan = camara_pan(adelante - a["LOOP_CAMARA_ADELANTO"], eje, z, distancia=a["LOOP_CAMARA_DISTANCIA"],
                            fovy=a["LOOP_CAMARA_FOVY"])
        volumen_camara(id_pan, adelante, eje, z, a["LOOP_CAMARA_VOL_LARGO"], a["LOOP_CAMARA_VOL_ANCHO"],
                       a["LOOP_CAMARA_VOL_ALTO"], entrar=a["LOOP_CAMARA_EASE"], salir=a["LOOP_CAMARA_EASE"],
                       prioridad=int(a["LOOP_CAMARA_PRIORIDAD"]))
        return
    # 0.7.17: con radio 30 el volumen de 14 m de alto se acababa a mitad de la subida y la cámara volvía de golpe
    # detrás de Sonic. Cámara escalada (más lejos y más alta, se ve el loop entero) y volumen que cubre todo el loop
    # (de −(r+10) a r+5: no toca el volumen de la cámara 2D, que empieza ~41 m después) y los dos carriles.
    s = max(1.0, radio / LOOP_RADIO_REF)
    z = arriba + a["LOOP_CAMARA_ALTO"] * s
    id_pan = camara_pan(adelante - a["LOOP_CAMARA_ADELANTO"] * s, eje, z, distancia=a["LOOP_CAMARA_DISTANCIA"],
                        fovy=a["LOOP_CAMARA_FOVY"])
    x0, x1 = adelante - radio - 10.0, adelante + radio + 5.0
    largo = max(a["LOOP_CAMARA_VOL_LARGO"], x1 - x0)
    ancho_v = max(a["LOOP_CAMARA_VOL_ANCHO"], abs(lado_salida - lado_entrada) + ancho + 8.0)
    alto_v = max(a["LOOP_CAMARA_VOL_ALTO"], 2 * radio + 8.0)
    volumen_camara(id_pan, (x0 + x1) / 2, (lado_entrada + lado_salida) / 2, arriba + alto_v / 2 - 4.0, largo, ancho_v,
                   alto_v, entrar=a["LOOP_CAMARA_EASE"], salir=a["LOOP_CAMARA_EASE"],
                   prioridad=int(a["LOOP_CAMARA_PRIORIDAD"]))


EXTRA_DASH = ("<Template>1</Template><m_CurveCorrectionForce>0</m_CurveCorrectionForce><m_IsLimitEdge>true</m_IsLimitEdge>"
              "<m_IsReverseCameraEnable>false</m_IsReverseCameraEnable><m_PathCorrectionForce>0.5</m_PathCorrectionForce>")


def loop(nombre, radio=10.0, ancho=10.0, desplazamiento=14.0, mat="gris"):
    """Loop de terreno (0.7.7, sin probar): una vuelta vertical completa desde el final de una carretera, con
    desplazamiento lateral para que la salida no choque con la entrada. Sonic va guiado por una spline @DP de dos rieles
    (modo dash: ChangeMode_3DtoDash a la entrada y, girado, a la salida; campos de ghz200). El cursor sale desplazado
    al costado con el mismo rumbo. Conviene llegar con paneles de dash."""
    n = 48

    def lateral(a):
        return desplazamiento * (1 - math.cos(a / 2)) / 2          # 0 → desplazamiento sin tirones

    def p(a, v=0.0, sobre=0.0):
        r = radio - sobre                                           # sobre > 0: hacia el centro (encima de la pista)
        return K.frame(r * math.sin(a), lateral(a) + v, radio - r * math.cos(a))

    # sólido de 1 m de grosor (0.7.9): en la 0.7.8 cada cara estaba duplicada en el mismo plano con la normal invertida
    # y con boost parecía que se atravesaba el suelo
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        am = (a0 + a1) / 2
        centro = p(am, 0, radio)                                    # centro del loop a esa altura del recorrido
        fuera = p(am, 0, -radio)
        pista = [p(a0, -ancho / 2), p(a1, -ancho / 2), p(a1, ancho / 2), p(a0, ancho / 2)]
        dorso = [p(a0, -ancho / 2, -1), p(a1, -ancho / 2, -1), p(a1, ancho / 2, -1), p(a0, ancho / 2, -1)]
        SOLIDO.cara(pista, mat, hacia=centro)                       # la pista (cara hacia el centro)
        SOLIDO.cara(dorso, mat, hacia=fuera)                        # el dorso, 1 m más afuera
        for v in (-ancho / 2, ancho / 2):                           # laterales
            lado_pt = p(am, v * 3, 0)
            SOLIDO.cara([p(a0, v), p(a1, v), p(a1, v, -1), p(a0, v, -1)], mat, hacia=lado_pt)
    rieles = []
    for v in (-(ancho / 2 - 1), ancho / 2 - 1):
        pts = [K.frame(-8, v, 0)] + [p(2 * math.pi * k / n, v) for k in range(n + 1)] + [K.frame(8, desplazamiento + v, 0)]
        rieles.append(pts)
    CURVAS.append((f"{nombre}@DP", rieles))
    # pared invisible (0.7.16) en el plano medio del loop, entre el carril de entrada y el de salida: sin ella se
    # saltaba de uno a otro sin dar la vuelta. 0.7.17: tope 0,85 × radio (antes 0,4; con 12 m se saltaba por encima
    # subiendo despacio sin panel): el borde de la pista solo llega al plano medio en a ≈ 89° (z ≈ radio), y a
    # 0,85 × radio queda a 6,7 m de lado (la pared está a d/2 = 7). 0,3 m de grosor: no se puede quedar encima.
    alto_muro = min(AJUSTES["LOOP_MURO_ALTO"], 0.85 * radio)
    x0, x1 = -radio - 5.0, radio + 2.0
    xc, yc, zc = K.frame((x0 + x1) / 2, desplazamiento / 2, -2.0)
    INVISIBLE.caja((xc, yc, zc), (x1 - x0, 0.3, alto_muro + 2.0), K.th, "gris")
    camara_loop(0.0, 0.0, desplazamiento, 0.0, radio=radio, ancho=ancho)
    cambio_modo("ChangeMode_3DtoDash", -6, ancho=ancho + 6, alto=25, extra=EXTRA_DASH)
    K.x -= desplazamiento * math.sin(K.th)
    K.y += desplazamiento * math.cos(K.th)
    registrar_eje(0.0)
    sumar_tiempo(2 * math.pi * radio / VEL["rapido"], 2 * math.pi * radio)
    cambio_modo("ChangeMode_3DtoDash", 6, salida=True, ancho=ancho + 6, alto=25, extra=EXTRA_DASH)


def quickstep(nombre, largo, dz=0.0, ancho=16, mat="gris", mat_muro=None):
    """Tramo de quickstep (3 carriles a 4 m) cuesta abajo/arriba. Entrada a -5 m y salida 20 m antes del final.
    Devuelve el Tramo. Los obstáculos van centrados en los carriles (lado -4, 0, 4)."""
    ritmo("rapido")
    a_quickstep(-5)
    t = carretera(largo, ancho=ancho, dz=dz, mat=mat, mat_muro=mat_muro)
    muestras = [float(s) for s in range(0, int(largo) + 1, 25)]
    if largo - muestras[-1] > 1.0:
        muestras.append(float(largo))
    CURVAS.append((f"{nombre}@QS", [[t.estado(s)[:3] for s in muestras]]))
    QUICKSTEPS.append(f"{nombre}@QS")
    with en(t, largo - 20):
        a_quickstep(0, salida=True)
    ritmo("3d")
    return t


def riel(nombre, largo, caida, plataforma_final=40, ancho=14, mat="gris", vuelta=None, desplazamiento=4.0):
    """Riel de grind sobre el vacío desde el final de una carretera: baja 'caida' m en 'largo' m.
    vuelta: radio de un loop vertical a mitad del riel (o None). Crea la carretera de llegada (sin paneles, para frenar)."""
    p0 = K.frame(-6, 0, 0.35)
    p1 = K.frame(largo * 0.45, 0, -caida * 0.4)
    p2 = K.frame(largo, 0, -caida)
    if vuelta:
        # loop vertical en p1 (0.7.7): círculo de radio 'vuelta' que avanza 0 m y se desplaza 'desplazamiento' m al
        # costado (para no cruzarse consigo mismo); el resto del riel sigue desplazado. Panel de grind justo antes.
        x1 = largo * 0.45
        pts_loop = []
        for k in range(1, 32):
            a = 2 * math.pi * k / 32
            suave = (1 - math.cos(a / 2)) / 2                   # 0 → 1 sin tirones
            pts_loop.append(K.frame(x1 + vuelta * math.sin(a), desplazamiento * suave, -caida * 0.4 + vuelta * (1 - math.cos(a))))
        p2 = K.frame(largo, desplazamiento, -caida)
        puntos = [p0, p1] + pts_loop + [K.frame(x1 + 0.5, desplazamiento, -caida * 0.4 - 0.1), p2]
        f = (x1 - 8 + 6) / (x1 + 6)                             # 8 m antes del loop, sobre el riel
        grind_dash(tuple(a + (b - a) * f for a, b in zip(p0, p1)))
        camara_loop(x1, 0.0, desplazamiento, -caida * 0.4)   # cámara del primer loop de ghz200 (0.7.11)
    else:
        puntos = [p0, p1, p2]
    riel_grind(f"{nombre}@GR", puntos)
    grind_dash(tuple(a + (b - a) * 0.1 for a, b in zip(p0, p1)))
    suelo_muerte(4, largo - 5, ancho=40, profundidad=caida + 17)
    K.avanzar(largo - 2, -caida - 0.35)
    sumar_tiempo(largo / VEL["grind"], largo)
    return carretera(plataforma_final, ancho=ancho, mat=mat)


# ----------------------------------------------------------------------------------------------
# Gimmicks nuevos de la 0.7.4 (campos copiados de los originales; sin probar todavía en el juego).
# Con GIMMICKS_NUEVOS = 0 en ajustes.conf no se colocan JumpPole, Pulley ni WallJumpBlock.
# ----------------------------------------------------------------------------------------------
def gimmicks_activos():
    return AJUSTES["GIMMICKS_NUEVOS"] >= 0.5


def barra_acrobacia(adelante, lado=0.0, arriba=2.0):
    """JumpPole (barra de acrobacia, campos de ghz200): Sonic gira en ella y sale alto si salta en el momento justo.
    Solo funciona en 2D: los originales están en planos 2D (ssh200 x ≈ -641, ghz200 x = 2047,5) y en 3D no se cogía
    (prueba de la 0.7.4). Funciona en 2D (0.7.5), pero suelta en el aire es difícil de usar: va junto a una pared, como
    salvavidas en los huecos de tramo_2d (0.7.7)."""
    return obj("JumpPole", "<AddMaxVelocity>0</AddMaxVelocity><AddMinVelocity>0</AddMinVelocity><GroundOffset>0</GroundOffset>"
               "<IsCastShadow>true</IsCastShadow><Range>30</Range>", adelante, lado, arriba, q=q_yaw())


def barra_giro(adelante, arriba=3.0, largo=8.0, lado=0.0):
    """IronPole3D (barra horizontal de ssh200): se llega con homing, Sonic queda girando y sale con altura al pulsar
    salto (confirmado en la 0.7.6). Definida en #SonicActionCommon/#SystemCommon (común). El eje de la barra es el Z
    local: con q_yaw(pi/2) queda cruzada a la pista. Position es UN EXTREMO y la barra crece PoleLen hacia -Z local, es
    decir hacia la derecha de la pista (captura de la prueba de la 0.7.6): con lado = largo / 2 queda centrada."""
    return obj("IronPole3D", "<CameraEaseTimeEnter>0.6</CameraEaseTimeEnter><CameraEaseTimeKeep>0</CameraEaseTimeKeep>"
               "<CameraEaseTimeLeave>1.2</CameraEaseTimeLeave><CameraID><SetObjectID>0</SetObjectID></CameraID>"
               f"<GroundOffset>0</GroundOffset><GuideSide>1</GuideSide><IsCastShadow>true</IsCastShadow><PoleLen>{largo:g}</PoleLen>"
               "<Range>100</Range>", adelante, lado, arriba, q=q_yaw(math.pi / 2))


def barra_2d(nombre, hueco=16.0, subida=3.0, ancho=8.0, mat="gris", mat_llegada=None):
    """Tramo 2D con una barra de acrobacia sobre un hueco. Se llama al final de una carretera recta de al menos 20 m.
    Respeta MARGEN_CAMBIO_2D: entrada plana, hueco con el JumpPole a 3 m del borde y 2 m por encima, plataforma de
    llegada 'subida' m más alta y vuelta a 3D. Devuelve el Tramo de salida."""
    margen = AJUSTES["MARGEN_CAMBIO_2D"]
    franja, con_embudo = embudo_2d(ancho, mat)  # 0.7.17: franja de la carretera, terreno de 8 m y embudo delante
    c0 = -1.0 if con_embudo else -12.0
    ritmo("2d")
    a_2d(c0, ancho_camino=franja)
    entrada = max(10.0, margen + c0)
    llegada = max(12.0, margen - 8.0)
    total = entrada + hueco + llegada
    curva_recta(f"{nombre}@SV", c0 - 5, total + 20, rieles=(-franja / 2, franja / 2))
    camara_2d(c0, total + 8, -25, subida + 30)
    plataforma(0, 0, 0, entrada, ancho, alto=2, mat=mat)
    plataforma(entrada + hueco, 0, subida, llegada, ancho, alto=2 + subida, mat=mat_llegada or mat)
    anillos(2, entrada - 2, cada=2.0)
    anillos(entrada + hueco + 2, total - 2, cada=2.0, arriba=subida + 0.8)
    barra_acrobacia(entrada + 3.0, 0, 2.0)
    suelo_muerte(entrada, hueco, ancho=40, profundidad=18)
    K.avanzar(total, subida)
    sumar_tiempo(total / VEL["2d"] + 1.0, total)
    ritmo("3d")
    a_2d(8, salida=True, ancho_camino=franja)
    return carretera(8 + margen, ancho=14, mat=mat_llegada or mat)


def panel_pared(adelante, z0, z1, ancho, mira_atras):
    """WallJumpBlock (ssh200): panel de salto en pared, visible y sólido, pegado a la cara de un muro, de la altura z0 a
    z1 (sobre el cursor). Convención confirmada en la prueba de la 0.7.5: Position = centro y el panel mide 2 × SizeY de
    alto (y 2 × SizeX de ancho). Su cara útil es -Z local; mira_atras=True: la cara mira hacia Sonic (muro delante);
    False: mira hacia adelante (muro detrás)."""
    return obj("WallJumpBlock", f"<GroundOffset>0</GroundOffset><IsCastShadow>false</IsCastShadow><Range>30</Range>"
               f"<SizeX>{ancho / 2:g}</SizeX><SizeY>{(z1 - z0) / 2:g}</SizeY><SizeZ>0.1</SizeZ>",
               adelante, 0.0, (z0 + z1) / 2, q=q_yaw(0.0 if mira_atras else math.pi))


def tirolina(nombre, largo, caida, alto_cable=2.0, llegada=40, ancho=14, mat="gris"):
    """Tirolina (Pulley, campos de ssz200) desde el final de una carretera: baja 'caida' m en 'largo' m sobre el vacío.
    La spline guía se declara en Stage.stg.xml (<Guide> con <ID>) y el Pulley la usa con PathID = ID. El Pulley va
    2,5 m antes del inicio del cable y 0,8 m por encima, como en ssz200. Crea la carretera de llegada."""
    p0 = K.frame(0.0, 0, alto_cable)
    p1 = K.frame(largo * 0.5, 0, alto_cable - caida * 0.55)
    p2 = K.frame(largo + 3.0, 0, alto_cable - caida)
    id_guia = len(GUIAS) + 1
    GUIAS.append((nombre, id_guia))
    CURVAS.append((nombre, [[p0, p1, p2]]))
    for a, b in ((p0, p1), (p1, p2)):                    # cable visual
        SOLO_VISUAL.prisma((a[0], a[1], a[2] + 1.2), (b[0], b[1], b[2] + 1.2), 0.08, "costura", n=4, tapas=False)
    if gimmicks_activos():
        obj("Pulley", "<EndPosition>3</EndPosition><GroundOffset>0</GroundOffset><IsCastShadow>false</IsCastShadow>"
            "<IsJumpCancel>true</IsJumpCancel><IsPoleAttackInvSide>false</IsPoleAttackInvSide><Length>1</Length>"
            f"<MinInitVel>0</MinInitVel><PathID>{id_guia}</PathID><Range>100</Range><StartPosition>0</StartPosition>",
            -2.5, 0.0, alto_cable + 0.8, q=q_yaw())
    suelo_muerte(2, largo - 2, ancho=40, profundidad=caida + 15)
    K.avanzar(largo, -caida)
    sumar_tiempo(largo / VEL["grind"], largo)
    return carretera(llegada, ancho=ancho, mat=mat)


def pozo_pared_2d(nombre, alto=14.0, ancho=8.0, mat="gris", mat_panel="cpz"):
    """Tramo 2D con un pozo de salto en pared (WallJumpBlock enfrentados, como en ssh200). Se llama al final de una
    carretera recta de al menos 20 m. Respeta MARGEN_CAMBIO_2D: entrada plana, pozo de 8 m entre una pared delantera
    (0..alto) y un bloque trasero colgado (3,5..alto+3, se entra por debajo), plataforma de arriba y vuelta a 3D a la
    altura 'alto'. Sin huecos: si se falla, se vuelve al suelo del pozo. Devuelve el Tramo de salida."""
    margen = AJUSTES["MARGEN_CAMBIO_2D"]
    franja, con_embudo = embudo_2d(ancho, mat)  # 0.7.17: franja de la carretera, terreno de 8 m y embudo delante
    c0 = -1.0 if con_embudo else -12.0
    ritmo("2d")
    a_2d(c0, ancho_camino=franja)
    x_pozo = max(0.0, margen + c0)                         # inicio del pozo (cara del bloque trasero)
    x_pared = x_pozo + 8.0                                  # cara de la pared delantera
    arriba_largo = max(12.0, margen - 8.0) + 2.0           # plataforma de arriba (incluye los 2 m de la pared)
    total = x_pared + arriba_largo
    curva_recta(f"{nombre}@SV", c0 - 5, total + 20, rieles=(-franja / 2, franja / 2))
    camara_2d(c0, total + 8, -25, alto + 30)
    plataforma(0, 0, 0, x_pared, ancho, alto=2, mat=mat)                             # suelo de entrada y del pozo
    plataforma(x_pozo - 4, 0, alto + 3, 4, ancho, alto=alto - 0.5, mat=mat)          # bloque trasero (3,5 .. alto+3)
    plataforma(x_pared, 0, alto, arriba_largo, ancho, alto=alto + 2, mat=mat)       # pared delantera + plataforma de arriba
    anillos(2, x_pozo - 6, cada=2.0)
    anillos(x_pared + 3, total - 3, cada=2.0, arriba=alto + 0.8)
    if gimmicks_activos():
        # un panel por cara, a la medida de la cara (convención en panel_pared; en la 0.7.5 las columnas de paneles
        # pequeños dejaban sin panel la parte baja del bloque trasero y el último metro de la pared delantera)
        panel_pared(x_pared - 0.05, 0.05, alto - 0.05, 3.0, mira_atras=True)
        panel_pared(x_pozo + 0.05, 3.55, alto + 2.95, 3.0, mira_atras=False)
    else:
        for x, z0, z1 in ((x_pared - 0.06, 0.5, alto - 0.3), (x_pozo + 0.06, 3.8, alto + 2.7)):
            visual(x, 0, z0, (0.1, 3.0, z1 - z0), mat_panel)                         # placas de color en las caras
    K.avanzar(total, alto)
    sumar_tiempo(total / VEL["2d"] + 4.0, total)          # ~4 s de saltos en el pozo
    ritmo("3d")
    a_2d(8, salida=True, ancho_camino=franja)
    return carretera(8 + margen, ancho=14, mat=mat)


# ----------------------------------------------------------------------------------------------
# Planeo: ChangeDiveBegin/End + cámara desde arriba
# ----------------------------------------------------------------------------------------------
CAMPOS_DIVE = "<DefaultStatus>0</DefaultStatus><GroundOffset>0</GroundOffset><IsCastShadow>false</IsCastShadow><Shape_Type>0</Shape_Type>"
Q_HORIZONTAL = (0.707107, 0.707107, 0.0, 0.0)           # caja tumbada, como en Chemical Plant


def camara_aterrizaje(centro, fondo_z, dist_salida=30.0, alto=10.0, lado=28.0):
    """Al aterrizar en el fondo del pozo la cámara se queda mirando desde arriba hasta que Sonic se mueve (prueba de
    la 0.7.2). Un volumen en los últimos 'alto' m activa un ObjCameraObjectLook (campos de ghz200) que sigue a Sonic
    (Target 0) mirando a un punto del túnel de salida, que sale en el rumbo actual (K.th) desde el centro. Así la
    cámara queda detrás de Sonic mirando a la salida sin depender de la convención del Yaw. Al entrar en el túnel,
    Sonic sale del volumen y vuelve la cámara normal.
    El objetivo es una ObjCameraParallel sin volumen (nunca se activa, no desaparece como un anillo)."""
    objetivo = (centro[0] + dist_salida * math.cos(K.th), centro[1] + dist_salida * math.sin(K.th), fondo_z + 2.0)
    id_obj = obj("ObjCameraParallel", "<Distance>10</Distance><Ease_Time_Enter>0</Ease_Time_Enter><Ease_Time_Leave>0</Ease_Time_Leave>"
                 "<Fovy>45</Fovy><GroundOffset>0</GroundOffset><IsCameraView>false</IsCameraView><IsCastShadow>false</IsCastShadow>"
                 "<IsCollision>false</IsCollision><IsControllable>false</IsControllable><OffsetPitch>0</OffsetPitch><OffsetYaw>0</OffsetYaw>"
                 "<Pitch>10</Pitch><Range>100000</Range><Target><SetObjectID>0</SetObjectID></Target>"
                 "<TargetOffset_Front>0</TargetOffset_Front><TargetOffset_Right>0</TargetOffset_Right><TargetOffset_Up>0</TargetOffset_Up>"
                 "<TargetOffset_Vel>0</TargetOffset_Vel><TargetPositionFix><x>0</x><y>0</y><z>0</z></TargetPositionFix><Target_Type>0</Target_Type>"
                 "<VelOffsetXYZ>0</VelOffsetXYZ><Yaw>0</Yaw><ZRot>0</ZRot>",
                 pos=objetivo, q=(1.0, 0.0, 0.0, 0.0))
    id_cam = obj("ObjCameraObjectLook", "<Distance>8</Distance><Ease_Time_Enter>0</Ease_Time_Enter><Ease_Time_Leave>0</Ease_Time_Leave>"
                 "<Fovy>50</Fovy><GroundOffset>0</GroundOffset><IsCameraView>false</IsCameraView><IsCastShadow>false</IsCastShadow>"
                 "<IsCollision>false</IsCollision><IsControllable>false</IsControllable><Range>100000</Range>"
                 f"<Target><SetObjectID>0</SetObjectID></Target><TargetObject><SetObjectID>{id_obj}</SetObjectID></TargetObject>"
                 "<TargetOffset_Front>0</TargetOffset_Front><TargetOffset_Right>0</TargetOffset_Right><TargetOffset_Up>0</TargetOffset_Up>"
                 "<TargetOffset_Vel>0</TargetOffset_Vel><TargetOffset_WorldX>0</TargetOffset_WorldX><TargetOffset_WorldY>2</TargetOffset_WorldY>"
                 "<TargetOffset_WorldZ>0</TargetOffset_WorldZ><TargetPositionFix><x>0</x><y>0</y><z>0</z></TargetPositionFix>"
                 "<Target_Type>0</Target_Type><VelOffsetXYZ>0</VelOffsetXYZ><ZRot>0</ZRot>",
                 pos=(centro[0], centro[1], fondo_z + 2.0), q=(1.0, 0.0, 0.0, 0.0))
    obj("ChangeVolumeCamera", f"<Collision_Height>{alto:g}</Collision_Height><Collision_Length>{lado:g}</Collision_Length>"
        f"<Collision_Width>{lado:g}</Collision_Width><DefaultStatus>0</DefaultStatus><Ease_Time_Enter>0.5</Ease_Time_Enter>"
        "<Ease_Time_Leave>1</Ease_Time_Leave><GroundOffset>0</GroundOffset><IsCameraView>false</IsCameraView><IsCastShadow>false</IsCastShadow>"
        "<IsEnableCollision>false</IsEnableCollision><LineType>0</LineType><PositionList /><Priority>0</Priority><Range>300</Range>"
        f"<Shape_Type>0</Shape_Type><Target><SetObjectID>{id_cam}</SetObjectID></Target>",
        pos=(centro[0], centro[1], fondo_z + alto / 2), q=(1.0, 0.0, 0.0, 0.0))


def volumen_camara(id_cam, adelante, lado, arriba, largo, ancho, alto, entrar=1.0, salir=1.0, prioridad=0):
    """ChangeVolumeCamera orientado con el rumbo (q_yaw): Length a lo largo del recorrido, Width lateral, Height
    vertical (misma convención que los triggers de cambio de modo); (adelante, lado, arriba) = centro de la caja."""
    return obj("ChangeVolumeCamera", f"<Collision_Height>{alto:g}</Collision_Height><Collision_Length>{largo:g}</Collision_Length>"
               f"<Collision_Width>{ancho:g}</Collision_Width><DefaultStatus>0</DefaultStatus><Ease_Time_Enter>{entrar:g}</Ease_Time_Enter>"
               f"<Ease_Time_Leave>{salir:g}</Ease_Time_Leave><GroundOffset>0</GroundOffset><IsCameraView>false</IsCameraView>"
               "<IsCastShadow>false</IsCastShadow><IsEnableCollision>false</IsEnableCollision><LineType>0</LineType><PositionList />"
               f"<Priority>{prioridad}</Priority><Range>300</Range><Shape_Type>0</Shape_Type><Target><SetObjectID>{id_cam}</SetObjectID></Target>",
               adelante, lado, arriba, q=q_yaw())


def camara_cenital_anillo(centro, hueco, z0, z1, prioridad=2):
    """Cámara cenital fija sobre un anillo alrededor de 'centro' (0.7.10), como la del riel de la torre del reloj de
    euc200 (ObjCameraParallel Pitch 85-89, Distance 4-5, Fovy 70, volúmenes Priority 1-2): su orientación no depende
    del rumbo de Sonic, así que no tiembla en las curvas del riel. Pitch y distancia en ajustes.conf (RIEL_CAMARA_*).
    Volumen: 8 cajas cuadradas de 2·hueco de lado alineadas con el rumbo, alrededor de un hueco cuadrado de ±hueco que
    deja libre el pozo central (y su cámara de planeo), entre las alturas z0 y z1 (Blender). La parte de arriba de la
    pantalla mira hacia el rumbo del cursor."""
    yaw = (math.degrees(K.th) - 90 + 180) % 360 - 180
    id_cam = obj("ObjCameraParallel", f"<Distance>{AJUSTES['RIEL_CAMARA_DISTANCIA']:g}</Distance><Ease_Time_Enter>0</Ease_Time_Enter>"
                 "<Ease_Time_Leave>0</Ease_Time_Leave><Fovy>70</Fovy><GroundOffset>0</GroundOffset><IsCameraView>false</IsCameraView>"
                 "<IsCastShadow>false</IsCastShadow><IsCollision>false</IsCollision><IsControllable>false</IsControllable>"
                 f"<OffsetPitch>0</OffsetPitch><OffsetYaw>0</OffsetYaw><Pitch>{AJUSTES['RIEL_CAMARA_PITCH']:g}</Pitch><Range>100000</Range>"
                 "<Target><SetObjectID>0</SetObjectID></Target><TargetOffset_Front>0</TargetOffset_Front><TargetOffset_Right>0</TargetOffset_Right>"
                 "<TargetOffset_Up>-0.2</TargetOffset_Up><TargetOffset_Vel>0</TargetOffset_Vel>"
                 "<TargetPositionFix><x>0</x><y>0</y><z>0</z></TargetPositionFix><Target_Type>0</Target_Type>"
                 f"<VelOffsetXYZ>0</VelOffsetXYZ><Yaw>{yaw:.1f}</Yaw><ZRot>0</ZRot>",
                 pos=(centro[0], centro[1], z1), q=(1.0, 0.0, 0.0, 0.0))
    lado_caja = 2 * hueco
    c, s = math.cos(K.th), math.sin(K.th)
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            if i == 0 and j == 0:
                continue
            f, l = i * lado_caja, j * lado_caja                    # adelante / izquierda respecto al rumbo
            pos = (centro[0] + f * c - l * s, centro[1] + f * s + l * c, (z0 + z1) / 2)
            obj("ChangeVolumeCamera", f"<Collision_Height>{z1 - z0:g}</Collision_Height><Collision_Length>{lado_caja:g}</Collision_Length>"
                f"<Collision_Width>{lado_caja:g}</Collision_Width><DefaultStatus>0</DefaultStatus><Ease_Time_Enter>1.2</Ease_Time_Enter>"
                "<Ease_Time_Leave>1</Ease_Time_Leave><GroundOffset>0</GroundOffset><IsCameraView>false</IsCameraView>"
                "<IsCastShadow>false</IsCastShadow><IsEnableCollision>false</IsEnableCollision><LineType>0</LineType><PositionList />"
                f"<Priority>{prioridad}</Priority><Range>300</Range><Shape_Type>0</Shape_Type><Target><SetObjectID>{id_cam}</SetObjectID></Target>",
                pos=pos, q=q_yaw())
    return id_cam


def camara_2d(desde, hasta, z_min=-25.0, z_max=35.0):
    """Cámara de los tramos 2D (0.7.8): la 2D por defecto quedaba muy cerca y no se veía el suelo. ObjCameraParallel que
    sigue a Sonic de lado (como los 2D de ghz200/ssh200: Distance 15-20, Pitch 0-15) con un volumen que cubre el tramo
    entre 'desde' y 'hasta' (metros desde el cursor). Yaw = rumbo + CAMARA_2D_GIRO: deducido de los planeos (la cámara
    mira hacia Yaw + 90°), así mira hacia la izquierda del recorrido y el avance queda a la derecha de la pantalla."""
    yaw = (math.degrees(K.th) + AJUSTES["CAMARA_2D_GIRO"] + 180) % 360 - 180
    id_cam = obj("ObjCameraParallel", f"<Distance>{AJUSTES['CAMARA_2D_DISTANCIA']:g}</Distance><Ease_Time_Enter>0</Ease_Time_Enter>"
                 "<Ease_Time_Leave>0</Ease_Time_Leave><Fovy>45</Fovy><GroundOffset>0</GroundOffset><IsCameraView>false</IsCameraView>"
                 "<IsCastShadow>false</IsCastShadow><IsCollision>false</IsCollision><IsControllable>false</IsControllable>"
                 f"<OffsetPitch>0</OffsetPitch><OffsetYaw>0</OffsetYaw><Pitch>{AJUSTES['CAMARA_2D_PITCH']:g}</Pitch><Range>100000</Range>"
                 "<Target><SetObjectID>0</SetObjectID></Target><TargetOffset_Front>0</TargetOffset_Front><TargetOffset_Right>0</TargetOffset_Right>"
                 f"<TargetOffset_Up>{AJUSTES['CAMARA_2D_ALTURA']:g}</TargetOffset_Up><TargetOffset_Vel>0</TargetOffset_Vel>"
                 "<TargetPositionFix><x>0</x><y>0</y><z>0</z></TargetPositionFix><Target_Type>0</Target_Type>"
                 f"<VelOffsetXYZ>0</VelOffsetXYZ><Yaw>{yaw:.1f}</Yaw><ZRot>0</ZRot>",
                 (desde + hasta) / 2, 0.0, 3.0)
    volumen_camara(id_cam, (desde + hasta) / 2, 0.0, (z_min + z_max) / 2, hasta - desde, 30.0, z_max - z_min)


def flecha_salida(centro, fondo_z, largo=16.0):
    """Flecha plana (solo visual, morada) en el suelo del pozo apuntando al túnel de salida (rumbo K.th). Referencia
    para ajustar el giro de la cámara de planeo: es correcto cuando, durante el planeo, la flecha apunta hacia arriba
    en la pantalla (prueba de la 0.7.3)."""
    c, s = math.cos(K.th), math.sin(K.th)
    z = fondo_z + 0.02
    cuerpo = largo * 0.6
    SOLO_VISUAL.caja((centro[0] - largo * 0.2 * c, centro[1] - largo * 0.2 * s, z), (cuerpo, largo * 0.16, 0.1), K.th, "costura")
    punta = (centro[0] + largo * 0.5 * c, centro[1] + largo * 0.5 * s)
    brazo = largo * 0.35
    for lado in (1, -1):
        a = K.th + math.pi + lado * math.radians(35)
        SOLO_VISUAL.caja((punta[0] + brazo / 2 * math.cos(a), punta[1] + brazo / 2 * math.sin(a), z),
                         (brazo, largo * 0.16, 0.1), a, "costura")


def zona_planeo(centro, prof, r_boca, giro_camara):
    """Planeo en un pozo vertical: centro = punto de la boca (Blender), prof = profundidad hasta el suelo.
    ChangeDiveBegin en la boca, ChangeDiveEndNoEvent a ~10 m del fondo, y un volumen de cámara que activa una cámara
    paralela que mira casi en vertical (como en Chemical Plant / Speed Highway).
    giro_camara: grados (vista desde arriba) sumados a 90° + rumbo. El pozo final usa 135 (confirmado en la 0.6.2);
    con un solo dato no se sabe si sirve para cualquier rumbo, así que cada pozo lleva el suyo."""
    fondo_z = centro[2] - prof
    obj("ChangeDiveBegin", f"<Collision_Height>{2 * r_boca:g}</Collision_Height><Collision_Length>2</Collision_Length>"
        f"<Collision_Width>{2 * r_boca:g}</Collision_Width>{CAMPOS_DIVE}<Range>300</Range>"
        f"<m_DebugCylinderHeight>{prof}</m_DebugCylinderHeight><m_Range>9</m_Range>",
        pos=(centro[0], centro[1], centro[2] - 4), q=Q_HORIZONTAL)
    obj("ChangeDiveEndNoEvent", "<Collision_Height>30</Collision_Height><Collision_Length>3</Collision_Length>"
        f"<Collision_Width>30</Collision_Width>{CAMPOS_DIVE}<Range>100</Range>",
        pos=(centro[0], centro[1], fondo_z + 8.5), q=Q_HORIZONTAL)    # caja de 3 m de grosor: el planeo acaba a ~10 m del suelo
    alto_vol = prof - 12
    yaw = (math.degrees(math.pi / 2 + K.th) + giro_camara + 180) % 360 - 180
    id_cam = obj("ObjCameraParallel", "<Distance>10</Distance><Ease_Time_Enter>0</Ease_Time_Enter><Ease_Time_Leave>0</Ease_Time_Leave>"
                 "<Fovy>50</Fovy><GroundOffset>0</GroundOffset><IsCameraView>false</IsCameraView><IsCastShadow>false</IsCastShadow>"
                 "<IsCollision>false</IsCollision><IsControllable>false</IsControllable><OffsetPitch>0</OffsetPitch><OffsetYaw>0</OffsetYaw>"
                 "<Pitch>85</Pitch><Range>100000</Range><Target><SetObjectID>0</SetObjectID></Target>"
                 "<TargetOffset_Front>0</TargetOffset_Front><TargetOffset_Right>0</TargetOffset_Right><TargetOffset_Up>0</TargetOffset_Up>"
                 "<TargetOffset_Vel>0</TargetOffset_Vel><TargetPositionFix><x>0</x><y>0</y><z>0</z></TargetPositionFix><Target_Type>0</Target_Type>"
                 f"<VelOffsetXYZ>0</VelOffsetXYZ><Yaw>{yaw:.1f}</Yaw><ZRot>0</ZRot>",
                 pos=(centro[0], centro[1], centro[2]), q=(1.0, 0.0, 0.0, 0.0))
    obj("ChangeVolumeCamera", f"<Collision_Height>{alto_vol:g}</Collision_Height><Collision_Length>28</Collision_Length>"
        "<Collision_Width>28</Collision_Width><DefaultStatus>0</DefaultStatus><Ease_Time_Enter>2</Ease_Time_Enter>"
        "<Ease_Time_Leave>1.1</Ease_Time_Leave><GroundOffset>0</GroundOffset><IsCameraView>false</IsCameraView><IsCastShadow>false</IsCastShadow>"
        "<IsEnableCollision>false</IsEnableCollision><LineType>0</LineType><PositionList /><Priority>0</Priority><Range>300</Range>"
        f"<Shape_Type>0</Shape_Type><Target><SetObjectID>{id_cam}</SetObjectID></Target>",
        pos=(centro[0], centro[1], centro[2] - 2 - alto_vol / 2), q=(1.0, 0.0, 0.0, 0.0))
    camara_aterrizaje(centro, fondo_z)
    flecha_salida(centro, fondo_z)
    # Spinner volando en el centro de la boca, 5 m por encima: un homing desde el borde deja caer centrado (0.7.4)
    enemigo("sph", pos=(centro[0], centro[1], centro[2] + 5.0))
    # el planeo dura ~6 s en 110 m con los parámetros del nivel (Sonic.prm.xml de escenario_bpc)
    sumar_tiempo(prof / 18.0, prof)
    return fondo_z
