"""Cierra conexiones pendientes tras el autorouter, de forma iterativa y verificada:
  1) plano VBUS en In2.Cu bajo el cargador (si hay VBUS pendiente)
  2) bucle: DRC (kicad-cli) -> pares sin conectar -> conectar cada par con
     pista directa/en L en F.Cu, o via+via con pista por B.Cu/In2.Cu.
  Cada via/pista se comprueba contra cobre de otras redes Y contra agujeros (PTH/NPTH)
  antes de agregarse; si un par no se puede cerrar completo, no se agrega nada.
uso: fix2.py <pcb>
"""
import sys, re, math, subprocess, os, pcbnew
PCB = sys.argv[1]; RPT = os.path.splitext(PCB)[0] + "_fix_drc.rpt"
CLI = r"C:\Program Files\KiCad\9.0\bin\kicad-cli.exe"
mm = pcbnew.FromMM; T = pcbnew.ToMM
CLR, HOLE_CLR = mm(0.15), mm(0.25)
VIA_D, VIA_H = 0.45, 0.25
ALL = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]

def drc_pairs():
    subprocess.run([CLI, "pcb", "drc", "--severity-error", "-o", RPT, PCB], capture_output=True)
    txt = open(RPT, encoding="utf-8").read(); out = []
    for blk in txt.split("\n[unconnected_items]")[1:]:
        pts = re.findall(r"@\(([\d.]+) mm, ([\d.]+) mm\): (?:Pad (\S+) \[([^\]]+)\] de (\S+)|(?:Pista|Vía) \[([^\]]+)\])", blk)[:2]
        if len(pts) == 2 and pts not in out and pts[::-1] not in out: out.append(pts)
    return out

