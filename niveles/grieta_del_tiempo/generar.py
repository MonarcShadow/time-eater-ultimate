# "Grieta del Tiempo" — versión 0 (caja gris).
# Genera en Blender todo el recorrido de las 8 secciones del diseño (niveles/acto2/diseno.md) con geometría
# simple, coloca los objetos (solo los de riesgo bajo) y escribe set data, Stage.stg.xml, splines y FBX.
#   blender --background --factory-startup --python niveles/grieta_del_tiempo/generar.py -- <carpeta_nivel> <salida>
#
# Ejes: Blender X/Y = plano horizontal, Z = arriba. Juego: (x, y, z) = (bx, bz, -by).
# Rumbo θ (Blender, desde +X hacia +Y). Yaw del juego φ = 90° + θ (comprobado: yaw 90 = avanzar hacia +X).
import importlib.util
import json
import math
import os
import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1:]
carpeta_nivel, salida = os.path.abspath(args[0]), os.path.abspath(args[1])
os.makedirs(salida, exist_ok=True)
with open(os.path.join(carpeta_nivel, "nivel.json"), encoding="utf-8") as f:
    cfg = json.load(f)
SLOT = cfg["slot"]

bpy.ops.wm.read_factory_settings(use_empty=True)
escena = bpy.context.scene
escena.unit_settings.system = "METRIC"
escena.unit_settings.scale_length = 1.0
escena.unit_settings.length_unit = "METERS"

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
MATS = {}
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
ORDEN_MATS = list(MATS)


# ----------------------------------------------------------------------------------------------
# Constructor de geometría: una sola malla con índice de material por cara
# ----------------------------------------------------------------------------------------------
class Malla:
    def __init__(self):
        self.v, self.f, self.mat, self.uv = [], [], [], []

    def quad(self, a, b, c, d, mat, uvs=None):
        i = len(self.v)
        self.v += [a, b, c, d]
        self.f.append((i, i + 1, i + 2, i + 3))
        self.mat.append(ORDEN_MATS.index(mat))
        self.uv.append(uvs or [(0, 0), (1, 0), (1, 1), (0, 1)])

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
SOLO_VISUAL = Malla()  # rieles de grind (sin colisión)
MUERTE = Malla()       # suelos de muerte bajo los huecos (solo colisión, tag DEAD)
OBJETOS = []           # (xml) set data
CURVAS = []            # (nombre, [[puntos riel 1], [puntos riel 2]?])
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

    def frame(self, adelante=0.0, lado=0.0, arriba=0.0):
        c, s = math.cos(self.th), math.sin(self.th)
        return (self.x + adelante * c - lado * s, self.y + adelante * s + lado * c, self.z + arriba)

    def avanzar(self, d, dz=0.0):
        self.x += d * math.cos(self.th)
        self.y += d * math.sin(self.th)
        self.z += dz


K = Cursor()


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


class en:
    """with en(tramo, s): coloca temporalmente el cursor en el punto s del tramo (sobre la carretera)."""

    def __init__(self, tramo, s):
        self.t, self.s = tramo, s

    def __enter__(self):
        self.guardado = (K.x, K.y, K.z, K.th)
        K.x, K.y, K.z, K.th = self.t.estado(self.s)
        return K

    def __exit__(self, *exc):
        K.x, K.y, K.z, K.th = self.guardado


def carretera(largo, ancho=12.0, dz=0.0, giro_grados=0.0, muros=1.2, mat="gris", mat_muro=None, paso=4.0, grosor=2.0):
    """Tramo de carretera desde el cursor: largo (m), desnivel total dz, giro total (curva suave). Devuelve un Tramo."""
    n = max(1, int(math.ceil(largo / paso)))
    giro = math.radians(giro_grados)
    secciones = []
    for i in range(n + 1):
        secciones.append((K.x, K.y, K.z, K.th, i * largo / n))
        if i < n:
            K.th += giro / n / 2
            K.avanzar(largo / n, dz / n)
            K.th += giro / n / 2
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
        if muros:
            for lado in (-ancho / 2, ancho / 2):
                p0, p1 = borde(x0, y0, z0, t0, lado, 0), borde(x1, y1, z1, t1, lado, 0)
                q0, q1 = borde(x0, y0, z0, t0, lado, muros), borde(x1, y1, z1, t1, lado, muros)
                if lado < 0:
                    SOLIDO.quad(p0, p1, q1, q0, mm)
                else:
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


