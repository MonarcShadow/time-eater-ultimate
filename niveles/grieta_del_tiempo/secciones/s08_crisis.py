# 8. Crisis al revés (nueva en 0.7.0): calles de Crisis City con lava y Takers, plataformas flotantes sobre la
# lava y colinas a cuadros de Green Hill incrustadas en la ciudad (~25 s)
from base import *  # noqa: F401,F403


def construir():
    seccion("8 Crisis al revés")
    costura(18)
    t = carretera(140, ancho=18, giro_grados=25, mat="csc", mat_muro="ghz", muros=1.0, muro_der=3.0)   # curva a la izquierda
    for s, lado in ((40, -4), (100, 4)):
        with en(t, s):
            enemigo("csc", 0, lado)
    for s, lado in ((25, 6), (70, -6), (115, 6)):
        with en(t, s):
            charco_dano(0, lado, 7, 4)
    for s in (30, 90):
        with en(t, s):
            decorado(0, -20, -10, (26, 10, 18), "ghz")                        # colina de Green Hill dentro de la ciudad
            decorado(0, 18, -4, (10, 8, 30), "csc")                           # edificio en ruinas
    anillos(10, 130, cada=6, tramo=t)
    t = carretera(100, ancho=18, giro_grados=-25, mat="csc", muros=1.0, muro_izq=3.0)               # curva a la derecha
    with en(t, 50):
        enemigo("csc", 0, 0)
    for s, lado in ((20, -5), (75, 5)):
        with en(t, s):
            charco_dano(0, lado, 8, 5)
    anillos(10, 90, cada=6, tramo=t, lado=4)
    # plataformas flotantes sobre la lava
    with en(t, 100):
        visual(80, 0, -18, (180, 70, 0.3), "csc")                            # mar de lava (adorno; abajo hay suelo de muerte)
    plataformas_3d(7, largo=16, hueco=7, ancho=10, mats=("csc", "ghz"), dz=(0, 1.5, -1.5), muerte=20, enemigos="csc")
    t = carretera(40, ancho=14, mat="ghz")
    with en(t, 20):
        arco_costura(14)
    tramo_2d("s8_2d", (0, 1.5, 3.0, 1.5, 0), mats=("csc", "ghz"), mat_salida="ghz")