class Fixer:
    def __init__(self):
        self.b = pcbnew.LoadBoard(PCB); self.b.BuildConnectivity()
        bb = self.b.GetBoardEdgesBoundingBox(); self.edge = (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())
        self.keep = [z for z in self.b.Zones() if z.GetIsRuleArea()]
    def others(self, net):
        for t in self.b.GetTracks():
            if t.GetNetname() != net: yield t
        for fp in self.b.GetFootprints():
            for p in fp.Pads():
                if p.GetNetname() != net or p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH: yield p
    def collides(self, it, net, layers):
        x0, y0, x1, y1 = self.edge; m = mm(0.5)
        bbx = it.GetBoundingBox()
        if bbx.GetLeft() < x0 + m or bbx.GetTop() < y0 + m or bbx.GetRight() > x1 - m or bbx.GetBottom() > y1 - m: return True
        isvia = it.GetClass() == "PCB_VIA"
        if isvia and any(z.GetDoNotAllowVias() and z.Outline().Contains(it.GetPosition()) for z in self.keep): return True
        for o in self.others(net):
            if isinstance(o, pcbnew.PAD):
                if o.HasHole():
                    hs = o.GetEffectiveHoleShape()
                    for l in layers:
                        if hs.Collide(it.GetEffectiveShape(l), HOLE_CLR): return True
                ls = [l for l in layers if o.IsOnLayer(l)]
            elif o.GetClass() == "PCB_VIA":
                if isvia and o.GetEffectiveHoleShape().Collide(it.GetEffectiveHoleShape(), HOLE_CLR): return True
                ls = layers
            else:
                ls = [l for l in layers if o.GetLayer() == l]
            for l in ls:
                if o.GetEffectiveShape(l).Collide(it.GetEffectiveShape(l), CLR): return True
        if isvia:
            for t in self.b.GetTracks():
                if t.GetClass() == "PCB_VIA" and t.GetNetname() == net and t.GetEffectiveHoleShape().Collide(it.GetEffectiveHoleShape(), HOLE_CLR): return True
        return False
    def via(self, p, net):
        v = pcbnew.PCB_VIA(self.b); v.SetPosition(p); v.SetWidth(pcbnew.F_Cu, mm(VIA_D)); v.SetDrill(mm(VIA_H)); v.SetNet(net); return v
    def trk(self, a, c, net, layer, w):
        t = pcbnew.PCB_TRACK(self.b); t.SetStart(a); t.SetEnd(c); t.SetWidth(mm(w)); t.SetLayer(layer); t.SetNet(net); return t
    def path(self, a, c, net, layer, w):
        n = net.GetNetname()
        for mid in (None, pcbnew.VECTOR2I(a.x, c.y), pcbnew.VECTOR2I(c.x, a.y)):
            segs = [self.trk(a, c, net, layer, w)] if mid is None else [self.trk(a, mid, net, layer, w), self.trk(mid, c, net, layer, w)]
            if not any(self.collides(s, n, [layer]) for s in segs): return segs
        return None
    def endpoint(self, x, y, ref, num, net):
        if ref:
            pad = next(p for p in self.b.FindFootprintByReference(ref).Pads() if p.GetNumber() == num)
            return pad.GetPosition(), pcbnew.F_Cu
        best = None
        for t in self.b.GetTracks():
            if t.GetNetname() != net: continue
            pts = [t.GetPosition()] if t.GetClass() == "PCB_VIA" else [t.GetStart(), t.GetEnd()]
            for p in pts:
                d = math.hypot(T(p.x) - float(x), T(p.y) - float(y))
                if best is None or d < best[0]: best = (d, p, t)
        it = best[2]
        return best[1], (None if it.GetClass() == "PCB_VIA" else it.GetLayer())
    def drop_via(self, p, lay, net):
        n = net.GetNetname()
        for t in self.b.GetTracks():
            if t.GetClass() == "PCB_VIA" and t.GetNetname() == n and math.hypot(T(t.GetPosition().x - p.x), T(t.GetPosition().y - p.y)) < 1.2:
                if lay is None: return t.GetPosition(), []
                s = self.path(p, t.GetPosition(), net, lay, 0.25)
                if s is not None: return t.GetPosition(), s
        if lay is None: return p, []
        for r in (0.0, 0.7, 0.9, 1.1, 1.3, 1.6, 2.0, 2.5, 3.0):
            for ang in range(0, 360, 15):
                q = pcbnew.VECTOR2I(p.x + mm(r * math.cos(math.radians(ang))), p.y + mm(r * math.sin(math.radians(ang))))
                v = self.via(q, net)
                if self.collides(v, n, ALL): continue
                s = [] if r == 0 else [self.trk(p, q, net, lay, 0.25)]
                if s and self.collides(s[0], n, [lay]): continue
                return q, [v] + s
        return None
    def connect(self, pr):
        (x1, y1, num1, net1, ref1, tn1), (x2, y2, num2, net2, ref2, tn2) = pr
        n = net1 or tn1; net = self.b.FindNet(n)
        a, la = self.endpoint(x1, y1, ref1, num1, n); c, lc = self.endpoint(x2, y2, ref2, num2, n)
        if la == lc == pcbnew.F_Cu:
            s = self.path(a, c, net, pcbnew.F_Cu, 0.25)
            if s: return s
        va = self.drop_via(a, la, net)
        if not va: return None
        for x in va[1]: self.b.Add(x)          # provisional para que la 2a via lo vea
        vc = self.drop_via(c, lc, net)
        for x in va[1]: self.b.Remove(x)
        if not vc: return None
        for lay in (pcbnew.B_Cu, pcbnew.In2_Cu):
            s = self.path(va[0], vc[0], net, lay, 0.3)
            if s is not None: return va[1] + vc[1] + s
        return None
    def vbus_plane(self):
        z = pcbnew.ZONE(self.b); z.SetLayer(pcbnew.In2_Cu); z.SetNet(self.b.FindNet("/VBUS")); z.SetAssignedPriority(5)
        o = z.Outline(); o.NewOutline()
        for x, y in ((0.6, 0.6), (80.0, 0.6), (80.0, 34.0), (0.6, 34.0)): o.Append(mm(x), mm(y))
        z.SetLocalClearance(mm(0.3)); z.SetMinThickness(mm(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL); self.b.Add(z)
    def save(self):
        self.b.BuildConnectivity(); pcbnew.ZONE_FILLER(self.b).Fill(self.b.Zones()); pcbnew.SaveBoard(PCB, self.b)

pairs = drc_pairs(); print("pendientes iniciales:", len(pairs), flush=True)
f = Fixer()
if any((p[0][3] or p[0][5]) == "/VBUS" for p in pairs) and not any(z.GetNetname() == "/VBUS" for z in f.b.Zones()):
    f.vbus_plane(); f.save()
for it in range(5):
    pairs = drc_pairs()
    if not pairs: break
    f = Fixer(); ok = 0
    for pr in pairs:
        items = f.connect(pr)
        if items:
            for x in items: f.b.Add(x)
            ok += 1
    f.save(); print(f"iteracion {it+1}: {len(pairs)} pendientes, {ok} cerrados", flush=True)
    if ok == 0: break
left = drc_pairs()
print("pendientes finales:", len(left), [(p[0][3] or p[0][5]) for p in left])