def xyz(tag, p):
    return f"<{tag}><x>{p[0]:.3f}</x><y>{p[1]:.3f}</y><z>{p[2]:.3f}</z></{tag}>"


def rot(q):
    return f"<Rotation><w>{q[0]:.6f}</w><x>{q[1]:.6f}</x><y>{q[2]:.6f}</y><z>{q[3]:.6f}</z></Rotation>"


def obj(tipo, campos, adelante=0.0, lado=0.0, arriba=0.0, q=None, pos=None):
    p = a_juego(pos if pos else K.frame(adelante, lado, arriba))
    q = q or q_yaw()
    OBJETOS.append(f"  <{tipo}>{campos}{xyz('Position', p)}{rot(q)}<SetObjectID>{nuevo_id()}</SetObjectID></{tipo}>")
    return p


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
        f"<Speed>{velocidad}</Speed><SpeedMax>60</SpeedMax><SpeedMin>30</SpeedMin>", adelante, lado, 0.0)


def resorte_vertical(adelante, lado=0.0, arriba=0.0, velocidad=30, a_3d=False):
    obj("Spring", "<AimDirection>0</AimDirection><BaseRotation>0</BaseRotation><DebugShotTimeLength>2</DebugShotTimeLength>"
        f"<FirstSpeed>{velocidad}</FirstSpeed><GroundOffset>0</GroundOffset><IsBreak>false</IsBreak><IsCastShadow>true</IsCastShadow>"
        "<IsChangeCameraWhenPathChange>true</IsChangeCameraWhenPathChange><IsHomingAttackEnable>false</IsHomingAttackEnable>"
        "<IsLongBase>false</IsLongBase><IsPathChange>false</IsPathChange><IsSideSet>false</IsSideSet>"
        "<IsStartVelocityConstant>true</IsStartVelocityConstant><IsWallWalk>false</IsWallWalk><IsWithBase>false</IsWithBase>"
        "<IsYawUpdate>false</IsYawUpdate><KeepVelocityDistance>5</KeepVelocityDistance><MotionType>0</MotionType>"
        "<OutOfControl>0.4</OutOfControl><Range>60</Range><m_IsConstantFrame>false</m_IsConstantFrame>"
        "<m_IsConstantPosition>true</m_IsConstantPosition><m_IsMonkeyHunting>false</m_IsMonkeyHunting>"
        f"<m_IsStopBoost>false</m_IsStopBoost><m_IsTo3D>{'true' if a_3d else 'false'}</m_IsTo3D>"
        "<m_MonkeyTarget><x>0</x><y>0</y><z>0</z></m_MonkeyTarget>",
        adelante, lado, arriba, q=(1.0, 0.0, 0.0, 0.0))


def rampa_salto(adelante, lado=0.0, boost=50, normal=35):
    obj("JumpBoard", "<AngleType>0</AngleType><GroundOffset>0</GroundOffset>"
        f"<ImpulseSpeedOnBoost>{boost}</ImpulseSpeedOnBoost><ImpulseSpeedOnNormal>{normal}</ImpulseSpeedOnNormal>"
        "<IsCastShadow>false</IsCastShadow><IsTo3D>false</IsTo3D><LookBack>false</LookBack><OutOfControl>1.5</OutOfControl>"
        "<Range>60</Range><RigidBody>true</RigidBody>", adelante, lado, 0.0)


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
            c = (a[0] + dx * (t0 + t1) / 2, a[1] + dy * (t0 + t1) / 2, a[2] + dz * (t0 + t1) / 2 - 0.15)
            SOLO_VISUAL.caja(c, (largo / n + 0.05, 0.25, 0.25), math.atan2(dy, dx), "costura")


# ==============================================================================================
# EL RECORRIDO
# ==============================================================================================
ZONAS = ("ghz", "cpz", "ssz", "sph", "cte", "ssh", "csc", "euc", "pla")
INICIO = K.frame(2, 0, 0.1)

# --- 1. Colina contaminada: Green Hill + tuberías de Chemical Plant + cielo de Speed Highway -----
t = carretera(40, ancho=14, mat="ghz")
anillos(10, 30, tramo=t)
for i, s in enumerate((10, 22, 34)):                         # tuberías de Chemical Plant reventando la colina
    with en(t, s):
        decorado(0, 13 + i, -2, (5, 5, 9 + 3 * i), "cpz", 20 * i)
