# Genera la escena del nivel de prueba "solo un camino" y exporta lo que necesitan los conversores.
# Se ejecuta con el Blender aislado:
#   blender --background --factory-startup --python niveles/prueba_camino/crear_escena.py -- <carpeta_salida>
# (scripts\construir_nivel_prueba.ps1 lo llama con las variables BLENDER_USER_* del entorno del mod)
#
# Ejes: Blender X = juego X (dirección de avance), Blender Z = juego Y (arriba), Blender Y = juego -Z.
import os
import sys

import bpy

LARGO = 40.0      # m de camino (de x=-5 a x=35)
INICIO_X = -5.0
ANCHO = 8.0       # m (eje Y de Blender)
GROSOR = 1.0      # m bajo la superficie (la superficie queda en z=0)
RIEL_2D = 1.0     # separación de cada riel del camino 2D respecto al centro (m)

salida = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else os.path.dirname(__file__)
os.makedirs(salida, exist_ok=True)
aqui = os.path.dirname(os.path.abspath(__file__))

# --- escena limpia en metros -------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
escena = bpy.context.scene
escena.unit_settings.system = "METRIC"
escena.unit_settings.scale_length = 1.0
escena.unit_settings.length_unit = "METERS"


def coleccion(nombre):
    c = bpy.data.collections.new(nombre)
    escena.collection.children.link(c)
    return c


def caja(nombre, col, x0, x1, y0, y1, z0, z1):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    caras = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    me = bpy.data.meshes.new(nombre)
    me.from_pydata(v, [], caras)
    me.update()
    ob = bpy.data.objects.new(nombre, me)
    col.objects.link(ob)
    return ob


# --- textura y material del suelo ------------------------------------------------------
tex_path = os.path.join(salida, "teu_suelo_dif.png")
img = bpy.data.images.new("teu_suelo_dif", 256, 256)
pix = []
for y in range(256):
    for x in range(256):
        cuadro = ((x // 32) + (y // 32)) % 2
        r, g, b = (0.55, 0.15, 0.75) if cuadro else (0.15, 0.05, 0.25)   # morado "Time Eater"
        pix += [r, g, b, 1.0]
img.pixels = pix
img.filepath_raw = tex_path
img.file_format = "PNG"
img.save()

mat = bpy.data.materials.new("teu_suelo")
if mat.node_tree is None:          # Blender < 5 crea los materiales sin nodos
    mat.use_nodes = True
nodos = mat.node_tree.nodes
bsdf = nodos.get("Principled BSDF")
nodo_tex = nodos.new("ShaderNodeTexImage")
nodo_tex.image = img
mat.node_tree.links.new(nodo_tex.outputs["Color"], bsdf.inputs["Base Color"])

# --- geometría visual ---------------------------------------------------------------------
col_nivel = coleccion("Nivel")
camino = caja("teu_camino", col_nivel, INICIO_X, INICIO_X + LARGO, -ANCHO / 2, ANCHO / 2, -GROSOR, 0.0)
camino.data.materials.append(mat)
# UV: una repetición de la textura cada 4 m
uv = camino.data.uv_layers.new(name="UVMap")
for poly in camino.data.polygons:
    for li in poly.loop_indices:
        co = camino.data.vertices[camino.data.loops[li].vertex_index].co
        n = poly.normal
        if abs(n.z) > 0.5:
            uv.data[li].uv = (co.x / 4.0, co.y / 4.0)
        elif abs(n.y) > 0.5:
            uv.data[li].uv = (co.x / 4.0, co.z / 4.0)
        else:
            uv.data[li].uv = (co.y / 4.0, co.z / 4.0)

# --- colisión (modelo aparte; el tag de superficie va en el nombre) -----------------------
col_colision = coleccion("Colision")
suelo_col = caja("teu_camino_col@ROCK", col_colision, INICIO_X, INICIO_X + LARGO, -ANCHO / 2, ANCHO / 2, -GROSOR, 0.0)

# --- camino 2D para Sonic clásico (@SV = dos rieles paralelos) ------------------------------
curva = bpy.data.curves.new("teu_camino@SV", type="CURVE")
curva.dimensions = "3D"
for lado in (-RIEL_2D, RIEL_2D):   # primer riel en z de juego positivo, como en los path del juego
    s = curva.splines.new("POLY")
    s.points.add(1)
    s.points[0].co = (INICIO_X + 0.5, lado, 0.0, 1.0)
    s.points[1].co = (INICIO_X + LARGO - 0.5, lado, 0.0, 1.0)
col_paths = coleccion("Splines")
ob_curva = bpy.data.objects.new("teu_camino@SV", curva)
col_paths.objects.link(ob_curva)

# --- referencia de Sonic y marcadores (no se exportan) ---------------------------------------
col_ref = coleccion("Referencias")
ref = caja("REF_Sonic", col_ref, -0.25, 0.25, -0.25, 0.25, 0.0, 1.0)
ref.display_type = "WIRE"
for nombre, x in (("REF_Inicio", 0.0), ("REF_Meta", 25.0)):
    e = bpy.data.objects.new(nombre, None)
    e.empty_display_type = "SINGLE_ARROW"
    e.empty_display_size = 2.0
    e.location = (x, 0.0, 0.0)
    col_ref.objects.link(e)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(salida, "prueba_camino.blend"))


# --- exportar ------------------------------------------------------------------------------
def seleccionar(*objs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]


def exportar_fbx(obj, ruta):
    seleccionar(obj)
    bpy.ops.export_scene.fbx(filepath=ruta, use_selection=True, apply_scale_options="FBX_SCALE_UNITS",
                             add_leaf_bones=False, object_types={"MESH"}, path_mode="COPY", embed_textures=False)


exportar_fbx(camino, os.path.join(salida, "teu_camino.fbx"))
exportar_fbx(suelo_col, os.path.join(salida, "teu_camino_col.fbx"))

# splines con el exportador de zatsick160 (el mismo que usa el addon Time Eater Tools)
import importlib.util
herr = os.environ.get("TEU_HERRAMIENTAS") or os.path.join(aqui, "..", "..", "herramientas")
spec = importlib.util.spec_from_file_location("BlenderToXML", os.path.join(herr, "blender-scripts", "BlenderToXML.py"))
b2x = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b2x)
seleccionar(ob_curva)
b2x.xmlPath = os.path.join(salida, "bde.path.xml")
b2x.processData()

print("TEU_ESCENA_OK", salida)
