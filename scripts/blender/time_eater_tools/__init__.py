# Time Eater Tools - utilidades de Blender para el mod Time Eater Ultimate (Sonic Generations 2011).
# Panel en la barra lateral del Viewport 3D (tecla N) > pestaña "Time Eater".
#
# Reglas que aplica (documentadas en la bóveda Obsidian, wiki/niveles):
#   - Generations usa metros; Sonic mide 0.5 x 0.5 x 1.0 m.
#   - FBX para Hedgehog Converter / Havok Converter: "Apply Scalings: FBX Units Scale" y sin leaf bones.
#   - Nombres con puntos extra (p. ej. "Material.001") rompen la carga en el juego.
#   - Splines: curvas Poly con sufijo @SV/@GR/@QS/@DP, exportadas con BlenderToXML.py (zatsick160).

import importlib.util
import os

import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper

REF_NAME = "REF_Sonic"
REF_COLLECTION = "Referencias"
SPLINE_SUFFIXES = ("@SV", "@GR", "@QS", "@DP")


def herramientas_dir():
    """Carpeta herramientas/ del mod (la define abrir_blender.bat)."""
    return os.environ.get("TEU_HERRAMIENTAS", "")


# ---------------------------------------------------------------------------
# Escena
# ---------------------------------------------------------------------------

class TEU_OT_setup_scene(bpy.types.Operator):
    """Unidades métricas, escala 1.0 y metros (como Sonic Generations)"""
    bl_idname = "teu.setup_scene"
    bl_label = "Configurar escena"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        units = context.scene.unit_settings
        units.system = "METRIC"
        units.scale_length = 1.0
        units.length_unit = "METERS"
        self.report({"INFO"}, "Escena en metros, escala 1.0")
        return {"FINISHED"}


class TEU_OT_add_sonic_reference(bpy.types.Operator):
    """Caja de 0.5 x 0.5 x 1.0 m con el tamaño de Sonic (no se exporta)"""
    bl_idname = "teu.add_sonic_reference"
    bl_label = "Añadir referencia de Sonic"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        coll = bpy.data.collections.get(REF_COLLECTION)
        if coll is None:
            coll = bpy.data.collections.new(REF_COLLECTION)
            context.scene.collection.children.link(coll)
        mesh = bpy.data.meshes.new(REF_NAME)
        # Caja con la base en z=0 (los pies de Sonic en el suelo)
        sx, sy, sz = 0.25, 0.25, 1.0
        verts = [(-sx, -sy, 0), (sx, -sy, 0), (sx, sy, 0), (-sx, sy, 0),
                 (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)]
        faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        mesh.from_pydata(verts, [], faces)
        obj = bpy.data.objects.new(REF_NAME, mesh)
        obj.location = context.scene.cursor.location
        obj.display_type = "WIRE"
        obj.hide_render = True
        coll.objects.link(obj)
        self.report({"INFO"}, "Referencia de Sonic añadida en el cursor 3D")
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Validación
# ---------------------------------------------------------------------------

class TEU_OT_fix_names(bpy.types.Operator):
    """Quita los sufijos '.001' de materiales y texturas (rompen la carga en el juego)"""
    bl_idname = "teu.fix_names"
    bl_label = "Corregir nombres con puntos"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        cambiados = 0
        for coleccion in (bpy.data.materials, bpy.data.images):
            for item in coleccion:
                if "." in item.name and not item.name.lower().endswith((".png", ".dds", ".tga", ".jpg")):
                    nuevo = item.name.replace(".", "_")
                    if nuevo not in coleccion:
                        item.name = nuevo
                        cambiados += 1
                    else:
                        self.report({"WARNING"}, f"No se renombró '{item.name}': ya existe '{nuevo}'")
        self.report({"INFO"}, f"{cambiados} nombre(s) corregido(s)")
        return {"FINISHED"}


def problemas_de_escena():
    problemas = []
    if bpy.context.scene.unit_settings.system != "METRIC" or abs(bpy.context.scene.unit_settings.scale_length - 1.0) > 1e-6:
        problemas.append("La escena no está en metros / escala 1.0")
    for m in bpy.data.materials:
        if m.users and "." in m.name:
            problemas.append(f"Material con punto: {m.name}")
    for o in bpy.data.objects:
        if o.type == "CURVE" and o.name.endswith(SPLINE_SUFFIXES):
            if any(s.type != "POLY" for s in o.data.splines):
                problemas.append(f"Spline no Poly: {o.name}")
    return problemas


