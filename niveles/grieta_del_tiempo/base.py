# Herramientas comunes del generador de "Grieta del Tiempo": geometría (Malla), cursor del recorrido, carreteras,
# objetos del set data, plantillas de enemigos, checkpoints, cámara de planeo y estimación del tiempo de juego.
# Lo usan generar.py y cada sección (secciones/sNN_*.py) con "from base import *".
#
# Ejes: Blender X/Y = plano horizontal, Z = arriba. Juego: (x, y, z) = (bx, bz, -by).
# Rumbo θ (Blender, desde +X hacia +Y). Yaw del juego φ = 90° + θ (comprobado: yaw 90 = avanzar hacia +X).
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
ORDEN_MATS = list(COLORES)
MATS = {}
ZONAS = ("ghz", "cpz", "ssz", "sph", "cte", "ssh", "csc", "euc", "pla")


def crear_materiales(salida):
    for nombre, (ca, cb) in COLORES.items():
        img = bpy.data.images.new(f"teu_{nombre}_dif", 128, 128)
        pix = []
        for y in range(128):
            for x in range(128):
                r, g, b = ca if ((x // 16) + (y // 16)) % 2 else cb
                pix += [r, g, b, 1.0]
        img.pixels = pix
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
        self.mat.append(ORDEN_MATS.index(mat))
        self.uv.append(uvs or [(0, 0), (1, 0), (1, 1), (0, 1)][:len(pts)])

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
            self.quad(*pts, mat, [(0, 0), (L / 4, 0), (L / 4, H / 4 + W / 4), (0, H / 4 + W / 4)])

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
OBJETOS = []           # (xml) set data
CURVAS = []            # (nombre, [[puntos riel 1], [puntos riel 2]?])
QUICKSTEPS = []        # nombres de splines @QS (se declaran en Stage.stg.xml como SingleForward)
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
              muro_izq=None, muro_der=None):
    """Tramo de carretera desde el cursor: largo (m), desnivel total dz, giro total (curva suave). Devuelve un Tramo.
    muro_izq / muro_der (altura en m) permiten un muro distinto por lado; izquierda = lado +, derecha = lado −."""
    alturas_muro = {ancho / 2: muros if muro_izq is None else muro_izq, -ancho / 2: muros if muro_der is None else muro_der}
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
        a, b = borde(x0, y0, z0, t0, -ancho / 2, 0), borde(x1, y1, z1, t1, -ancho / 2, 0)
        c, d = borde(x1, y1, z1, t1, ancho / 2, 0), borde(x0, y0, z0, t0, ancho / 2, 0)
        uvs = [(s0 / 4, -ancho / 8), (s1 / 4, -ancho / 8), (s1 / 4, ancho / 8), (s0 / 4, ancho / 8)]
        SOLIDO.quad(a, b, c, d, mat, uvs)                                            # superficie
        ab, bb = borde(x0, y0, z0, t0, -ancho / 2, -grosor), borde(x1, y1, z1, t1, -ancho / 2, -grosor)
        cb, db = borde(x1, y1, z1, t1, ancho / 2, -grosor), borde(x0, y0, z0, t0, ancho / 2, -grosor)
        SOLIDO.quad(db, cb, bb, ab, mat)                                             # fondo
        SOLIDO.quad(ab, bb, b, a, mat)                                               # lateral izq.
        SOLIDO.quad(c, cb, db, d, mat)                                               # lateral der.
        for lado, alto_muro in alturas_muro.items():
            if not alto_muro:
                continue
            p0, p1 = borde(x0, y0, z0, t0, lado, 0), borde(x1, y1, z1, t1, lado, 0)
            q0, q1 = borde(x0, y0, z0, t0, lado, alto_muro), borde(x1, y1, z1, t1, lado, alto_muro)
            SOLIDO.quad(p0, p1, q1, q0, mm)          # dos caras: se ve y colisiona desde ambos lados
            SOLIDO.quad(p1, p0, q0, q1, mm)
    MIN_Z[0] = min(MIN_Z[0], min(sec[2] for sec in secciones) - grosor)
    return Tramo(secciones)


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


def suelo_muerte(adelante, largo, ancho=30.0, profundidad=15.0):
    x, y, z = K.frame(adelante + largo / 2, 0, -profundidad)
    MUERTE.caja((x, y, z - 1), (largo, ancho, 1.0), K.th, "gris")
    MIN_Z[0] = min(MIN_Z[0], z - 1)


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


def anillos(desde, hasta, cada=2.5, lado=0.0, arriba=0.8, tramo=None):
    """Fila de anillos. Con tramo, 'desde'/'hasta' son distancias sobre el tramo (siguen curvas y pendientes)."""
    d = desde
    while d <= hasta + 1e-6:
        if tramo:
            with en(tramo, d):
                obj("Ring", CAMPOS_RING, 0, lado, arriba)
        else:
            obj("Ring", CAMPOS_RING, d, lado, arriba)
        d += cada


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
    Calibrado en el juego: hueco de 28 m -> 60/60 ángulo 0; hueco de 22 m (a una isla) -> 68/62 ángulo 1."""
    obj("JumpBoard", f"<AngleType>{angulo}</AngleType><GroundOffset>0</GroundOffset>"
        f"<ImpulseSpeedOnBoost>{boost}</ImpulseSpeedOnBoost><ImpulseSpeedOnNormal>{normal}</ImpulseSpeedOnNormal>"
        "<IsCastShadow>false</IsCastShadow><IsTo3D>false</IsTo3D><LookBack>false</LookBack><OutOfControl>1.5</OutOfControl>"
        "<Range>60</Range><RigidBody>true</RigidBody>", adelante, lado, 0.0,
        q=q_superficie(math.pi))      # el frente del JumpBoard es el contrario al del DashPanel (probado en 0.4.0)


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
    "csc": ("EnemyTaker3D", 0.0, ["EnemyTaker"]),
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


def enemigo(zona, adelante=0.0, lado=0.0):
    """Enemigo de la zona indicada, mirando hacia Sonic. Los puntos de patrulla (WayPointA/B) de la plantilla se
    sustituyen por la posición del enemigo (en los originales eran su propia posición)."""
    if zona not in ENEMIGOS_ACTIVOS:
        zona = "euc"
    tipo, alto, _ = ENEMIGOS[zona]
    ZONAS_USADAS.add(zona)
    p = a_juego(K.frame(adelante, lado, alto))
    campos = PLANTILLAS[tipo]
    for wp in ("WayPointA", "WayPointB"):
        m = re.search(f"<{wp}><x>([^<]*)</x><y>([^<]*)</y><z>([^<]*)</z></{wp}>", campos)
        if m and any(float(v) != 0.0 for v in m.groups()):
            campos = campos.replace(m.group(0), xyz(wp, p))
    return obj(tipo, campos, adelante, lado, alto, q=q_yaw(math.pi))


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


def grind_dash(pos_blender, velocidad=60):
    obj("GrindDashPanel", "<GroundOffset>0</GroundOffset><IsCastShadow>true</IsCastShadow><IsFront>true</IsFront>"
        f"<IsStartVelocityConstant>true</IsStartVelocityConstant><OutOfControl>2.5</OutOfControl><Range>100</Range><Speed>{velocidad}</Speed>",
        pos=pos_blender)


def cambio_modo(tipo, adelante, salida=False, ancho=30, alto=40, extra="", arriba=0.0):
    """Trigger de cambio de modo. Cruzarlo en su dirección activa el modo; un trigger girado 180° (salida)
    se cruza 'por detrás' y devuelve al modo 3D normal."""
    p = K.frame(adelante, 0, arriba)
    pj = a_juego(p)
    destino = (pj[0], pj[1] - 5.0, pj[2])
    q = q_yaw(math.pi if salida else 0.0)
    campos = (f"<Collision_Height>{alto}</Collision_Height><Collision_Width>{ancho}</Collision_Width><GroundOffset>0</GroundOffset>"
              f"<IsCastShadow>true</IsCastShadow><Range>100</Range>{xyz('TargetDirection', destino)}"
              "<m_IsChangeCamera>true</m_IsChangeCamera><m_IsEnableFromBack>true</m_IsEnableFromBack>"
              f"<m_IsEnableFromFront>true</m_IsEnableFromFront>{extra}")
    obj(tipo, campos, adelante, 0, arriba, q=q)


def a_2d(adelante, salida=False, arriba=0.0):
    cambio_modo("ChangeMode_3Dto2D", adelante, salida, arriba=arriba,
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
        n = max(1, int(largo / 2))
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            # barra fina con la cara superior 0,10 m bajo la spline (Sonic apoya los pies en la spline)
            c = (a[0] + dx * (t0 + t1) / 2, a[1] + dy * (t0 + t1) / 2, a[2] + dz * (t0 + t1) / 2 - 0.25)
            SOLO_VISUAL.caja(c, (largo / n + 0.05, 0.15, 0.15), math.atan2(dy, dx), "costura")


# ----------------------------------------------------------------------------------------------
# Patrones de recorrido reutilizables
# ----------------------------------------------------------------------------------------------
def tramo_2d(nombre, alturas, mats=("gris", "gris"), largo_plat=9.0, hueco=5.0, ancho=6.0, tubos=None,
             resortes=(), ancho_salida=14, mat_salida="gris"):
    """Tramo de plataformas en 2D (patrón de la sección 1, probado en el juego). Se llama al final de una carretera
    recta de al menos 20 m: el cambio a 2D va 12 m antes del final; la vuelta a 3D, 8 m dentro de la carretera de
    salida (30 m), que esta función también crea. alturas: altura de cada plataforma respecto al suelo (subidas de
    1,5 m como máximo, o un resorte en 'resortes' = índices de plataforma). Devuelve el Tramo de salida."""
    ritmo("2d")
    a_2d(-12)
    total = len(alturas) * largo_plat + (len(alturas) - 1) * hueco + 3.0
    curva_recta(f"{nombre}@SV", -17, total + 20, rieles=(-1.0, 1.0))
    suelo_muerte(0, total, profundidad=15 + max(alturas))
    x = 0.0
    for i, h in enumerate(alturas):
        largo = largo_plat + (3.0 if i == len(alturas) - 1 else 0.0)
        plataforma(x, 0, h, largo, ancho, alto=3, mat=mats[i % len(mats)])
        anillos(x + 2, x + largo - 2, cada=2.0, arriba=h + 0.8)
        if i in resortes:
            resorte_vertical(x + largo - 1.5, 0, h, velocidad=26)
        if tubos:
            tubo((x + largo / 2, 0, h - 16), (x + largo / 2, 0, h - 3.1), 1.8, tubos)
        x += largo + hueco
    x -= hueco
    K.avanzar(x, alturas[-1])          # la carretera de salida va a la altura de la última plataforma
    sumar_tiempo(x / VEL["2d"], x)
    ritmo("3d")
    a_2d(8, salida=True)
    return carretera(30, ancho=ancho_salida, mat=mat_salida)


def plataformas_3d(n, largo=18.0, hueco=7.0, ancho=10.0, mats=("gris",), dz=(0.0,), muerte=25.0, enemigos=None):
    """Serie de plataformas flotantes en 3D separadas por huecos que se saltan sin ayuda (7 m a velocidad normal).
    dz: cambio de altura al pasar a cada plataforma (cíclico; ±1,5 m como máximo). enemigos: zona o None."""
    ritmo("plataformas")
    total = n * largo + (n - 1) * hueco
    suelo_muerte(-2, total + 4, ancho=40, profundidad=muerte)
    for i in range(n):
        if i:
            K.avanzar(hueco, dz[i % len(dz)])
            sumar_tiempo(hueco / VEL["plataformas"], hueco)
        t = carretera(largo, ancho=ancho, mat=mats[i % len(mats)], muros=0)
        anillos(4, largo - 4, cada=3, tramo=t)
        if enemigos and i % 2 == 1:
            with en(t, largo / 2):
                enemigo(enemigos, 0, 2.5 if i % 4 == 1 else -2.5)
    ritmo("3d")


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


def riel(nombre, largo, caida, plataforma_final=40, ancho=14, mat="gris"):
    """Riel de grind sobre el vacío desde el final de una carretera: baja 'caida' m en 'largo' m.
    Crea la carretera de llegada (sin paneles, para frenar)."""
    p0 = K.frame(-6, 0, 0.35)
    p1 = K.frame(largo * 0.45, 0, -caida * 0.4)
    p2 = K.frame(largo, 0, -caida)
    riel_grind(f"{nombre}@GR", [p0, p1, p2])
    grind_dash(tuple(a + (b - a) * 0.1 for a, b in zip(p0, p1)))
    suelo_muerte(4, largo - 5, ancho=40, profundidad=caida + 17)
    K.avanzar(largo - 2, -caida - 0.35)
    sumar_tiempo(largo / VEL["grind"], largo)
    return carretera(plataforma_final, ancho=ancho, mat=mat)


# ----------------------------------------------------------------------------------------------
# Planeo: ChangeDiveBegin/End + cámara desde arriba
# ----------------------------------------------------------------------------------------------
CAMPOS_DIVE = "<DefaultStatus>0</DefaultStatus><GroundOffset>0</GroundOffset><IsCastShadow>false</IsCastShadow><Shape_Type>0</Shape_Type>"
Q_HORIZONTAL = (0.707107, 0.707107, 0.0, 0.0)           # caja tumbada, como en Chemical Plant


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
    # el planeo dura ~6 s en 110 m con los parámetros del nivel (Sonic.prm.xml de escenario_bpc)
    sumar_tiempo(prof / 18.0, prof)
    return fondo_z
