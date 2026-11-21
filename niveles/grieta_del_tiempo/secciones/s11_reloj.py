# 11. Dentro del reloj (nueva en 0.7.0): la torre del reloj de Rooftop Run por dentro, con un primer planeo más
# corto que el final y en otra dirección (sirve para comprobar el giro de la cámara de planeo). (~15 s)
from base import *  # noqa: F401,F403

# Giro de la cámara de este planeo, en grados (vista desde arriba): se ajusta en ajustes.conf (GIRO_CAMARA_RELOJ).
# Con 135 (0.7.1, Yaw −75) la salida quedaba casi 180° detrás; 0.7.2 probó 315 (Yaw 105) y el usuario, con 180,
# lo ve "casi ideal".
GIRO_CAMARA_RELOJ = AJUSTES["GIRO_CAMARA_RELOJ"]


def riel_secreto(centro, fondo_z, radio=24.0, paso=4.0):
    """Riel semioculto (0.7.7): sale de encima de la torre, casi de frente y 14 m sobre la explanada (0.7.11; ajustes
    RIEL_SECRETO_*; desde la 0.7.9 solo se llega encadenando homing con dos Spinners), baja en espiral por
    FUERA de la torre con cámara cenital fija (radio 24 m; la
    explanada llega a 22 y las paredes a 15,5), da 2 vueltas, se abre
    hacia el túnel de salida y aterriza en la carretera de salida a ~46 m del centro, más allá del checkpoint del fondo:
    más rápido, pero sin ese checkpoint. Un engranaje decorativo en el borde lo tapa a medias. No suma tiempo (atajo)."""
    th = K.th                                            # rumbo de salida (el túnel está en esta dirección)
    # dirección del inicio: RIEL_SECRETO_ANGULO grados a la izquierda del frente (0.7.11: 20; 0.7.10: 45; 0.7.9: 90),
    # para que los Spinners y el riel queden delante de la cámara al llegar
    a0 = th + math.radians(AJUSTES["RIEL_SECRETO_ANGULO"])
    alto = AJUSTES["RIEL_SECRETO_ALTO"]                  # m sobre la explanada (0.7.11: 14; antes 9,5)
    # empieza ENCIMA de la torre: solo se llega encadenando homing, Spinner del centro (+5, zona_planeo) → Spinner
    # lateral → riel. 0.7.11: el lateral pasa de r 7 / +8 a r 13 / alto − 4 (~14 m del central; antes ~7,6 m, tan
    # juntos que no se veían en cámara al encadenarlos)
    enemigo("sph", pos=(centro[0] + 13 * math.cos(a0), centro[1] + 13 * math.sin(a0), centro[2] + alto - 4.0))
    plano = []                                           # (x, y) en planta
    for r in (17.0, 19.0, 21.0):                         # tramo radial hacia fuera, por encima de la explanada
        plano.append((centro[0] + r * math.cos(a0), centro[1] + r * math.sin(a0)))
    for k in range(1, 9):                                # curva suave de radial a tangente (1/8 de vuelta)
        u = k / 8
        a = a0 - (math.pi / 4) * u * u
        r = 21 + (radio - 21) * (1 - (1 - u) ** 2)
        plano.append((centro[0] + r * math.cos(a), centro[1] + r * math.sin(a)))
    a_ini = a0 - math.pi / 4
    a_fin = th + math.pi / 4                             # fin de la espiral; después, curva de apertura hasta 'th'
    giro = (a_fin - a_ini) - 2 * 2 * math.pi             # sentido horario, 2 vueltas
    n = max(8, int(abs(giro) * radio / paso))
    for k in range(1, n + 1):
        a = a_ini + giro * k / n
        plano.append((centro[0] + radio * math.cos(a), centro[1] + radio * math.sin(a)))
    for k in range(1, 9):                                # apertura: de tangente a radial, sin esquinas
        u = k / 8
        a = th + (math.pi / 4) * (1 - u) ** 2
        r = radio + 8 * u * u
        plano.append((centro[0] + r * math.cos(a), centro[1] + r * math.sin(a)))
    for r in (36.0, 41.0, 46.0):                         # recta final sobre la carretera de salida
        plano.append((centro[0] + r * math.cos(th), centro[1] + r * math.sin(th)))
    largos = [0.0]
    for p, q in zip(plano, plano[1:]):
        largos.append(largos[-1] + math.hypot(q[0] - p[0], q[1] - p[1]))
    z0, z1 = centro[2] + alto, fondo_z + 0.35
    puntos = [(x, y, z0 + (z1 - z0) * s / largos[-1]) for (x, y), s in zip(plano, largos)]
    puntos[-1] = (puntos[-1][0], puntos[-1][1], z1)
    riel_grind("s11_riel_secreto@GR", puntos)
    grind_dash(tuple(a + (b - a) * 0.3 for a, b in zip(puntos[0], puntos[1])), giro=a0 - th)   # sale hacia fuera (a0)
    # cámara cenital fija como la del riel de la torre de euc200 (0.7.10): la de detrás temblaba en la espiral. Desde
    # debajo de la explanada hasta 6 m sobre el fondo (el túnel de salida queda con la cámara normal), fuera del pozo.
    camara_cenital_anillo(centro, 15.0, fondo_z + 6.0, centro[2] - 2.5)
    # engranaje decorativo en el borde de la explanada, delante del inicio del riel
    SOLO_VISUAL.disco((centro[0] + 22.5 * math.cos(a0 + 0.12), centro[1] + 22.5 * math.sin(a0 + 0.12), centro[2] + 3.0),
                      3.0, (math.cos(a0 + 0.12 + math.pi / 2), math.sin(a0 + 0.12 + math.pi / 2), 0.0), "euc", n=10, grosor=0.6)


