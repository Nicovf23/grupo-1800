import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); n = 0
for fp in b.GetFootprints():
    t = fp.Reference(); t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8))); t.SetTextThickness(pcbnew.FromMM(0.12)); n += 1
    v = fp.Value()
    if v.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS): v.SetVisible(False)
pcbnew.SaveBoard(sys.argv[1], b); print("referencias ajustadas:", n)
