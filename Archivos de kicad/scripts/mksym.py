"""Genera la libreria CDJ.kicad_sym con simbolos que KiCad 9 no trae.
Pines tomados de los datasheets oficiales:
  BQ25798  - TI SLUSDV2C (jun-2026), Tabla 5-1, encapsulado RQM0029A (VQFN-HR 29)
  BTS723GW - Infineon BTS 723 GW, 'Pin Definitions and Functions', PG-DSO-14
"""
import uuid

BQ25798 = dict(
    name="BQ25798", ref="U", fp="CDJ:TI_RQM0029A_VQFN-HR-29_4x4mm",
    ds="https://www.ti.com/lit/ds/symlink/bq25798.pdf",
    desc="I2C 1-4S 5A buck-boost charger, dual input, MPPT",
    left=[("VBUS", "2", "power_in"), ("VBUS", "3", "power_in"), ("VAC1", "9", "input"), ("VAC2", "8", "input"),
          ("ACDRV1", "11", "passive"), ("ACDRV2", "10", "passive"), ("D+", "6", "bidirectional"), ("D-", "7", "bidirectional"),
          ("~{CE}", "13", "input"), ("SCL", "14", "input"), ("SDA", "15", "bidirectional"), ("~{INT}", "21", "open_collector"),
          ("~{QON}", "12", "input"), ("STAT", "1", "open_collector"), ("PROG", "20", "passive"), ("ILIM_HIZ", "17", "input")],
    right=[("PMID", "29", "power_out"), ("BTST1", "4", "passive"), ("SW1", "28", "output"), ("SW2", "26", "output"),
           ("BTST2", "19", "passive"), ("REGN", "5", "power_out"), ("SYS", "25", "power_out"), ("BAT", "22", "power_in"),
           ("BAT", "23", "power_in"), ("BATP", "18", "input"), ("SDRV", "24", "output"), ("TS", "16", "input"),
           ("GND", "27", "power_in")],
)
BTS723GW = dict(
    name="BTS723GW", ref="U", fp="Package_SO:SOIC-14_3.9x8.7mm_P1.27mm",
    ds="https://www.infineon.com/cms/en/product/power/smart-power-switches/high-side-switches/classic-profet-24v/bts723gw/",
    desc="Smart dual high-side switch 2x100mOhm, status feedback (PROFET)",
    left=[("IN1", "2", "input"), ("IN2", "6", "input"), ("ST1", "3", "open_collector"), ("ST2", "5", "open_collector"),
          ("SPU", "11", "power_in"), ("GND", "4", "power_in")],
    right=[("VBB", "1", "power_in"), ("VBB", "7", "passive"), ("VBB", "8", "passive"), ("VBB", "14", "passive"),
           ("OUT1", "12", "output"), ("OUT1", "13", "passive"), ("OUT2", "9", "output"), ("OUT2", "10", "passive")],
)

BQ25756 = dict(
    name="BQ25756", ref="U", fp="Package_DFN_QFN:QFN-36-1EP_5x6mm_P0.5mm_EP3.6x4.6mm",
    ds="https://www.ti.com/lit/ds/symlink/bq25756.pdf",
    desc="1-14 cell bidirectional buck-boost charge controller, I2C (TI SLUSEN5A Tabla 4-1, RRV0036A)",
    left=[("VAC", "32", "power_in"), ("VAC", "33", "passive"), ("ACP", "30", "input"), ("ACN", "29", "input"), ("ACUV", "34", "input"),
          ("ACOV", "35", "input"), ("SCL", "1", "input"), ("SDA", "2", "bidirectional"), ("~{INT}", "3", "open_collector"),
          ("STAT1", "4", "open_collector"), ("STAT2", "5", "open_collector"), ("~{PG}", "6", "open_collector"), ("~{CE}", "7", "input"),
          ("TS", "8", "input"), ("ICHG", "9", "passive"), ("ILIM_HIZ", "10", "passive"), ("FSW_SYNC", "36", "passive"),
          ("NC", "15", "no_connect"), ("NC", "16", "no_connect"), ("NC", "31", "no_connect")],
    right=[("HIDRV1", "27", "output"), ("BTST1", "26", "passive"), ("SW1", "28", "passive"), ("LODRV1", "25", "output"),
           ("HIDRV2", "19", "output"), ("BTST2", "20", "passive"), ("SW2", "18", "passive"), ("LODRV2", "21", "output"),
           ("REGN", "24", "power_out"), ("DRV_SUP", "23", "power_in"), ("SRP", "14", "input"), ("SRN", "13", "input"),
           ("FB", "12", "input"), ("FBG", "11", "passive"), ("PGND", "17", "power_in"), ("PGND", "22", "passive"), ("EP", "37", "passive")],
)

