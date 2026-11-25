# 1. Colina contaminada: Green Hill + tuberías de Chemical Plant + cielo de Speed Highway (~30 s)
from base import *  # noqa: F401,F403


def construir():
    seccion("1 Colina contaminada", checkpoint=False)
    # detrás de la salida: 12 m más de terreno cerrado por paredes, para no caer al vacío corriendo hacia atrás (la pared
    # de la 0.7.11, pegada a Sonic, hacía que la cámara empezara mirando desde arriba; 0.7.14: rectangular en lugar
    # del semicírculo de la 0.7.13)
    fondo_rectangular(12, 14, "ghz", alto_fondo=2.5, alto_lados=1.2, mat_muro="cpz")
    t = carretera(40, ancho=14, mat="ghz")
    anillos(10, 30, tramo=t)
    for i, s in enumerate((10, 22, 34)):                         # tuberías de Chemical Plant reventando la colina:
        with en(t, s):                                           # suben por un lado, cruzan sobre la pista y bajan por el otro
            alto_t = 9 + 3 * i
            tubo((0, 12, -4), (0, 12, alto_t), 2.2, "cpz")
            tubo((0, 12, alto_t), (0, -12, alto_t), 2.2, "cpz")
            tubo((0, -12, alto_t), (0, -12, -4), 2.2, "cpz")
            visual(3, 9.5, 0.0, (5, 4, 0.05), "cpz", 15 * i)       # charco de Mega Mack sobre la hierba (fuera de la pista)
    for lado in (-18, 18):                                       # acantilados a cuadros de Green Hill a los lados
        with en(t, 20):
            decorado(0, lado, -6, (36, 8, 10 + (4 if lado > 0 else 0)), "ghz")
    with en(t, 6):                                               # panel solo en la recta inicial, lejos de la curva
        dash_panel(0)
    # curva a la derecha abierta (110 m) y con muro exterior (izquierdo) de 3 m para no salirse
    t = carretera(110, ancho=14, giro_grados=-45, dz=-8, mat="ghz", mat_muro="cpz", muro_izq=3.0)
    with en(t, 55):                                              # tanque de Chemical Plant con una tubería hacia la colina
        tubo((0, 16, -6), (0, 16, 12), 5.0, "cpz", n=12)
        tubo((0, 16, 8), (-25, 22, 8), 1.5, "cpz")
    with en(t, 30):
        decorado(0, 14, -6, (20, 6, 9), "ghz")
    with en(t, 80):
        decorado(0, -16, -4, (6, 6, 20), "sph")                  # torre nocturna de Speed Highway al otro lado
    anillos(10, 100, cada=5, tramo=t)
    t = carretera(30, ancho=14, mat="ghz")
    with en(t, 10):
        arco_costura(14)
    # colinas onduladas (nuevo en 0.7.0): Motoras de Green Hill y Landers de Chemical Plant entre las tuberías
    for k, dz in enumerate((6, -6, 5, -5)):
        t = carretera(45, ancho=16, dz=dz, mat="ghz", mat_muro="cpz")
        anillos(8, 38, cada=5, tramo=t, lado=-4 if k % 2 else 4)
        with en(t, 25):
            enemigo("ghz" if k % 2 == 0 else "cpz", 0, 4 if k % 2 else -4)
        if k % 2 == 0:
            with en(t, 12):
                tubo((0, 14, -6), (0, 14, 11), 2.0, "cpz")
                tubo((0, 14, 11), (0, -14, 11), 2.0, "cpz")
                tubo((0, -14, 11), (0, -14, -6), 2.0, "cpz")
        with en(t, 30):
            decorado(0, -18 if k % 2 else 18, -8, (30, 8, 12 + 2 * k), "ghz")
    # islotes de hierba sobre un barranco de Mega Mack (huecos que se saltan sin ayuda)
    t = carretera(20, ancho=14, mat="ghz")
    plataformas_3d(4, largo=16, hueco=6, ancho=11, mats=("ghz", "cpz"), dz=(0, 1.0, -1.0), muerte=20, enemigos="ghz")
    # loop clásico de Green Hill (0.7.7; desde la 0.7.11 más grande, radio LOOP_RADIO, y su bajada lleva directo al
    # tramo 2D): recta tras los islotes (40 m de margen sin huecos antes del cambio a 2D, el homing se corta al
    # cruzarlo), dos paneles para coger velocidad y la vuelta
    t = carretera(60, ancho=14, mat="ghz")
    for s in (30, 46):
        with en(t, s):
            dash_panel(0)
    anillos(50, 58, cada=2.0, tramo=t)
    loop("s1_loop", radio=AJUSTES["LOOP_RADIO"], ancho=10, desplazamiento=14, mat="ghz")
    # al pie del loop: recta de 12 m y embudo de 30 m de 12 a 6 m (el ancho de las plataformas 2D), con paredes
    # sólidas de 4 m; el cambio a 2D va al FINAL del embudo (0.7.13). En la 0.7.12 iba a 2,8 m de la salida del modo
    # dash (como en ghz200), con Sonic aún a un lado de la pista ancha: la cámara pasaba a 2D pero no se fijaba la
    # profundidad y era fácil caerse.
    carretera(12, ancho=12, muros=4, muro_solido=True, mat="ghz", mat_muro="cpz")
    carretera(30, ancho=12, ancho_final=6, muros=4, muro_solido=True, mat="ghz", mat_muro="cpz")

    # tramo 2D: plataformas sobre tuberías y Mega Mack (el Egg Fighter de la salida se quitó: estaba dentro del margen;
    # la sección 2 ya empieza con uno)
    tramo_2d("s1_2d", (0, 1.5, 3.0, 1.0, 2.5, 0, 1.5, 3.0, 1.5, 0), mats=("ghz", "cpz"), tubos="cpz", mat_salida="ghz",
             enemigos="ghz", cambio=-1.0)            # franja de 6 m: el ancho del final del embudo
