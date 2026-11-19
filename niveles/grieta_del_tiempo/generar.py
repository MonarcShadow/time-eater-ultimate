# "Grieta del Tiempo" — caja gris de 14 secciones (diseño: niveles/acto2/diseno.md).
# Construye en Blender el recorrido sección a sección (secciones/sNN_*.py, con las herramientas de base.py),
# coloca los objetos y escribe set data, Stage.stg.xml, splines y FBX.
#   blender --background --factory-startup --python niveles/grieta_del_tiempo/generar.py -- <carpeta_nivel> <salida>
import importlib
import importlib.util
import json
import math
import os
import re
import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1:]
carpeta_nivel, salida = os.path.abspath(args[0]), os.path.abspath(args[1])
os.makedirs(salida, exist_ok=True)
with open(os.path.join(carpeta_nivel, "nivel.json"), encoding="utf-8") as f:
    cfg = json.load(f)
SLOT = cfg["slot"]

aqui = os.path.dirname(os.path.abspath(__file__))
if aqui not in sys.path:
    sys.path.insert(0, aqui)

bpy.ops.wm.read_factory_settings(use_empty=True)
escena = bpy.context.scene
escena.unit_settings.system = "METRIC"
escena.unit_settings.scale_length = 1.0
escena.unit_settings.length_unit = "METERS"

import base  # noqa: E402
from base import (CURVAS, K, MIN_Z, MUERTE, DANO, OBJETOS, QUICKSTEPS, SOLIDO, SOLO_VISUAL, Malla,  # noqa: E402
                  a_juego, xyz)

base.crear_materiales(salida)

# ==============================================================================================
# EL RECORRIDO: las secciones en orden
# ==============================================================================================
SECCIONES = ["s01_colina", "s02_calle", "s03_mar", "s04_autopista", "s05_fabrica", "s06_tanque", "s07_rascacielos",
             "s08_crisis", "s09_persecucion", "s10_jardin", "s11_reloj", "s12_caida", "s13_eco", "s14_blanco"]
# Salida original del nivel: principio de la sección 1 (juego: x 2, y 0.1, z 0, Yaw 90). Copia en salida_original.txt.
INICIO_ORIGINAL = K.frame(2, 0, 0.1)
base.cambio_bgm(8)          # experimento 0.7.2: que la música suene desde la primera carga (ver base.cambio_bgm)
for nombre in SECCIONES:
    importlib.import_module("secciones." + nombre).construir()
FINAL = importlib.import_module("secciones.s14_blanco").FINAL[0]

# Salida de prueba (ajustes.conf: INICIO_SECCION): aparecer en el checkpoint de una sección para no jugar todo el nivel
n_inicio = int(base.AJUSTES["INICIO_SECCION"])
if 1 < n_inicio <= len(base.INICIOS_SECCION):
    INICIO, rumbo_inicio = base.INICIOS_SECCION[n_inicio - 1]
    YAW_INICIO = (90 + math.degrees(rumbo_inicio) + 180) % 360 - 180
    print(f"TEU_AVISO salida de prueba en el checkpoint de la sección {base.SECCIONES[n_inicio - 1][0]} "
          "(poner INICIO_SECCION = 0 antes de publicar)")
else:
    if n_inicio not in (0, 1):
        print(f"TEU_AVISO INICIO_SECCION = {n_inicio} no existe (hay {len(base.INICIOS_SECCION)} secciones): salida original")
    INICIO, YAW_INICIO = INICIO_ORIGINAL, 90.0
print(f"TEU_INICIO {'original' if INICIO is INICIO_ORIGINAL else f'sección {n_inicio}'}: "
      f"juego ({a_juego(INICIO)[0]:.1f}, {a_juego(INICIO)[1]:.1f}, {a_juego(INICIO)[2]:.1f}), Yaw {YAW_INICIO:.1f}")

# informes: tiempo estimado, solapes del recorrido y archivos de enemigos que debe cargar nivel.json
base.informe_tiempo()
base.comprobar_solapes()
base.comprobar_margen_2d()
faltan = [a for a in base.archivos_enemigos() if a not in cfg.get("enemigos", [])]
if faltan:
    print(f"TEU_AVISO faltan en nivel.json 'enemigos': {', '.join(faltan)}")

# ==============================================================================================
# Escena de Blender, exportación y XML
# ==============================================================================================
def coleccion(nombre):
    c = bpy.data.collections.new(nombre)
    escena.collection.children.link(c)
    return c


