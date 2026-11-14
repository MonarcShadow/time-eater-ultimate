"""Extrae plantillas (campos sin Position/Rotation/SetObjectID) de objetos de los actos originales.
Elige la instancia más 'simple' (la más frecuente en su forma de campos) y vacía los enlaces a otros objetos."""
import sys, os, re, collections
import xml.etree.ElementTree as ET

base, salida = sys.argv[1], sys.argv[2]
QUIERO = {
    "EnemyMotora3D": "ghz200", "EnemyLander3D": "cpz200", "EnemyEggRobo3D": "ssz200", "EnemySpinner": "sph200",
    "EnemyGunHunter3D": "cte200", "EnemyPawnLance3D": "ssh200", "EnemyTaker3D": "csc200", "EnemyPawnPla3D": "pla200",
    "PointMarker": "ghz200", "SszUpDownPole": "ssz200", "SszUpDownPoleStand": "ssz200", "GeneralFloor": "ghz200",
}
fuera = {"Position", "Rotation", "SetObjectID"}


def ser(e):
    """Serializa un elemento hijo como XML compacto."""
    s = ET.tostring(e, encoding="unicode")
    return re.sub(r">\s+<", "><", s).strip()


res = {}
for tipo, zona in QUIERO.items():
    raiz = ET.parse(os.path.join(base, "#" + zona, "setdata_base.set.xml")).getroot()
    inst = [e for e in raiz if e.tag == tipo]
    if not inst:
        print("NO", tipo); continue
    formas = collections.Counter()
    porforma = {}
    for e in inst:
        campos = "".join(ser(c) for c in e if c.tag not in fuera)
        # vacía referencias a otros objetos
        campos = re.sub(r"<SetObjectID>\d+</SetObjectID>", "<SetObjectID>0</SetObjectID>", campos)
        formas[campos] += 1
        porforma.setdefault(campos, e)
    campos, n = formas.most_common(1)[0]
    res[tipo] = campos
    print(f"== {tipo} ({len(inst)} en {zona}, forma más común x{n})")
    print("  ", campos[:900])

with open(salida, "w", encoding="utf-8") as f:
    f.write("# Plantillas de campos de objetos copiadas de los actos originales (generado por un script de análisis).\n")
    f.write("# Sin Position/Rotation/SetObjectID; los enlaces a otros objetos van a 0.\n")
    f.write("PLANTILLAS = {\n")
    for k, v in res.items():
        f.write(f"    {k!r}: {v!r},\n")
    f.write("}\n")
