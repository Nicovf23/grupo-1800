"""Rutea los pares pendientes con A* sobre rejilla (0.25 mm) usando el cobre real como obstaculo.
Reutiliza la logica de vias de fix2.py. uso: maze.py <pcb>
"""
import sys, os, math, heapq, pcbnew
sys.argv = [sys.argv[0], sys.argv[1]]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fix2.py"), encoding="utf-8").read()
src = src.split("pairs = drc_pairs(); print(")[0]          # solo definiciones
exec(src)
G = mm(0.125); W = 0.2; HW = mm(W / 2)

def astar(f, a, c, net, layer):
    n = net.GetNetname()
    x0 = a.x - G * int((a.x - min(a.x, c.x) + mm(6)) / G); y0 = a.y - G * int((a.y - min(a.y, c.y) + mm(6)) / G)
    x1, y1 = max(a.x, c.x) + mm(6), max(a.y, c.y) + mm(6)
    nx, ny = int((x1 - x0) / G) + 1, int((y1 - y0) / G) + 1
    blk = bytearray(nx * ny); inflate = CLR + HW
    ex0, ey0, ex1, ey1 = f.edge
    for i in range(nx):
        for j in range(ny):
            X, Y = x0 + i * G, y0 + j * G
            if X < ex0 + mm(0.6) or Y < ey0 + mm(0.6) or X > ex1 - mm(0.6) or Y > ey1 - mm(0.6): blk[j * nx + i] = 1
    for o in f.others(n):
        if isinstance(o, pcbnew.PAD):
            on = o.IsOnLayer(layer); hole = o.HasHole()
            if not on and not hole: continue
        elif o.GetClass() != "PCB_VIA" and o.GetLayer() != layer: continue
        bb = o.GetBoundingBox(); bb.Inflate(inflate + mm(0.3))
        if bb.GetRight() < x0 or bb.GetLeft() > x1 or bb.GetBottom() < y0 or bb.GetTop() > y1: continue
        sh = o.GetEffectiveShape(layer)
        hs = o.GetEffectiveHoleShape() if (isinstance(o, pcbnew.PAD) and o.HasHole()) else None
        for i in range(max(0, int((bb.GetLeft() - x0) / G)), min(nx, int((bb.GetRight() - x0) / G) + 1)):
            for j in range(max(0, int((bb.GetTop() - y0) / G)), min(ny, int((bb.GetBottom() - y0) / G) + 1)):
                if blk[j * nx + i]: continue
                P = pcbnew.VECTOR2I(x0 + i * G, y0 + j * G)
                if sh.Collide(P, inflate) or (hs is not None and hs.Collide(P, HOLE_CLR + HW)): blk[j * nx + i] = 1
    s = (round((a.x - x0) / G), round((a.y - y0) / G)); t = (round((c.x - x0) / G), round((c.y - y0) / G))
    for (i, j) in (s, t): blk[j * nx + i] = 0
    D8 = [(1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
    openq = [(0, s)]; g = {s: 0}; prev = {}
    while openq:
        _, u = heapq.heappop(openq)
        if u == t: break
        for dx, dy, w in D8:
            v = (u[0] + dx, u[1] + dy)
            if not (0 <= v[0] < nx and 0 <= v[1] < ny) or blk[v[1] * nx + v[0]]: continue
            if dx and dy and (blk[u[1] * nx + v[0]] or blk[v[1] * nx + u[0]]): continue
            ng = g[u] + w + (0.2 if u in prev and (u[0] - prev[u][0], u[1] - prev[u][1]) != (dx, dy) else 0)
            if ng < g.get(v, 1e18):
                g[v] = ng; prev[v] = u; heapq.heappush(openq, (ng + math.hypot(t[0] - v[0], t[1] - v[1]), v))
    if t not in prev: print('   A* sin camino en', layer, flush=True); return None
    pts = [t]
    while pts[-1] != s: pts.append(prev[pts[-1]])
    pts.reverse()
    # simplificar colineales
    simp = [pts[0]]
    for k in range(1, len(pts) - 1):
        d1 = (pts[k][0] - simp[-1][0], pts[k][1] - simp[-1][1]); d2 = (pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1])
        if d1[0] * d2[1] - d1[1] * d2[0] != 0: simp.append(pts[k])
    simp.append(pts[-1])
    P = [pcbnew.VECTOR2I(x0 + i * G, y0 + j * G) for i, j in simp]; P[0], P[-1] = a, c
    segs = [f.trk(P[k], P[k + 1], net, layer, W) for k in range(len(P) - 1)]
    if any(f.collides(sg, n, [layer]) for sg in segs): print('   camino A* falla verificacion exacta', flush=True); return None
    return segs

pairs = drc_pairs(); print("pendientes:", len(pairs), flush=True)
f = Fixer(); res = []
for pr in pairs:
    (x1, y1, num1, net1, ref1, tn1), (x2, y2, num2, net2, ref2, tn2) = pr
    n = net1 or tn1; net = f.b.FindNet(n)
    a, la = f.endpoint(x1, y1, ref1, num1, n); c, lc = f.endpoint(x2, y2, ref2, num2, n)
    done = False
    if la == lc == pcbnew.F_Cu:
        s = astar(f, a, c, net, pcbnew.F_Cu)
        if s:
            for x in s: f.b.Add(x)
            done = True
    if not done:
        va = f.drop_via(a, la, net)
        print('  ', n, 'via extremo A:', bool(va), flush=True)
        if va:
            for x in va[1]: f.b.Add(x)
            vc = f.drop_via(c, lc, net)
            print('  ', n, 'via extremo B:', bool(vc), flush=True)
            if vc:
                for x in vc[1]: f.b.Add(x)
                for lay in (pcbnew.B_Cu, pcbnew.In2_Cu):
                    s = astar(f, va[0], vc[0], net, lay)
                    if s:
                        for x in s: f.b.Add(x)
                        done = True; break
                if not done:
                    for x in vc[1]: f.b.Remove(x)
            if not done:
                for x in va[1]: f.b.Remove(x)
    res.append((n, done))
f.save(); print("resultado:", res)
