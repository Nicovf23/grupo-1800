import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); b.BuildConnectivity()
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b); print("zonas rellenadas:", len(b.Zones()))
