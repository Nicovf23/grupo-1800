import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); ok = pcbnew.ImportSpecctraSES(b, sys.argv[2]); print("SES importado:", ok)
b.BuildConnectivity(); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[3], b)
print("pistas:", sum(1 for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"), "vias:", sum(1 for t in b.GetTracks() if t.GetClass() == "PCB_VIA"))
