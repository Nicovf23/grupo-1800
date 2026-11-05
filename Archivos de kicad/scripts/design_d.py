"""Carrito Don Julio - placa principal rev D (LiPo 6S, ESP32 DevKit V1).
Cambios vs rev A: componentes del profesor (AP63203WU, APH0630T4R7M, MBRA340T, 1N5819HW, SMF24CA, SMF3.3,
BTS723GW, ESD5Z3.3T, C41/C42/C43/C44/C45/C46, C1/C2, JP1, R73, TP6/8/12), carga de la LiPo 4S por USB-C
(CH224K + BQ25756 + BQ76930, 6S), sin riel de 5 V, programacion por header UART.
Categoria BOM por componente en campo 'cat': A reutilizado, B adaptado, C nuevo.
Fuentes de valores: AP63203 (Diodes, Tabla 2), BQ25798 (TI SLUSDV2C Fig. 8-1, Tabla 7-1),
BQ76920 (TI SLUSBK2I Tabla 9-1/9-2, Recommended Operating Conditions), CH224K (WCH DS1 sec. 5.2/5.5/6.1),
BTS723GW (Infineon), ESD5Z (onsemi).
"""
R0603 = "Resistor_SMD:R_0603_1608Metric"
R2512 = "Resistor_SMD:R_2512_6332Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
C1206 = "Capacitor_SMD:C_1206_3216Metric"
SOD123 = "Diode_SMD:D_SOD-123"
SOD123F = "Diode_SMD:D_SOD-123F"
SOD523 = "Diode_SMD:D_SOD-523"
SOT235 = "Package_TO_SOT_SMD:SOT-23-5"
HDR3 = "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical"
HDR6 = "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical"
PH2 = "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical"
PH4 = "Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical"
XT30 = "Connector_AMASS:AMASS_XT30PW-M_1x02_P2.50mm_Horizontal"
LED0603 = "LED_SMD:LED_0603_1608Metric"
SW = "Button_Switch_SMD:SW_SPST_TL3342"
TP = "TestPoint:TestPoint_Pad_D1.5mm"
ELEC10 = "Capacitor_SMD:CP_Elec_10x10.5"
ELEC8 = "Capacitor_SMD:CP_Elec_8x10.5"

P = []
def add(ref, lib, sym, val, fp, mpn, pins, blk, cat="C", fn=""):
    P.append(dict(ref=ref, lib=lib, sym=sym, value=val, fp=fp, mpn=mpn, pins=pins, blk=blk, cat=cat, fn=fn))
def R(ref, val, a, b, blk, fp=R0603, mpn="1% 0603", cat="C", fn=""): add(ref, "Device", "R", val, fp, mpn, {"1": a, "2": b}, blk, cat, fn)
def C(ref, val, a, b, blk, fp=C0603, mpn="X7R 0603", cat="C", fn=""): add(ref, "Device", "C", val, fp, mpn, {"1": a, "2": b}, blk, cat, fn)
def ESD(ref, net, blk): add(ref, "Device", "D_Zener", "ESD5Z3.3T", SOD523, "onsemi ESD5Z3.3T1G", {"1": net, "2": "GND"}, blk, "A", "ESD linea expuesta")
def TPt(ref, net, blk, cat="C"): add(ref, "Connector", "TestPoint", net, TP, "Pad de prueba", {"1": net}, blk, cat, "Punto de prueba")

# ======================= 1. BATERIA 6S: entrada, fusible, balanceo =======================
B = "BAT"
add("J1", "Connector_Generic", "Conn_01x02", "BATERIA 6S (XT30)", XT30, "AMASS XT30PW-M", {"1": "VBAT_RAW", "2": "GND"}, B, "C", "Toma de bateria en paralelo con el ESC")
add("F1", "Device", "Fuse", "5A", "Fuse:Fuse_Littelfuse-NANO2-451_453", "Littelfuse 0451005.MRL (5A, verificar Vr>=32V)", {"1": "VBAT_RAW", "2": "VBAT"}, B, "C", "Sobrecorriente placa+cargador")
add("D10", "Device", "D_TVS", "SMF26CA", SOD123F, "Littelfuse SMF26CA", {"1": "VBAT", "2": "GND"}, B, "B", "TVS bateria (6S 25.2V < 26V VRWM; SMF24CA no sirve a 6S)")
add("C41", "Device", "C_Polarized", "220uF 50V", ELEC10, "Aluminio 220uF/50V", {"1": "VBAT", "2": "GND"}, B, "A", "Bulk bateria")
TPt("TP6", "VBAT", B, "A")
add("J2", "Connector_Generic", "Conn_01x07", "BALANCEO 6S (JST-XH)", "Connector_JST:JST_XH_B7B-XH-A_1x07_P2.50mm_Vertical", "JST B7B-XH-A",
    {"1": "BAL0", "2": "BAL1", "3": "BAL2", "4": "BAL3", "5": "BAL4", "6": "BAL5", "7": "BAL6"}, B, "C", "Conector de balanceo de la LiPo 6S")

