# 9. Persecución desincronizada: tejados de Rooftop Run que colapsan como Sky Sanctuary (~20 s)
from base import *  # noqa: F401,F403


def tejados(n, primero=0, enemigos=False):
    """Tejados de 26 m separados por huecos de 7 m que se saltan sin ayuda."""
    for i in range(primero, primero + n):
        t = carretera(26, ancho=14, mat="euc" if i % 2 == 0 else "ssz", muros=0.5, mat_muro="cte")
        anillos(4, 20, cada=4, tramo=t)
        if i % 2 == 1:
            with en(t, 6):
                dash_panel(0)
        elif enemigos:
            with en(t, 15):
                enemigo("euc" if i % 4 == 0 else "cte", 0, 3 if i % 4 == 0 else -3)
        with en(t, 13):
            decorado(0, -10, -20, (16, 4, 18), "euc")                         # fachadas de Spagonia
            decorado(0, 12, -22, (20, 8, 16 + 3 * (i % 5)), "euc")             # casas vecinas más bajas, con chimenea
            decorado(4, 12, -6 + 3 * (i % 5), (1.4, 1.4, 3), "cte")
        with en(t, 21):
            decorado(0, 5.6 if i % 2 else -5.6, 0, (1.2, 1.2, 2.6), "cte")    # chimenea en el borde del tejado
        # rampa en el borde (0.7.4): yendo rápido (panel o boost) lanza al tejado siguiente sin saltar.
        # 8 m de ancho y centrada: quedan 3 m a cada lado para saltar normal. Altura y ángulo en ajustes.conf
        # (a 45° se salía demasiado alto, prueba de la 0.7.4).
        alto_rampa = AJUSTES["RAMPA_TEJADO_ALTO"]
        largo_rampa = alto_rampa / math.tan(math.radians(max(5.0, min(80.0, AJUSTES["RAMPA_TEJADO_ANGULO"]))))
        with en(t, 26 - largo_rampa):
            cuna(0, 0, largo_rampa, 8, alto_rampa, "cte")
        if i == 0:
            with en(t, 1):
                costura(14)
        suelo_muerte(0, 7, ancho=40, profundidad=18)
        K.avanzar(7)
        sumar_tiempo(7 / VEL["3d"], 7)


def construir():
    seccion("9 Persecución desincronizada")
    carretera(20, ancho=14, mat="euc")
    tejados(5)
    decorado(-40, 25, -15, (30, 8, 6), "ssh")                                 # el mar a la altura de los tejados
    carretera(10, ancho=14, mat="euc", muros=0)
    riel("s9_riel", 90, 8, plataforma_final=60, mat="euc")                     # tejado largo y sin paneles para frenar
    # hueco de 24 m que solo se cruza con el light speed dash (nuevo en 0.7.4): anillos desde 6 m antes del borde
    anillos(-6, 26, cada=2.0, arriba=1.2, dash=True)
    suelo_muerte(0, 24, ancho=40, profundidad=18)
    K.avanzar(24)
    sumar_tiempo(24 / VEL["rapido"], 24)
    # segunda tanda de tejados (nuevo en 0.7.0), con Egg Fighters y GunHunters, y otro riel más largo
    tejados(4, primero=5, enemigos=True)
    # espiral de anillos de light dash (0.7.7; antes una barra de acrobacia, difícil de usar suelta en el aire):
    # hueco de 16 m y el tejado siguiente 10 m más alto. La hélice da 1 vuelta alrededor del eje de avance con el radio
    # modulado por sin(pi·f): empieza y acaba tangente hacia adelante (en la 0.7.7, 2 vueltas de radio fijo arrancaban
    # de lado y Sonic salía recto). Anillos cada 1 m de recorrido real. Sin light dash no se llega.
    carretera(20, ancho=14, mat="euc", muros=0.5, mat_muro="cte")
    HUECO, SUBIDA, RADIO, VUELTAS, PASO = 16.0, 10.0, 3.5, 1, 1.0

    def helice(f):
        a, r = 2 * math.pi * VUELTAS * f, RADIO * math.sin(math.pi * f)
        return (-2 + (HUECO + 4) * f, r * math.sin(a), 1.2 + SUBIDA * f + r * (1 - math.cos(a)))
    muestras = [helice(i / 2000) for i in range(2001)]
    arco = [0.0]
    for p, q in zip(muestras, muestras[1:]):
        arco.append(arco[-1] + math.dist(p, q))
    anillos(-8, -3, cada=PASO, arriba=1.2, dash=True)                         # arranque sobre el tejado
    siguiente = 0.0
    for p, s in zip(muestras, arco):
        if s >= siguiente - 1e-6:
            obj("Ring", CAMPOS_RING_DASH, *p)
            siguiente += PASO
    suelo_muerte(0, HUECO, ancho=40, profundidad=18)
    K.avanzar(HUECO, SUBIDA)
    sumar_tiempo(HUECO / VEL["3d"] + 2.0, HUECO)
    carretera(20, ancho=14, mat="ssz", muros=0.5, mat_muro="cte")
    carretera(10, ancho=14, mat="euc", muros=0)
    t = riel("s9_riel_b", 110, 10, plataforma_final=50, mat="ssz")
    anillos(10, 40, cada=5, tramo=t)
    tejados(3, primero=9, enemigos=True)                                      # los últimos tejados antes del jardín
    carretera(30, ancho=14, mat="euc")