with en(t, 36):
    dash_panel(0)
t = carretera(70, ancho=14, giro_grados=-45, dz=-8, mat="ghz", mat_muro="cpz")
with en(t, 35):
    decorado(0, 15, -4, (8, 8, 14), "cpz", 30)
with en(t, 50):
    decorado(0, -16, -4, (6, 6, 20), "sph")                  # torre nocturna de Speed Highway al otro lado
anillos(10, 60, cada=5, tramo=t)
t = carretera(30, ancho=14, mat="ghz")
with en(t, 5):
    dash_panel(0)
with en(t, 25):                                              # arco de "costura" morada sobre la pista
    decorado(0, 0, 6, (2, 14, 1), "costura")
    decorado(0, -7.5, 0, (2, 1, 6), "costura")
    decorado(0, 7.5, 0, (2, 1, 6), "costura")
# tramo 2D: plataformas sobre tuberías y Mega Mack (la primera plataforma empieza donde acaba la carretera)
a_2d(2)
curva_recta("s1_2d@SV", -5, 95, rieles=(-1.0, 1.0))
suelo_muerte(0, 90)
alturas = (0, 1.5, 3.0, 1.0, 2.5, 0)
x2d = 0.0
for i, h in enumerate(alturas):
    largo = 9.0 if i < len(alturas) - 1 else 12.0
    plataforma(x2d, 0, h, largo, 6, alto=3, mat="ghz" if i % 2 == 0 else "cpz")
    anillos(x2d + 2, x2d + largo - 2, cada=2.0, arriba=h + 0.8)
    if i == 2:
        resorte_vertical(x2d + largo - 1.5, 0, h, velocidad=22)
    decorado(x2d + largo / 2, 0, h - 13, (3, 5, 9), "cpz")     # tubo de Chemical Plant bajo cada plataforma
    if i < len(alturas) - 1:
        x2d += largo + 5.0
x2d += 12.0                                                  # fin de la última plataforma
K.avanzar(x2d)
a_2d(-3, salida=True)
carretera(30, ancho=14, mat="ghz")

# --- 2. Calle sobre las ruinas: City Escape + Sky Sanctuary (+ Egg Fighters de Rooftop Run en la v1) ---
carretera(20, ancho=16, mat="cte")
a_quickstep(-5)
curva_recta("s2_qs@QS", -5, 205, arriba=0.0)
t = carretera(200, ancho=16, dz=-25, mat="cte", mat_muro="ssz")
# curva_recta es recta y horizontal: el quickstep va en bajada, así que la spline se recalcula sobre el tramo
CURVAS[-1] = ("s2_qs@QS", [[t.estado(s)[:3] for s in range(0, 201, 25)]])
for s, lado in ((30, -4), (50, 4), (70, 0), (90, -4), (105, 4), (120, 0), (140, -4), (155, 4)):   # "autos" por carril
    with en(t, s):
        decorado(0, lado, 0, (3.5, 2.2, 1.6), "cte")
for s in (15, 60, 100, 130, 170):
    anillos(s, s + 10, cada=2.5, tramo=t)
for s in (40, 110, 180):                                     # columnas de ruinas a los lados
    with en(t, s):
        decorado(0, -11, -20, (4, 4, 30), "ssz")
        decorado(8, 11, -20, (4, 4, 34), "ssz")
with en(t, 196):
    a_quickstep(0, salida=True)
with en(t, 186):
    dash_panel(0)
with en(t, 197):
    rampa_salto(0)
# islas de asfalto sobre las nubes (huecos entre islas)
suelo_muerte(0, 120, ancho=40, profundidad=25)
K.avanzar(22)
for i in range(3):
    t = carretera(18, ancho=12, mat="cte" if i % 2 == 0 else "ssz", muros=0)
    anillos(4, 14, cada=2.5, tramo=t)
    with en(t, 9):
        decorado(0, 0, -12, (10, 8, 10), "ssz")                # ruina flotante bajo la isla
    K.avanzar(9)
carretera(25, ancho=14, mat="ssz")

