# 11. Dentro del reloj (nueva en 0.7.0): la torre del reloj de Rooftop Run por dentro, con un primer planeo más
# corto que el final y en otra dirección (sirve para comprobar el giro de la cámara de planeo). (~15 s)
from base import *  # noqa: F401,F403

# Giro de la cámara de este planeo, en grados (vista desde arriba). 135 es el valor confirmado en el pozo final,
# que va en otra dirección: si aquí la cámara no mira hacia la salida, ajustar este número y reconstruir.
GIRO_CAMARA_RELOJ = 135


def construir():
    seccion("11 Dentro del reloj")
    costura(16)
    t = carretera(120, ancho=16, giro_grados=70, mat="euc", muros=1.0, muro_der=3.0)    # curva larga a la izquierda
    for s in (30, 90):
        with en(t, s):
            enemigo("euc", 0, 3 if s == 30 else -3)
    anillos(10, 110, cada=7, tramo=t)
    t = carretera(40, ancho=16, mat="euc", muros=1.5)
    with en(t, 20):
        arco_costura(16, alto=8)
    carretera(10, ancho=14, mat="costura", muros=0)

    # el pozo: una explanada alrededor de la boca, 8 ruedas dentadas como paredes y un túnel de salida abajo
    R_BOCA, R_EXPL, PROF = 11.0, 22.0, 60
    centro = K.frame(R_EXPL, 0, 0)
    fondo_z = centro[2] - PROF
    ang_entrada, ang_salida = K.th + math.pi, K.th
    SEG = 20
    for k in range(SEG):
        a0, a1 = 2 * math.pi * k / SEG, 2 * math.pi * (k + 1) / SEG

        def pt(r, a, dz=0.0):
            return (centro[0] + r * math.cos(a), centro[1] + r * math.sin(a), centro[2] + dz)
        SOLIDO.quad(pt(R_BOCA, a0), pt(R_EXPL, a0), pt(R_EXPL, a1), pt(R_BOCA, a1), "euc")
        SOLIDO.quad(pt(R_BOCA, a1, -2), pt(R_EXPL, a1, -2), pt(R_EXPL, a0, -2), pt(R_BOCA, a0, -2), "euc")
        SOLIDO.quad(pt(R_BOCA, a0, -2), pt(R_BOCA, a0), pt(R_BOCA, a1), pt(R_BOCA, a1, -2), "euc")
        SOLIDO.quad(pt(R_EXPL, a1, -2), pt(R_EXPL, a1), pt(R_EXPL, a0), pt(R_EXPL, a0, -2), "euc")

    def dif_ang(a, b):
        return abs((a - b + math.pi) % (2 * math.pi) - math.pi)
    for i in range(8):
        ang = 2 * math.pi * i / 8 + math.pi / 8
        cx, cy = centro[0] + 14 * math.cos(ang), centro[1] + 14 * math.sin(ang)
        base_z, tope = fondo_z, centro[2] + 8
        if dif_ang(ang, ang_entrada) < math.radians(50):
            tope = centro[2] - 2
        if dif_ang(ang, ang_salida) < math.radians(30):
            base_z = fondo_z + 9                              # túnel de salida
        SOLIDO.caja((cx, cy, base_z), (3, 9, tope - base_z), ang, "euc" if i % 2 else "sph")
        # engranajes (solo visuales) en la pared, a distintas alturas: el reloj por dentro
        SOLO_VISUAL.disco((centro[0] + 12 * math.cos(ang), centro[1] + 12 * math.sin(ang), centro[2] - 15 - 9 * (i % 4)),
                          3.5, (math.cos(ang), math.sin(ang), 0.0), "euc", n=10, grosor=0.5)
    for k in range(10):                                     # anillos en espiral
        a_esp = k * 0.8
        obj("Ring", CAMPOS_RING, pos=(centro[0] + 4 * math.cos(a_esp), centro[1] + 4 * math.sin(a_esp), centro[2] - 10 - 3.5 * k))
    for k in range(4):                                      # péndulos/escombros a esquivar, lejos del centro
        a = k * math.pi / 2 + 0.4
        SOLIDO.caja((centro[0] + 7 * math.cos(a), centro[1] + 7 * math.sin(a), centro[2] - 22 - 9 * k), (2.5, 2.5, 1.2), a, "sph")
    zona_planeo(centro, PROF, R_BOCA, GIRO_CAMARA_RELOJ)
    SOLIDO.caja((centro[0], centro[1], fondo_z - 2), (36, 36, 2), K.th, "euc")   # suelo del fondo
    MIN_Z[0] = min(MIN_Z[0], fondo_z - 2)

    # salida por el túnel y vuelta al rumbo anterior (curva a la derecha)
    K.x, K.y = centro[0] + 17 * math.cos(K.th), centro[1] + 17 * math.sin(K.th)
    K.z = fondo_z
    registrar_eje(0.0)
    t = carretera(60, ancho=14, mat="sph", muros=1.0)
    with en(t, 40):
        enemigo("sph", 0, 0)
    anillos(10, 55, cada=5, tramo=t)
    t = carretera(120, ancho=16, giro_grados=-70, mat="sph", mat_muro="euc", muros=1.0, muro_izq=3.0)
    anillos(10, 110, cada=7, tramo=t)
    carretera(30, ancho=14, mat="euc")
