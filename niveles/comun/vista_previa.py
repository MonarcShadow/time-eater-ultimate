# Renderiza vistas de control de un nivel construido (geometría + marcadores de objetos del set data).
#   blender --background <nivel>.blend --python niveles/comun/vista_previa.py -- <setdata.xml> <path.xml> <carpeta_png>
# Colores de marcadores: anillos amarillos, paneles/rampas/resortes azules, cambios de modo rojos, meta blanca.
import math
import os
import sys
import xml.etree.ElementTree as ET

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
setdata, pathxml, salida = args[0], args[1], args[2]
os.makedirs(salida, exist_ok=True)
escena = bpy.context.scene

for ob in list(bpy.data.objects):
    if ob.name.startswith("teu_camino_col") or ob.name.startswith("teu_muerte"):
        ob.hide_render = True


def material(nombre, color):
    m = bpy.data.materials.new(nombre)
    m.diffuse_color = (*color, 1.0)
    return m


# --- comprobaciones automáticas (antes de crear los marcadores, para que los rayos solo toquen el nivel) ---
dg = bpy.context.evaluated_depsgraph_get()
ABAJO = Vector((0, 0, -1))


def hay_suelo(p, alto=1.5, alcance=4.0):
    ok, _, _, _, ob, _ = escena.ray_cast(dg, p + Vector((0, 0, alto)), ABAJO, distance=alcance)
    return ok and ob.name.startswith("teu_camino")


avisos = 0
for el in ET.parse(setdata).getroot():
    p = el.find("Position")
    gx, gy, gz = (float(p.find(c).text) for c in "xyz")
    pos = Vector((gx, -gz, gy))
    if el.tag.startswith("ChangeMode_"):
        r = el.find("Rotation")
        th = 2 * math.atan2(float(r.find("y").text), float(r.find("w").text)) - math.pi / 2
        d = Vector((math.cos(th), math.sin(th), 0))
        for nombre, q in (("en el trigger", pos), ("8 m antes/después", pos + d * 8), ("8 m después/antes", pos - d * 8)):
            if not hay_suelo(q):
                avisos += 1
                print(f"TEU_AVISO {el.tag} en ({gx:.0f},{gy:.0f},{gz:.0f}): no hay suelo {nombre} (¿precipicio cerca?)")
    elif el.tag in ("DashPanel", "JumpBoard", "Spring", "PointMarker"):
        if not hay_suelo(pos, alto=1.0, alcance=1.6):
            avisos += 1
            print(f"TEU_AVISO {el.tag} en ({gx:.0f},{gy:.0f},{gz:.0f}): no está apoyado en el suelo")
    elif el.tag.startswith("Enemy") and el.tag not in ("EnemySpinner", "EnemyEggRobo3D"):   # los voladores no se comprueban
        if not hay_suelo(pos, alto=1.0, alcance=2.5):
            avisos += 1
            print(f"TEU_AVISO {el.tag} en ({gx:.0f},{gy:.0f},{gz:.0f}): enemigo sin suelo debajo")
print(f"TEU_COMPROBACION avisos={avisos}")

COLORES = {"Ring": (1, 0.85, 0), "DashPanel": (0, 0.4, 1), "JumpBoard": (0, 0.4, 1), "Spring": (0, 0.8, 1),
           "GrindDashPanel": (0, 1, 0.5), "GoalRing": (1, 1, 1)}
mats = {}
marcas = []
for el in ET.parse(setdata).getroot():
    p = el.find("Position")
    gx, gy, gz = (float(p.find(c).text) for c in "xyz")
    pos = Vector((gx, -gz, gy))                       # juego -> Blender
    tipo = el.tag
    color = COLORES.get(tipo, (1, 0, 0) if tipo.startswith("ChangeMode") else (1, 0.3, 0.8))
    if tipo not in mats:
        mats[tipo] = material("m_" + tipo, color)
    r = 0.6 if tipo == "Ring" else (2.5 if tipo.startswith("ChangeMode") or tipo == "GoalRing" else 1.2)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=pos, segments=8, ring_count=6)
    bpy.context.object.data.materials.append(mats[tipo])
    marcas.append(pos)