# --- 3. Mar en llamas: Seaside Hill + lava de Crisis City + tornado ----------------------------------
t = carretera(160, ancho=34, giro_grados=35, mat="ssh", mat_muro="ssh", muros=0.6)
for s, lado in ((20, -6), (45, 8), (70, -3), (95, 10), (120, -8)):           # manchas de lava (decorado bajo)
    with en(t, s):
        decorado(0, lado, 0, (10, 7, 0.15), "csc")
for s, lado in ((35, 13), (85, -14), (130, 12)):                             # pilares de las ruinas
    with en(t, s):
        decorado(0, lado, 0, (3, 3, 10), "ssh")
with en(t, 140):
    decorado(0, -30, -10, (12, 12, 60), "csc", 15)                          # "tornado" de Crisis City (columna)
with en(t, 100):
    decorado(0, 30, -10, (6, 6, 25), "ghz")                                 # puente de Green Hill arrastrado
anillos(10, 140, cada=6, tramo=t)
for s in (60, 110, 146):
    with en(t, s):
        dash_panel(0)
with en(t, 158):
    rampa_salto(0, boost=55, normal=40)
suelo_muerte(0, 40, ancho=50, profundidad=20)
K.avanzar(28)

# --- 4. Fábrica dentro de la torre: Planet Wisp + Rooftop Run + Chemical Plant (2D, subida) ----------
carretera(30, ancho=20, mat="euc", muros=0)
plataforma(0, 0, 0, 34, 10, alto=2, mat="euc")                            # suelo de la torre bajo la escalera (si caes, vuelves al resorte)
decorado(-15, -12, 0, (30, 2, 45), "euc")                                 # paredes de la torre
decorado(-15, 12, 0, (30, 2, 45), "euc")
a_2d(-8)
curva_recta("s4_2d@SV", -12, 40, rieles=(-1.0, 1.0))
# escalera hacia adelante: cada resorte queda fuera de la proyección de la plataforma siguiente
resorte_vertical(-4, 0, 0, velocidad=26)
escalones = [(0, 6, 8), (6, 12, 8), (12, 18, 8), (18, 24, 14)]           # (inicio, altura, largo)
for i, (ini, h, largo) in enumerate(escalones):
    plataforma(ini, 0, h, largo, 6, alto=1.2, mat="pla" if i % 2 == 0 else "cpz")
    anillos(ini + 1, ini + largo - 1, cada=2.0, arriba=h + 1.0)
    if i < len(escalones) - 1:
        resorte_vertical(ini + 2, 0, h, velocidad=26)
decorado(26, 0, 31, (6, 6, 1.5), "pla")                                   # "prensa" de Planet Wisp sobre la salida
a_2d(28, salida=True, arriba=24)                                          # salida a 3D arriba de la escalera
K.avanzar(32)
K.z += 24

# --- 5. Rascacielos invertido: Speed Highway + fachada de Chemical Plant + cascada de Green Hill ------
carretera(15, ancho=14, mat="sph")
t = carretera(150, ancho=14, dz=-60, mat="cpz", mat_muro="sph")          # bajada empinada por la "fachada"
for s in (10, 50, 90, 130):
    with en(t, s):
        dash_panel(0)
anillos(20, 140, cada=8, tramo=t)
for s in (30, 80, 125):                                                   # reflectores de Speed Highway
    with en(t, s):
        decorado(0, -9, 0, (1.5, 1.5, 4), "sph")
with en(t, 110):
    decorado(0, 20, -60, (14, 6, 50), "ghz")                              # cascada de Green Hill al costado
carretera(35, ancho=14, mat="ghz")
resorte_vertical(-5, 0, 0, velocidad=30)
plataforma(0, 0, 8, 30, 14, alto=8, mat="sph")                            # escalón de 8 m (subir con el resorte)
K.avanzar(30)
K.z += 8

# --- 6. Persecución desincronizada: tejados de Rooftop Run que colapsan como Sky Sanctuary --------------
for i in range(5):
    t = carretera(26, ancho=14, mat="euc" if i % 2 == 0 else "ssz", muros=0.5, mat_muro="cte")
    anillos(4, 20, cada=4, tramo=t)
    if i % 2 == 1:
        with en(t, 6):
            dash_panel(0)
    with en(t, 13):
        decorado(0, -10, -20, (16, 4, 18), "euc")                         # fachadas de Spagonia
    suelo_muerte(0, 7, ancho=40, profundidad=18)
    K.avanzar(7)
