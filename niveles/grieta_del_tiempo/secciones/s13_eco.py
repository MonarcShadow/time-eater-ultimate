# 13. Eco del pasado (nueva en 0.7.0): al salir del pozo, la colina de la sección 1 vuelve desteñida (blanco y gris),
# como un recuerdo que el Time Eater ya se comió: mismas colinas, tuberías y plataformas 2D, con las curvas al revés. (~25 s)
from base import *  # noqa: F401,F403


def construir():
    seccion("13 Eco del pasado")
    t = carretera(60, ancho=14, mat="blanco", mat_muro="gris")
    with en(t, 20):
        arco_costura(14)
    anillos(25, 55, cada=5, tramo=t)
    # la curva de la colina, pero hacia el otro lado
    t = carretera(110, ancho=14, giro_grados=45, mat="blanco", mat_muro="gris", muro_der=3.0)
    with en(t, 55):
        tubo((0, -16, -6), (0, -16, 12), 5.0, "gris", n=12)
    with en(t, 30):
        decorado(0, -14, -6, (20, 6, 9), "blanco")
    anillos(10, 100, cada=5, tramo=t)
    for k, dz in enumerate((6, -6, 5, -5)):
        t = carretera(45, ancho=16, dz=dz, mat="blanco", mat_muro="gris")
        anillos(8, 38, cada=5, tramo=t, lado=4 if k % 2 else -4)
        with en(t, 25):
            enemigo("ghz" if k % 2 == 0 else "cpz", 0, -4 if k % 2 else 4)
        if k % 2 == 1:
            with en(t, 12):
                tubo((0, -14, -6), (0, -14, 11), 2.0, "gris")
                tubo((0, -14, 11), (0, 14, 11), 2.0, "gris")
                tubo((0, 14, 11), (0, 14, -6), 2.0, "gris")
        with en(t, 30):
            decorado(0, 18 if k % 2 else -18, -8, (30, 8, 12 + 2 * k), "blanco")
    t = carretera(30, ancho=14, mat="blanco")
    t = tramo_2d("s13_2d", (0, 1.5, 3.0, 1.5, 0, 1.5, 3.0, 1.5), mats=("blanco", "gris"), tubos="gris", mat_salida="blanco")
    # vuelta al rumbo: curva a la derecha
    t = carretera(110, ancho=16, giro_grados=-45, mat="blanco", mat_muro="gris", muro_izq=3.0)
    anillos(10, 100, cada=6, tramo=t)
    with en(t, 60):
        enemigo("ghz", 0, 3)
    carretera(30, ancho=16, mat="blanco")
