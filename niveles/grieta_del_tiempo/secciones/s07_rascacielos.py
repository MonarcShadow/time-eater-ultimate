# 7. Rascacielos invertido: Speed Highway + fachada de Chemical Plant + cascada de Green Hill (~20 s)
from base import *  # noqa: F401,F403


def construir():
    seccion("7 Rascacielos invertido")
    t = carretera(15, ancho=14, mat="sph")
    with en(t, 12):
        costura(14)
    ritmo("rapido")
    t = carretera(150, ancho=14, dz=-60, mat="cpz", mat_muro="sph")          # bajada empinada por la "fachada"
    for s in range(6, 150, 12):
        with en(t, s):
            for lado in (-8.6, 8.6):
                visual(0, lado, -1.0, (5, 0.3, 2.4), "sph")
    for s in (40, 100):
        with en(t, s):
            tubo((0, -14, -20), (0, -14, 6), 4.0, "cpz", n=12)
    for s in (10, 50, 90, 130):
        with en(t, s):
            dash_panel(0)
    anillos(20, 140, cada=8, tramo=t)
    for s in (30, 80, 125):
        with en(t, s):
            decorado(0, -9, 0, (1.5, 1.5, 4), "sph")
    with en(t, 110):
        decorado(0, 20, -60, (14, 6, 50), "ghz")                              # cascada de Green Hill al costado
        visual(0, 16.9, -58, (8, 0.3, 48), "ssh")
    ritmo("3d")
    carretera(35, ancho=14, mat="ghz")
    resorte_vertical(-3, 0, 0, velocidad=42, mantener=8)                      # escalón de 8 m (calibrado en el juego)
    plataforma(0, 0, 8, 30, 14, alto=8, mat="sph")
    K.avanzar(30)
    K.z += 8
    sumar_tiempo(2, 30)

    # segunda fachada (nuevo en 0.7.0): quickstep cuesta abajo entre ventanas y tanques, con coches en los carriles
    t = quickstep("s7_qs", 200, dz=-30, mat="sph", mat_muro="cpz")
    for s, lado in ((35, 4), (55, -4), (80, 0), (100, 4), (125, -4), (145, 0), (160, 4)):
        with en(t, s):
            decorado(0, lado, 0, (3.5, 2.2, 1.6), "sph")
    for s in (20, 70, 115, 170):
        anillos(s, s + 10, cada=2.5, tramo=t, lado=-4 if s % 2 else 4)
    for s in range(10, 200, 20):
        with en(t, s):
            for lado in (-9, 9):
                visual(0, lado, 1.0, (6, 0.3, 3), "sph")
    for s in (60, 140):
        with en(t, s):
            tubo((0, 15, -25), (0, 15, 8), 4.0, "cpz", n=12)
    t = carretera(50, ancho=16, mat="cpz")
    for s, zona, lado in ((15, "cte", 4), (30, "cpz", -4)):
        with en(t, s):
            enemigo(zona, 0, lado)
    # bajada en 2D por los andamios de la fachada
    tramo_2d("s7_2d", (0, -1.5, -3.0, -1.5, -3.0, -4.5, -6.0), mats=("sph", "cpz"), tubos="cpz", mat_salida="sph")
