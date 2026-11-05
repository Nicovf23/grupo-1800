"""Genera la PCB (rev C) desde design_c.py: contorno, 4 capas, huellas enlazadas al esquematico,
redes por pad, colocacion por zonas funcionales sin solapes, planos GND, clases de red.
uso: pcbgen.py <sch> <pcb_salida>
"""
import sys, os, re, pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import design_d as D
SCH, OUT = sys.argv[1], sys.argv[2]
# redes por pad tomadas de la netlist exportada por kicad-cli (misma nomenclatura que el esquema)
NETLIST = os.path.join(os.path.dirname(SCH), "net.txt")
padnet = {}
_nt = open(NETLIST, encoding="utf-8").read()
for _m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)(?=\(net \(code|\Z)', _nt, re.S):
    for _n in re.finditer(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"', _m.group(2)): padnet[(_n.group(1), _n.group(2))] = _m.group(1)
FP = r"C:/Program Files/KiCad/9.0/share/kicad/footprints/"
LOCALFP = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "CDJ.pretty")
mm = pcbnew.FromMM
BW, BH = 130.0, 100.0

# --- UUID de cada simbolo del esquematico (para enlazar huella <-> simbolo) ---
st = open(SCH, encoding="utf-8").read()
symuuid = {}
for m in re.finditer(r'\(symbol \(lib_id "[^"]+"\) \(at [^)]*\) \(unit 1\)[^\n]*\(uuid "([^"]+)"\)\n\t\t\(property "Reference" "([^"]+)"', st):
    symuuid[m.group(2)] = m.group(1)

b = pcbnew.BOARD()
b.SetCopperLayerCount(4)
ds = b.GetDesignSettings()
ds.SetBoardThickness(mm(1.6))
# reglas conservadoras compatibles con JLCPCB 4 capas
ds.m_TrackMinWidth = mm(0.15); ds.m_ViasMinSize = mm(0.45); ds.m_MinThroughDrill = mm(0.2); ds.m_MinClearance = mm(0.15)
ds.m_CopperEdgeClearance = mm(0.3)

# --- contorno con esquinas redondeadas ---
def seg(a, c):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(pcbnew.VECTOR2I(mm(a[0]), mm(a[1])))
    s.SetEnd(pcbnew.VECTOR2I(mm(c[0]), mm(c[1]))); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); b.Add(s)
def arc(cx, cy, sx, sy, ang):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetCenter(pcbnew.VECTOR2I(mm(cx), mm(cy)))
    s.SetStart(pcbnew.VECTOR2I(mm(sx), mm(sy))); s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(ang, pcbnew.DEGREES_T), True)
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); b.Add(s)
seg((0, 0), (BW, 0)); seg((BW, 0), (BW, BH)); seg((BW, BH), (0, BH)); seg((0, BH), (0, 0))  # rectangular (cierre exacto para DSN)

# --- clases de red ---
ns = ds.m_NetSettings
def netclass(name, w, clr, nets):
    nc = pcbnew.NETCLASS(name); nc.SetTrackWidth(mm(w)); nc.SetClearance(mm(clr)); nc.SetViaDiameter(mm(0.8)); nc.SetViaDrill(mm(0.4))
    ns.SetNetclass(name, nc)
    for n in nets: ns.SetNetclassPatternAssignment("/" + n, name)
dflt = ns.GetDefaultNetclass(); dflt.SetTrackWidth(mm(0.2)); dflt.SetClearance(mm(0.15)); dflt.SetViaDiameter(mm(0.6)); dflt.SetViaDrill(mm(0.3))
netclass("Potencia", 1.0, 0.15, ["VBAT", "VBAT_RAW", "VBAT_P", "VBUS", "CHG_VIN", "CHG_VOUT", "CHG_SW1", "CHG_SW2", "VSERVO", "ESC_BEC"])
netclass("Alim3V3", 0.5, 0.15, ["+3V3", "+3V3_REG", "BUCK_SW", "LT_*_OUT", "LT_*_LED"])

# --- huellas ---
nets = {}
def net(n):
    if n not in nets:
        nets[n] = pcbnew.NETINFO_ITEM(b, n); b.Add(nets[n])
    return nets[n]
