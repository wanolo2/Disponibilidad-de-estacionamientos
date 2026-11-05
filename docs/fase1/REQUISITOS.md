# ParkFlow - Requisitos del sistema

**Asignatura:** ISI601 - Taller de Diseño de Sistemas  
**Fecha:** 5 de noviembre de 2026


## 1. Requisitos funcionales


| **RF-01** | Consultar disponibilidad | Mostrar capacidad total, espacios libres y ocupados y estado de cada espacio. Lecturas desde la réplica. |
| **RF-02** | Registrar movimientos | El operador registrará entradas y salidas. Se validará el estado del espacio y se guardarán movimiento y cambio de ocupación en una sola transacción en la primaria. |
| **RF-03** | Consultar historial | Mostrar movimientos del más reciente al más antiguo, con filtros por fecha y rango horario y **50 registros por página**. Lecturas desde la réplica. |
| **RF-04** | Consultar estado del servicio | `GET /health` responderá HTTP 200 con JSON que indique el estado y la instancia (`INSTANCE_ID`) operativa. |

## 2. Requisitos no funcionales


| **RNF-01** | Rendimiento | El 95 % de las solicitudes GET en **≤ 500 ms**, POST en **≤ 1 s** y `/health` en **≤ 200 ms**. |
| **RNF-02** | Disponibilidad | **99 %** durante el horario operativo. Si cae una instancia, el balanceador deberá redirigir solicitudes a la otra en **≤ 10 s**. |
| **RNF-03** | RPO | Pérdida máxima objetivo de **30 s** de registros ante caída de la primaria. |
| **RNF-04** | RTO | Recuperar escrituras en **≤ 5 min**, mediante promoción manual de la réplica y ajuste de conexiones. |

## 3. Condiciones técnicas del proyecto

- **Arquitectura:** API Gateway como única entrada, balanceador independiente, dos instancias sin estado y PostgreSQL 16 con primaria para escrituras y réplica para lecturas.
- **Gateway:** enrutamiento por ruta y protección con API key o límite de peticiones por cliente.
- **Variables:** `DB_PRIMARY_URL`, `DB_REPLICA_URL` e `INSTANCE_ID`.
- **Cabeceras:** `X-Instance` en las respuestas y `X-DB: primary` o `X-DB: replica` cuando se consulte una base.
- **Rutas principales:** `GET /health`, `GET /api/v1/estacionamientos`, `GET /api/v1/estacionamientos/{id}/espacios` y `GET/POST /api/v1/movimientos`.