# ======================= 2. MONITOR/BALANCEO BQ76930 (TI SLUSBK2I Fig. 9-2, Tabla 9-3: 6 celdas) =======================
B = "AFE"
# Tabla 9-3 (6 celdas): VC10-VC9 c6 | VC9-VC8 corto | VC8-VC7 corto | VC7-VC6 c5 | VC6-VC5b c4 | VC5-VC4 c3 | VC4-VC3 corto | VC3-VC2 corto | VC2-VC1 c2 | VC1-VC0 c1
add("U5", "Battery_Management", "BQ76930DBT", "BQ7693003DBT", "Package_SO:TSSOP-30_4.4x7.8mm_P0.5mm", "TI BQ7693003DBTR (REGOUT 3.3V, I2C 0x08, CRC - verificar variante)",
    {"27": "AFE_VC0", "26": "AFE_VC1", "25": "AFE_VC2", "24": "AFE_VC2", "23": "AFE_VC2", "22": "AFE_VC5", "21": "AFE_VC5B", "20": "AFE_VC6",
     "19": "AFE_VC7", "18": "AFE_VC7", "17": "AFE_VC7", "16": "AFE_VC10", "15": "AFE_BAT", "9": "AFE_BAT", "10": "AFE_VC5X",
     "14": "AFE_CAP2", "11": "AFE_CAP2", "12": "AFE_CAP2", "13": "AFE_TS2", "8": "AFE_REGOUT", "7": "AFE_CAP1", "6": "AFE_TS1",
     "28": "GND", "29": "GND", "3": "GND", "4": "I2C_SDA", "5": "I2C_SCL", "30": "AFE_ALERT"}, B, "C", "Medicion por celda y balanceo 6S")
for i, (bal, vc) in enumerate([("BAL0", "AFE_VC0"), ("BAL1", "AFE_VC1"), ("BAL2", "AFE_VC2"), ("BAL3", "AFE_VC5"), ("BAL3", "AFE_VC5B"),
                               ("BAL4", "AFE_VC6"), ("BAL5", "AFE_VC7"), ("BAL6", "AFE_VC10")]):
    R(f"R{60+i}", "100", bal, vc, B, fn="Filtro entrada celda Rc (typ 100R)")
for i, (a, b) in enumerate([("AFE_VC0", "GND"), ("AFE_VC1", "AFE_VC0"), ("AFE_VC2", "AFE_VC1"), ("AFE_VC5", "AFE_VC2"),
                            ("AFE_VC5B", "AFE_VC5X"), ("AFE_VC6", "AFE_VC5B"), ("AFE_VC7", "AFE_VC6"), ("AFE_VC10", "AFE_VC7")]):
    C(f"C{60+i}", "1uF", a, b, B, mpn="X7R 0603 25V", fn="Filtro celda Cc (typ 1uF)")