col_nivel, col_col, col_spl, col_ref = coleccion("Nivel"), coleccion("Colision"), coleccion("Splines"), coleccion("Referencias")
ob_solido = SOLIDO.objeto("teu_camino", col_nivel)
ob_rieles = SOLO_VISUAL.objeto("teu_rieles", col_nivel)
ob_col = SOLIDO.objeto("teu_camino_col@ROCK", col_col)
ob_muerte = MUERTE.objeto("teu_muerte_col@DEAD", col_col)
ob_dano = DANO.objeto("teu_lava_col@DAMAGE", col_col)
# agua para correr encima (tags propios que añade construir_nivel.ps1; ver base.AGUA)
obs_agua = [base.AGUA[v].objeto(f"teu_agua_{v.lower()}_col@{tag}", col_col)
            for v, tag in (("A", "AGUAMUERTE"), ("B", "AGUAHONDA")) if base.AGUA[v].f]
ref = Malla()
ref.caja(INICIO, (0.5, 0.5, 1.0), 0, "gris")
r = ref.objeto("REF_Sonic", col_ref)
r.display_type = "WIRE"

obs_curvas = []
for nombre, rieles in CURVAS:
    cu = bpy.data.curves.new(nombre, type="CURVE")
    cu.dimensions = "3D"
    for pts in rieles:
        s = cu.splines.new("POLY")
        s.points.add(len(pts) - 1)
        for i, p in enumerate(pts):
            s.points[i].co = (p[0], p[1], p[2], 1.0)
    ob = bpy.data.objects.new(nombre, cu)
    col_spl.objects.link(ob)
    obs_curvas.append(ob)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(salida, cfg["nombre"] + ".blend"))


def seleccionar(objs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]


def exportar_fbx(objs, ruta):
    seleccionar(objs)
    bpy.ops.export_scene.fbx(filepath=ruta, use_selection=True, apply_scale_options="FBX_SCALE_UNITS",
                             add_leaf_bones=False, object_types={"MESH"}, path_mode="COPY", embed_textures=False)


exportar_fbx([ob_solido, ob_rieles], os.path.join(salida, "teu_camino.fbx"))
exportar_fbx([ob_col, ob_muerte, ob_dano] + obs_agua, os.path.join(salida, "teu_camino_col.fbx"))

herr = os.environ.get("TEU_HERRAMIENTAS") or os.path.join(carpeta_nivel, "..", "..", "herramientas")
spec = importlib.util.spec_from_file_location("BlenderToXML", os.path.join(herr, "blender-scripts", "BlenderToXML.py"))
b2x = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b2x)
seleccionar(obs_curvas)
b2x.xmlPath = os.path.join(salida, SLOT + ".path.xml")
b2x.processData()

