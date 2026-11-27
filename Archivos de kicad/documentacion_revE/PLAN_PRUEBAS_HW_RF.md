# Rev E: plan de pruebas de hardware y RF

Ninguna prueba de esta lista se ha hecho todavía. La placa **no está validada** hasta completar las fases 1–7 y anotar los resultados en una tabla con fecha, equipo y quien midió.

**Equipo mínimo:**
- Fuente de laboratorio de 0–30 V con limitación de corriente
- Multímetro
- Osciloscopio (≥ 50 MHz)
- Carga electrónica o resistencias de potencia
- Cámara térmica o termopar
- Batería 6S de prueba con su alarma de celdas
- Para RF: VNA (o NanoVNA V2 hasta 3 GHz) y antena 2.4 GHz con U.FL

## Fase 0: inspección sin alimentación

| # | Prueba | Criterio |
|---|---|---|
| 0.1 | Inspección visual y de puentes de estaño en el QFN56, el QFN36 y el LGA-14 (lupa o rayos X si es posible) | Sin puentes ni pines levantados |
| 0.2 | Resistencia +BATT–GND, +5V–GND, +3V3–GND, VDD_SPI–GND | > 1 kΩ (sin cortos) |
| 0.3 | JP1 abierto, JP2 abierto | Según el montaje |

## Fase 1: alimentación (sin ESP32 programado)

| # | Prueba | Criterio |
|---|---|---|
| 1.1 | Fuente de 12 V con límite de 100 mA en J1 | LMR36510 apagado (UVLO 17.2 V); consumo < 1 mA |
| 1.2 | Subir a 18 V | 5V_BUCK = 5.42 V ±3 %; +5V ≈ 5.05 V; corriente < 30 mA en vacío |
| 1.3 | Bajar hasta que se apague | Apaga a ≈ 15.7 V (±5 %) |
| 1.4 | 25.2 V | Mismas tensiones; ningún componente > 40 °C tras 10 min |
| 1.5 | Cerrar JP1 | +3V3 = 3.3 V ±3 %; supervisor libera CHIP_PU ≈ 200 ms después |
| 1.6 | Polaridad inversa 18 V con límite de 100 mA | Sin corriente (D2 bloquea); nada se calienta |
| 1.7 | Solo USB de datos (sin batería) | +5V ≈ 4.65 V; +3V3 correcto; **sin tensión en +BATT** |
| 1.8 | USB + batería a la vez | Sin corriente inversa hacia el USB (medir VBUS con el cable desconectado del PC: debe caer a 0) |
| 1.9 | Rizado en +3V3 con el osciloscopio (punta corta) | < 30 mV pp (*objetivo*; documentar el valor medido) |

## Fase 2: MCU, flash y USB

| # | Prueba | Criterio |
|---|---|---|
| 2.1 | Conectar USB-C de datos | El PC enumera "USB JTAG/serial debug unit" |
| 2.2 | `esptool.py chip_id` / `flash_id` | Chip ESP32-S3 (QFN56) revisión v0.2; flash Winbond 16 MB detectada |
| 2.3 | Grabar un ejemplo de ESP-IDF con PSRAM activada | Informa 2 MB de PSRAM, test de memoria correcto |
| 2.4 | Botones BOOT y RESET | Entra en modo descarga / reinicia |
| 2.5 | Brownout: bajar +3V3 (con JP1 abierto, fuente externa en TP8) | Reset por debajo de 2.93 V |
| 2.6 | Frecuencia del cristal (modo TX tone) | Desviación ≤ ±10 ppm; si no, ajustar C112/C113 |

## Fase 3: seguridad del control (OBLIGATORIA antes de conectar el motor)

Prueba siempre con el **ESC desconectado del motor** o con el coche en un soporte y las ruedas en el aire.