decorado(-40, 25, -15, (30, 8, 6), "ssh")                                 # el mar a la altura de los tejados
# riel de grind sobre el vacío hasta el siguiente tejado
carretera(10, ancho=14, mat="euc", muros=0)
p0 = K.frame(-6, 0, 0.35)
p1 = K.frame(40, 0, -3)
p2 = K.frame(90, 0, -8)
riel_grind("s6_riel@GR", [p0, p1, p2])
grind_dash(tuple(a + (b - a) * 0.1 for a, b in zip(p0, p1)))   # panel de grind al 10 % del primer tramo del riel
suelo_muerte(4, 85, ancho=40, profundidad=25)
K.avanzar(88)
K.z -= 8.35
carretera(30, ancho=14, mat="euc")

# --- 7. Caída de las 9 eras: pozo con forma de reloj de 9 horas -----------------------------------------
carretera(12, ancho=14, mat="costura", muros=0)
centro = K.frame(16, 0, 0)
PROF = 110
fondo_z = centro[2] - PROF
ang_entrada = K.th + math.pi
ang_salida = K.th


def dif_ang(a, b):
    return abs((a - b + math.pi) % (2 * math.pi) - math.pi)


for i, zona in enumerate(ZONAS):
    ang = 2 * math.pi * i / 9
    cx, cy = centro[0] + 16 * math.cos(ang), centro[1] + 16 * math.sin(ang)
    base = fondo_z
    tope = centro[2] + 14                               # paredes altas: frenan a Sonic si salta de más
    if dif_ang(ang, ang_entrada) < math.radians(25):
        tope = centro[2] - 3                            # la "hora" de la entrada es baja: se entra por encima
    if dif_ang(ang, ang_salida) < math.radians(25):
        base = fondo_z + 9                              # la de la salida deja un túnel abajo
    SOLIDO.caja((cx, cy, base), (4, 11, tope - base), ang, zona)
    for k in range(3):                                  # escombros de cada era hacia el centro
        r = 11 - k * 1.5
        SOLIDO.caja((centro[0] + r * math.cos(ang + 0.3), centro[1] + r * math.sin(ang + 0.3), centro[2] - 25 - 30 * k - i * 2),
                    (2.5, 2.5, 1.5), ang, zona)
for k in range(12):                                     # anillos en la caída
    obj("Ring", CAMPOS_RING, pos=(centro[0], centro[1], centro[2] - 10 - 8 * k))
SOLIDO.caja((centro[0], centro[1], fondo_z - 2), (44, 44, 2), K.th, "blanco")   # suelo blanco al fondo
MIN_Z[0] = min(MIN_Z[0], fondo_z - 2)

# --- 8. Blanco: White Space, todo desteñido; meta frente al ojo del Time Eater -------------------------
K.x, K.y = centro[0] + 20 * math.cos(K.th), centro[1] + 20 * math.sin(K.th)
K.z = fondo_z
carretera(90, ancho=16, mat="blanco", muros=0.4)
for i, zona in enumerate(ZONAS):                                          # piezas quietas y desteñidas
    lado = -18 if i % 2 else 18
    decorado(-85 + i * 9, lado, 2 + (i % 3) * 3, (5, 5, 5), "blanco", 25 * i)
riel_grind("s8_aguja@GR", [K.frame(-70, -5, 0.35), K.frame(-40, -5, 0.35)])  # la aguja del reloj
anillos(-80, -45, cada=5, lado=4)
decorado(30, 0, 25, (4, 30, 30), "costura")                               # el "ojo" del Time Eater en el cielo
obj("GoalRing", "<GroundOffset>0</GroundOffset><IsCastShadow>true</IsCastShadow><IsMessageOn>false</IsMessageOn><Radius>4</Radius>"
    f"<Range>200</Range>{xyz('ResultPosition', a_juego(K.frame(-20, 0, 0)))}<SENumber>6</SENumber>",
    -20, 0, 1.5, q=(0.707107, 0.707107, 0.0, 0.0))
FINAL = K.frame(0, 0, 0)

# ==============================================================================================
# Escena de Blender, exportación y XML
# ==============================================================================================
def coleccion(nombre):
    c = bpy.data.collections.new(nombre)
    escena.collection.children.link(c)
    return c


