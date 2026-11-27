# Carrito Don Julio, revisión E: auditoría de arquitectura

**Fecha:** 13 de noviembre de 2026
**Estado:** 🟡 EN DESARROLLO. Bloque 1 de 8 (arquitectura). Nada fabricado ni probado.
**Base:** rev D3 (`cdj_revD3\`, rama `kicad-revD-en-desarrollo`, commit 56a8de1). La rev D3 no se modifica.

Fuentes primarias usadas en este bloque:

| Documento | Versión | Qué se tomó |
|---|---|---|
| Espressif *ESP32-S3 Series Datasheet* | v2.2 | Tabla 1-1 (variantes), tabla 2-14 (pines flash/PSRAM), sección 2.3.5 (restricciones de GPIO), figura 7-1 (encapsulado) |
| Espressif *PCN20251001* | 2025-11-28 | ESP32-S3R2 → ESP32-S3RH2 |
| Espressif *ESP32-S3 Hardware Design Guidelines*, Schematic Checklist | web, consultada el 13-11-2026 | Alimentación, cristal, CHIP_PU, RF, USB, strapping |
| TI *LMR36015* SNVSB49D | sept. 2020 | Tabla 6 (variantes), tabla 7 (pines), 8.1 (máximos absolutos), tabla 10-1 (componentes) |
| Diodes *AP63200/01/03/05* | DS | Rango de entrada 3.8–32 V, máximo absoluto 35 V DC |

---

## 1. Hechos verificados del ESP32-S3RH2

| Dato | Valor | Fuente |
|---|---|---|
| Flash interna | Ninguna | DS v2.2, tabla 1-1 |
| PSRAM interna | 2 MB, Quad SPI | DS v2.2, tabla 1-1 |
| VDD_SPI | 3.3 V (fijo para esta variante) | DS v2.2, tabla 1-1 |
| Temperatura ambiente | −40 a 105 °C | DS v2.2, tabla 1-1 y PCN20251001 |
| Revisión de chip | v0.2 | DS v2.2, tabla 1-1 |
| Relación con el S3R2 | El S3R2 pasa a EOL y lo sustituye el RH2. Mismo software (ESP-IDF compatible) | PCN20251001, sección 5.4 |
| Encapsulado | QFN56 7 × 7 mm, paso 0.4 mm, EPAD 4.0 × 4.0 mm (D2/E2 nom.) | DS v2.2, figura 7-1 |
| Huella KiCad | `Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP4x4mm` (coincide con la figura 7-1) | Biblioteca KiCad 9 |
| Símbolo KiCad | `MCU_Espressif:ESP32-S3`, pines 1–56 + 57 (GND/EPAD) comprobados contra la tabla 2-1 | Biblioteca KiCad 9 |

**Pines de memoria (DS tabla 2-14, modo Quad):**

| Pin | Nombre | PSRAM interna | Flash externa |
|---|---|---|---|
| 28 | SPICS1 | CE# | — |
| 30 | SPIHD | SIO3 | HOLD# / IO3 |
| 31 | SPIWP | SIO2 | WP# / IO2 |
| 32 | SPICS0 | — | CS# |
| 33 | SPICLK | CLK | CLK |
| 34 | SPIQ | SO / SIO1 | DO / IO1 |
| 35 | SPID | SI / SIO0 | DI / IO0 |

- La flash externa comparte el bus con la PSRAM interna y se selecciona con SPICS0.
- **GPIO26–GPIO32** son prioridad P4 (DS 2.3.5): no se usan para nada más.
- **GPIO33–GPIO37** solo se ocupan en modo SPI de 8 líneas (DS 2.3.5, P3). Con el RH2 (Quad) **quedan libres**, a diferencia del S3R8.
- La flash debe ser de 3.3 V (VDD_SPI = 3.3 V vía RSPI desde VDD3P3_RTC). La guía pide mantener VDD3P3_RTC por encima de 3.0 V.

**Pendiente:** Espressif no publica una lista de flash validadas; la guía remite a su soporte técnico. La candidata es Winbond W25Q128JVSIQ (16 MB, 3.3 V, SOIC-8 208 mil, símbolo `Memory_Flash:W25Q128JVS` en KiCad 9). Se verificará con su datasheet en el bloque 3. Queda marcada como **no validada por Espressif** hasta tener respuesta.

---

## 2. Problemas de la rev D3 y decisión para la rev E

| # | Problema (rev D3) | Evidencia | Decisión rev E | Prioridad |
|---|---|---|---|---|
| P1 | El AP63203 se alimenta directamente de VBAT. Su máximo absoluto es 35 V DC y la entrada recomendada 3.8–32 V. Con 6S (25.2 V) solo quedan 6.8 V de margen operativo y el TVS SMF26CA recorta a unos 42 V. Los picos de frenado regenerativo del ESC pueden superar 32 V. | Datasheet AP6320x; AUDITORIA rev D sección 3 | **Etapa previa LMR36015 (60 V, 66 V transitorio)** de VBAT a 5 V. El AP63203, el L1 y los condensadores del profesor se mantienen, pero alimentados desde 5 V. | **Alta** |
| P2 | El ESP32 DevKit V1 está en zócalo, con retroalimentación desde su regulador y el ancho de filas sin verificar. | AUDITORIA rev D sección 2, puntos 3–5 | Se cambia por el ESP32-S3RH2 soldado, con flash, cristal, USB y RF propios. Desaparecen los puntos 3, 4 y 5. | **Alta** |
| P3 | El USB-C es solo de carga (CH224K a 20 V). La programación dependía del micro-USB del DevKit. | design_d.py | **Segundo USB-C, solo datos y 5 V**, a GPIO19/20. La OR de 5 V (USB o buck) usa el MBRA340T del profesor, así no hay retroalimentación hacia el USB ni hacia la batería. | **Alta** |
| P4 | El motor solo se detiene por software. El OE de los buffers lo maneja un GPIO. | design_d.py, bloque OUT | **Failsafe por hardware:** un monoestable reactivable con latido del ESP32 habilita el OE del buffer del ESC. Sin latido (reset, cuelgue o arranque) el OE se desactiva, ESC_SIG queda a GND por la resistencia de 10 kΩ y el ESC entra en su failsafe. A esto se suman el interruptor físico de armado en serie con el OE y el modo Sport por botón con confirmación. | **Alta** |
| P5 | El BQ76930 se trata como BMS, pero no tiene MOSFET de corte (CHG/DSG sin conectar). | design_d.py, bloque AFE | Se mantiene solo como **monitor y balanceador**. Se documenta que **no es BMS**. La protección de descarga del pack depende del corte por bajo voltaje (LVC) del ESC, y el firmware solo inhibe el acelerador. La protección de carga la da el propio BQ25756 (FB, ICHG, TS). Ver sección 4. | Alta |
| P6 | El plano GND de In1 queda fragmentado por pistas del autorouter. | AUDITORIA rev D, problema 2 | **In1 = GND continuo, sin pistas** (regla del autorouter y comprobación con script). Imprescindible para la línea RF de 50 Ω. | Alta |
| P7 | Zona del cargador (VBUS, CHG_TS, CHG_DRV) completada con autorouter más A*, con vías de 0.45/0.2 mm y tramos de 0.10–0.15 mm. | AUDITORIA rev D, secciones 4 y 6 | El cargador **se mantiene** (decisión del usuario, 13-11-2026). Se rutea **a mano primero** (lazo de potencia y nodos de conmutación) con vías estándar 0.6/0.3 mm, y luego el autorouter para el resto. | Media |
| P8 | No hay ninguna RF diseñada en la placa (la antena era del DevKit). | — | Red CLC + línea coplanar con plano (CPWG) de 50 Ω calculada para el stackup JLC de 4 capas + U.FL. Rendimiento **no validado** hasta medir con VNA. | Media |
| P9 | F1 (5 A) protege a la vez cargador, luces y lógica. | design_d.py | F1 se mantiene para la rama de potencia de la placa (cargador y luces). **Nuevo fusible F2 de unos 0.5 A** solo para la rama lógica antes del LMR36015 (valor exacto en el bloque 2). | Media |
| P10 | El conector de toma XT30 va en paralelo con el ESC. | design_d.py, J1 | Se mantiene el concepto: **la corriente batería → ESC va por cable XT90 a XT90 y no pasa por la PCB.** La PCB toma su alimentación por un mazo en Y con XT30 (la placa consume menos de 4 A). Ver sección 3. | Media |
| P11 | Placa de 130 × 100 mm con DevKit en zócalo. | — | Sin DevKit, la meta es **≤ 110 × 80 mm**. Medida final pendiente del chasis. | Baja |

---

## 3. Arquitectura de potencia

```
 PowerHobby 6S 5000mAh 100C (XT90)
   │ XT90 ════ cable AWG10–12 ════ XT90 ─► ESC ─► motor          (fuera de la PCB)
   │
   └─ derivación en Y (AWG18) ─► J1 XT30 de la PCB
                                 │
                       F1 5 A ── VBAT ──┬─ D1 SMF26CA (ESD/transitorio corto)
                                        ├─ C41 220 µF 50 V
                                        ├─► BQ25756 + CH224K (cargador, J3 USB-C de carga)
                                        ├─► BTS723GW ×2 (luces)
                                        ├─► BQ76930 (monitor 6S, vía J2 balanceo)
                                        └─ F2 ~0.5 A ─ D14 MBRA340 (polaridad) ─ filtro π ─► LMR36015 (VBAT → 5 V, 1.5 A máx.)
                                                                                          │
   J_USB USB-C (datos, 5 V) ─ Schottky ──────────────────────────────── OR ── +5V_SYS ──┤
                                                                                          ▼
                                                                    AP63203 (5 V → 3.3 V, 2 A) + L1 APH0630 (profesor)
                                                                                          │
                                                                    ferrita + LC ─► +3V3 ─► ESP32-S3RH2, flash, IMU, buffers
                                                                    supervisor de 3.0 V ─► CHIP_PU (con RC 10 kΩ / 1 µF)
   ESC BEC ─► VSERVO ─► servo y receptor RC (separado de +3V3; JP2 abierto por defecto)
```

**Por qué dos etapas y no una sola de 60 V a 3.3 V:**
1. El AP63203, el L1 APH0630 y los condensadores C42–C45 son piezas obligatorias del profesor. Desde 5 V trabajan con mucho margen, con un ciclo de trabajo de unos 66 % frente al 13–18 % que tenían desde 25 V.
2. El USB de datos (5 V) y el buck (5 V) se combinan antes del regulador de 3.3 V. Así se puede programar en banco sin batería y sin retroalimentación.
3. Doble filtrado frente al ruido del ESC: el filtro π, el lazo del LMR36015 y el lazo del AP63203.

**Margen de tensión de cada elemento conectado a VBAT** (25.2 V con pack lleno):

| Elemento | Máximo absoluto | Margen | Fuente |
|---|---|---|---|
| LMR36015 VIN | 66 V (60 V operativo) | Amplio | SNVSB49D 8.1 |
| AP63203 VIN | 35 V DC | Ya no ve VBAT | DS Diodes |
| BQ25756, BTS723GW, BQ76930 | Se revisan en el bloque 2/6 contra su datasheet | — | Pendiente |
| D1 SMF26CA | VRWM 26 V > 25.2 V | Ajustado (0.8 V) | Pendiente de recalcular en el bloque 2 |

**Riesgo abierto:** con D1 a 26 V de VRWM y 25.2 V de pack lleno, el TVS queda muy cerca de conducir cuando la batería sale del cargador. En el bloque 2 se evalúa cambiarlo por un SMBJ28A o SMBJ30A (mayor energía) comparando con los máximos absolutos del BQ25756 y de los BTS723GW.

---

## 4. Protección de batería: qué hace cada pieza y qué no

| Función | Quién la hace en rev E | ¿Independiente del firmware? |
|---|---|---|
| Medir las 6 celdas | BQ76930 (ADC 14 bits, I2C) | Sí mide; leerlo requiere firmware |
| Balanceo | BQ76930, bits CELLBAL por I2C | **No**: lo activa el firmware |
| OV/UV de celda | Comparadores del BQ76930, que activan sus salidas CHG/DSG | Sí, pero **CHG/DSG no mueven ningún MOSFET** porque no hay MOSFET de corte en la placa |
| Corte de descarga del pack (motor) | **LVC del ESC** (corte por bajo voltaje). Debe configurarse en el ESC | Sí (lo hace el ESC) |
| Corte de carga | BQ25756: tensión de fin de carga por resistencias FB (25.14 V), corriente ICHG, NTC en TS | **Sí** (resistencias, no registros) |
| Sobrecorriente de la rama de placa | F1 5 A | Sí |
| Sobrecorriente de la rama lógica | F2 ~0.5 A (nuevo) | Sí |
| Temperatura de batería | NTC en CHG_TS (BQ25756 detiene la carga) | Sí, solo durante la carga |

**Conclusión:** la rev E **no es un BMS completo**. Un MOSFET de corte capaz de los picos de este pack (100C nominal sobre 5 Ah) no cabe en esta PCB, y ese camino de corriente está fuera de la placa a propósito. Se recomienda:
- Activar el LVC del ESC (3.3–3.5 V por celda).
- Usar un cargador balanceador externo durante las primeras pruebas, hasta validar el BQ25756 con una batería de prueba supervisada. El cargador integrado se mantiene en la placa, pero CHG_CE permite deshabilitarlo.

---

## 5. Seguridad del control (requisitos de hardware)

| Requisito | Implementación | Estado ante reset o falta de alimentación |
|---|---|---|
| Parada al reiniciar el ESP32 | Los GPIO quedan en alta impedancia al reset; el OE del buffer del ESC tiene pull-up (deshabilitado) y ESC_SIG tiene pull-down de 10 kΩ | Sin pulsos → failsafe del ESC |
| Watchdog | Monoestable 74LVC1G123 reactivado por el latido del ESP32 (unos 100 Hz) → habilita el OE. Además, el watchdog interno del ESP32 (firmware) | Si el latido se para, el OE se desactiva en un tiempo de RC (unos 50 ms, se calcula en el bloque 5) |
| Interruptor de armado | Interruptor físico en serie con el OE (AND con el monoestable) | Abierto = el ESC nunca recibe pulsos |
| Pérdida de radio | Firmware (CRSF/ELRS failsafe) **más** el failsafe del propio receptor | Si el firmware falla, el monoestable corta |
| Modo Sport | Botón físico **y** confirmación por firmware; LED dedicado | En el arranque el modo Sport queda desactivado por defecto |
| Límites térmicos | NTC de motor y ESC al ADC1 (firmware) | Solo firmware: lo cubre el corte térmico del ESC |
| Batería baja | BQ76930 → firmware limita el acelerador; LVC del ESC como respaldo por hardware | — |

---

## 6. Archivos

**Se mantiene intacto:** `cdj_revD3\` y la rama `kicad-revD-en-desarrollo`.

**Nuevos, en `carrito don julio\cdj_revE\`:**

| Archivo | Contenido | Bloque |
|---|---|---|
| `docs\AUDITORIA_ARQ_revE.md` | Este documento | 1 ✅ |
| `docs\diagrama_bloques_revE.png` | Diagrama de bloques y de alimentación | 1 ✅ |
| `cdj_revE.kicad_pro/.kicad_sch` | Esquemático KiCad 9 (generado y verificado contra la netlist) | 2–6 |
| `CDJ_revE.kicad_sym`, `CDJ_revE.pretty\` | Símbolos y huellas propios (LMR36015 RNX, BQ25756, BTS723GW…) | 2–6 |
| `docs\GPIO_revE.csv` | Tabla de pines completa | 5 |
| `docs\CALCULOS_POTENCIA_TERMICA.md` | Cálculos de reguladores, pérdidas y temperatura | 2, 7 |
| `cdj_revE.kicad_pcb` | PCB de 4 capas | 7 |
| `docs\BOM_revE.csv` | BOM con MPN y LCSC verificables | 8 |
| `erc.rpt`, `drc.rpt` | Informes de kicad-cli | 8 |
| `fab\PRELIMINAR\` | Gerbers, taladros, CPL y STEP | 8 |
| `docs\PLAN_PRUEBAS_HW_RF.md` | Pruebas de alimentación, carga, failsafe y RF | 8 |

**Scripts de generación:** en el scratchpad, no en el repositorio, por petición anterior del usuario.

---

## 7. Datos que siguen faltando (no bloquean el esquemático)

- Modelo de ESC y motor, y relación de transmisión.
- Medidas del chasis para la PCB.
- Dimensiones reales del pack PowerHobby (hard case) y del espacio disponible.
- Confirmación de Espressif sobre la flash elegida.
