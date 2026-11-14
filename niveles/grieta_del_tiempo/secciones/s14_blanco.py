# 14. Blanco: White Space, todo desteñido; meta frente al ojo del Time Eater (~15 s)
from base import *  # noqa: F401,F403

FINAL = [None]


def construir():
    seccion("14 Blanco")
    # fragmentos en 2D (nuevo en 0.7.0): trozos blancos de las zonas flotando en el vacío
    t = carretera(40, ancho=16, mat="blanco", muros=0.4)
    with en(t, 10):
        arco_costura(16)
    tramo_2d("s14_2d", (0, 1.5, 3.0, 1.5, 3.0, 4.5, 3.0, 1.5, 0), mats=("blanco", "gris"), mat_salida="blanco")
    # avenida blanca (nuevo en 0.7.0): las 9 zonas desteñidas a los lados y paneles para el último sprint
    ritmo("rapido")
    t = carretera(220, ancho=22, mat="blanco", muros=0.4)
    for i, zona in enumerate(ZONAS):
        with en(t, 15 + i * 22):
            lado = 16 if i % 2 else -16
            decorado(0, lado, -2, (8, 6, 6 + (i % 3) * 4), zona if i < 3 else "blanco")   # el color se va comiendo
            if i % 3 == 0:
                costura(22)
    for s in (10, 80, 150):
        with en(t, s):
            dash_panel(0)
    anillos(20, 210, cada=7, tramo=t)
    ritmo("3d")
    t = carretera(90, ancho=26, mat="blanco", muros=0.4)
    costura(26, -88)
    for i, zona in enumerate(ZONAS):                                          # piezas quietas y desteñidas de las 9 zonas
        lado = -22 if i % 2 else 22
        decorado(-85 + i * 9, lado, 2 + (i % 3) * 3, (5, 5, 5), "blanco", 25 * i)
        tubo((-82 + i * 9, -lado * 1.3, -4), (-82 + i * 9, -lado * 1.3, 6 + (i % 4) * 4), 1.5, "blanco", n=8)
    riel_grind("s14_aguja@GR", [K.frame(-80, -6, 0.35), K.frame(-38, -6, 0.35)])  # la aguja del reloj
    tubo((-38, -6, 0.1), (-34, -6, 0.1), 0.5, "costura", solido=False, n=6)   # punta de la aguja
    anillos(-80, -45, cada=5, lado=5)
    aro_impulso(-38, 5)                                                       # DashRing (orientación confirmada en 0.6.0)
    adelante_v = (math.cos(K.th), math.sin(K.th), 0.0)                        # el ojo del Time Eater: disco morado con pupila blanca
    SOLIDO.disco(K.frame(34, 0, 22), 16, adelante_v, "costura", n=20, grosor=2)
    SOLO_VISUAL.disco(K.frame(32.6, 0, 22), 6, adelante_v, "blanco", n=16, grosor=0.4)
    SOLO_VISUAL.disco(K.frame(32.2, 0, 22), 2.5, adelante_v, "sph", n=12, grosor=0.4)
    obj("GoalRing", "<GroundOffset>0</GroundOffset><IsCastShadow>true</IsCastShadow><IsMessageOn>false</IsMessageOn><Radius>4</Radius>"
        f"<Range>200</Range>{xyz('ResultPosition', a_juego(K.frame(-20, 0, 0)))}<SENumber>6</SENumber>",
        -20, 0, 2.3, q=q_yaw())           # el GoalRing solo lleva giro horizontal (vertical por defecto)
    FINAL[0] = K.frame(0, 0, 0)