fps = {}; unmapped = []
for p in D.P:
    if not p["fp"]: continue
    lib, name = p["fp"].split(":")
    fp = pcbnew.FootprintLoad(LOCALFP if lib == "CDJ" else FP + lib + ".pretty", name)
    if fp is None: sys.exit(f"no se pudo cargar {p['fp']}")
    fp.SetReference(p["ref"]); fp.SetValue(p["value"]); fp.SetFPID(pcbnew.LIB_ID(lib, name))
    if p["ref"] in symuuid: fp.SetPath(pcbnew.KIID_PATH("/" + symuuid[p["ref"]]))
    fp.SetSheetname("/"); fp.SetSheetfile(os.path.basename(SCH))
    b.Add(fp); fps[p["ref"]] = (fp, p)
    nc = set(D.NC.get(p["ref"], []))
    for pad in fp.Pads():
        num = pad.GetNumber()
        if (p["ref"], num) in padnet: pad.SetNet(net(padnet[(p["ref"], num)]))
        elif num and num not in nc and pad.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH: unmapped.append(f'{p["ref"]}.{num}')

# --- colocacion ---
def bbox(fp):
    cy = fp.GetCourtyard(pcbnew.F_CrtYd)
    bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False)
    return bb
placed = []  # rectangulos ocupados (x0,y0,x1,y1) mm
def free(r):
    if r[0] < 0.5 or r[1] < 0.5 or r[2] > BW - 0.5 or r[3] > BH - 0.5: return False
    return all(r[2] <= q[0] or r[0] >= q[2] or r[3] <= q[1] or r[1] >= q[3] for q in placed)
def put(ref, x, y, rot=0):
    fp = fps[ref][0]; fp.SetOrientationDegrees(rot); fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    bb = bbox(fp); r = (pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))
    placed.append(r); return r
def pack(ref, zone, gap=0.6):
    fp = fps[ref][0]; fp.SetPosition(pcbnew.VECTOR2I(0, 0)); bb = bbox(fp)
    ox, oy = pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()); w, h = pcbnew.ToMM(bb.GetWidth()) + gap, pcbnew.ToMM(bb.GetHeight()) + gap
    for zx0, zy0, zx1, zy1 in (zone, (0, 0, BW, BH)):
        y = zy0
        while y + h <= zy1:
            x = zx0
            while x + w <= zx1:
                rr = (x, y, x + w, y + h)
                if free(rr):
                    fp.SetPosition(pcbnew.VECTOR2I(mm(x - ox + gap / 2), mm(y - oy + gap / 2))); placed.append(rr); return True
                x += 0.5
            y += 0.5
    return False

# 1) piezas ancladas al borde / criticas
anch = {}
H = [r for r in fps if r.startswith("H")]
for ref, (x, y) in zip(H, [(4, 4), (BW - 4, BH - 4), (4, BH - 4), (BW - 4, 58)]): put(ref, x, y)
esp = next(r for r, (f, p) in fps.items() if p["sym"] == "ESP32_DevKit_V1"); ESPX, ESPY = BW - 28.0, 14.3; put(esp, ESPX, ESPY)  # pin1 del DevKit; antena al borde superior   # cuerpo del modulo al ras del borde superior: antena en el borde
usb = next(r for r, (f, p) in fps.items() if p["sym"].startswith("USB_C")); put(usb, 14, 5.5, 0)      # USB-C en el borde superior
bat = next(r for r, (f, p) in fps.items() if p["value"].startswith("BATERIA")); put(bat, 6, 62, 270)   # XT30 bateria, borde izquierdo
bal = next(r for r, (f, p) in fps.items() if p["value"].startswith("BALANCEO")); put(bal, 17, 93, 0)  # balanceo abajo-izquierda
vsv = next(r for r, (f, p) in fps.items() if p["value"].startswith("VSERVO IN")); put(vsv, BW - 6, 74, 90)  # XT30 BEC, borde derecho
ind = next(r for r, (f, p) in fps.items() if p["sym"] == "L" and p["blk"] == "USBC"); put(ind, 48, 15)   # inductor cargador
imu = next(r for r, (f, p) in fps.items() if p["sym"] == "LSM6DSL"); put(imu, 70, 59)                    # IMU cerca del centro
fixed = {esp, usb, bat, bal, vsv, ind, imu, *H}

ZONES = {"USBC": (0, 0, 80, 50), "MCU": (78, 0, BW, 50), "BAT": (0, 50, 32, BH), "AFE": (32, 50, 62, 78),
         "PWR": (32, 78, 62, BH), "IMU": (62, 52, 78, 66), "AUX": (78, 50, 104, 66), "RC": (104, 50, BW, BH),
         "OUT": (78, 66, 104, 82), "LUCES": (62, 82, 104, BH), "MECH": (0, 0, BW, BH)}
