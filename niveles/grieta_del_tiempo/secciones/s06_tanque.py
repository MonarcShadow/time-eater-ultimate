# 6. Tanque en la playa (nueva en 0.7.0): ruinas de Seaside Hill con un tanque químico hundido de Chemical Plant.
# En la fase 2 el tanque se llenará de agua (tramo bajo el agua con burbujas de aire). (~25 s)
from base import *  # noqa: F401,F403


def construir():
    seccion("6 Tanque en la playa")
    costura(16)
    t = carretera(120, ancho=16, giro_grados=30, mat="ssh", muros=0.6, muro_der=3.0)   # curva a la izquierda
    for s in range(0, 121, 30):
        with en(t, s):
            visual(0, 0, -2.5, (32, 120, 0.2), "ssh")
    with en(t, 60):
        enemigo("ssh", 0, 3)
    anillos(10, 110, cada=6, tramo=t)
    t = carretera(30, ancho=16, mat="ssh")
    # puentes rotos de las ruinas: plataformas separadas por huecos que se saltan sin ayuda
    plataformas_3d(6, largo=16, hueco=6, ancho=12, mats=("ssh", "ssz"), dz=(0, 1.0, -1.0), enemigos="ssh")
    t = carretera(40, ancho=16, mat="ssh")
    for k in range(4):
        with en(t, 10 * k):
            visual(0, 0, -6, (12, 60, 0.2), "ssh")
    # el tanque químico hundido: rampa abajo, fondo largo, rampa arriba (muros altos de metal)
    t = carretera(60, ancho=16, dz=-8, mat="cpz", mat_muro="cpz", muros=3)
    anillos(10, 50, cada=5, tramo=t)
    t = carretera(80, ancho=16, mat="cpz", mat_muro="cpz", muros=4)
    for s, lado in ((30, -4), (55, 4)):
        with en(t, s):
            enemigo("cpz", 0, lado)
    for s in (10, 40, 70):
        with en(t, s):
            tubo((0, 10.5, 0), (0, 10.5, 9), 1.2, "cpz")
            tubo((0, -10.5, 0), (0, -10.5, 9), 1.2, "cpz")
            visual(0, 0, 9, (3, 22, 0.4), "cpz")                    # aros del tanque
    anillos(5, 75, cada=5, tramo=t, lado=-3)
    t = carretera(60, ancho=16, dz=8, mat="cpz", mat_muro="cpz", muros=3)
    t = carretera(40, ancho=14, mat="ssh")
    with en(t, 15):
        enemigo("ssh", 0, -3)
    tramo_2d("s6_2d", (0, 1.5, 0, 1.5, 3.0, 1.5), mats=("cpz", "ssh"), tubos="cpz", mat_salida="ssh")
