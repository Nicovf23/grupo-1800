# Rev E: qué cambia respecto a la rev D3 y por qué

**Estado:** 🟡 PRELIMINAR. Diseño completo en KiCad 10, **sin fabricar ni probar**. No apto para producción hasta completar `PLAN_PRUEBAS_HW_RF.md`.

## Resumen

| Bloque | Rev D3 | Rev E | Motivo |
|---|---|---|---|
| Microcontrolador | ESP32 DevKit V1 en zócalo | **ESP32-S3RH2** soldado (QFN56) + flash W25Q128JV 16 MB + cristal 40 MHz | Pedido del prompt maestro; elimina zócalo, retroalimentación del DevKit y dudas de pinout (auditoría D, puntos 3–5) |
| Programación | Micro-USB del DevKit | **USB-C de datos (J6)** con USB nativo GPIO19/20, USBLC6-2SC6, 22 Ω serie | El USB-C J3 sigue siendo solo de carga (CH224K a 20 V) |
| Alimentación lógica | AP63203 directo desde VBAT (máx. abs. 35 V) | **LMR36510** (65 V, 70 V abs.) 6S → 5.42 V → OR con USB → **AP63203** 5 V → 3.3 V | Margen frente a picos del ESC; el AP63203 del profesor ya no ve la batería |
| Protección lógica | F1 5 A común | F1 5 A (cargador + luces) **+ F2 0.5 A solo lógica** | Pedido del prompt |
| Arranque | — (DevKit) | CHIP_PU RC 10k/1 µF + **TPS3839K33** (2.93 V) vía BAT54WS + botones RESET y BOOT + pads UART0 | Guía de Espressif (supervisor si la alimentación sube lenta) |
| Failsafe | OE de los buffers por GPIO (solo software) | **Monoestable 74LVC1G123** alimentado por el latido del ESP32 + interruptor de armado en su CLR → OE de **74LVC1G126**; pull-down de 10 k en ESC_SIG y SERVO_SIG | Parada del motor sin depender del firmware |
| RF | Antena del DevKit | Red CLC 0201 (C116/L5/C117, valores en el rango de la guía) + 0 Ω/DNP lado antena + **U.FL J7** | Antena externa; adaptación a ajustar con VNA |
| Batería | Tratada como protegida por el BQ76930 | BQ76930 documentado **como monitor/balanceo, no BMS**; corte por el LVC del ESC | El BQ76930 no tiene MOSFET de corte (CHG/DSG sin conectar) |
| Cargador | BQ25756 + CH224K | **Igual** (decisión del usuario 13-11-2026); red VBUS renombrada a CHG_VBUS | Evita confusión con el VBUS del USB de datos |
| Supervisión de pack | Solo BQ76930 | + divisor **VBAT_SENSE** 100k/12k a ADC1 | Lectura de respaldo si el BQ76930 falla |
| PCB | 130 × 100 mm, In1 fragmentado | **125 × 95 mm**, 4 capas JLC04161H-7628, **In1 = GND sólido** (sin pistas por regla DRU), In2 señales | Retorno continuo para RF y USB |
| Formato | KiCad 9 | **KiCad 10** | Las herramientas de generación escriben formato 10 |

## Valores verificados contra datasheet (fuente)