# Colocacion guiada por conectividad: cada pieza busca (en espiral) el hueco libre mas cercano al
# centroide de las piezas ya colocadas con las que comparte redes (sin contar redes globales).
GLOBAL = {"GND", "+3V3", "VBAT", "VSERVO", "I2C_SDA", "I2C_SCL", "CHG_REGN", "VBUS"}
pos = {r: (pcbnew.ToMM(fps[r][0].GetPosition().x), pcbnew.ToMM(fps[r][0].GetPosition().y)) for r in fixed}
netsof = {r: {n for n in p["pins"].values() if n not in GLOBAL} for r, (f, p) in fps.items()}
def spiral(ref, zone, anchor, gap=0.5):
    fp = fps[ref][0]; fp.SetPosition(pcbnew.VECTOR2I(0, 0)); bb = bbox(fp)
    ox, oy = pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()); w, h = pcbnew.ToMM(bb.GetWidth()) + gap, pcbnew.ToMM(bb.GetHeight()) + gap
    for zx0, zy0, zx1, zy1 in (zone, (0, 0, BW, BH)):
        ax = min(max(anchor[0], zx0 + w / 2), zx1 - w / 2); ay = min(max(anchor[1], zy0 + h / 2), zy1 - h / 2)
        for k in range(0, 260):
            d = k * 0.5; pts = [(0, 0)] if k == 0 else [(dx * 0.5, s * d) for dx in range(-k, k + 1) for s in (-1, 1)] + [(s * d, dy * 0.5) for dy in range(-k + 1, k) for s in (-1, 1)]
            for dx, dy in pts:
                x0, y0 = ax + dx - w / 2, ay + dy - h / 2; rr = (x0, y0, x0 + w, y0 + h)
                if rr[0] >= zx0 and rr[1] >= zy0 and rr[2] <= zx1 and rr[3] <= zy1 and free(rr):
                    fp.SetPosition(pcbnew.VECTOR2I(mm(x0 - ox + gap / 2), mm(y0 - oy + gap / 2))); placed.append(rr)
                    pos[ref] = (x0 + w / 2, y0 + h / 2); return True
    return False
def prio(r):
    f, p = fps[r]; return (0 if r[0] in "UQL" or "Conn" in p["sym"] or p["sym"].startswith("USB") else 1, list(fps).index(r))
fail = []
for r in sorted((r for r in fps if r not in fixed), key=prio):
    z = ZONES[fps[r][1]["blk"]]
    nb = [pos[o] for o in pos if netsof[o] & netsof[r]]
    anchor = (sum(x for x, y in nb) / len(nb), sum(y for x, y in nb) / len(nb)) if nb else ((z[0] + z[2]) / 2, (z[1] + z[3]) / 2)
    if not spiral(r, z, anchor): fail.append(r)

# --- planos de GND en capas internas y B.Cu ---
def zone(layer, netname, prio=0):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(net("/" + netname)); z.SetAssignedPriority(prio)
    o = z.Outline(); o.NewOutline()
    for x, y in ((0.5, 0.5), (BW - 0.5, 0.5), (BW - 0.5, BH - 0.5), (0.5, BH - 0.5)): o.Append(mm(x), mm(y))
    z.SetLocalClearance(mm(0.3)); z.SetMinThickness(mm(0.25)); b.Add(z)
for L in (pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu): zone(L, "GND")
# keepout de cobre bajo la antena del ESP32 (todas las capas)
k = pcbnew.ZONE(b); k.SetIsRuleArea(True); k.SetDoNotAllowTracks(True); k.SetDoNotAllowVias(True); k.SetDoNotAllowCopperPour(True)
k.SetDoNotAllowPads(True); k.SetDoNotAllowFootprints(False); k.SetLayerSet(pcbnew.LSET.AllCuMask())
o = k.Outline(); o.NewOutline()
# zona de antena del DevKit: desde el borde hasta 2.5 mm antes de la primera fila de pines; 10 mm extra a la izquierda
ax0, ax1, ay1 = ESPX - 2.0 - 10, BW, ESPY - 2.5
for x, y in ((ax0, 0), (ax1, 0), (ax1, ay1), (ax0, ay1)): o.Append(mm(x), mm(y))
b.Add(k)

# relleno de zonas: lo hace kicad-cli (pcb drc --refill-zones); ZONE_FILLER desde Python provoca segfault
b.BuildConnectivity()
pcbnew.SaveBoard(OUT, b)
print(f"PCB {BW}x{BH} mm, 4 capas: {len(fps)} huellas, {len(nets)} redes, enlazadas al esquema: {sum(1 for r in fps if r in symuuid)}")
print("sin colocar:", fail or "ninguna")
print("pads con numero sin red (revisar):", unmapped[:30] or "ninguno")