# Alimentacion: BAT desde PACK+ por Rf/Cf + diodo desde la entrada superior; VC5X desde la toma media por Rf/Cf + diodo (sec. 9.1.3: diodo convencional, no Schottky)
R("R68", "100", "VBAT", "AFE_BAT", B, fn="Rf BAT (typ 100R)")
C("C68", "10uF 50V", "AFE_BAT", "GND", B, C1206, "X7R 1206 50V", fn="Cf BAT (typ 10uF)")
add("D17", "Device", "D", "1N4148W", SOD123, "Diodes 1N4148W-7-F", {"2": "AFE_VC10", "1": "AFE_BAT"}, B, "C", "Diodo entrada superior -> BAT (9.1.3)")
R("R69", "100", "BAL3", "AFE_VC5X", B, fn="Rf VC5X (typ 100R)")
C("C69", "10uF 25V", "AFE_VC5X", "GND", B, C0805, "X7R 0805 25V", fn="Cf VC5X")
add("D23", "Device", "D", "1N4148W", SOD123, "Diodes 1N4148W-7-F", {"2": "AFE_VC5", "1": "AFE_VC5X"}, B, "C", "Diodo toma media -> VC5X (9.1.3)")
C("C70b", "1uF", "AFE_CAP2", "AFE_VC5X", B, mpn="X7R 0603 25V", fn="CAP2 1uF (ref. VC5X)")
R("R70b", "10k", "AFE_TS2", "AFE_VC5X", B, fn="TS2 sin NTC: 10k a VC5X (Tabla 9-1)")
C("C71b", "4.7uF", "AFE_REGOUT", "GND", B, C0805, "X7R 0805 10V", fn="REGOUT (1-4.7uF)")
C("C72b", "1uF", "AFE_CAP1", "GND", B, fn="CAP1 1uF")
add("TH1", "Device", "Thermistor_NTC", "10k 3435K", "Resistor_SMD:R_0603_1608Metric", "Murata NCP18XH103F03RB", {"1": "AFE_TS1", "2": "GND"}, B, "C", "TS1 temperatura placa (obligatorio)")
add("D11", "Device", "D_Schottky", "1N5819HW", SOD123, "Diodes 1N5819HW-7-F", {"1": "AFE_BOOT_K", "2": "AFE_BOOT_A"}, B, "B", "Pulso de arranque TS1 (aislado del GPIO)")
R("R66", "1k", "AFE_BOOT", "AFE_BOOT_A", B, fn="Serie boot")
R("R67", "1k", "AFE_BOOT_K", "AFE_TS1", B, fn="Serie boot")
R("R59", "1M", "AFE_ALERT", "GND", B, fn="RALERT 1M a VSS")

# ======================= 3. CARGA USB-C: CH224K (20V PD) + BQ25756 buck-boost (TI SLUSEN5A Fig. 7-1) =======================
B = "USBC"
add("J3", "Connector", "USB_C_Receptacle_USB2.0_16P", "USB-C (SOLO CARGA)", "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", "HRO TYPE-C-31-M-12",
    {**{p: "VBUS" for p in ("A4", "A9", "B4", "B9")}, **{p: "GND" for p in ("A1", "A12", "B1", "B12", "S1")},
     "A5": "USB_CC1", "B5": "USB_CC2"}, B, "C", "Entrada de carga PD")
add("D12", "Device", "D_TVS", "SMF24CA", SOD123F, "Littelfuse SMF24CA", {"1": "VBUS", "2": "GND"}, B, "A", "TVS VBUS (PD 20V < 24V VRWM)")
add("U6", "Interface_USB", "CH224K", "CH224K", "Package_SO:SSOP-10-1EP_3.9x4.9mm_P1mm_EP2.1x3.3mm", "WCH CH224K (LCSC C970725)",
    {"1": "CH_VDD", "7": "USB_CC1", "6": "USB_CC2", "4": "CH_DPDM", "5": "CH_DPDM", "8": "CH_VBUS", "11": "GND"}, B, "C", "Negocia 20V PD (CFG1 NC=20V, DP-DM unidos: solo PD)")
R("R70", "1k", "VBUS", "CH_VDD", B, fn="Serie VDD (ref. WCH)")
C("C70", "1uF", "CH_VDD", "GND", B, fn="Desacoplo VDD")
R("R71", "10k", "VBUS", "CH_VBUS", B, fn="Serie deteccion VBUS")
C("C73", "10uF 35V", "VBUS", "GND", B, C1206, "X5R 1206 35V"); C("C74", "10uF 35V", "VBUS", "GND", B, C1206, "X5R 1206 35V")
# Sensado de entrada RAC_SNS 5 mOhm + filtros (10R, 470nF diferencial, 2x100nF modo comun)
R("R72", "5m", "VBUS", "CHG_VIN", B, "Resistor_SMD:R_1206_3216Metric", "Shunt 5mOhm 1206 1W", fn="RAC_SNS")
R("R73a", "10", "VBUS", "CHG_ACP", B); R("R74", "10", "CHG_VIN", "CHG_ACN", B)
C("C75", "470nF", "CHG_ACP", "CHG_ACN", B, mpn="X7R 0603 50V"); C("C76", "100nF", "CHG_ACP", "GND", B, mpn="X7R 0603 50V"); C("C77", "100nF", "CHG_ACN", "GND", B, mpn="X7R 0603 50V")
for i in range(4): C(f"C{78+i}", "10uF 50V", "CHG_VIN", "GND", B, C1206, "X5R 1206 50V", fn="Entrada puente (TI 80uF)")
add("U7", "CDJ", "BQ25756", "BQ25756", "Package_DFN_QFN:QFN-36-1EP_5x6mm_P0.5mm_EP3.6x4.6mm", "TI BQ25756RRVR (LCSC C19272232)",
    {"1": "I2C_SCL", "2": "I2C_SDA", "3": "CHG_INT", "4": "CHG_STAT1", "5": "CHG_STAT2", "6": "CHG_PG", "7": "CHG_CE", "8": "CHG_TS",
     "9": "CHG_ICHG", "10": "CHG_ILIM", "11": "CHG_FBG", "12": "CHG_FB", "13": "CHG_SRN", "14": "CHG_SRP", "17": "GND", "18": "CHG_SW2",
     "19": "CHG_HD2", "20": "CHG_BT2", "21": "CHG_LD2", "22": "GND", "23": "CHG_DRV", "24": "CHG_REGN", "25": "CHG_LD1", "26": "CHG_BT1",
     "27": "CHG_HD1", "28": "CHG_SW1", "29": "CHG_ACN", "30": "CHG_ACP", "32": "VBUS", "33": "VBUS", "34": "CHG_ACUV", "35": "CHG_ACOV",
     "36": "CHG_FSW", "37": "GND"}, B, "C", "Controlador cargador buck-boost 1-14S")