| # | Prueba | Criterio |
|---|---|---|
| 3.1 | Sin firmware (ESP32 en blanco) | ESC_SIG en bajo constante (pull-down); FS_OK = 0 |
| 3.2 | Firmware con latido, interruptor de armado abierto | FS_OK = 0, ESC_SIG en bajo |
| 3.3 | Armado cerrado + latido | FS_OK = 1; los pulsos llegan a ESC_SIG |
| 3.4 | Detener el latido por firmware (simular cuelgue) | FS_OK cae a 0 en un tiempo ≤ 60 ms (medir tw real) |
| 3.5 | Pulsar RESET con armado cerrado | ESC_SIG sin pulsos durante todo el reinicio |
| 3.6 | Cortar la alimentación lógica (JP1) con el ESC alimentado por su BEC | Sin pulsos; el ESC entra en failsafe (comprobar con el manual del ESC) |
| 3.7 | Pérdida de radio (apagar emisora) | Firmware y receptor: acelerador neutro en ≤ 1 s |
| 3.8 | Modo Sport sin pulsar el botón | Imposible activarlo |
| 3.9 | Configurar el corte por bajo voltaje (LVC) del ESC | 3.3–3.5 V por celda; probarlo con batería de prueba |

## Fase 4: sensores y E/S

| # | Prueba | Criterio |
|---|---|---|
| 4.1 | Escaneo I2C | 0x08 (BQ76930), 0x6A (LSM6DSL), 0x6B (BQ25756) |
| 4.2 | VBAT_SENSE frente al multímetro | Error < 2 % tras calibrar |
| 4.3 | NTC motor y ESC con resistencias de 10 kΩ | ≈ 25 °C |
| 4.4 | Lectura de las 6 celdas del BQ76930 | Error ≤ 10 mV frente al multímetro |
| 4.5 | Balanceo de una celda (resistencia de prueba) | Corriente de balanceo según el datasheet de TI |
| 4.6 | Luces con LED real | Corriente y temperatura de R51/R52 (2512) |
| 4.7 | Receptor CRSF/ELRS | Tramas válidas a la velocidad configurada |

## Fase 5: cargador (con supervisión)

| # | Prueba | Criterio |
|---|---|---|
| 5.1 | Cargador PD de 20 V **sin batería** | CH224K negocia 20 V (CHG_VBUS ≈ 20 V); BQ25756 sin oscilaciones |
| 5.2 | Batería 6S de prueba al 50 %, NTC conectado | ICHG ≈ 2.0 A; fin de carga a 25.14 V ±0.5 % |
| 5.3 | Temperatura de Q1–Q4, L2 y R303/R310 tras 30 min | < 70 °C (*objetivo*; documentar) |
| 5.4 | NTC desconectado | No carga |
| 5.5 | CHG_CE en alto desde el firmware | Carga detenida |

## Fase 6: RF (no declarar válida sin estas medidas)

| # | Prueba | Criterio |
|---|---|---|
| 6.1 | VNA en el U.FL con el chip apagado, mirando hacia el chip | Medir S11 y ajustar C116/L5/C117 hacia el punto conjugado indicado por Espressif (35+j0 Ω en el chip) |
| 6.2 | Antena externa sola en el VNA | S11 < −10 dB en 2.400–2.4835 GHz |
| 6.3 | Potencia TX con la herramienta de certificación de Espressif (o un medidor de potencia) | Según la tabla 6-2 del datasheet, sin degradación > 2 dB |
| 6.4 | Alcance real con el motor girando | RSSI y pérdida de paquetes registrados |
| 6.5 | Emisiones (si se requiere CE/FCC) | Laboratorio acreditado; fuera del alcance de este proyecto escolar |

## Fase 7: integración en el chasis

| # | Prueba | Criterio |
|---|---|---|
| 7.1 | Vibración: 10 min de conducción | Sin fallos de conexión; revisar soldaduras de los conectores |
| 7.2 | Temperatura de la placa tras una carrera | Ningún componente > 85 °C |
| 7.3 | Temperatura del XT90 y del cable del ESC | Según el fabricante del conector |
