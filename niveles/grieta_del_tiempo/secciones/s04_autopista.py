# 4. Autopista entre nubes (nueva en 0.7.0): carretera nocturna de Speed Highway flotando sobre las nubes de
# Sky Sanctuary, con Spinners, nubes que rebotan hacia anillos, un riel y letreros en 2D (~25 s)
from base import *  # noqa: F401,F403


def farolas(t, cada=20):
    for k, s in enumerate(range(5, int(t.largo), cada)):
        with en(t, s):
            lado = 10.5 if k % 2 else -10.5
            tubo((0, lado, 0), (0, lado, 7), 0.3, "sph", n=6)
            decorado(0, lado * 0.9, 7, (1.2, 2.5, 0.4), "sph")
            visual(0, -lado * 1.6, -14, (14, 10, 3), "ssz")     # nubes de Sky Sanctuary bajo la autopista


def nubes_bonus(t, posiciones, lado=7.0):
    for s in posiciones:
        with en(t, s):
            nube(0, lado, 0.5)
            for h in (6, 9, 12):
                obj("Ring", CAMPOS_RING, 0, lado, h)


def construir():
    seccion("4 Autopista entre nubes")
    costura(18)
    ritmo("rapido")
    t = carretera(60, ancho=18, mat="sph", muros=1.0)
    farolas(t)
    with en(t, 15):
        dash_panel(0)
    anillos(20, 55, cada=5, tramo=t)
    t = carretera(160, ancho=18, giro_grados=30, mat="sph", muros=1.0, muro_der=3.0)    # curva a la izquierda, sin paneles
    farolas(t)
    for s, lado in ((40, 4), (100, -4)):
        with en(t, s):
            enemigo("sph", 0, lado)
    anillos(10, 150, cada=8, tramo=t)
    t = carretera(120, ancho=18, mat="sph", muros=1.0)
    farolas(t)
    for s in (10, 60):
        with en(t, s):
            dash_panel(0, -3)
    nubes_bonus(t, (30, 90))
    with en(t, 75):
        enemigo("sph", 0, -4)
    t = carretera(160, ancho=18, giro_grados=-30, mat="sph", muros=1.0, muro_izq=3.0)  # curva a la derecha, sin paneles
    farolas(t)
    with en(t, 80):
        enemigo("ssz", 0, 3)
    anillos(10, 150, cada=8, tramo=t)
    ritmo("3d")
    t = carretera(30, ancho=16, mat="sph")
    # riel de la autopista: baja 10 m sobre las nubes
    t = riel("s4_riel", 120, 10, plataforma_final=40, mat="ssz")
    anillos(5, 30, cada=5, tramo=t)
    # letreros en 2D
    t = tramo_2d("s4_2d", (0, 1.5, 3.0, 1.5, 0, 1.5, 0), mats=("sph", "ssz"), mat_salida="ssz")
    t = carretera(150, ancho=16, mat="ssz", muros=0.8)
    for s, zona, lado in ((50, "ssz", 4), (100, "sph", -4)):
        with en(t, s):
            enemigo(zona, 0, lado)
    nubes_bonus(t, (70, 120), lado=-6)
    anillos(10, 140, cada=7, tramo=t)
    for s in (25, 75, 125):
        with en(t, s):
            tubo((0, 13, -18), (0, 13, 9), 2.0, "ssz", n=8)