C("C82", "1uF 50V", "VBUS", "GND", B, mpn="X7R 0603 50V", fn="VAC 1uF")
R("R75", "1M", "VBUS", "CHG_ACUV", B, fn="RAC1 (ventana 4.4-21.9V)"); R("R76", "261k", "CHG_ACUV", "CHG_ACOV", B, fn="RAC2"); R("R77", "73.2k", "CHG_ACOV", "GND", B, fn="RAC3")
# Puente H con 4 N-MOSFET 60 V (equivalente a AONS66614 de la Tabla 7-1)
for q, d, s, g in [("Q1", "CHG_VIN", "CHG_SW1", "CHG_HD1"), ("Q2", "CHG_SW1", "GND", "CHG_LD1"), ("Q3", "CHG_SW2", "GND", "CHG_LD2"), ("Q4", "CHG_VOUT", "CHG_SW2", "CHG_HD2")]:
    add(q, "Transistor_FET", "BSC028N06LS3", "BSC028N06LS3", "Package_TO_SOT_SMD:TDSON-8-1", "Infineon BSC028N06LS3 (60V 2.8mOhm, logic level)", {"5": d, "1": s, "2": s, "3": s, "4": g}, B, "C", "Puente buck-boost")
add("L2", "Device", "L", "10uH", "Inductor_SMD:L_Vishay_IHLP-6767", "Vishay IHLP6767GZER100M01 (Tabla 7-1)", {"1": "CHG_SW1", "2": "CHG_SW2"}, B, "C", "Inductor buck-boost 250kHz")
C("C83", "100nF", "CHG_BT1", "CHG_SW1", B, mpn="X7R 0603 25V", fn="Bootstrap 1"); C("C84", "100nF", "CHG_BT2", "CHG_SW2", B, mpn="X7R 0603 25V", fn="Bootstrap 2")
add("D24", "Device", "D_Schottky", "1N5819HW", SOD123, "Diodes 1N5819HW-7-F", {"2": "CHG_DRV", "1": "CHG_BT1"}, B, "B", "Diodo bootstrap 1 (40V > 25.2+5V)")
add("D28", "Device", "D_Schottky", "1N5819HW", SOD123, "Diodes 1N5819HW-7-F", {"2": "CHG_DRV", "1": "CHG_BT2"}, B, "B", "Diodo bootstrap 2")
R("R78", "10", "CHG_REGN", "CHG_DRV", B, fn="REGN -> DRV_SUP (Fig. 7-1)")
C("C85", "4.7uF", "CHG_REGN", "GND", B, C0805, "X7R 0805 16V"); C("C86", "4.7uF", "CHG_DRV", "GND", B, C0805, "X7R 0805 16V")
for i in range(4): C(f"C{87+i}", "10uF 50V", "CHG_VOUT", "GND", B, C1206, "X5R 1206 50V", fn="Salida puente (TI 80uF)")
# Sensado de bateria RBAT_SNS 5 mOhm (obligatorio 5 mOhm para KICHG) + filtros
R("R79", "5m", "CHG_VOUT", "VBAT", B, "Resistor_SMD:R_1206_3216Metric", "Shunt 5mOhm 1206 1W", fn="RBAT_SNS")
R("R80", "10", "CHG_VOUT", "CHG_SRP", B); R("R81", "10", "VBAT", "CHG_SRN", B)
C("C91b", "470nF", "CHG_SRP", "CHG_SRN", B, mpn="X7R 0603 50V"); C("C92b", "100nF", "CHG_SRP", "GND", B, mpn="X7R 0603 50V"); C("C93", "100nF", "CHG_SRN", "GND", B, mpn="X7R 0603 50V")
# Programacion por resistencias
R("R82", "249k", "VBAT", "CHG_FB", B, fn="FB RTOP (TI 249k)"); R("R83", "16.2k", "CHG_FB", "CHG_FBG", B, fn="FB RBOT: 25.14V = 4.19V/celda")
R("R84", "24.9k", "CHG_ICHG", "GND", B, fn="ICHG = 50AkOhm/24.9k = 2.0A")
R("R85", "6.65k", "CHG_ILIM", "GND", B, fn="ILIM = 20AkOhm/6.65k = 3.0A (60W)")
R("R86", "133k", "CHG_FSW", "GND", B, fn="fsw 250kHz (Tabla 6-2)")
R("R87", "5.23k", "CHG_REGN", "CHG_TS", B, fn="TS RT1 (TI 5.24k)"); R("R88", "30.1k", "CHG_TS", "GND", B, fn="TS RT2 (TI 30.31k)")
add("J4", "Connector_Generic", "Conn_01x02", "NTC BATERIA 10k (103AT)", PH2, "JST B2B-PH-K-S", {"1": "CHG_TS", "2": "GND"}, B, "C", "NTC pegado a la LiPo: sin NTC no carga")
for k, (net, col) in enumerate([("CHG_STAT1", "NARANJA STAT1"), ("CHG_STAT2", "VERDE STAT2"), ("CHG_PG", "AZUL PG")]):
    add(f"D{29+k}", "Device", "LED", col, LED0603, "LED 0603", {"2": "CHG_REGN", "1": f"{net}_K"}, B, "C", "Indicador cargador")
    R(f"R{89+k}", "2.2k", f"{net}_K", net, B)