| Componente | Dato | Fuente |
|---|---|---|
| ESP32-S3RH2 | Sin flash, PSRAM 2 MB Quad, VDD_SPI 3.3 V, −40..105 °C, rev v0.2 | Espressif DS v2.2, tabla 1-1; PCN20251001 |
| ESP32-S3RH2 | PSRAM en SPICS1; flash en SPICS0; GPIO26–32 no usar; GPIO33–37 libres en Quad | DS v2.2, tabla 2-14, 2.3.5 |
| ESP32-S3RH2 | Pico TX 340 mA (802.11b 21 dBm) | DS v2.2, tabla 5-7 |
| ESP32-S3RH2 | Huella QFN56 7×7, EPAD 4.0×4.0 | DS v2.2, figura 7-1 |
| LMR36510 | Pines, 70 V abs., 400 kHz/5 V: 22 µH, 2×22 µF, 100k/24.9k, 2.2 µF + 220 nF | TI SNVSBD7B tablas 5-1, 6.1, 8-1 |
| LMR36510 | EN 1.231 V, hist. 110 mV; RθJA 42.9 °C/W | SNVSBD7B |
| AP63203 | 3.8–32 V, 35 V abs., θJA 89 °C/W, tabla 2 | Diodes AP6320x DS |
| SRN6045TA-220M | 22 µH, DCR 96 mΩ, Irms 2.3 A, Isat 3.3 A | Bourns SRN6045TA |
| TPS3839K33 | VIT− 2.93 V (2.857–2.974), td 200 ms, push-pull | TI SBVS193D |
| SN74LVC1G123 | Pinout DCU (tabla 4-1) | TI SCES586E |
| SN74LVC1G126 | OE pin 1 activo alto; tabla de función | TI SCES224S |
| Impedancias | USB 90 Ω: 0.2474/0.1524 mm; RF 50 Ω coplanar gap 8 mil: 0.3058 mm | Calculadora JLCPCB (tabla en la skill kicad-pcb-placement) |

## Lo que NO está verificado

- **Flash W25Q128JV:** compatible con ESP-IDF por uso común, pero Espressif no publica lista validada → confirmar con su soporte.
- **Cristal 40 MHz** (CL 10 pF, C112/C113 15 pF): MPN sin elegir; ajustar con prueba de desvío TX.
- **Red RF:** valores iniciales del rango de la guía; sin VNA no hay adaptación real.
- **Tiempo del monoestable** (~47 ms): el datasheet solo da curvas; medir.
- **Pull-up de 47 k en ST del BTS723GW:** valor típico, comprobar con el datasheet de Infineon.
- **D1 SMF26CA:** margen de 0.8 V sobre el pack lleno.
- **Orientación de XT30 y USB-C** en la PCB: deducida del courtyard; mirar el visor 3D.
- **Nodos de conmutación del cargador** (CHG_SW1/2): 16–19 mm entre U19 y L2 en esta colocación automática; revisar a mano antes de fabricar.
- Las hojas 02–05 del esquemático están dibujadas de forma automática (cada pin con su etiqueta): la conectividad está verificada con la netlist de KiCad, pero la legibilidad es menor que la de la hoja de potencia.

## Cómo regenerar

```
cd cdj_revE\generador
python gen_revE.py            (esquemático; venv con schlib)
python bom_revE.py            (BOM)
"C:\Program Files\KiCad\10.0\bin\python.exe" autoplace.py .. --place --force   (recoloca TODO lo no bloqueado)
"C:\Program Files\KiCad\10.0\bin\python.exe" pcb_fab.py                        (clases de red, stackup, DRU)
"C:\Program Files\KiCad\10.0\bin\python.exe" route_revE.py --prep / --import   (planos + FreeRouting)
```
Los `.kicad_sch` son generados: cualquier cambio de esquemático va en `gen_revE.py` / `spec_resto.py`.

## Estado de la PCB (15-11-2026)

| Verificación | Resultado |
|---|---|
| ERC (`docs/erc_revE.rpt`) | 0 errores, 2 avisos (SA0/SDX de la IMU a GND a propósito) |
| Netlist esquemático vs especificación | Coincide exactamente |
| DRC errores de reglas (`docs/drc_revE.rpt`) | **0** (249 avisos de serigrafía) |
| Paridad esquemático ↔ PCB | 0 diferencias |
| **Conexiones sin rutear** | **73** (+3V3 28, GND 13, +BATT 10, VBUS 3 y unas 19 señales sueltas) |

Ruteo: FreeRouting 2.5 (20 pasadas, ~79-87 sin rutear), planos GND en F.Cu/In1/B.Cu con 109 vías junto a pads y 179 de rejilla, plano +3V3 en In2 con 26 vías a pads. Las 73 restantes hay que terminarlas **a mano en KiCad 10** (push & shove) o recolocando la zona densa del cargador (centro-izquierda); el A* automático fue demasiado lento en esa densidad.
