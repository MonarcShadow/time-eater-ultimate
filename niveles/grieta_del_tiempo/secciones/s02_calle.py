# 2. Calle sobre las ruinas: City Escape + Sky Sanctuary + Egg Fighters de Rooftop Run (~30 s)
from base import *  # noqa: F401,F403


def construir():
    seccion("2 Calle sobre las ruinas")
    costura(14)
    t = carretera(20, ancho=16, mat="cte")
    with en(t, 6):
        egg_fighter(0, 3.5)
    t = quickstep("s2_qs", 200, dz=-25, mat="cte", mat_muro="ssz")
    for s, lado in ((30, -4), (50, 4), (70, 0), (90, -4), (105, 4), (120, 0), (140, -4), (155, 4)):   # "autos" por carril
        with en(t, s):
            decorado(0, lado, 0, (3.5, 2.2, 1.6), "cte")
    for s in (15, 60, 100, 130, 170):
        anillos(s, s + 10, cada=2.5, tramo=t)
    for s in (40, 110, 180):                                     # columnas de las ruinas de Sky Sanctuary a los lados
        with en(t, s):
            tubo((0, -11, -20), (0, -11, 10), 2.0, "ssz", n=8)
            tubo((8, 11, -20), (8, 11, 14), 2.0, "ssz", n=8)
    for k, s in enumerate(range(10, 200, 24)):                   # fachadas de City Escape cosidas a trozos de ruina blanca
        with en(t, s):
            for lado in (-17, 17):
                alto_e = 14 + ((k * 7 + (3 if lado > 0 else 0)) % 5) * 4
                decorado(0, lado, -8, (18, 8, 8 + alto_e), "cte")
                decorado(0, lado, alto_e, (12, 6, 5), "ssz")
                visual(0, lado - (4.1 if lado > 0 else -4.1), 3, (10, 0.1, 4), "sph")   # ventanas iluminadas
    with en(t, 186):
        dash_panel(0)
    with en(t, 197):
        rampa_salto(0, boost=68, normal=62, angulo=1)            # calibrada en el juego para el hueco de 22 m
    # islas de asfalto sobre las nubes (huecos entre islas)
    suelo_muerte(0, 120, ancho=40, profundidad=25)
    K.avanzar(22)
    ritmo("plataformas")
    for i in range(3):
        t = carretera(18, ancho=12, mat="cte" if i % 2 == 0 else "ssz", muros=0)
        anillos(4, 14, cada=2.5, tramo=t)
        with en(t, 9):
            decorado(0, 0, -12, (10, 8, 10), "ssz")                # ruina flotante bajo la isla
            tubo((0, -7.5, -30), (0, -7.5, 4), 1.2, "ssz", n=8)    # columna rota a un lado
            visual(-9.6, 3, -1.5, (1.5, 3, 1.2), "cte", 20)        # trozos de asfalto desprendidos (sin colisión)
            visual(9.8, -2, -2.5, (1.2, 2.5, 1.0), "cte", -15)
        K.avanzar(9)
    ritmo("3d")
    t = carretera(25, ancho=14, mat="ssz")
    with en(t, 10):
        egg_fighter(0, -3)
    with en(t, 18):
        egg_fighter(0, 3)

    # plaza de ruinas (nuevo en 0.7.0): Egg Robos de Sky Sanctuary, nubes que rebotan hacia anillos (opcionales)
    # y una plataforma giratoria de adorno a un lado. Nada de esto hace falta para avanzar.
    t = carretera(120, ancho=24, giro_grados=20, mat="ssz", muros=0.8, muro_der=3.0)
    anillos(10, 110, cada=6, tramo=t)
    for s, lado in ((30, 5), (70, -5), (100, 5)):
        with en(t, s):
            enemigo("ssz", 0, lado)
    for s in (40, 58):
        with en(t, s):
            nube(0, -8, 0.5)
            for h in (6, 9, 12):
                obj("Ring", CAMPOS_RING, 0, -8, h)
    with en(t, 85):
        plataforma_giratoria(0, 8, 4)
    for s in (20, 60, 100):
        with en(t, s):
            tubo((0, 14, -20), (0, 14, 12), 2.2, "ssz", n=8)
            decorado(0, 14, 12, (6, 6, 1.5), "ssz")
    # avenida de City Escape con GunHunters
    t = carretera(100, ancho=16, giro_grados=-20, mat="cte", mat_muro="cte", muro_izq=3.0)
    for s, lado in ((35, -4), (75, 4)):
        with en(t, s):
            enemigo("cte", 0, lado)
    anillos(10, 90, cada=5, tramo=t)
    for k, s in enumerate(range(8, 100, 20)):
        with en(t, s):
            for lado in (-15, 15):
                decorado(0, lado, -6, (16, 6, 16 + (k * 5) % 12), "cte")
    t = carretera(60, ancho=16, mat="cte")
    with en(t, 10):
        enemigo("euc", 0, 3)
    # 2D sobre las ruinas
    tramo_2d("s2_2d", (0, 1.5, 0, 1.5, 3.0, 1.5, 0), mats=("ssz", "cte"), mat_salida="ssz")
