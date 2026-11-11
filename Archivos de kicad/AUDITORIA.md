# Auditoría del diseño: revisión D

**Fecha:** 11 de noviembre de 2026
**Estado:** 🟡 **EN DESARROLLO**, no apto para producción.

Esta auditoría separa lo que se **verificó con herramientas** de lo que **no se ha verificado**. Nada de esta placa se ha fabricado ni probado en hardware.

---

## 1. Verificaciones que pasan

| Verificación | Herramienta | Resultado |
|---|---|---|
| Netlist del esquemático contra la lista de conexiones del diseño, pin por pin | Netlist exportada con `kicad-cli` | **575 de 575 pines correctos**, sin redes fusionadas |
| ERC (reglas eléctricas del esquemático) | `kicad-cli sch erc` | **0 errores.** 2 avisos esperados: pines de la IMU atados a GND a propósito |
| Paridad esquemático ↔ PCB | `kicad-cli pcb drc --schematic-parity` | **0 diferencias** |
| Separaciones, cortos y bordes en la PCB | `kicad-cli pcb drc` | **0 errores** (solo avisos de serigrafía) |
| Conexiones ruteadas | `kicad-cli pcb drc` | **0 conexiones sin rutear** |
| Huellas | Bibliotecas oficiales de KiCad 9 | Todas existen. La huella QFN-36 del BQ25756 se comparó pad por pad con el dibujo RRV0036A de TI |
| Pines de los integrados | Datasheets oficiales | Tomados de las tablas de pines (TI, Diodes, Infineon, WCH, ST, onsemi) |

## 2. Problemas abiertos (bloquean la fabricación)

| # | Problema | Impacto | Cómo resolver |
|---|---|---|---|
| 1 | **Ruteo del cargador sin revisión visual**: la zona de U5 se completó con herramientas automáticas y ajustes por coordenadas; pasa el DRC pero nadie la ha revisado en pantalla | Posibles recorridos poco limpios en pistas de potencia o de sensado | Abrir la PCB en KiCad y revisar la zona del BQ25756 (lazo de potencia, SRP/SRN, ACP/ACN) |
| 2 | **Plano de GND en In1 fragmentado**: el autorouter usó In1 para señales (unos 1.8 m de pista) | Más ruido para la IMU y el ADC. B.Cu sí tiene GND casi continuo | Reubicar componentes del cargador y volver a rutear con In1 reservado, o rutear a mano |
| 3 | **Orden de pines del DevKit V1 sin verificar físicamente** | Si el clon difiere, conexiones cruzadas | Comparar la serigrafía del DevKit real con `documentacion/PINES_DEVKIT_revD.csv` |
| 4 | **Ancho entre filas del DevKit desconocido** (22.86 o 25.4 mm según el clon) | El zócalo no encaja | La huella trae ambas filas; medir el DevKit real y soldar en la fila correcta |
| 5 | **Retroalimentación del DevKit**: se alimenta por su pin 3V3 | Con USB conectado, sin batería y JP1 cerrado, su regulador alimenta la placa al revés | Abrir JP1 al programar en banco, o agregar un diodo o interruptor |

## 3. Valores no verificados en hardware ni por simulación

| Bloque | Qué falta comprobar |
|---|---|
| Cargador BQ25756 | Valores calculados con las fórmulas del datasheet (FB 249k/16.2k → 25.14 V; ICHG 24.9k → 2 A; ILIM 6.65k → 3 A; ventana 4.4–21.9 V). Estabilidad del lazo, temperatura de los MOSFET y del inductor con carga real |
| MOSFET del cargador | Se usa BSC028N06LS3 (Infineon, 60 V, 2.8 mΩ) como equivalente al AONS66614 que recomienda TI. No validado en este circuito |
| Monitor BQ76930 | Conexión 6S según la Tabla 9-3; balanceo y lectura de celdas sin probar en hardware |
| TVS SMF26CA en VBAT | Con 6S la tensión de recorte (~42 V) supera el máximo absoluto del AP63203 (35 V DC). Protege contra ESD, no contra transitorios largos |
| Fusible F1 | 0451005.MRL (5 A): verificar tensión nominal ≥ 32 V en el datasheet |
| SMF3.3 | Verificar el sufijo exacto (SMF3.3A) |
| Resistencias de LED | 1.1k/1.2k en 2512 dimensionadas para 1 LED a 25.2 V (0.45 W) |
| Camino de VBUS | Del USB-C a R17 va por un plano en F.Cu más un plano en In2 cosidos con 6 vías. Capacidad de corriente a 3 A no calculada |
| Térmica | Sin análisis térmico. Placa 130 × 100 mm, 4 capas |

## 4. Puntos resueltos

### Inductor del AP63203 (L1): se mantiene APH0630T4R7M (4.7 µH)

La Tabla 2 del datasheet de Diodes sugiere 3.9 µH para la versión de 3.3 V. Se verificó el componente del profesor con las ecuaciones de diseño del mismo datasheet, con entrada de 18 a 25.2 V (6S) y fsw = 1.1 MHz:

