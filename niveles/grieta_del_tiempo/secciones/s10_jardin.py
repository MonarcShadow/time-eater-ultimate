# 10. Jardín de cristal (nueva en 0.7.0): fábrica-jardín de Planet Wisp con ruinas de Sky Sanctuary; alterna 3D,
# un 2D largo, plataformas giratorias de adorno y un quickstep entre cristales (~30 s)
from base import *  # noqa: F401,F403


def cristales(t, cada=18):
    for k, s in enumerate(range(6, int(t.largo), cada)):
        with en(t, s):
            lado = 13 if k % 2 else -13
            tubo((0, lado, -2), (1.5, lado * 1.15, 9 + (k % 3) * 3), 1.2, "pla", n=5)
            decorado(0, -lado * 1.2, -6, (5, 5, 7), "ssz")


def construir():
    seccion("10 Jardín de cristal")
    costura(16)
    t = carretera(160, ancho=16, giro_grados=-30, mat="pla", mat_muro="ssz", muros=1.0, muro_izq=3.0)  # curva a la derecha
    cristales(t)
    for s, lado in ((50, 3), (110, -3)):
        with en(t, s):
            enemigo("pla", 0, lado)
    anillos(10, 150, cada=7, tramo=t)
    t = carretera(40, ancho=14, mat="pla")
    t = tramo_2d("s10_2d", (0, 1.5, 3.0, 4.5, 3.0, 1.5, 3.0, 1.5, 0, 1.5), mats=("pla", "ssz"), mat_salida="ssz")
    t = carretera(120, ancho=18, mat="ssz", muros=0.8)
    cristales(t, 24)
    for s, lado in ((35, 7), (85, -7)):
        with en(t, s):
            plataforma_giratoria(0, lado, 4)
    for s, zona, lado in ((55, "sph", 0), (100, "ssz", 3)):
        with en(t, s):
            enemigo(zona, 0, lado)
    anillos(10, 110, cada=6, tramo=t)
    plataformas_3d(4, largo=16, hueco=6, ancho=10, mats=("pla", "ssz"), dz=(0, 1.0, -1.0))
    t = carretera(100, ancho=16, giro_grados=30, mat="ssz", muros=1.0, muro_der=3.0)   # curva a la izquierda
    cristales(t, 25)
    anillos(10, 90, cada=6, tramo=t)
    t = carretera(30, ancho=16, mat="pla")
    t = quickstep("s10_qs", 200, dz=-15, mat="pla", mat_muro="ssz")
    for s, lado in ((35, -4), (55, 4), (75, 0), (95, -4), (115, 4), (135, 0), (160, -4)):   # cristales en los carriles
        with en(t, s):
            tubo((0, lado, 0), (0, lado, 2.2), 1.0, "pla", n=5)
    for s in (15, 85, 150):
        anillos(s, s + 10, cada=2.5, tramo=t)
    carretera(40, ancho=16, mat="ssz")
