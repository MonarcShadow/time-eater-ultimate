# 12. Caída de las 9 eras: pozo con forma de reloj de 9 horas (~20 s de planeo desde la 0.7.2)
# La entrada es un agujero en el suelo: una explanada (anillo) rodea la boca del pozo, y un ChangeDiveBegin
# horizontal en la boca activa el planeo (parámetros copiados de Chemical Plant / Speed Highway).
from base import *  # noqa: F401,F403

# Giro de la cámara de planeo (grados, vista desde arriba): se ajusta en ajustes.conf (GIRO_CAMARA_PLANEO).
# 135 confirmado en el juego (0.6.2) para este pozo.
GIRO_CAMARA_PLANEO = AJUSTES["GIRO_CAMARA_PLANEO"]
# Rumbo con el que se confirmó ese giro (grados). Si las secciones anteriores cambian el rumbo de llegada, el giro
# deja de estar comprobado y el generador avisa.
RUMBO_CONFIRMADO = -10.0
# Profundidad del pozo: el planeo cae a ~18 m/s (DivingFloatMaxVelocityDown del Sonic.prm.xml del nivel) y va de
# la boca −4 m hasta 8,5 m sobre el fondo: 370 m ≈ 20 s (pedido en la prueba de la 0.7.1; antes 110 m ≈ 6 s).
PROF = 370
SALIDA = {}


def construir():
    seccion("12 Caída de las 9 eras")
    rumbo = math.degrees(K.th)
    if abs((rumbo - RUMBO_CONFIRMADO + 180) % 360 - 180) > 0.5:
        print(f"TEU_AVISO el pozo final llega con rumbo {rumbo:.1f}° (confirmado con {RUMBO_CONFIRMADO}°): revisar la cámara")
    carretera(12, ancho=14, mat="costura", muros=0)
    R_BOCA, R_EXPLANADA = 13.0, 26.0
    centro = K.frame(R_EXPLANADA, 0, 0)
    fondo_z = centro[2] - PROF
    ang_entrada = K.th + math.pi
    ang_salida = K.th

    def dif_ang(a, b):
        return abs((a - b + math.pi) % (2 * math.pi) - math.pi)

    SEG = 24                                                # explanada: anillo entre la boca y el borde exterior
    for k in range(SEG):
        a0, a1 = 2 * math.pi * k / SEG, 2 * math.pi * (k + 1) / SEG

        def pt(r, a, dz=0.0):
            return (centro[0] + r * math.cos(a), centro[1] + r * math.sin(a), centro[2] + dz)
        SOLIDO.quad(pt(R_BOCA, a0), pt(R_EXPLANADA, a0), pt(R_EXPLANADA, a1), pt(R_BOCA, a1), "costura")            # suelo
        SOLIDO.quad(pt(R_BOCA, a1, -2), pt(R_EXPLANADA, a1, -2), pt(R_EXPLANADA, a0, -2), pt(R_BOCA, a0, -2), "costura")  # fondo
        SOLIDO.quad(pt(R_BOCA, a0, -2), pt(R_BOCA, a0), pt(R_BOCA, a1), pt(R_BOCA, a1, -2), "costura")              # canto interior
        SOLIDO.quad(pt(R_EXPLANADA, a1, -2), pt(R_EXPLANADA, a1), pt(R_EXPLANADA, a0), pt(R_EXPLANADA, a0, -2), "costura")
    for i, zona in enumerate(ZONAS):
        ang = 2 * math.pi * i / 9
        cx, cy = centro[0] + 16 * math.cos(ang), centro[1] + 16 * math.sin(ang)
        base = fondo_z
        tope = centro[2] + 12                               # las "horas" sobresalen 12 m: frenan a Sonic si cruza volando
        if dif_ang(ang, ang_entrada) < math.radians(50):
            tope = centro[2] - 2                            # del lado de la entrada quedan bajo la explanada
        if dif_ang(ang, ang_salida) < math.radians(25):
            base = fondo_z + 9                              # la de la salida deja un túnel abajo
        SOLIDO.caja((cx, cy, base), (4, 11, tope - base), ang, zona)
    # escombros de las 9 eras para esquivar en el planeo: una capa cada 30 m, pegados a la pared (r 8–10) para dejar
    # libre el centro, donde baja la espiral de anillos (r 4,5). Sin los blancos de la 0.7.1 (a r 4: Sonic aterrizaba
    # en ellos y se cortaba el planeo).
    capa = 0
    for prof_e in range(22, PROF - 25, 30):
        for j in range(3):
            i = (capa * 3 + j) % 9
            ang = 2 * math.pi * (j / 3 + capa * 0.37)
            r = 10.0 if (capa + j) % 2 else 8.0
            SOLIDO.caja((centro[0] + r * math.cos(ang), centro[1] + r * math.sin(ang), centro[2] - prof_e),
                        (3.0, 3.0, 1.5), ang, ZONAS[i])
        capa += 1
    zona_planeo(centro, PROF, R_BOCA, GIRO_CAMARA_PLANEO)
    for k in range(int((PROF - 20) / 4)):                   # anillos en espiral por todo el pozo
        a_esp = k * 0.7
        obj("Ring", CAMPOS_RING, pos=(centro[0] + 4.5 * math.cos(a_esp), centro[1] + 4.5 * math.sin(a_esp), centro[2] - 10 - 4.0 * k))
    SOLIDO.caja((centro[0], centro[1], fondo_z - 2), (44, 44, 2), K.th, "blanco")   # suelo blanco al fondo
    MIN_Z[0] = min(MIN_Z[0], fondo_z - 2)
    # el cursor sale por el túnel, al nivel del fondo
    K.x, K.y = centro[0] + 20 * math.cos(K.th), centro[1] + 20 * math.sin(K.th)
    K.z = fondo_z
    registrar_eje(0.0)