# splines del path.xml como tubos rojos/verdes
raiz = ET.parse(pathxml).getroot()
for geo in raiz.iter("geometry"):
    nombre = geo.get("name")
    nodo = next(n for n in raiz.iter("node") if n.get("name") + "-geometry" == nombre)
    tx, ty, tz = (float(v) for v in nodo.find("translate").text.split())
    for s3 in geo.iter("spline3d"):
        pts = []
        for k in s3.iter("knot"):
            x, y, z = (float(v) for v in k.find("point").text.split())
            pts.append(Vector((x + tx, -(z + tz), y + ty)))
        cu = bpy.data.curves.new(nombre, "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = 0.4
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for i, v in enumerate(pts):
            sp.points[i].co = (*v, 1)
        ob = bpy.data.objects.new(nombre, cu)
        ob.data.materials.append(material("m_" + nombre, (0.1, 1, 0.1) if "@GR" in nombre else (1, 0.1, 0.1)))
        escena.collection.objects.link(ob)

escena.render.engine = "BLENDER_WORKBENCH"
escena.display.shading.light = "STUDIO"
escena.display.shading.color_type = "MATERIAL"
escena.display.shading.show_shadows = True
escena.render.resolution_x, escena.render.resolution_y = 1600, 900
escena.world = bpy.data.worlds.new("w")
escena.world.color = (0.05, 0.05, 0.08)

nivel = [o for o in bpy.data.objects if o.name == "teu_camino"][0]
bb = [nivel.matrix_world @ Vector(c) for c in nivel.bound_box]
centro = sum(bb, Vector()) / 8
tam = max((max(v[i] for v in bb) - min(v[i] for v in bb)) for i in range(3))

cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
escena.collection.objects.link(cam)
escena.camera = cam


def mirar(ob, objetivo):
    ob.rotation_euler = (objetivo - ob.location).to_track_quat("-Z", "Y").to_euler()


def render(nombre):
    escena.render.filepath = os.path.join(salida, nombre + ".png")
    bpy.ops.render.render(write_still=True)


# vista cenital ortográfica
cam_data.type = "ORTHO"
cam_data.ortho_scale = tam * 1.05
cam_data.clip_end = 5000
cam.location = centro + Vector((0, 0, 1500))
cam.rotation_euler = (0, 0, 0)
render("00_cenital")

# vistas en perspectiva por tramos del recorrido (cada ~1/6 de los marcadores, en orden)
cam_data.type = "PERSP"
cam_data.lens = 24
n = len(marcas)
for k, i in enumerate(range(0, n, max(1, n // int(os.environ.get("TEU_VISTAS", "8"))))):
    p = marcas[i]
    cam.location = p + Vector((-30, 35, 28))
    mirar(cam, p + Vector((25, 0, -5)))
    render(f"{k + 1:02d}_tramo")
# vistas laterales en cada entrada a 2D (para revisar las secciones de plataformas)
k = 0
for el in ET.parse(setdata).getroot():
    if el.tag != "ChangeMode_3Dto2D":
        continue
    r = el.find("Rotation")
    w, y = float(r.find("w").text), float(r.find("y").text)
    th = 2 * math.atan2(y, w) - math.pi / 2                    # rumbo en Blender
    p = el.find("Position")
    gx, gy, gz = (float(p.find(c).text) for c in "xyz")
    pos = Vector((gx, -gz, gy))
    adelante = Vector((math.cos(th), math.sin(th), 0))
    lado = Vector((-math.sin(th), math.cos(th), 0))
    cam.location = pos + adelante * 15 - lado * 55 + Vector((0, 0, 12))
    mirar(cam, pos + adelante * 15 + Vector((0, 0, 8)))
    k += 1
    render(f"2d_{k:02d}")

# vistas de cada zona de planeo (ChangeDiveBegin): desde arriba en diagonal y de lado
k = 0
for el in ET.parse(setdata).getroot():
    if el.tag != "ChangeDiveBegin":
        continue
    p = el.find("Position")
    gx, gy, gz = (float(p.find(c).text) for c in "xyz")
    pos = Vector((gx, -gz, gy))
    k += 1
    cam.location = pos + Vector((-45, 30, 45))
    mirar(cam, pos + Vector((0, 0, -10)))
    render(f"pozo_{k:02d}_arriba")
    cam.location = pos + Vector((-20, 120, -40))
    mirar(cam, pos + Vector((0, 0, -55)))
    render(f"pozo_{k:02d}_lado")
print("TEU_PREVIA_OK")
