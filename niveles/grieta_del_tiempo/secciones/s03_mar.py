# 3. Mar en llamas: Seaside Hill + lava de Crisis City + tornado (~20 s)
from base import *  # noqa: F401,F403


def mar(t, cada=26):
    """Placa de mar de Seaside Hill bajo la pista (visual)."""
    for s in range(0, int(t.largo) + 1, cada):
        with en(t, s):
            visual(0, 0, -2.5, (30, 150, 0.2), "ssh")


def construir():
    seccion("3 Mar en llamas")
    costura(14)
    # pasarela recta sobre el mar (nuevo en 0.7.0): en la fase 2 será el tramo para correr sobre el agua.
    # Pawns con lanza de Seaside Hill y dos manchas de lava.
    t = carretera(200, ancho=20, mat="ssh", muros=0.6)
    mar(t)
    for s, lado in ((50, -4), (110, 4), (160, -3)):
        with en(t, s):
            enemigo("ssh", 0, lado)
    for s, lado in ((80, 5), (135, -6)):
        with en(t, s):
            charco_dano(0, lado, 8, 5)
    anillos(10, 190, cada=6, tramo=t)
    for s in (30, 90, 150):
        with en(t, s):
            tubo((0, 14, -3), (0, 14, 8), 1.4, "ssh", n=8)
            tubo((0, -14, -3), (0, -14, 8), 1.4, "ssh", n=8)
    # curva a la izquierda sin paneles y con muro exterior (derecho) de 3 m; después, recta con panel y rampa
    t = carretera(130, ancho=34, giro_grados=35, mat="ssh", mat_muro="ssh", muros=0.6, muro_der=3.0)
    mar(t)
    for s, lado in ((20, -6), (45, 8), (70, -3), (95, 10), (118, -8)):           # manchas de lava de Crisis City: hacen daño
        with en(t, s):
            charco_dano(0, lado, 10, 7)
    for s, lado in ((35, 13), (85, -14), (120, 12)):                             # pilares de las ruinas (uno ya sin color)
        with en(t, s):
            tubo((0, lado, -3), (0, lado, 10), 1.6, "blanco" if s == 120 else "ssh", n=8)
            decorado(0, lado, 10, (4.5, 4.5, 1), "blanco" if s == 120 else "ssh")
    with en(t, 110):                                                            # tornado de Crisis City
        for k in range(6):
            tubo((0, -36, -10 + k * 11), (2 * math.sin(k), -36 + 2 * math.cos(k), 1 + k * 11), 3 + k * 1.6, "csc", solido=False, n=9)
    with en(t, 80):
        decorado(0, 30, -10, (6, 6, 25), "ghz")                                 # puente de Green Hill arrastrado
    anillos(10, 125, cada=6, tramo=t)
    t = carretera(50, ancho=34, mat="ssh", muros=0.6)                           # recta final: panel y rampa alineados
    mar(t, 30)
    anillos(5, 30, cada=5, tramo=t)
    with en(t, 32):
        dash_panel(0)
    with en(t, 47):
        rampa_salto(0, boost=60, normal=60)                                     # calibrada para el hueco de 28 m
    suelo_muerte(0, 40, ancho=50, profundidad=20)
    K.avanzar(28)
    # aterrizaje y costa en llamas (nuevo en 0.7.0): curva con Takers de Crisis City, luego ruinas en 2D
    t = carretera(40, ancho=20, mat="ssh", muros=0.6)
    mar(t)
    t = carretera(160, ancho=20, giro_grados=-30, mat="csc", mat_muro="ssh", muros=0.6, muro_izq=3.0)
    mar(t, 32)
    for s, lado in ((40, 4), (100, -4)):
        with en(t, s):
            enemigo("csc", 0, lado)
    for s, lado in ((60, -6), (125, 5)):
        with en(t, s):
            charco_dano(0, lado, 8, 5)
    anillos(10, 150, cada=7, tramo=t)
    with en(t, 80):
        for k in range(5):
            tubo((0, 40, -10 + k * 11), (2 * math.cos(k), 40 + 2 * math.sin(k), 1 + k * 11), 3 + k * 1.4, "csc", solido=False, n=9)
    t = carretera(30, ancho=16, mat="ssh")
    tramo_2d("s3_2d", (0, 1.5, 0, 1.5, 0), mats=("ssh", "csc"), mat_salida="ssh")