# ---------------------------------------------------------------------------
# Exportación
# ---------------------------------------------------------------------------

class TEU_OT_export_fbx(bpy.types.Operator, ExportHelper):
    """FBX para Hedgehog Converter (terreno) o Havok Converter (colisión)"""
    bl_idname = "teu.export_fbx"
    bl_label = "Exportar FBX (Hedgehog/Havok)"
    filename_ext = ".fbx"
    filter_glob: StringProperty(default="*.fbx", options={"HIDDEN"})

    def execute(self, context):
        # Se exporta solo la selección, excluyendo la referencia de Sonic
        ref = bpy.data.objects.get(REF_NAME)
        ref_sel = bool(ref and ref.select_get())
        if ref_sel:
            ref.select_set(False)
        try:
            bpy.ops.export_scene.fbx(
                filepath=self.filepath,
                use_selection=True,
                apply_unit_scale=True,
                apply_scale_options="FBX_SCALE_UNITS",
                add_leaf_bones=False,
                bake_anim=False,
                path_mode="COPY",
                embed_textures=False,
            )
        finally:
            if ref_sel:
                ref.select_set(True)
        self.report({"INFO"}, f"FBX exportado: {self.filepath}")
        return {"FINISHED"}


def _cargar_blendertoxml():
    ruta = os.path.join(herramientas_dir(), "blender-scripts", "BlenderToXML.py")
    if not os.path.isfile(ruta):
        raise FileNotFoundError(f"No se encontró {ruta}. Ejecuta scripts/descargar_herramientas.ps1")
    spec = importlib.util.spec_from_file_location("teu_blendertoxml", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class TEU_OT_export_splines(bpy.types.Operator, ExportHelper):
    """Exporta las curvas Poly seleccionadas a un path.xml de Sonic Generations (BlenderToXML.py, GPL-3.0, zatsick160)"""
    bl_idname = "teu.export_splines"
    bl_label = "Exportar splines (path.xml)"
    filename_ext = ".xml"
    filter_glob: StringProperty(default="*.xml", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return any(o.type == "CURVE" for o in context.selected_objects)

    def execute(self, context):
        malas = [o.name for o in context.selected_objects
                 if o.type != "CURVE" or any(s.type != "POLY" for s in o.data.splines)]
        if malas:
            self.report({"ERROR"}, "Solo curvas de tipo Poly: " + ", ".join(malas))
            return {"CANCELLED"}
        sin_sufijo = [o.name for o in context.selected_objects if not o.name.endswith(SPLINE_SUFFIXES)]
        if sin_sufijo:
            self.report({"WARNING"}, "Sin sufijo @SV/@GR/@QS/@DP (se exportan como guide path): " + ", ".join(sin_sufijo))
        try:
            modulo = _cargar_blendertoxml()
        except FileNotFoundError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        modulo.xmlPath = self.filepath
        modulo.processData()
        self.report({"INFO"}, f"Splines exportados: {self.filepath}")
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Panel
# ---------------------------------------------------------------------------

class TEU_PT_panel(bpy.types.Panel):
    bl_label = "Time Eater Ultimate"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Time Eater"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Escena")
        col.operator(TEU_OT_setup_scene.bl_idname, icon="SCENE_DATA")
        col.operator(TEU_OT_add_sonic_reference.bl_idname, icon="MESH_CUBE")

        col = layout.column(align=True)
        col.label(text="Revisión")
        problemas = problemas_de_escena()
        if problemas:
            for p in problemas[:6]:
                col.label(text=p, icon="ERROR")
            if len(problemas) > 6:
                col.label(text=f"... y {len(problemas) - 6} más")
        else:
            col.label(text="Sin problemas detectados", icon="CHECKMARK")
        col.operator(TEU_OT_fix_names.bl_idname, icon="SORTALPHA")

        col = layout.column(align=True)
        col.label(text="Exportar (selección)")
        col.operator(TEU_OT_export_fbx.bl_idname, icon="EXPORT")
        col.operator(TEU_OT_export_splines.bl_idname, icon="CURVE_PATH")
        if not herramientas_dir():
            layout.label(text="Abre Blender con scripts/abrir_blender.bat", icon="INFO")


CLASES = (
    TEU_OT_setup_scene,
    TEU_OT_add_sonic_reference,
    TEU_OT_fix_names,
    TEU_OT_export_fbx,
    TEU_OT_export_splines,
    TEU_PT_panel,
)


def register():
    for c in CLASES:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(CLASES):
        bpy.utils.unregister_class(c)
