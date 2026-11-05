# Auditoría del diseño: revisión D

**Fecha:** 5 de noviembre de 2026
**Estado:** 🟡 **EN DESARROLLO**, no apto para producción.

Esta auditoría separa lo que se **verificó con herramientas** de lo que **no se ha verificado**. Nada de esta placa se ha fabricado ni probado en hardware.

---

## 1. Verificaciones que pasan

| Verificación | Herramienta | Resultado |
|---|---|---|
| Netlist del esquemático contra la lista de conexiones del diseño, pin por pin | Netlist exportada con `kicad-cli` | **575 de 575 pines correctos**, sin redes fusionadas |
| ERC (reglas eléctricas del esquemático) | `kicad-cli sch erc` | **0 errores.** 2 avisos esperados: pines de la IMU atados a GND a propósito |
| Paridad esquemático ↔ PCB | `kicad-cli pcb drc --schematic-parity` | **0 diferencias** |
| Separaciones, cortos y bordes en la PCB | `kicad-cli pcb drc` | **0 errores de separación ni cortos** |
| Huellas | Bibliotecas oficiales de KiCad 9 | Todas existen. La huella QFN-36 del BQ25756 se comparó pad por pad con el dibujo RRV0036A de TI |
| Pines de los integrados | Datasheets oficiales | Tomados de las tablas de pines (TI, Diodes, Infineon, WCH, ST, onsemi) |

## 2. Problemas abiertos (bloquean la fabricación)

| # | Problema | Impacto | Cómo resolver |
|---|---|---|---|
| 1 | **3 conexiones sin rutear** junto a U5 (BQ25756): VBUS, CHG_TS y CHG_DRV | La placa no funcionaría | Rutear a mano en KiCad con el router "Empujar". Coordenadas en `documentacion/LEEME_ANTES_DE_FABRICAR.txt` |
| 2 | **Plano de GND en In1 fragmentado**: el autorouter usó In1 para señales | Más ruido para la IMU y el ADC. B.Cu sí tiene GND casi continuo | Reubicar componentes del cargador y volver a rutear con In1 reservado, o rutear a mano |
| 3 | **Orden de pines del DevKit V1 sin verificar físicamente** | Si el clon difiere, conexiones cruzadas | Comparar la serigrafía del DevKit real con `documentacion/PINES_DEVKIT_revD.csv` |
| 4 | **Ancho entre filas del DevKit desconocido** (22.86 o 25.4 mm según el clon) | El zócalo no encaja | La huella trae ambas filas; medir el DevKit real y soldar en la fila correcta |
| 5 | **Retroalimentación del DevKit**: se alimenta por su pin 3V3 | Con USB conectado, sin batería y JP1 cerrado, su regulador alimenta la placa al revés | Abrir JP1 al programar en banco, o agregar un diodo o interruptor |

## 3. Valores no verificados en hardware ni por simulación

| Bloque | Qué falta comprobar |
|---|---|
| Cargador BQ25756 | Valores calculados con las fórmulas del datasheet (FB 249k/16.2k → 25.14 V; ICHG 24.9k → 2 A; ILIM 6.65k → 3 A; ventana 4.4–21.9 V). Estabilidad del lazo, temperatura de los MOSFET y del inductor con carga real |
| MOSFET del cargador | Se usa BSC028N06LS3 (Infineon, 60 V, 2.8 mΩ) como equivalente al AONS66614 que recomienda TI. No validado en este circuito |
| Inductor del AP63203 | APH0630T4R7M (4.7 µH, del profesor). El datasheet recomienda 3.9 µH para la versión de 3.3 V; el rizado calculado es 26 %. Confirmar con el profesor |
| Monitor BQ76930 | Conexión 6S según la Tabla 9-3. Variante con REGOUT 3.3 V e I2C 0x08 por confirmar al comprar |
| TVS SMF26CA en VBAT | Con 6S la tensión de recorte (~42 V) supera el máximo absoluto del AP63203 (35 V DC). Protege contra ESD, no contra transitorios largos |
| Fusible F1 | 0451005.MRL (5 A): verificar tensión nominal ≥ 32 V en el datasheet |
| SMF3.3 | Verificar el sufijo exacto (SMF3.3A) |
| Resistencias de LED | 1.1k/1.2k en 2512 dimensionadas para 1 LED a 25.2 V (0.45 W) |
| Térmica | Sin análisis térmico. Placa 130 × 100 mm, 4 capas |

## 4. Fuera del alcance de esta revisión

- **Firmware:** no escrito. Modo Sport, curvas de acelerador, failsafe y comunicación con el cargador, el monitor y la IMU quedan pendientes.
- **Motor y ESC:** no seleccionados. Falta la relación de transmisión. Con 6S se requiere KV ≈ 179 × relación.
- **Imágenes de referencia del profesor:** no recibidas. La selección de componentes se basa en la lista escrita.
- **Espacio en el chasis:** desconocido. La placa de 130 × 100 mm es provisional.

## 5. Avisos de DRC aceptados (no afectan el funcionamiento)

- Serigrafía superpuesta o sobre cobre (cosmético).
- 5 alivios térmicos con un solo radio en pads de GND.

## 6. Checklist para pasar a producción

- [ ] Rutear las 3 conexiones pendientes y obtener DRC con 0 "sin conectar"
- [ ] Revisar o mejorar el plano GND de In1
- [ ] Verificar el pinout y el ancho del DevKit real
- [ ] Confirmar el inductor del AP63203 y la variante del BQ76930
- [ ] Revisión del diseño por el profesor o un tercero
- [ ] Ajustar el tamaño de la placa al chasis
- [ ] Regenerar los archivos de fabricación y cambiar el estado a "candidato a producción"
- [ ] Prototipo: pruebas de alimentación, carga (con batería de prueba y supervisión), comunicación I2C y salidas