DEVKIT = dict(
    name="ESP32_DevKit_V1", ref="U", fp="CDJ:ESP32_DevKit_V1_30P",
    ds="https://www.mischianti.org/2021/02/17/doit-esp32-dev-kit-v1-high-resolution-pinout-and-specs/",
    desc="DOIT ESP32 DevKit V1 30 pines (ESP32-WROOM-32) en zocalo; orden fisico verificar con serigrafia",
    left=[("EN", "1", "input"), ("VP/IO36", "2", "input"), ("VN/IO39", "3", "input"), ("IO34", "4", "input"), ("IO35", "5", "input"),
          ("IO32", "6", "bidirectional"), ("IO33", "7", "bidirectional"), ("IO25", "8", "bidirectional"), ("IO26", "9", "bidirectional"),
          ("IO27", "10", "bidirectional"), ("IO14", "11", "bidirectional"), ("IO12", "12", "bidirectional"), ("IO13", "13", "bidirectional"),
          ("GND", "14", "power_in"), ("VIN", "15", "passive")],
    right=[("IO23", "16", "bidirectional"), ("IO22", "17", "bidirectional"), ("TX0/IO1", "18", "bidirectional"), ("RX0/IO3", "19", "bidirectional"),
           ("IO21", "20", "bidirectional"), ("IO19", "21", "bidirectional"), ("IO18", "22", "bidirectional"), ("IO5", "23", "bidirectional"),
           ("TX2/IO17", "24", "bidirectional"), ("RX2/IO16", "25", "bidirectional"), ("IO4", "26", "bidirectional"), ("IO2", "27", "bidirectional"),
           ("IO15", "28", "bidirectional"), ("GND", "29", "passive"), ("3V3", "30", "power_in")],
)

def fmt(v): return ("%.2f" % v).rstrip("0").rstrip(".")
def eff(): return '(effects (font (size 1.27 1.27)))'

def sym(d):
    n = max(len(d["left"]), len(d["right"]))
    h = (n + 1) * 2.54; top = round(h / 2 / 2.54) * 2.54; w = 12.7
    s = [f'\t(symbol "{d["name"]}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)',
         f'\t\t(property "Reference" "{d["ref"]}" (at 0 {fmt(top + 2.54)} 0) {eff()})',
         f'\t\t(property "Value" "{d["name"]}" (at 0 {fmt(-top - 2.54)} 0) {eff()})',
         f'\t\t(property "Footprint" "{d["fp"]}" (at 0 {fmt(-top - 5.08)} 0) (effects (font (size 1.27 1.27)) (hide yes)))',
         f'\t\t(property "Datasheet" "{d["ds"]}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
         f'\t\t(property "Description" "{d["desc"]}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
         f'\t\t(symbol "{d["name"]}_0_1" (rectangle (start {fmt(-w)} {fmt(top)}) (end {fmt(w)} {fmt(-top)}) (stroke (width 0.254) (type default)) (fill (type background))))',
         f'\t\t(symbol "{d["name"]}_1_1"']
    for side, x, ang in (("left", -w - 5.08, 0), ("right", w + 5.08, 180)):
        for i, (nm, num, typ) in enumerate(d[side]):
            y = top - 2.54 * (i + 1)
            s.append(f'\t\t\t(pin {typ} line (at {fmt(x)} {fmt(y)} {ang}) (length 5.08) (name "{nm}" {eff()}) (number "{num}" {eff()}))')
    s += ['\t\t)', '\t)']
    return "\n".join(s)

lib = '(kicad_symbol_lib (version 20241209) (generator "cdj_mksym") (generator_version "9.0")\n' + \
      sym(BQ25798) + "\n" + sym(BTS723GW) + "\n" + sym(BQ25756) + "\n" + sym(DEVKIT) + "\n)\n"
open("CDJ.kicad_sym", "w", encoding="utf-8").write(lib)
open("fp-lib-table", "w", encoding="utf-8").write(
    '(fp_lib_table\n  (version 7)\n  (lib (name "CDJ")(type "KiCad")(uri "${KIPRJMOD}/CDJ.pretty")(options "")(descr "Carrito Don Julio"))\n)\n')
open("sym-lib-table", "w", encoding="utf-8").write(
    '(sym_lib_table\n  (version 7)\n  (lib (name "CDJ")(type "KiCad")(uri "${KIPRJMOD}/CDJ.kicad_sym")(options "")(descr "Carrito Don Julio"))\n)\n')
# verificacion: numeros de pin unicos y completos
for d, total in ((BQ25798, 29), (BTS723GW, 14), (BQ25756, 37), (DEVKIT, 30)):
    nums = [p[1] for p in d["left"] + d["right"]]
    assert len(nums) == len(set(nums)) == total, (d["name"], sorted(nums, key=int))
print("CDJ.kicad_sym OK: BQ25798 (29), BTS723GW (14), BQ25756 (37 pines)")
