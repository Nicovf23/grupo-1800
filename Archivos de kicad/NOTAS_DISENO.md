# Notas de diseño: placa principal Carrito Don Julio

## Historial de revisiones

| Rev | Cambio principal | Motivo |
|---|---|---|
| A | Arquitectura inicial: TPS54360 (5 V) + LDO + ESP32-S3 | Primera propuesta |
| B | Componentes del profesor (AP63203, BTS723GW, ESD5Z3.3T…) + carga USB-C 4S (BQ25798) | Requisito del profesor + carga dentro del carro |
| C | Batería **6S**: BQ25756 + BQ76930, SMF26CA en batería | Decisión del equipo (24 V) |
| D | **ESP32 DevKit V1** en zócalo; IMU por I2C | Decisión del equipo |
| D (v2) | Inductor del cargador IHLP-4040; más holgura alrededor del BQ25756; BQ7693002 | Reducir tamaño y congestión del cargador |

## Decisiones tomadas por el equipo

- Una sola LiPo **6S** para motor y electrónica.
- Batería cargada **dentro del carro por USB-C**; el USB-C de la placa es solo para carga.
- **ESP32 DevKit V1**; se programa por su micro-USB.

## Supuestos (pendientes de confirmar)

- Placa de 130 × 100 mm (provisional, depende del chasis).
- Luces alimentadas a tensión de batería, con 1 LED y su resistencia por canal.
- El receptor RC se alimenta del BEC (VSERVO), no de la placa.
- El servo se alimenta de un BEC externo por XT30 (o del BEC del ESC con el puente JP2).

## Cálculos principales

| Parámetro | Cálculo | Resultado |
|---|---|---|
| RPM de rueda a 60 km/h (Ø 100 mm) | 16.67 m/s / 0.3142 m × 60 | 3,183 RPM |
| KV necesario en 6S | 3,183 × relación / (22.2 V × 0.8) | ≈ 179 × relación |
| Potencia pico estimada (0–60 km/h en 2 s) | — | ≈ 1 kW eléctricos |
| Tensión de carga | 1.536 V × (1 + 249k/16.2k) | 25.14 V (4.19 V por celda) |
| Corriente de carga | 50 A·kΩ / 24.9 kΩ | 2.0 A (≈ 2.5–3 h para 5000 mAh) |
| Límite de entrada USB | 20 A·kΩ / 6.65 kΩ | 3.0 A (60 W) |
| Ventana de entrada del cargador | 1.1 V / 1.2 V con 1M/261k/73.2k | 4.39–21.9 V |
| Rizado del inductor de 3.3 V (L1 = 4.7 µH) | 3.3 × (Vin − 3.3) / (Vin × 4.7 µH × 1.1 MHz) | 0.52–0.56 A (26–28 %), pico 2.28 A |

## Clasificación de componentes (requisito del profesor)

| Categoría | Significado | Cantidad |
|---|---|---|
| A | Reutilizados directamente de la lista del profesor | 26 |
| B | Del profesor, con adaptación | 8 |
| C | Nuevos, necesarios para el carro | 170 |
| D | Bloques de la referencia que no aplican (RS-485, 0–10 V, 4–20 mA, relés, E/S industriales, EnergyMeter) | 0 en placa |

El detalle por pieza está en `documentacion/BOM_revD.csv`.
