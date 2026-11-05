"""Generador directo de .kicad_sch (KiCad 9) a partir de un modulo de diseno (lista P de componentes).
Una sola pasada: incrusta lib_symbols, coloca simbolos, pone stub + etiqueta en cada pin y X en pines NC.
uso: fastgen.py <dir_scripts> <modulo> <salida.kicad_sch> <titulo>
"""
import sys, os, re, uuid, importlib
sys.path.insert(0, sys.argv[1])
D = importlib.import_module(sys.argv[2]); OUT = sys.argv[3]; TITLE = sys.argv[4]
SYS = r"C:/Program Files/KiCad/9.0/share/kicad/symbols/"
LOCAL = {"CDJ": os.path.join(os.path.dirname(OUT), "CDJ.kicad_sym")}
U = lambda: str(uuid.uuid4())
G = 1.27

def block(t, start):
    """devuelve el texto del s-expr balanceado que empieza en t[start]=='('"""
    d = 0; i = start; q = False
    while True:
        c = t[i]
        if c == '"' and t[i - 1] != '\\': q = not q
        elif not q:
            if c == '(': d += 1
            elif c == ')':
                d -= 1
                if d == 0: return t[start:i + 1]
        i += 1

_cache = {}
def libtext(lib):
    if lib not in _cache:
        _cache[lib] = open(LOCAL.get(lib, SYS + lib + ".kicad_sym"), encoding="utf-8").read()
    return _cache[lib]

def raw_symbol(lib, name):
    t = libtext(lib)
    m = re.search(r'\n\s*\(symbol "%s"\s' % re.escape(name), t)
    if not m: raise KeyError(f"{lib}:{name}")
    return block(t, t.index("(", m.start()))

PROPS = re.compile(r'\(property "([^"]+)"')
def props(b):
    out = {}
    for m in PROPS.finditer(b):
        out[m.group(1)] = block(b, m.start())
    return out

def flat_symbol(lib, name):
    b = raw_symbol(lib, name)
    m = re.search(r'\(extends "([^"]+)"\)', b)
    if not m: return b
    parent = m.group(1); pb = flat_symbol(lib, parent)
    cp, pp = props(b), props(pb)
    for k, v in pp.items():                      # propiedades del hijo sustituyen a las del padre
        if k in cp: pb = pb.replace(v, cp[k], 1)
    pb = pb.replace(f'(symbol "{parent}"', f'(symbol "{name}"', 1)
    pb = re.sub(r'\(symbol "%s_(\d+_\d+)"' % re.escape(parent), lambda mm: f'(symbol "{name}_{mm.group(1)}"', pb)
    return pb

def embed(lib, name):
    b = flat_symbol(lib, name)
    return b.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)

PIN = re.compile(r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)\s*\(length [-\d.]+\)(.*?)\(number "([^"]*)"', re.S)
def pins_of(b):
    res = {}
    for m in PIN.finditer(b):
        x, y, a = float(m.group(1)), float(m.group(2)), float(m.group(3) or 0)
        res.setdefault(m.group(5), (x, y, a))
    return res

def snap(v): return round(v / G) * G

out_syms, out_wires, out_labels, out_nc = [], [], [], []
libsyms = {}
root = U(); proj = os.path.splitext(os.path.basename(OUT))[0]
# --- empaquetado por tamano real (evita que stubs de simbolos vecinos se toquen) ---
for p in D.P:
    key = f'{p["lib"]}:{p["sym"]}'
    if key not in libsyms: libsyms[key] = embed(p["lib"], p["sym"])
def bbox(key):
    ps = pins_of(libsyms[key]).values()
    xs = [x for x, y, a in ps] or [0]; ys = [-y for x, y, a in ps] or [0]
    m = 7.62  # stub 2.54 + margen para texto
    return min(xs) - m - 10, max(xs) + m + 10, min(ys) - m, max(ys) + m
SHEET_W, SHEET_H, MARG, BLOCK_W = 841, 594, 15, 200
order = list(dict.fromkeys(p["blk"] for p in D.P)); place = {}
cx, cy, colw = MARG, MARG + 10, 0
for blk in order:
    items = [p for p in D.P if p["blk"] == blk]
    bx = by = 0; rowh = 0; local = {}; bw = 0
    for p in items:
        x0, x1, y0, y1 = bbox(f'{p["lib"]}:{p["sym"]}'); w, h = x1 - x0, y1 - y0
        if bx + w > BLOCK_W and bx > 0: bx = 0; by += rowh; rowh = 0
        local[p["ref"]] = (bx - x0, by - y0); bx += w; rowh = max(rowh, h); bw = max(bw, bx)
    bh = by + rowh
    if cy + bh > SHEET_H - MARG and cy > MARG + 10: cx += colw + 10; cy = MARG + 10; colw = 0
    for r, (lx, ly) in local.items(): place[r] = (cx + lx, cy + ly)
    cy += bh + 10; colw = max(colw, bw)
