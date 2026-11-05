# ParkFlow - Estimación de carga

**Asignatura:** ISI601 - Taller de Diseño de Sistemas  
**Fecha:** 5 de noviembre de 2026

## 1. Supuestos

Se considera inicialmente **un estacionamiento de 200 espacios**, abierto **12 horas diarias**.

| Actividad | Cálculo | Solicitudes diarias |
| --- | --- | ---: |
| 5 pantallas que consultan cada 30 segundos | 5 × 12 horas × 120 consultas/hora | 7.200 GET |
| 700 conductores que consultan 4 veces | 700 × 4 | 2.800 GET |
| 250 entradas y 250 salidas | 250 + 250 | 500 POST |

**Resultado:** 10.000 lecturas y 500 escrituras diarias; relación **20:1**, superior al mínimo de 10:1 solicitado.

## 2. Carga promedio y hora punta

El promedio se calcula sobre 12 horas (`43.200 segundos`). Para la hora punta se suponen **600 consultas de pantallas, 600 consultas web y 100 movimientos** en una hora.

| Indicador | Promedio | Hora punta |
| --- | ---: | ---: |
| Lecturas por hora | 833,3 | 1.200 |
| Escrituras por hora | 41,7 | 100 |
| **Lecturas por segundo** | **0,231** | **0,333** |
| **Escrituras por segundo** | **0,012** | **0,028** |
| Relación lecturas/escrituras | 20:1 | 12:1 |

Ejemplo de cálculo: `10.000 / 43.200 = 0,231 GET/s` en promedio; `1.200 / 3.600 = 0,333 GET/s` en hora punta.

## 3. Crecimiento esperado

La meta es ampliar el sistema de **1 a 5 estacionamientos**, pasando de **200 a 1.000 espacios** en total. Si cada estacionamiento mantiene una actividad similar:

| Indicador | 1 estacionamiento | 5 estacionamientos |
| --- | ---: | ---: |
| Lecturas diarias | 10.000 | 50.000 |
| Escrituras diarias | 500 | 2.500 |
| Lecturas por segundo en hora punta | 0,333 | 1,667 |
| Escrituras por segundo en hora punta | 0,028 | 0,139 |

El balanceador y las dos instancias servirán tanto para distribuir la carga como para mantener el servicio si una instancia falla.

## 4. Almacenamiento a cinco años

Se estima **250 bytes por movimiento** (datos, índices y sobrecarga), **365 días al año** y un **30 % de margen**.

| Escenario | Movimientos en 5 años | Almacenamiento con margen |
| --- | ---: | ---: |
| 1 estacionamiento: 500 movimientos/día | 912.500 | 297 MB |
| 5 estacionamientos: 2.500 movimientos/día | 4.562.500 | **1,48 GB por base** |

Como habrá una **base primaria y una réplica**, la proyección conservadora para cinco estacionamientos es de **2,96 GB entre ambas**. Se supone que los cinco operan durante los cinco años para no subestimar la capacidad.

**Nota:** Son estimaciones académicas de solicitudes GET/POST y almacenamiento de datos del negocio. Un POST puede realizar varias operaciones SQL. No se incluyen respaldos, archivos WAL ni logs; esos requerirán espacio adicional.
