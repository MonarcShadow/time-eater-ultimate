# Genera la escena de un nivel "camino recto" a partir del nivel.json de su carpeta y exporta lo que
# necesitan los conversores (FBX visual, FBX de colisión, textura y, si es 2D, el path.xml).
#   blender --background --factory-startup --python niveles/comun/crear_camino.py -- <carpeta_nivel> <carpeta_salida>
# Ejes: Blender X = juego X (avance), Blender Z = juego Y (arriba), Blender Y = juego -Z.
import importlib.util
import json
import os
import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1:]
carpeta_nivel, salida = os.path.abspath(args[0]), os.path.abspath(args[1])
os.makedirs(salida, exist_ok=True)
with open(os.path.join(carpeta_nivel, "nivel.json"), encoding="utf-8") as f:
    cfg = json.load(f)
esc = cfg["escena"]
slot = cfg["slot"]
LARGO, INICIO_X, ANCHO, GROSOR = esc["largo"], esc.get("inicio_x", -5.0), esc["ancho"], 1.0
COLOR_A, COLOR_B = esc.get("color_a", [0.55, 0.15, 0.75]), esc.get("color_b", [0.15, 0.05, 0.25])

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


# textura a cuadros y material
img = bpy.data.images.new("teu_suelo_dif", 256, 256)
pix = []
for y in range(256):
    for x in range(256):
        r, g, b = COLOR_A if ((x // 32) + (y // 32)) % 2 else COLOR_B
        pix += [r, g, b, 1.0]
img.pixels = pix
img.filepath_raw = os.path.join(salida, "teu_suelo_dif.png")
img.file_format = "PNG"
img.save()
mat = bpy.data.materials.new("teu_suelo")
if mat.node_tree is None:          # Blender < 5 crea los materiales sin nodos
    mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
nodo_tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
nodo_tex.image = img
mat.node_tree.links.new(nodo_tex.outputs["Color"], bsdf.inputs["Base Color"])

# camino visual (UV: una repetición cada 4 m)
col_nivel = coleccion("Nivel")
camino = caja("teu_camino", col_nivel, INICIO_X, INICIO_X + LARGO, -ANCHO / 2, ANCHO / 2, -GROSOR, 0.0)
camino.data.materials.append(mat)
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

# colisión aparte (tag de superficie en el nombre)
col_colision = coleccion("Colision")
suelo_col = caja("teu_camino_col@" + esc.get("tag_colision", "ROCK"), col_colision,
                 INICIO_X, INICIO_X + LARGO, -ANCHO / 2, ANCHO / 2, -GROSOR, 0.0)

# camino 2D opcional (@SV = dos rieles; el primero en z de juego positivo, como en los path del juego)
ob_curva = None
if esc.get("camino_2d"):
    curva = bpy.data.curves.new("teu_camino@SV", type="CURVE")
    curva.dimensions = "3D"
    for lado in (-1.0, 1.0):
        s = curva.splines.new("POLY")
        s.points.add(1)
        s.points[0].co = (INICIO_X + 0.5, lado, 0.0, 1.0)
        s.points[1].co = (INICIO_X + LARGO - 0.5, lado, 0.0, 1.0)
    ob_curva = bpy.data.objects.new("teu_camino@SV", curva)
    coleccion("Splines").objects.link(ob_curva)

# referencias (no se exportan): caja de Sonic y marcadores de inicio y meta
col_ref = coleccion("Referencias")
ref = caja("REF_Sonic", col_ref, -0.25, 0.25, -0.25, 0.25, 0.0, 1.0)
ref.display_type = "WIRE"
for nombre, x in (("REF_Inicio", 0.0), ("REF_Meta", esc.get("meta_x", LARGO - 10))):
    e = bpy.data.objects.new(nombre, None)
    e.empty_display_type = "SINGLE_ARROW"
    e.empty_display_size = 2.0
    e.location = (x, 0.0, 0.0)
    col_ref.objects.link(e)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(salida, cfg["nombre"] + ".blend"))


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

if ob_curva:
    herr = os.environ.get("TEU_HERRAMIENTAS") or os.path.join(carpeta_nivel, "..", "..", "herramientas")
    spec = importlib.util.spec_from_file_location("BlenderToXML", os.path.join(herr, "blender-scripts", "BlenderToXML.py"))
    b2x = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(b2x)
    seleccionar(ob_curva)
    b2x.xmlPath = os.path.join(salida, slot + ".path.xml")
    b2x.processData()

print("TEU_ESCENA_OK", salida)