col_nivel, col_col, col_spl, col_ref = coleccion("Nivel"), coleccion("Colision"), coleccion("Splines"), coleccion("Referencias")
ob_solido = SOLIDO.objeto("teu_camino", col_nivel)
ob_rieles = SOLO_VISUAL.objeto("teu_rieles", col_nivel)
ob_col = SOLIDO.objeto("teu_camino_col@ROCK", col_col)
ob_muerte = MUERTE.objeto("teu_muerte_col@DEAD", col_col)
ref = Malla()
ref.caja(INICIO, (0.5, 0.5, 1.0), 0, "gris")
r = ref.objeto("REF_Sonic", col_ref)
r.display_type = "WIRE"

obs_curvas = []
for nombre, rieles in CURVAS:
    cu = bpy.data.curves.new(nombre, type="CURVE")
    cu.dimensions = "3D"
    for pts in rieles:
        s = cu.splines.new("POLY")
        s.points.add(len(pts) - 1)
        for i, p in enumerate(pts):
            s.points[i].co = (p[0], p[1], p[2], 1.0)
    ob = bpy.data.objects.new(nombre, cu)
    col_spl.objects.link(ob)
    obs_curvas.append(ob)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(salida, cfg["nombre"] + ".blend"))


def seleccionar(objs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]


def exportar_fbx(objs, ruta):
    seleccionar(objs)
    bpy.ops.export_scene.fbx(filepath=ruta, use_selection=True, apply_scale_options="FBX_SCALE_UNITS",
                             add_leaf_bones=False, object_types={"MESH"}, path_mode="COPY", embed_textures=False)


exportar_fbx([ob_solido, ob_rieles], os.path.join(salida, "teu_camino.fbx"))
exportar_fbx([ob_col, ob_muerte], os.path.join(salida, "teu_camino_col.fbx"))

herr = os.environ.get("TEU_HERRAMIENTAS") or os.path.join(carpeta_nivel, "..", "..", "herramientas")
spec = importlib.util.spec_from_file_location("BlenderToXML", os.path.join(herr, "blender-scripts", "BlenderToXML.py"))
b2x = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b2x)
seleccionar(obs_curvas)
b2x.xmlPath = os.path.join(salida, SLOT + ".path.xml")
b2x.processData()

# XML generados (se copian al archivo #<slot> y reemplazan a los de escenario_<slot>)
dir_xml = os.path.join(salida, "escenario")
os.makedirs(dir_xml, exist_ok=True)
with open(os.path.join(dir_xml, "setdata_base.set.xml"), "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="utf-8" standalone="no" ?>\n<SetObject>\n' + "\n".join(OBJETOS) + "\n</SetObject>\n")
inicio_j = a_juego(INICIO)
dead = math.floor(MIN_Z[0] - 40)
with open(os.path.join(dir_xml, "Stage.stg.xml"), "w", encoding="utf-8") as f:
    f.write(f"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!-- Grieta del Tiempo v0 (caja gris), generado por niveles/grieta_del_tiempo/generar.py -->
<Stage>
  <Sonic>
    {xyz('Position', inicio_j)}
    <Yaw>90</Yaw>
    <Start>
      <Mode>None</Mode>
      <Speed>0</Speed>
      <Time>0</Time>
    </Start>
    <DeadHeight>{dead}</DeadHeight>
    <CameraView>Forward</CameraView>
  </Sonic>
  <BGM>
    <IsStream>true</IsStream>
    <Container>{cfg.get("bgm_container", "SNG15_BPC")}</Container>
    <Name>{cfg.get("bgm_nombre", "Boss_Perfect_Chaos1")}</Name>
  </BGM>
  <Path>
    <Container>{SLOT}</Container>
    <SingleForward>
      <Name>s2_qs@QS</Name>
      <PathNum>3</PathNum>
      <Space>4</Space>
    </SingleForward>
    <IsTerrain>false</IsTerrain>
    <IsAutoLoad>true</IsAutoLoad>
    <IsRender>false</IsRender>
  </Path>
</Stage>
""")

print(f"TEU_RESUMEN objetos={len(OBJETOS)} caras={len(SOLIDO.f)} splines={len(CURVAS)} deadheight={dead} "
      f"final=({FINAL[0]:.0f},{FINAL[1]:.0f},{FINAL[2]:.0f})")
print("TEU_ESCENA_OK", salida)
