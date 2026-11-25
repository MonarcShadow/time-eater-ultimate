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
    anillos(-6, 26, arriba=1.2, dash=True)                                     # a LIGHT_DASH_SEPARACION (0.7.10)
    suelo_muerte(0, 24, ancho=40, profundidad=18)
    K.avanzar(24)
    sumar_tiempo(24 / VEL["rapido"], 24)
    # segunda tanda de tejados (nuevo en 0.7.0), con Egg Fighters y GunHunters, y otro riel más largo
    tejados(4, primero=5, enemigos=True)
    # desafío aéreo (0.7.9; antes una espiral de light dash, en la que Sonic salía recto sin girar): resortes en el borde
    # del tejado, Spinners para encadenar homing, fila de anillos de light dash y un aro de impulso que apunta hacia
    # abajo, al tejado de llegada (4 m más alto), donde un panel de dash lleva al otro lado.
    # 0.7.10: la fila de 10 m se cruzaba con un air boost. Hueco de LIGHT_DASH_HUECO y fila en S suave como la del
    # inicio del desafío 4 de Planet Wisp (pla204: anillos a 1,13 m, ≤ 6° por anillo): ±2 m de lado.
    # 0.7.14: los 2 Spinners (a 7 y 13 m) estaban muy juntos. Ahora 3, a 20 m de los resortes, 25 m del primero y
    # 20 m del segundo; la fila empieza 1 m sobre el tercero. Todo el borde lleva resortes iguales (rebota al llegar).
    t = carretera(20, ancho=14, mat="euc", muros=0.5, mat_muro="cte")
    HUECO, SUBIDA = max(90.0, AJUSTES["LIGHT_DASH_HUECO"]), 4.0
    X_RESORTES = -1.5                                       # respecto al final del tejado
    with en(t, 20 + X_RESORTES):
        for lado in (-6, -4, -2, 0, 2, 4, 6):
            resorte_vertical(0, lado, 0, velocidad=30, mantener=6)
    x1 = X_RESORTES + 20.0
    x2, x3 = x1 + 25.0, x1 + 45.0
    enemigo("sph", x1, 0, arriba=11.0)
    enemigo("sph", x2, 0, arriba=13.0)
    # 0.7.15: el tercero, LIGHT_DASH_REBOTE m (4) bajo el primer anillo (+14): con el rebote del homing Sonic sube
    # unos 3 m y queda a la altura de la fila (a 1 m pasaba por encima)
    enemigo("sph", x3, 0, arriba=14.0 - AJUSTES["LIGHT_DASH_REBOTE"])
    # 0.7.17: con LIGHT_DASH_HUECO 250 la S de ±2 m era una recta. Ahora es una espiral (hélice alrededor del eje de
    # avance) de radio LIGHT_DASH_ESPIRAL_RADIO: empieza en lo alto de la vuelta (14 m, sobre el tercer Spinner) y
    # acaba en lo alto, 1 m más abajo, antes del aro. El paso sale del giro máximo: la curvatura de una hélice es
    # R / (R² + c²), con c = paso / 2π, y entre dos anillos (a LIGHT_DASH_SEPARACION) gira curvatura × separación;
    # se deja un 15 % de margen bajo LIGHT_DASH_GIRO_MAX. Si no caben 2 vueltas, el hueco se alarga.
    R = AJUSTES["LIGHT_DASH_ESPIRAL_RADIO"]
    k_max = math.radians(0.85 * AJUSTES["LIGHT_DASH_GIRO_MAX"]) / AJUSTES["LIGHT_DASH_SEPARACION"]
    paso_min = 2 * math.pi * math.sqrt(max(0.0, R / k_max - R * R))
    if HUECO - 2.0 - x3 < 2 * paso_min:
        HUECO = x3 + 2.0 + 2 * paso_min
    largo_fila = HUECO - 2.0 - x3
    vueltas = max(2, int(largo_fila / paso_min)) if paso_min > 0 else 2
    n_ctl = max(8, int(largo_fila / 2.0))
    def helice(u):
        fase = 2 * math.pi * vueltas * u
        return (x3 + largo_fila * u, R * math.sin(fase), 14.0 - u - R + R * math.cos(fase))
    fila_light_dash([helice(k / n_ctl) for k in range(n_ctl + 1)],
                    fantasmas=(helice(-1 / n_ctl), helice(1 + 1 / n_ctl)))
    aro_impulso_inclinado(HUECO - 0.5, 0, 12.0, velocidad=30, bajada_grados=40)
    suelo_muerte(0, HUECO, ancho=40, profundidad=18)
    K.avanzar(HUECO, SUBIDA)
    sumar_tiempo(HUECO / VEL["3d"] + 3.0, HUECO)
    t = carretera(24, ancho=14, mat="ssz", muros=0.5, mat_muro="cte")
    with en(t, 9):
        dash_panel(0)
    anillos(3, 7, cada=2.0, tramo=t)
    carretera(10, ancho=14, mat="euc", muros=0)
    t = riel("s9_riel_b", 110, 10, plataforma_final=50, mat="ssz")
    anillos(10, 40, cada=5, tramo=t)
    tejados(3, primero=9, enemigos=True)                                      # los últimos tejados antes del jardín
    carretera(30, ancho=14, mat="euc")
