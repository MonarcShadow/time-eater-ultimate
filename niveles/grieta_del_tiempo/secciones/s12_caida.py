# 12. Caída de las 9 eras: pozo con forma de reloj de 9 horas (~10 s)
# La entrada es un agujero en el suelo: una explanada (anillo) rodea la boca del pozo, y un ChangeDiveBegin
# horizontal en la boca activa el planeo (parámetros copiados de Chemical Plant / Speed Highway).
from base import *  # noqa: F401,F403

# Giro de la cámara de planeo (grados, vista desde arriba): 135 confirmado en el juego (0.6.2) para este pozo.
GIRO_CAMARA_PLANEO = 135
# Rumbo con el que se confirmó ese giro (grados). Si las secciones anteriores cambian el rumbo de llegada, el giro
# deja de estar comprobado y el generador avisa.
RUMBO_CONFIRMADO = -10.0
SALIDA = {}


def construir():
    seccion("12 Caída de las 9 eras")
    rumbo = math.degrees(K.th)
    if abs((rumbo - RUMBO_CONFIRMADO + 180) % 360 - 180) > 0.5:
        print(f"TEU_AVISO el pozo final llega con rumbo {rumbo:.1f}° (confirmado con {RUMBO_CONFIRMADO}°): revisar la cámara")
    carretera(12, ancho=14, mat="costura", muros=0)
    R_BOCA, R_EXPLANADA = 13.0, 26.0
    centro = K.frame(R_EXPLANADA, 0, 0)
    PROF = 110
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
        for k in range(3):                                  # escombros de cada era para esquivar en el planeo;
            r = 10 - k * 3.0                                # cuanto más abajo, más cerca del centro y más desteñidos
            prof_e = 22 + 28 * k + i * 3
            SOLIDO.caja((centro[0] + r * math.cos(ang + 0.3), centro[1] + r * math.sin(ang + 0.3), centro[2] - prof_e),
                        (3.0, 3.0, 1.5), ang, "blanco" if k == 2 else zona)
    zona_planeo(centro, PROF, R_BOCA, GIRO_CAMARA_PLANEO)
    for k in range(24):                                     # anillos en espiral: guían el planeo alrededor de los escombros
        a_esp = k * 0.7
        obj("Ring", CAMPOS_RING, pos=(centro[0] + 4.5 * math.cos(a_esp), centro[1] + 4.5 * math.sin(a_esp), centro[2] - 10 - 3.6 * k))
    SOLIDO.caja((centro[0], centro[1], fondo_z - 2), (44, 44, 2), K.th, "blanco")   # suelo blanco al fondo
    MIN_Z[0] = min(MIN_Z[0], fondo_z - 2)
    # el cursor sale por el túnel, al nivel del fondo
    K.x, K.y = centro[0] + 20 * math.cos(K.th), centro[1] + 20 * math.sin(K.th)
    K.z = fondo_z
    registrar_eje(0.0)