R("R92", "10k", "CHG_CE", "GND", B, fn="CE bajo = carga habilitada sin ESP32 (limites HW)")
R("R93", "10k", "+3V3", "CHG_INT", B, fn="Pull-up INT")
TPt("TP20", "VBUS", B); TPt("TP21", "CHG_VOUT", B); TPt("TP22", "CHG_INT", B)


# ======================= 4. ALIMENTACION 3.3V: AP63203 (Diodes Tabla 2) =======================
B = "PWR"
add("D14", "Diode", "MBRA340", "MBRA340T3G", "Diode_SMD:D_SMA", "onsemi MBRA340T3G", {"2": "VBAT", "1": "VBAT_P"}, B, "A", "Proteccion polaridad inversa logica")
add("C46", "Device", "C_Polarized", "100uF 50V", ELEC8, "Aluminio 100uF/50V", {"1": "VBAT_P", "2": "GND"}, B, "A", "Bulk entrada buck")
C("C42", "10uF 50V", "VBAT_P", "GND", B, C1206, "X5R 1206 50V", "A", "C1 datasheet (10uF)")
add("U3", "Regulator_Switching", "AP63203WU", "AP63203WU-7", "Package_TO_SOT_SMD:TSOT-23-6", "Diodes AP63203WU-7", {"3": "VBAT_P", "2": "BUCK_EN", "4": "GND", "5": "BUCK_SW", "6": "BUCK_BST", "1": "+3V3_REG"}, B, "A", "3.3V 2A desde bateria")
C("C43", "100nF", "BUCK_BST", "BUCK_SW", B, mpn="X7R 0603 25V", cat="A", fn="C3 BST (100nF)")
add("L1", "Device", "L", "4.7uH", "Inductor_SMD:L_APV_APH0630", "APV APH0630T4R7M", {"1": "BUCK_SW", "2": "+3V3_REG"}, B, "B", "Inductor (datasheet sugiere 3.9uH; 4.7uH verificado ripple 26%)")
C("C44", "22uF 16V", "+3V3_REG", "GND", B, C1206, "X5R 1206 16V", "A", "C2 datasheet (2x22uF)")
C("C45", "22uF 16V", "+3V3_REG", "GND", B, C1206, "X5R 1206 16V", "A", "C2 datasheet (2x22uF)")
add("JP1", "Jumper", "SolderJumper_2_Bridged", "3V3", "Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm", "Puente soldadura (cerrado)", {"1": "+3V3_REG", "2": "+3V3"}, B, "A", "Abrir para medir consumo / aislar 3.3V")
add("D15", "Device", "D_Zener", "SMF3.3A", SOD123F, "Littelfuse SMF3.3A (verificar sufijo)", {"1": "+3V3", "2": "GND"}, B, "A", "TVS riel 3.3V")
C("C1", "47uF 10V", "+3V3", "GND", B, C1206, "X5R 1206 10V", "B", "Bulk junto al ESP32 (picos WiFi)")
R("R73", "0", "BUCK_EN", "PWR_SW", B, cat="A", fn="0R: EN del buck (DNP = placa apagada)")
add("J5", "Connector_Generic", "Conn_01x02", "INTERRUPTOR (abierto=ON)", PH2, "JST B2B-PH-K-S", {"1": "PWR_SW", "2": "GND"}, B, "C", "Interruptor de electronica en chasis")
TPt("TP8", "+3V3", B, "A"); TPt("TP12", "GND", B, "A")

