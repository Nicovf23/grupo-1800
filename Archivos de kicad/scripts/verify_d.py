"""Compara la netlist exportada por kicad-cli (formato kicadsexpr) contra design.P."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys_path_fix=1
import sys, re, collections; import design_d as D
t = open(sys.argv[1], encoding="utf-8").read()
got = {}
for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)\)\s*(?=\(net |\)\s*\)\s*$)', t, re.S):
    name = m.group(1).lstrip("/")
    for n in re.finditer(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2)):
        got[(n.group(1), n.group(2))] = name
exp = {(p["ref"], pin): net for p in D.P if not p["ref"].startswith("#") for pin, net in p["pins"].items()}
bad = [(k, v, got.get(k)) for k, v in exp.items() if got.get(k) != v]
# nets que se unieron por error: dos nets esperadas distintas en la misma net real
real = collections.defaultdict(set)
for k, v in exp.items():
    if k in got: real[got[k]].add(v)
merged = {r: s for r, s in real.items() if len(s) > 1}
print(f"pines esperados: {len(exp)}  coinciden: {len(exp)-len(bad)}  mal: {len(bad)}")
for b in bad[:40]: print("  MAL", b)
print("nets fusionadas:", merged or "ninguna")
