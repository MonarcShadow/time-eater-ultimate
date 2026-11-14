# "Grieta del Tiempo" — caja gris de 14 secciones (diseño: niveles/acto2/diseno.md).
# Construye en Blender el recorrido sección a sección (secciones/sNN_*.py, con las herramientas de base.py),
# coloca los objetos y escribe set data, Stage.stg.xml, splines y FBX.
#   blender --background --factory-startup --python niveles/grieta_del_tiempo/generar.py -- <carpeta_nivel> <salida>
import importlib
import importlib.util
import json
import math
import os
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
INICIO = K.frame(2, 0, 0.1)
for nombre in SECCIONES:
    importlib.import_module("secciones." + nombre).construir()
FINAL = importlib.import_module("secciones.s14_blanco").FINAL[0]

# informes: tiempo estimado, solapes del recorrido y archivos de enemigos que debe cargar nivel.json
base.informe_tiempo()
base.comprobar_solapes()
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
exportar_fbx([ob_col, ob_muerte, ob_dano], os.path.join(salida, "teu_camino_col.fbx"))

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
quicksteps = "".join(f"""
    <SingleForward>
      <Name>{n}</Name>
      <PathNum>3</PathNum>
      <Space>4</Space>
    </SingleForward>""" for n in QUICKSTEPS)
with open(os.path.join(dir_xml, "Stage.stg.xml"), "w", encoding="utf-8") as f:
    f.write(f"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!-- Grieta del Tiempo (caja gris), generado por niveles/grieta_del_tiempo/generar.py -->
<Stage>
  <Sonic>
    {xyz('Position', inicio_j)}
    <Yaw>90</Yaw>
    <Start>
      <Mode>None</Mode>
      <Speed>0</Speed>
      <Time>0</Time>
    </Start>
    <DeadHeight>{dead}</DeadHeight>
    <CameraView>Forward</CameraView>
  </Sonic>
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

print(f"TEU_RESUMEN objetos={len(OBJETOS)} caras={len(SOLIDO.f)} splines={len(CURVAS)} deadheight={dead} "
      f"checkpoints={base.PM_ID[0]} final=({FINAL[0]:.0f},{FINAL[1]:.0f},{FINAL[2]:.0f})")
print("TEU_ESCENA_OK", salida)
