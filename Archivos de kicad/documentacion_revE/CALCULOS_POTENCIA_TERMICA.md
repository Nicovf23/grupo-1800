# Rev E: cálculos de potencia y térmicos

**Estado:** cálculo de diseño. **No hay mediciones.** Los valores marcados como *estimado* deben confirmarse en banco (ver `PLAN_PRUEBAS_HW_RF.md`).

## 1. Consumo del riel de 3.3 V (peor caso)

| Carga | Corriente | Fuente |
|---|---|---|
| ESP32-S3RH2, TX 802.11b 1 Mbps a 21 dBm (pico) | 340 mA | DS v2.2, tabla 5-7 |
| Flash W25Q128JV activa | ≤ 25 mA | *estimado*; confirmar con el datasheet de Winbond |
| LSM6DSL | < 1 mA | *estimado* (ST) |
| 8 buffers 74LVC1G12x + monoestable | < 1 mA | *estimado* |
| LEDs (estado, armado) | 3 mA | 1 kΩ con LED azul |
| Pull-ups, divisores, supervisor | < 2 mA | Cálculo |
| **Total pico** | **≈ 370 mA** | |

La guía de Espressif pide una fuente de **≥ 500 mA**. El AP63203 da 2 A (DS Diodes), así que el margen es 5.4×.

## 2. Cadena de alimentación (pico de 370 mA en 3.3 V)

| Etapa | Cálculo | Resultado |
|---|---|---|
| Salida 3.3 V | 3.3 V × 0.37 A | 1.22 W |
| AP63203 desde 5 V (η ≈ 88 %, *estimado* de la curva del datasheet) | 1.22 / 0.88 | 1.39 W → 0.28 A en +5V |
| D3 MBRA340 (Vf ≈ 0.35 V a 0.3 A, *estimado*) | 0.35 V × 0.28 A | 0.10 W |
| Salida del LMR36510 (5.42 V) | 5.42 × 0.28 | 1.52 W |
| LMR36510 (η ≈ 87 % a 24 V, *estimado* de SNVSBD7B fig. de eficiencia) | 1.52 / 0.87 | 1.75 W → **79 mA a 22.2 V**, **97 mA a 18 V** |

- F2 (0.5 A) tiene un margen de 5× sobre el consumo de régimen. El pico de conexión (C46 100 µF + C42) lo debe absorber un fusible de **retardo**; elegir el MPN con esa curva.
- La rama lógica consume ≈ **1.8 W** en pico y ≈ 0.5 W con el WiFi inactivo (*estimado*).

## 3. Temperaturas de los reguladores

| Componente | Pérdida | RθJA | ΔT (sobre ambiente) | Tj con 60 °C ambiente | Máx. |
|---|---|---|---|---|---|
| LMR36510 (HSOIC-8 PowerPAD) | 1.75 − 1.52 = 0.23 W | 42.9 °C/W (SNVSBD7B, EVM) | 10 °C | 70 °C | 150 °C |
| AP63203 (TSOT-26) | 1.39 − 1.22 = 0.17 W | 89 °C/W (DS Diodes) | 15 °C | 75 °C | 125 °C (abs.) |
| L3 SRN6045TA-220M | 96 mΩ × 0.28² = 7.5 mW | — | despreciable | — | Irms 2.3 A |
| L1 APH0630 | 33 mΩ × 0.37² = 4.5 mW | — | despreciable | — | — |

Las RθJA de los datasheets son de placas de referencia. La PCB de 4 capas con el plano GND y las vías bajo el pad térmico debe quedar igual o mejor. **Se debe medir con cámara térmica.**

## 4. Cargador BQ25756 (rev D, sin cambios)

| Dato | Valor | Fuente |
|---|---|---|
| Tensión de fin de carga | 25.14 V (4.19 V/celda) | FB 249k/16.2k |
| Corriente de carga | 2.0 A | ICHG 24.9k |
| Límite de entrada | 3.0 A (60 W a 20 V) | ILIM 6.65k |
| Inductor L2 | IHLP4040DZER100M5A, 6.5 A; pico ≈ 3.5 A; pérdida DCR ≈ 0.28 W a 3 A | AUDITORIA rev D |
| Tiempo de carga 5 Ah de 20 % a 100 % | ≈ 4 Ah / 2 A ≈ **2 h** (más la fase CV) | Cálculo |

Potencia de carga: 25 V × 2 A = 50 W. Las pérdidas de MOSFET e inductor (≈ 2–3 W, *estimado*) **no se han medido**: se recomienda cargar sobre una superficie no inflamable y con supervisión en las primeras pruebas.

## 5. Caminos de alta corriente fuera de la PCB

| Tramo | Corriente | Recomendación |
|---|---|---|
| Batería → ESC | Picos de cientos de A (100C × 5 Ah = 500 A teórico) | XT90 + cable de silicona AWG10 (≤ 30 cm). **No pasa por la PCB.** |
| Derivación Y → J1 (XT30) | ≤ 3 A (carga 2 A + luces + lógica) | AWG18; XT30 nominal 15 A (AMASS) |
| Luces (BTS723GW) | ≤ 0.1 A por LED | Pistas de 0.5 mm |

Caída de tensión en el cable del ESC (AWG10, 3.3 mΩ/m, 0.3 m de ida y vuelta = 1 mΩ) a 100 A: **0.1 V y 10 W en el cable**. Es tolerable en pulsos; vigilar la temperatura del XT90 tras una carrera.

## 6. Divisores y tiempos

| Circuito | Cálculo |
|---|---|
| VBAT_SENSE | 25.2 V × 12k / 112k = **2.70 V** (ADC1 con atenuación 12 dB); 18 V → 1.93 V |
| UVLO del LMR36510 | Von = 1.231 × (1 + 1.3M/100k) = **17.2 V**; Voff = 15.7 V (SNVSBD7B, VEN-VOUT-H y la histéresis) |
| Supervisor TPS3839K33 | Reset por debajo de **2.93 V** (2.857–2.974 V); 200 ms tras recuperarse (SBVS193D) |
| CHIP_PU | RC 10 kΩ × 1 µF = 10 ms (guía: 10k/1µF) más el supervisor |
| Monoestable failsafe | tw ≈ Rext × Cext = 100 kΩ × 470 nF ≈ **47 ms** (*estimado*: SCES586E solo da curvas, fig. 5-3). Con un latido de 100 Hz hay un margen de 4.7×. **Medir con osciloscopio.** |