# XML generados (se copian al archivo #<slot> y reemplazan a los de escenario_<slot>)
dir_xml = os.path.join(salida, "escenario")
os.makedirs(dir_xml, exist_ok=True)
with open(os.path.join(dir_xml, "setdata_base.set.xml"), "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="utf-8" standalone="no" ?>\n<SetObject>\n' + "\n".join(OBJETOS) + "\n</SetObject>\n")
inicio_j = a_juego(INICIO)
dead = math.floor(MIN_Z[0] - 40)

# Mundo de Havok: si Sonic o los objetos salen de él, la física se detiene (anillos, paneles y checkpoints dejan de
# funcionar: el "Ghost Mode" que describe el Unleashed Project; nos pasó en la 0.7.0 a ~4 km del origen).
# Se declara como en el Stage.stg.xml del Time Eater (#blb: ±5000), cubriendo todo el nivel con margen.
pts_j = [a_juego(v) for m in (SOLIDO, SOLO_VISUAL, MUERTE) for v in m.v]
for linea in OBJETOS:
    mpos = re.search(r"<Position><x>([^<]*)</x><y>([^<]*)</y><z>([^<]*)</z></Position>", linea)
    if mpos:
        pts_j.append(tuple(float(c) for c in mpos.groups()))
MARGEN = 1000
mundo_min = [min(p[i] for p in pts_j) - MARGEN for i in range(3)]
mundo_max = [max(p[i] for p in pts_j) + MARGEN for i in range(3)]
mundo_min[1] = min(mundo_min[1], dead - 200)
quicksteps = "".join(f"""
    <SingleForward>
      <Name>{n}</Name>
      <PathNum>3</PathNum>
      <Space>4</Space>
    </SingleForward>""" for n in QUICKSTEPS)
# splines guía de las tirolinas: el Pulley las usa con PathID = ID (como GuidePath001..005 en ssz200)
quicksteps += "".join(f"""
    <Guide>
      <Name>{n}</Name>
      <ID>{i}</ID>
    </Guide>""" for n, i in base.GUIAS)
with open(os.path.join(dir_xml, "Stage.stg.xml"), "w", encoding="utf-8") as f:
    f.write(f"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!-- Grieta del Tiempo (caja gris), generado por niveles/grieta_del_tiempo/generar.py -->
<Stage>
  <Sonic>
    {xyz('Position', inicio_j)}
    <Yaw>{YAW_INICIO:g}</Yaw>
    <Start>
      <Mode>None</Mode>
      <Speed>0</Speed>
      <Time>0</Time>
    </Start>
    <DeadHeight>{dead}</DeadHeight>
    <CameraView>Forward</CameraView>
  </Sonic>
  <World>
    {xyz('Min', [math.floor(c) for c in mundo_min])}
    {xyz('Max', [math.ceil(c) for c in mundo_max])}
  </World>
  <BGM>
    <IsStream>true</IsStream>
    <Container>{cfg.get("bgm_container", "SNG15_BPC")}</Container>
    <Name>{cfg.get("bgm_nombre", "Boss_Perfect_Chaos1")}</Name>
  </BGM>
  <Path>
    <Container>{SLOT}</Container>{quicksteps}
    <IsTerrain>false</IsTerrain>
    <IsAutoLoad>true</IsAutoLoad>
    <IsRender>false</IsRender>
  </Path>
</Stage>
""")

# Parámetros de Sonic solo para este escenario (redefinición parcial, como hace el #bpc original con <Water>):
# - Planeo más lento que el global de bb3\#Sonic.ar.00 (Float 40, Dive 90.1, BeginGravityScale 2.4).
# - Alcance del homing desde ajustes.conf (global: ForwardView 21.1 / 21.1; SideView 13.5 / 18.3).
h3d = base.AJUSTES["HOMING_ALCANCE_3D"]
h2d = base.AJUSTES["HOMING_ALCANCE_2D"]
h2d_n = h2d * 18.3 / 13.5


def homing(lejos, lejos_n):
    return f"""
    <Category>
      <HomingAttack>
        <Param>
          <HomingLockonCollisionFar>{lejos:g}</HomingLockonCollisionFar>
          <HomingLockonCollisionFarN>{lejos_n:.1f}</HomingLockonCollisionFarN>
        </Param>
      </HomingAttack>
    </Category>"""


with open(os.path.join(dir_xml, "Sonic.prm.xml"), "w", encoding="utf-8") as f:
    f.write(f"""<?xml version="1.0" encoding="utf-8" standalone="no" ?>
<!-- Parámetros de Sonic solo para Grieta del Tiempo, generado por niveles/grieta_del_tiempo/generar.py.
     El alcance del homing se cambia en niveles/grieta_del_tiempo/ajustes.conf. -->
<Sonic.prm.xml>
  <Common>
    <Category>
      <Diving>
        <Param>
          <DivingDamageTime>1</DivingDamageTime>
          <DivingDamageVelocityDecreaseRate>0.5</DivingDamageVelocityDecreaseRate>
          <DivingDiveBeginGravityScale>1.2</DivingDiveBeginGravityScale>
          <DivingDiveBeginHorzVelocityRate>0.85</DivingDiveBeginHorzVelocityRate>
          <DivingDiveEndSpeed>20</DivingDiveEndSpeed>
          <DivingDiveMaxVelocityDown>45</DivingDiveMaxVelocityDown>
          <DivingDiveVelocityFront>0.7</DivingDiveVelocityFront>
          <DivingDiveVelocitySide>0.7</DivingDiveVelocitySide>
          <DivingFloatMaxVelocityDown>18</DivingFloatMaxVelocityDown>
          <DivingFloatVelocityFront>0.4</DivingFloatVelocityFront>
          <DivingFloatVelocitySide>0.4</DivingFloatVelocitySide>
          <DivingRotationMax>20</DivingRotationMax>
        </Param>
      </Diving>
    </Category>
  </Common>
  <ForwardView>{homing(h3d, h3d)}
  </ForwardView>
  <SideView>{homing(h2d, h2d_n)}
  </SideView>
</Sonic.prm.xml>
""")

print(f"TEU_HOMING 3D={h3d:g} m, 2D={h2d:g}/{h2d_n:.1f} m; camara reloj={base.AJUSTES['GIRO_CAMARA_RELOJ']:g}, "
      f"planeo final={base.AJUSTES['GIRO_CAMARA_PLANEO']:g}")
print(f"TEU_RESUMEN objetos={len(OBJETOS)} caras={len(SOLIDO.f)} splines={len(CURVAS)} deadheight={dead} "
      f"checkpoints={base.PM_ID[0]} mundo=({mundo_min[0]:.0f},{mundo_min[1]:.0f},{mundo_min[2]:.0f})-({mundo_max[0]:.0f},{mundo_max[1]:.0f},{mundo_max[2]:.0f}) final=({FINAL[0]:.0f},{FINAL[1]:.0f},{FINAL[2]:.0f})")
print("TEU_ESCENA_OK", salida)
