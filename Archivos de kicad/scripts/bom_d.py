import sys, csv, collections; sys.path.insert(0, "."); import design_d as D
rows = collections.OrderedDict()
for p in D.P:
    if p["ref"].startswith("#"): continue
    r = rows.setdefault((p["cat"], p["value"], p["fp"], p["mpn"]), dict(refs=[], fn=p["fn"])); r["refs"].append(p["ref"])
with open("revD/BOM_revD.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["Categoria", "Referencias", "Cant", "Valor", "Fabricante / N. parte", "Encapsulado", "Funcion"])
    for (cat, val, fp, mpn), r in sorted(rows.items(), key=lambda kv: (kv[0][0], kv[1]["refs"][0])):
        w.writerow([cat, " ".join(sorted(r["refs"])), len(r["refs"]), val, mpn, fp.split(":")[-1], r["fn"]])
dk = next(p for p in D.P if p["sym"] == "ESP32_DevKit_V1")
names = {"1": "EN", "2": "VP/GPIO36", "3": "VN/GPIO39", "4": "GPIO34", "5": "GPIO35", "6": "GPIO32", "7": "GPIO33", "8": "GPIO25", "9": "GPIO26", "10": "GPIO27",
         "11": "GPIO14", "12": "GPIO12", "13": "GPIO13", "14": "GND", "15": "VIN", "16": "GPIO23", "17": "GPIO22", "18": "TX0/GPIO1", "19": "RX0/GPIO3", "20": "GPIO21",
         "21": "GPIO19", "22": "GPIO18", "23": "GPIO5", "24": "TX2/GPIO17", "25": "RX2/GPIO16", "26": "GPIO4", "27": "GPIO2", "28": "GPIO15", "29": "GND", "30": "3V3"}
with open("revD/PINES_DEVKIT_revD.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["Pin zocalo", "Lado", "Pin DevKit", "Senal"])
    for n in map(str, range(1, 31)):
        w.writerow([n, "izquierdo" if int(n) <= 15 else "derecho", names[n], dk["pins"].get(n, "libre (NC)")])
c = collections.Counter(p["cat"] for p in D.P if not p["ref"].startswith("#"))
print("BOM:", len(rows), "lineas,", sum(c.values()), "piezas", dict(sorted(c.items())))