# ======================= 5. ESP32 DevKit V1 (DOIT, 30 pines, en zocalo) =======================
B = "MCU"
# Alimentado por el pin 3V3 desde el AP63203 (VIN sin conectar). Programacion/depuracion por el micro-USB del DevKit.
dk = {"2": "NTC_MOTOR", "3": "NTC_ESC", "4": "RC_CH1_3V", "5": "RC_CH2_3V", "6": "RC_CH3_3V", "7": "SPORT_BTN",
      "8": "ESC_PWM_3V", "9": "SERVO_PWM_3V", "10": "IMU_INT1", "11": "AFE_ALERT", "12": "LT_REAR", "13": "CHG_CE",
      "14": "GND", "16": "AFE_BOOT", "17": "I2C_SCL", "20": "I2C_SDA", "21": "LT_ST_B", "22": "LT_ST_A", "23": "LT_AUX",
      "24": "RC_TX", "25": "RC_RX_3V", "26": "OUT_EN_N", "27": "LT_FRONT", "28": "LT_SPORT", "29": "GND", "30": "+3V3"}
add("U4", "CDJ", "ESP32_DevKit_V1", "ESP32 DevKit V1 (30p)", "CDJ:ESP32_DevKit_V1_30P", "DOIT ESP32 DevKit V1 30 pines + 2x tira hembra 1x15 2.54mm", dk, B, "C", "MCU en zocalo")
C("C13", "22uF", "+3V3", "GND", B, C0805, "X5R 0805 10V", fn="Desacoplo 3V3 junto al zocalo")
C("C16", "100nF", "+3V3", "GND", B)
R("R13", "2.2k", "+3V3", "PWR_LED_A", B)
add("D16", "Device", "LED", "VERDE 3V3", LED0603, "LED verde 0603", {"2": "PWR_LED_A", "1": "GND"}, B)

# ======================= 6. IMU (LSM6DSL, SPI) =======================
B = "IMU"
add("U8", "Sensor_Motion", "LSM6DSL", "LSM6DSL", "Package_LGA:LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y", "ST LSM6DSLTR",
    {"5": "+3V3", "8": "+3V3", "6": "GND", "7": "GND", "12": "+3V3", "13": "I2C_SCL", "14": "I2C_SDA", "1": "GND", "4": "IMU_INT1", "2": "GND", "3": "GND"}, B, "C", "IMU 6 ejes por I2C (0x6A)")
C("C18", "100nF", "+3V3", "GND", B); C("C19", "100nF", "+3V3", "GND", B); C("C20", "1uF", "+3V3", "GND", B)

# ======================= 7. RECEPTOR RC (alimentado por BEC) =======================
B = "RC"
add("J7", "Connector_Generic", "Conn_01x04", "RX SERIE (CRSF/SBUS/iBUS)", PH4, "JST B4B-PH-K-S", {"1": "VSERVO", "2": "RC_TX_OUT", "3": "RC_RX_IN", "4": "GND"}, B)
R("R14", "220", "RC_TX", "RC_TX_OUT", B); ESD("D18", "RC_TX_OUT", B)
for j, sig in (("J8", "RC_CH1"), ("J9", "RC_CH2"), ("J10", "RC_CH3")):
    add(j, "Connector_Generic", "Conn_01x03", f"{sig} PWM", HDR3, "Header 1x03 2.54mm", {"1": f"{sig}_IN", "2": "VSERVO", "3": "GND"}, B)
