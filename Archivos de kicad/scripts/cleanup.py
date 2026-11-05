import sys, re, pcbnew
pcb, rpt = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard(pcb); t = open(rpt, encoding="utf-8").read()
pos = [(float(x), float(y)) for x, y in re.findall(r"\[via_dangling\][^\n]*\n[^\n]*\n\s*@\(([\d.]+) mm, ([\d.]+) mm\)", t)]
rm = 0
for v in [x for x in b.GetTracks() if x.GetClass() == "PCB_VIA"]:
    p = v.GetPosition()
    if any(abs(pcbnew.ToMM(p.x) - x) < 0.01 and abs(pcbnew.ToMM(p.y) - y) < 0.01 for x, y in pos): b.Remove(v); rm += 1
b.BuildConnectivity(); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(pcb, b); print("vias colgantes eliminadas:", rm)