def construir():
    seccion("11 Dentro del reloj")
    costura(16)
    t = carretera(120, ancho=16, giro_grados=70, mat="euc", muros=1.0, muro_der=3.0)    # curva larga a la izquierda
    for s in (30, 90):
        with en(t, s):
            enemigo("euc", 0, 3 if s == 30 else -3)
    anillos(10, 110, cada=7, tramo=t)
    t = carretera(40, ancho=16, mat="euc", muros=1.5)
    with en(t, 20):
        arco_costura(16, alto=8)
    carretera(10, ancho=14, mat="costura", muros=0)

    # el pozo: una explanada alrededor de la boca, 8 ruedas dentadas como paredes y un túnel de salida abajo
    # 195 m: ~10 s de planeo (antes 60 m, ~3 s: la cámara pasaba casi todo el planeo en su transición de 2 s)
    R_BOCA, R_EXPL, PROF = 11.0, 22.0, 195
    centro = K.frame(R_EXPL, 0, 0)
    fondo_z = centro[2] - PROF
    ang_entrada, ang_salida = K.th + math.pi, K.th
    SEG = 20
    for k in range(SEG):
        a0, a1 = 2 * math.pi * k / SEG, 2 * math.pi * (k + 1) / SEG

        def pt(r, a, dz=0.0):
            return (centro[0] + r * math.cos(a), centro[1] + r * math.sin(a), centro[2] + dz)
        SOLIDO.quad(pt(R_BOCA, a0), pt(R_EXPL, a0), pt(R_EXPL, a1), pt(R_BOCA, a1), "euc")
        SOLIDO.quad(pt(R_BOCA, a1, -2), pt(R_EXPL, a1, -2), pt(R_EXPL, a0, -2), pt(R_BOCA, a0, -2), "euc")
        SOLIDO.quad(pt(R_BOCA, a0, -2), pt(R_BOCA, a0), pt(R_BOCA, a1), pt(R_BOCA, a1, -2), "euc")
        SOLIDO.quad(pt(R_EXPL, a1, -2), pt(R_EXPL, a1), pt(R_EXPL, a0), pt(R_EXPL, a0, -2), "euc")

    def dif_ang(a, b):
        return abs((a - b + math.pi) % (2 * math.pi) - math.pi)
    for i in range(8):
        ang = 2 * math.pi * i / 8 + math.pi / 8
        cx, cy = centro[0] + 14 * math.cos(ang), centro[1] + 14 * math.sin(ang)
        base_z, tope = fondo_z, centro[2] + 8
        if dif_ang(ang, ang_entrada) < math.radians(50):
            tope = centro[2] - 2
        if dif_ang(ang, ang_salida) < math.radians(30):
            base_z = fondo_z + 9                              # túnel de salida
        SOLIDO.caja((cx, cy, base_z), (3, 9, tope - base_z), ang, "euc" if i % 2 else "sph")
        # engranajes (solo visuales) en la pared, cada ~20 m de profundidad: el reloj por dentro
        for z in range(15 + 9 * (i % 4), PROF - 15, 20):
            SOLO_VISUAL.disco((centro[0] + 12 * math.cos(ang), centro[1] + 12 * math.sin(ang), centro[2] - z),
                              3.5, (math.cos(ang), math.sin(ang), 0.0), "euc", n=10, grosor=0.5)
    for k in range(int((PROF - 20) / 4)):                  # anillos en espiral por todo el pozo
        a_esp = k * 0.8
        obj("Ring", CAMPOS_RING, pos=(centro[0] + 4 * math.cos(a_esp), centro[1] + 4 * math.sin(a_esp), centro[2] - 10 - 4.0 * k))
    for k in range(int((PROF - 37) / 25) + 1):             # péndulos/escombros a esquivar, lejos del centro
        a = k * math.pi / 2 + 0.4
        SOLIDO.caja((centro[0] + 7 * math.cos(a), centro[1] + 7 * math.sin(a), centro[2] - 22 - 25 * k), (2.5, 2.5, 1.2), a, "sph")
    zona_planeo(centro, PROF, R_BOCA, GIRO_CAMARA_RELOJ)
    SOLIDO.caja((centro[0], centro[1], fondo_z - 2), (36, 36, 2), K.th, "euc")   # suelo del fondo
    MIN_Z[0] = min(MIN_Z[0], fondo_z - 2)
    riel_secreto(centro, fondo_z)

    # salida por el túnel y vuelta al rumbo anterior (curva a la derecha)
    K.x, K.y = centro[0] + 17 * math.cos(K.th), centro[1] + 17 * math.sin(K.th)
    K.z = fondo_z
    registrar_eje(0.0)
    punto_control(3)                     # checkpoint del fondo (0.7.7): quien baja por el riel secreto se lo salta
    t = carretera(60, ancho=14, mat="sph", muros=1.0)
    with en(t, 40):
        enemigo("sph", 0, 0)
    anillos(10, 55, cada=5, tramo=t)
    t = carretera(120, ancho=16, giro_grados=-70, mat="sph", mat_muro="euc", muros=1.0, muro_izq=3.0)
    anillos(10, 110, cada=7, tramo=t)
    carretera(30, ancho=14, mat="euc")