for u, nin, nout, rs, rp, cd, d in [("U9", "RC_RX_IN", "RC_RX_3V", "R15", "R19", "C23", "D19"), ("U10", "RC_CH1_IN", "RC_CH1_3V", "R16", "R20", "C24", "D20"),
                                   ("U11", "RC_CH2_IN", "RC_CH2_3V", "R17", "R21", "C25", "D21"), ("U12", "RC_CH3_IN", "RC_CH3_3V", "R18", "R22", "C26", "D22")]:
    mid = nin.replace("_IN", "_R")
    R(rs, "1k", nin, mid, B); R(rp, "100k", mid, "GND", B); ESD(d, mid, B)
    add(u, "74xGxx", "74LVC1G125", "74LVC1G125", SOT235, "TI SN74LVC1G125DBVR", {"1": "GND", "2": mid, "3": "GND", "4": nout, "5": "+3V3"}, B, "C", "Buffer entrada 5V-tolerante")
    C(cd, "100nF", "+3V3", "GND", B)

# ======================= 8. SALIDAS ESC / SERVO =======================
B = "OUT"
R("R27", "10k", "+3V3", "OUT_EN_N", B, fn="Salidas deshabilitadas en arranque")
for u, nin, nb, nsig, rs, rp, cd, d in [("U13", "ESC_PWM_3V", "ESC_SIG_B", "ESC_SIG", "R23", "R24", "C21", "D25"),
                                       ("U14", "SERVO_PWM_3V", "SERVO_SIG_B", "SERVO_SIG", "R25", "R26", "C22", "D26")]:
    add(u, "74xGxx", "74LVC1G125", "74LVC1G125", SOT235, "TI SN74LVC1G125DBVR", {"1": "OUT_EN_N", "2": nin, "3": "GND", "4": nb, "5": "+3V3"}, B, "C", "Buffer salida con OE")
    R(rs, "100", nb, nsig, B); R(rp, "10k", nsig, "GND", B); ESD(d, nsig, B); C(cd, "100nF", "+3V3", "GND", B)
add("J11", "Connector_Generic", "Conn_01x03", "ESC", HDR3, "Header 1x03 2.54mm", {"1": "ESC_SIG", "2": "ESC_BEC", "3": "GND"}, B)
add("JP2", "Jumper", "SolderJumper_2_Open", "BEC ESC->VSERVO", "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm", "Puente soldadura (abierto)", {"1": "ESC_BEC", "2": "VSERVO"}, B)
add("J12", "Connector_Generic", "Conn_01x03", "SERVO", HDR3, "Header 1x03 2.54mm", {"1": "SERVO_SIG", "2": "VSERVO", "3": "GND"}, B)
add("J13", "Connector_Generic", "Conn_01x02", "VSERVO IN (BEC)", XT30, "AMASS XT30PW-M", {"1": "VSERVO", "2": "GND"}, B)
add("C2", "Device", "C_Polarized", "470uF 16V", ELEC8, "Aluminio 470uF/16V low-ESR", {"1": "VSERVO", "2": "GND"}, B, "B", "Bulk servo (C2 profesor: valor adaptado)")

# ======================= 9. LUCES: 2x BTS723GW desde VBAT =======================
B = "LUCES"
for k, (u, ch1, ch2, st, rg) in enumerate([("U15", "FRONT", "REAR", "LT_ST_A", "R90"), ("U16", "SPORT", "AUX", "LT_ST_B", "R91")]):
    add(u, "CDJ", "BTS723GW", "BTS723GW", "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm", "Infineon BTS723GWXUMA1",
        {"1": "VBAT", "7": "VBAT", "8": "VBAT", "14": "VBAT", "2": f"LT_{ch1}_IN", "6": f"LT_{ch2}_IN", "3": st, "5": st,
         "11": "+3V3", "4": f"BTS{k+1}_GND", "12": f"LT_{ch1}_OUT", "13": f"LT_{ch1}_OUT", "9": f"LT_{ch2}_OUT", "10": f"LT_{ch2}_OUT"}, B, "A",
        "Interruptor high-side 2 canales con diagnostico")
    R(rg, "150", f"BTS{k+1}_GND", "GND", B, fn="GND logico (proteccion inversion, datasheet)")
    C(f"C{91+k}", "100nF 50V", "VBAT", "GND", B, mpn="X7R 0603 50V")
for n, (ch, rv, rin, rl, j, desc) in enumerate([("FRONT", "1.1k", "R92", "R51", "J14", "blancas delanteras"), ("REAR", "1.2k", "R93", "R52", "J15", "rojas traseras"),
                                                 ("SPORT", "1.2k", "R94", "R53", "J16", "rojas Modo Sport"), ("AUX", "1.2k", "R95", "R54", "J17", "freno/aux")]):
    R(rin, "2.2k", f"LT_{ch}", f"LT_{ch}_IN", B, fn="Serie entrada BTS")
    R(rl, rv, f"LT_{ch}_OUT", f"LT_{ch}_LED", B, R2512, "2512 1W (1 LED a 6S: 0.45W; 0R si el modulo trae R)", "B" if rl in ("R51", "R52") else "C", "Limitadora LED")
    add(j, "Connector_Generic", "Conn_01x02", f"LUZ {desc}", PH2, "JST B2B-PH-K-S", {"1": f"LT_{ch}_LED", "2": "GND"}, B)