| Criterio del datasheet | Resultado con 4.7 µH | ¿Cumple? |
|---|---|---|
| Inductancia entre 2.2 y 10 µH | 4.7 µH | Sí |
| Rizado ΔIL entre 30 y 50 % de 2 A (Ec. 7) | 0.52–0.56 A (26–28 %); con 3.9 µH sería 31–33 % | Ligeramente por debajo |
| Corriente nominal ≥ 2.7 A (35 % sobre 2 A) | 5.2–6 A térmica | Sí |
| Saturación por encima de la corriente pico (Ec. 8: 2.28 A) y del límite del convertidor (3.1 A máx.) | Isat 8–9 A | Sí |
| DCR < 100 mΩ | 33 mΩ máx. | Sí |

**Justificación:** la carga real es de unos 0.6 A, y el datasheet recomienda más inductancia para mejor eficiencia a carga ligera. El ciclo de trabajo es de 13–18 %, lejos del 50 % donde aparece la oscilación subarmónica en modo corriente. El rizado de salida es menor que con 3.9 µH. El componente pasa a categoría **A** (reutilizado sin cambios).

### Variante del monitor BQ76930 (U1): BQ7693002DBTR

Según la tabla de variantes del datasheet de TI (SLUSBK2I):

| Variante | Dirección I2C | REGOUT | CRC |
|---|---|---|---|
| BQ7693000 / 01 | 0x08 | 2.5 V | No / Sí |
| **BQ7693002** | **0x08** | **3.3 V** | **No** |
| BQ7693003 | 0x08 | 3.3 V | Sí |

Se elige **BQ7693002DBTR**:
- Su REGOUT de 3.3 V coincide con el bus I2C de 3.3 V del ESP32.
- Sin CRC, el firmware es más simple.
- Tiene stock en LCSC (C2871830).
- Su pinout es idéntico al de la BQ7693003.

### Cargador recolocado y ruteo completo (11 de noviembre de 2026)

Se recolocaron a mano los componentes del cargador para dejar los pasivos críticos junto al BQ25756 y se volvió a rutear toda la placa. Resultado: 0 conexiones sin rutear y 0 errores de DRC.

| Componente | Distancia al pin de U5 antes | Ahora |
|---|---|---|
| C29 (REGN) | 45 mm | 2.0 mm |
| C27 (bootstrap 1) | 33 mm | 2.3 mm |
| C28 (bootstrap 2) | 29 mm | 2.6 mm |
| C30 (DRV_SUP) | 25 mm | 2.4 mm |
| C35/C36 (filtro SRP/SRN) | ~30 mm | 6–7 mm |

Otros cambios de este ruteo:
- VBUS: plano en F.Cu entre el USB-C y R17, y plano en In2 bajo el cargador, cosidos con 6 vías.
- 6 vías a GND dentro del pad térmico del BQ25756 (antes dependía de una sola vía externa).
- Junto a los pines de U5 se usaron 5 vías de 0.45/0.2 mm y tramos de 0.15 mm para poder sacar todas las señales.

### Inductor del cargador (L2): IHLP4040DZER100M5A

El inductor del cargador pasó del IHLP-6767 (17 × 17 mm) al Vishay IHLP4040DZER100M5A (10 µH, 6.5 A, DCR 30.9 mΩ, LCSC C511353), de unos 10 × 10 mm. Con 3 A de entrada y 2 A de carga, el pico de corriente en el inductor ronda 3.5 A, por debajo de los 6.5 A nominales. Pérdida en el DCR: unos 0.28 W a 3 A.

## 5. Fuera del alcance de esta revisión

- **Firmware:** no escrito. Modo Sport, curvas de acelerador, failsafe y comunicación con el cargador, el monitor y la IMU quedan pendientes.
- **Motor y ESC:** no seleccionados. Falta la relación de transmisión. Con 6S se requiere KV ≈ 179 × relación.
- **Imágenes de referencia del profesor:** no recibidas. La selección de componentes se basa en la lista escrita.
- **Espacio en el chasis:** desconocido. La placa de 130 × 100 mm es provisional.

## 6. Avisos de DRC aceptados (no afectan el funcionamiento)

- Serigrafía superpuesta o sobre cobre (cosmético).

No son avisos de DRC, pero conviene saberlo: hay 4 tramos cortos de 0.10–0.12 mm de ancho, y 5 pads GND pasantes (J13, J14, J20, pines 14 y 29 del DevKit) con conexión sólida al plano, que necesitan más calor al soldar.

## 7. Checklist para pasar a producción

- [x] Rutear todas las conexiones y obtener DRC con 0 "sin conectar" (ver sección 4)
- [ ] Revisar visualmente en KiCad el ruteo alrededor del BQ25756
- [ ] Confirmar con el fabricante vías de 0.45/0.2 mm en 4 capas
- [ ] Revisar o mejorar el plano GND de In1
- [ ] Verificar el pinout y el ancho del DevKit real
- [x] Verificar el inductor del AP63203 (ver sección 4)
- [x] Confirmar la variante del BQ76930 (BQ7693002DBTR, ver sección 4)
- [ ] Revisión del diseño por el profesor o un tercero
- [ ] Ajustar el tamaño de la placa al chasis
- [ ] Regenerar los archivos de fabricación y cambiar el estado a "candidato a producción"
- [ ] Prototipo: pruebas de alimentación, carga (con batería de prueba y supervisión), comunicación I2C y salidas