if cx + colw > SHEET_W: print("AVISO: el diseno excede el ancho de la hoja A1")
cnt = {}
OUTV = {0: (-1, 0, 180, "right"), 180: (1, 0, 0, "left"), 90: (0, 1, 270, "left"), 270: (0, -1, 90, "left")}
for p in D.P:
    key = f'{p["lib"]}:{p["sym"]}'
    if key not in libsyms: libsyms[key] = embed(p["lib"], p["sym"])
    pins = pins_of(libsyms[key])
    X, Y = place[p["ref"]]; X, Y = snap(X), snap(Y)
    hidden = p["ref"].startswith("#")
    s = [f'\t(symbol (lib_id "{key}") (at {X:g} {Y:g} 0) (unit 1) (exclude_from_sim no) (in_bom {"no" if hidden or p["ref"].startswith(("H", "TP", "JP")) else "yes"}) (on_board {"no" if hidden else "yes"}) (dnp no) (uuid "{U()}")',
         f'\t\t(property "Reference" "{p["ref"]}" (at {X + 2.54:g} {Y - 3.81:g} 0) (effects (font (size 1.27 1.27)) {"(hide yes)" if hidden else "(justify left)"}))',
         f'\t\t(property "Value" "{p["value"]}" (at {X + 2.54:g} {Y + 3.81:g} 0) (effects (font (size 1.27 1.27)) {"(hide yes)" if hidden else "(justify left)"}))',
         f'\t\t(property "Footprint" "{p["fp"]}" (at {X:g} {Y:g} 0) (effects (font (size 1.27 1.27)) (hide yes)))',
         f'\t\t(property "Datasheet" "" (at {X:g} {Y:g} 0) (effects (font (size 1.27 1.27)) (hide yes)))',
         f'\t\t(property "MPN" "{p["mpn"]}" (at {X:g} {Y:g} 0) (effects (font (size 1.27 1.27)) (hide yes)))',
         f'\t\t(property "BOM_Cat" "{p.get("cat", "")}" (at {X:g} {Y:g} 0) (effects (font (size 1.27 1.27)) (hide yes)))']
    s += [f'\t\t(pin "{n}" (uuid "{U()}"))' for n in pins]
    s += [f'\t\t(instances (project "{proj}" (path "/{root}" (reference "{p["ref"]}") (unit 1))))', '\t)']
    out_syms.append("\n".join(s))
    for pn, net in p["pins"].items():
        if pn not in pins: raise KeyError(f'{p["ref"]} no tiene pin {pn}')
        px, py, a = pins[pn]; ax, ay = X + px, Y - py
        ux, uy, lang, just = OUTV[int(a) % 360]
        ex, ey = ax + ux * 2.54, ay + uy * 2.54
        out_wires.append(f'\t(wire (pts (xy {ax:g} {ay:g}) (xy {ex:g} {ey:g})) (stroke (width 0) (type default)) (uuid "{U()}"))')
        out_labels.append(f'\t(label "{net}" (at {ex:g} {ey:g} {lang}) (effects (font (size 1.27 1.27)) (justify {just} bottom)) (uuid "{U()}"))')
    for pn in D.NC.get(p["ref"], []):
        px, py, a = pins[pn]
        out_nc.append(f'\t(no_connect (at {X + px:g} {Y - py:g}) (uuid "{U()}"))')

W = [tuple(map(float, m.groups())) for m in re.finditer(r'\(wire \(pts \(xy ([-\d.]+) ([-\d.]+)\) \(xy ([-\d.]+) ([-\d.]+)\)\)', "\n".join(out_wires))]
Lb = [(m.group(1), float(m.group(2)), float(m.group(3))) for m in re.finditer(r'\(label "([^"]+)" \(at ([-\d.]+) ([-\d.]+)', "\n".join(out_labels))]
endnet = {(round(x, 2), round(y, 2)): n for n, x, y in Lb}
def onseg(px, py, w):
    x1, y1, x2, y2 = w
    if abs(x1 - x2) < 1e-6: return abs(px - x1) < 1e-3 and min(y1, y2) - 1e-3 <= py <= max(y1, y2) + 1e-3
    return abs(py - y1) < 1e-3 and min(x1, x2) - 1e-3 <= px <= max(x1, x2) + 1e-3
bad = [(n, endnet.get((round(w[2], 2), round(w[3], 2))), x, y) for w in W for n, x, y in Lb if n != endnet.get((round(w[2], 2), round(w[3], 2))) and onseg(x, y, w)]
if bad: sys.exit("COLISIONES: %s" % bad[:10])
libblk = "\n".join("\t\t" + v.replace("\n", "\n\t") for v in libsyms.values())
doc = f'''(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0")
\t(uuid "{root}")
\t(paper "A1")
\t(title_block (title "{TITLE}") (company "Carrito Don Julio") (rev "B") (comment 1 "Generado desde design_b.py - verificado contra netlist"))
\t(lib_symbols
{libblk}
\t)
{chr(10).join(out_syms)}
{chr(10).join(out_wires)}
{chr(10).join(out_labels)}
{chr(10).join(out_nc)}
\t(sheet_instances (path "/" (page "1")))
\t(embedded_fonts no)
)
'''
open(OUT, "w", encoding="utf-8").write(doc)
print(f"OK {OUT}: {len(out_syms)} simbolos, {len(out_labels)} etiquetas, {len(out_nc)} NC, {len(libsyms)} simbolos de libreria")