# ======================= 10. SENSORES / BOTON SPORT / I2C =======================
B = "AUX"
add("J18", "Connector_Generic", "Conn_01x02", "NTC MOTOR 10k", PH2, "JST B2B-PH-K-S", {"1": "NTC_MOTOR", "2": "GND"}, B)
R("R44", "10k", "+3V3", "NTC_MOTOR", B); C("C31", "100nF", "NTC_MOTOR", "GND", B)
add("J19", "Connector_Generic", "Conn_01x02", "NTC ESC 10k", PH2, "JST B2B-PH-K-S", {"1": "NTC_ESC", "2": "GND"}, B)
R("R45", "10k", "+3V3", "NTC_ESC", B); C("C32", "100nF", "NTC_ESC", "GND", B)
add("J20", "Connector_Generic", "Conn_01x02", "BOTON AUTORIZ. SPORT", PH2, "JST B2B-PH-K-S", {"1": "SPORT_BTN_EXT", "2": "GND"}, B)
R("R46", "1k", "SPORT_BTN_EXT", "SPORT_BTN", B); R("R47", "10k", "+3V3", "SPORT_BTN", B); C("C33", "100nF", "SPORT_BTN", "GND", B)
ESD("D27", "SPORT_BTN", B)
add("J21", "Connector_Generic", "Conn_01x04", "I2C EXP", PH4, "JST B4B-PH-K-S", {"1": "+3V3", "2": "I2C_SDA", "3": "I2C_SCL", "4": "GND"}, B)
R("R48", "4.7k", "+3V3", "I2C_SDA", B); R("R49", "4.7k", "+3V3", "I2C_SCL", B)

# ======================= 11. MECANICO / FLAGS =======================
B = "MECH"
for i in range(4):
    add(f"H{i+1}", "Mechanical", "MountingHole_Pad", "M3", "MountingHole:MountingHole_3.2mm_M3_Pad_Via", "M3 + arandela antivibracion", {"1": "GND"}, B)
for i, net in enumerate(["GND", "VBAT", "VBAT_P", "VSERVO", "VBUS", "AFE_BAT", "+3V3", "CH_VDD", "BTS1_GND", "BTS2_GND", "CHG_DRV"]):
    add(f"#FLG{i+1:02d}", "power", "PWR_FLAG", "PWR_FLAG", "", "", {"1": net}, B)


NC = {"U4": ["1", "15", "18", "19"], "U8": ["9", "10", "11"], "J3": ["A6", "B6", "A7", "B7", "A8", "B8"],
      "U5": ["1", "2"], "U6": ["9", "2", "3", "10"], "U7": ["15", "16", "31"]}

# ---- renumeracion automatica (evita referencias duplicadas); se conservan las del profesor ----
import re as _re
KEEP = {"U3", "L1", "U4", "C1", "C2", "C41", "C42", "C43", "C44", "C45", "C46", "D18", "D19", "D20", "D21", "D22", "D25", "R51", "R52", "R73", "JP1", "TP6", "TP8", "TP12"}
_used = {}; _map = {}
for _r in KEEP:
    _m = _re.match(r"([A-Z#]+)(\d+)", _r); _used.setdefault(_m.group(1), set()).add(int(_m.group(2)))
_new = []
for _p in P:
    _r = _p["ref"]
    if _r in KEEP or _r.startswith("#") or _r.startswith("H"): _new.append(_r); _map.setdefault(_r, _r); continue
    _pre = _re.match(r"[A-Z]+", _r).group(0); _n = 1
    while _n in _used.setdefault(_pre, set()): _n += 1
    _used[_pre].add(_n); _new.append(f"{_pre}{_n}"); _map.setdefault(_r, f"{_pre}{_n}")
for _p, _n2 in zip(P, _new): _p["ref"] = _n2
NC = {_map[k]: v for k, v in NC.items()}
REFMAP = _map
BLOCKS = {}; POS = {}
_refs = [p["ref"] for p in P]
assert len(_refs) == len(set(_refs)), "referencias duplicadas: %s" % sorted({r for r in _refs if _refs.count(r) > 1})
