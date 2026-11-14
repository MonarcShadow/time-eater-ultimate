# 5. Fábrica dentro de la torre: Planet Wisp + Rooftop Run + Chemical Plant (2D, subida) (~30 s)
from base import *  # noqa: F401,F403


def construir():
    seccion("5 Fábrica dentro de la torre")
    costura(16)
    # nave de la fábrica (nuevo en 0.7.0): Pawns de Planet Wisp entre cintas transportadoras y prensas
    t = carretera(150, ancho=18, mat="pla", mat_muro="euc", muros=2.5)
    for s, lado in ((40, 4), (80, -4), (120, 3)):
        with en(t, s):
            enemigo("pla", 0, lado)
    for s in range(15, 150, 30):
        with en(t, s):
            visual(0, 7.5, 0.02, (20, 2.5, 0.05), "pla")           # cintas transportadoras (adorno)
            decorado(0, -12, 0, (6, 4, 10), "pla")                  # máquinas a un lado
            decorado(0, 0, 14, (4, 18, 1.2), "euc")                 # vigas del techo
    anillos(10, 140, cada=6, tramo=t)
    t = carretera(30, ancho=20, mat="euc", muros=0)                # suelo de entrada a la torre

    # torre (probada en el juego): escalera hacia adelante en 2D con resortes
    plataforma(0, 0, 0, 34, 10, alto=2, mat="euc")                # suelo de la torre bajo la escalera (si caes, vuelves al resorte)
    decorado(-15, -12, 0, (30, 2, 45), "euc")                     # paredes de la torre
    decorado(-15, 12, 0, (30, 2, 45), "euc")
    decorado(17, 12, 0, (34, 2, 45), "euc")                       # la pared del fondo sigue a lo largo de la escalera
    costura(18, -29)
    izq = (-math.sin(K.th), math.cos(K.th), 0.0)
    for ad, alt, radio, mat_e in ((-24, 8, 5, "euc"), (-12, 19, 7, "pla"), (-2, 9, 4, "pla"),
                                  (8, 30, 6, "euc"), (18, 14, 5, "cpz"), (26, 38, 4, "euc")):
        lados = (-10.7, 10.7) if ad < 0 else (10.7,)              # engranajes del reloj / de la fábrica en las paredes
        for lado in lados:
            SOLO_VISUAL.disco(K.frame(ad + (3 if lado > 0 else 0), lado, alt), radio, izq, mat_e, n=12, grosor=0.5)
    a_2d(-8)
    curva_recta("s5_2d@SV", -12, 50, rieles=(-1.0, 1.0))
    resorte_vertical(-4, 0, 0, velocidad=26)
    escalones = [(0, 6, 8), (6, 12, 8), (12, 18, 8), (18, 24, 14)]           # (inicio, altura, largo)
    for i, (ini, h, largo) in enumerate(escalones):
        plataforma(ini, 0, h, largo, 6, alto=1.2, mat="pla" if i % 2 == 0 else "cpz")
        anillos(ini + 1, ini + largo - 1, cada=2.0, arriba=h + 1.0)
        if i < len(escalones) - 1:
            ultimo = i == len(escalones) - 2
            resorte_vertical(ini + 2, 0, h, velocidad=32 if ultimo else 26, mantener=7 if ultimo else 5)
    decorado(26, 0, 31, (6, 6, 1.5), "pla")                                   # "prensa" de Planet Wisp sobre la salida
    a_2d(40, salida=True, arriba=24)                                          # salida a 3D ya en la carretera de arriba
    K.avanzar(32)
    K.z += 24
    sumar_tiempo(10, 60)                                                      # la subida en 2D

    # pasillo de engranajes en lo alto (nuevo en 0.7.0) y bajada en 2D por las máquinas
    t = carretera(180, ancho=16, mat="euc", mat_muro="pla", muros=1.5)
    for s, zona, lado in ((50, "euc", -3), (95, "pla", 3), (140, "euc", 3)):
        with en(t, s):
            enemigo(zona, 0, lado)
    for s in range(20, 180, 40):
        with en(t, s):
            SOLO_VISUAL.disco(K.frame(0, 11, 6), 5, (-math.sin(K.th), math.cos(K.th), 0.0), "euc", n=12, grosor=0.5)
            tubo((0, -10, -12), (0, -10, 8), 1.5, "cpz")
    anillos(10, 170, cada=6, tramo=t)
    t = carretera(30, ancho=16, mat="pla")
    tramo_2d("s5_2d_b", (0, -1.5, -3.0, -1.5, -3.0, -4.5, -3.0, -4.5), mats=("pla", "cpz"), tubos="cpz", mat_salida="pla")
