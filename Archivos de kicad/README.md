# Carrito Don Julio: placa principal (KiCad)

> ⚠️ **ESTADO: EN DESARROLLO. NO ES UNA VERSIÓN DE PRODUCCIÓN.**
> El ruteo está completo (DRC: 0 errores, 0 conexiones sin rutear), pero no mandar a fabricar todavía: faltan verificaciones físicas y una revisión del diseño (ver [AUDITORIA.md](AUDITORIA.md)).

**Revisión:** D, ruteo 3 (11 de noviembre de 2026)
**Herramienta:** KiCad 9.0
**Vehículo:** RC 1:7, 4WD, batería LiPo 6S (22.2 V nominal / 25.2 V cargada)

## Qué hace esta placa

| Bloque | Componentes principales |
|---|---|
| Microcontrolador | ESP32 DevKit V1 (DOIT, 30 pines) en zócalo |
| Sensor de movimiento | IMU LSM6DSL (I2C, dirección 0x6A) |
| Carga de batería por USB-C | CH224K (pide 20 V por PD) → BQ25756 (buck-boost 6S) |
| Monitoreo y balanceo de celdas | BQ76930 (6 celdas, por el cable de balanceo) |
| Alimentación 3.3 V | AP63203WU (componente recomendado por el profesor) |
| Luces | 2× BTS723GW (4 canales con diagnóstico) |
| Radio control | Entradas PWM ×3 + serie (CRSF/SBUS/iBUS), protegidas |
| Salidas | ESC y servo con buffer y habilitación |
| Protección | ESD5Z3.3T, SMF24CA/SMF26CA, SMF3.3, MBRA340T, fusible |

## Estructura de la carpeta

| Carpeta | Contenido |
|---|---|
| `proyecto_revD/` | Proyecto KiCad editable: esquemático, PCB, librería propia `CDJ` (símbolos y huellas) |
| `fabricacion_PRELIMINAR/` | Gerbers, taladros, BOM, posiciones (CPL) y modelo STEP. **Preliminares, no fabricar** |
| `documentacion/` | Esquemático en PDF, vista 3D, BOM clasificada (A/B/C), mapa de pines del DevKit, instrucciones y `EXPLICACION_PLACA.md` (qué hace cada componente y cada parte del PCB) |
| `reportes/` | Informes ERC, DRC y verificación de la netlist |
| `AUDITORIA.md` | Qué está verificado, qué no, y qué falta para producción |
| `NOTAS_DISENO.md` | Decisiones de diseño, supuestos y cálculos |

## Cómo abrir

1. Abrir `proyecto_revD/cdj_revD.kicad_pro` con KiCad 9.
2. La librería `CDJ` se carga sola desde la carpeta del proyecto (`sym-lib-table` y `fp-lib-table`).
