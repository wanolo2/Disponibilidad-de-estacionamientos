
# ParkFlow — Pruebas de fallos (Fase 3)

## Prueba 1 — Caída de una instancia FastAPI

**Fecha:** 19 de noviembre de 2026.

**Objetivo:** Comprobar que el sistema continúa respondiendo cuando una instancia FastAPI deja de funcionar.

**Procedimiento:**
1. Se verificó que los seis contenedores estaban funcionando.
2. Se detuvo `app-2` mediante `docker compose stop app-2`.
3. Se consultó `/health` a través de Kong.
4. Se consultó `/api/v1/estacionamientos`.
5. Se restauró la instancia con `docker compose start app-2`.

**Resultados:**
- GET /health: HTTP 200 OK.
- GET /api/v1/estacionamientos: HTTP 200 OK.
- X-Instance: app-1.
- X-DB: replica.
- Latencia upstream observada en la consulta: 2573 ms.
- No se midió el tiempo total de recuperación.

**Captura 1 "falla1_app2_detenida"** Se observa que app-2 (instancia 2) presenta estado Exited (0), mientras que app-1, Kong, NGINX y ambas bases de datos permanecen funcionando
**Captura 2 "falla1_disponibilidad_app1"**La solicitud de disponibilidad devuelve HTTP 200 OK mediante la instancia app-1 (X-Instance: app-1), consultando postgreSQL replica. Se confirma que el sistema continúa atendiendo solicitudes con una sola instancia operativa

**Conclusión:** Al dethener app-2, NGINX continuó atendiendo solicitudes mediante app-1. La aplicación mantuvo las consultas de disponibilidad desde PostgreSQL réplica.

## Prueba 2 — Fallo de comunicación con la réplica

**Fecha:** 19 de noviembre de 2026.

**Objetivo:** Evaluar el comportamiento de ParkFlow cuando la réplica deja de aplicar actualizaciones y cuando pierde completamente la comunicación con la aplicación.
**Experimento A - Lecturas desactualizadas**
**Procedimientos**
1. Se oausó la reproducción de WAL en postgreSQL réplica:
SELECT pg_wal_replay_pause()
2. Se verificó el estado mediante:
SELECT pg_is_wal_replay_paused()
3. El resultado fue t (true), confirmando la pausa.
4. Se registró una entrada del vehículo TEST22 en el espacio 2 mediante un POST hacia la primaria.
5. Se consultó la disponiblidad desde la API y directamente desde ambas bases de datos.

**Resultados**
La operación POST devolvió HTTP 201 Created con la cabecera X-DB: primary
Se observo la siguiente diferencia:
Base de datos       | Libres  | Ocupados
PostgreSQL Primaria |  199    |     1
PostgreSQL Réplica  |  200    |     0

La aplicación continuó leyendo desde la réplica, por lo que mostró información desactualizada
**Captura 1: "falla2_DBreplica_Pausada"** Se verificó que la replíca dejo de aplicar las actualizaciones recibidas

**Captura 2: "falla2_escritura_DBprimaria"** Se registro la entrada del vehiculo TEST22 con HTTP 201 Created y X-DB: Primary

**Captura 3: "falla2_lectura_desactualizada"**La primaria mostraba 199 espacios libres mientras que la réplica seguía mostrando 200

**Recuperación de la replicación**
Se reanudó la reproducción WAL mediante:
SELECT pg_wal_Replay_resume()
Posteriormente, la consulta a través de ParkFlow volvió a mostrar 199 espacios libres y 1 ocupado con HTTP 200 OK  y X-DB:Replica

**Captura 4: "falla2_DBreplica_recuperada"** La replica volvió a mostrar los datos actualizados

**Experimento B - Perdida de cominicación con la replica**

**Procedimiento**
1. Se identifcó la red Docker disponibilidad-de-estacionamientos_default
2. Se desconectó mediante:
docker network disconnect disponibilidad-de-estacionamientos_default parkflow-db-replica
3. Se realizó una solicitud GET a /api/v1/estacionamientos.
4. Se reconectó la replica mediante:
docker network connect --alias db-replica disponibilidad-de-estacionamientos_default parflow-db-replica
5. Se repitió la consulta para comprobrar la recuperación

**Resultados**
Comprobación                 |  Resultado

GET durante la conexión      |   HTTP 500 Internal Server Erro
GET despúes de reconectar    |    HTTP 200 OK
Base consulta tras recuperar |    replica
Disponilidad recuperada      |     199 libres, 1 ocupado

**Captura 1: falla2_replica_desconectada** la API devolvió HTTP 500 Internal server cuando perdío la conexion con la replica 

**Captura 2: falla2_conexión_recuperada** La API volvió a responder HTTP 200 OK y X-DB: replica mostrando la disponibilidad actualizada.

**Conclusión de la prueba 2**

Se comprobaron dos comportamientos diferentes:

**Retraso en la replicación** La aplicación continuó funcionando pero mostró datos desactualizados

**Perdida de conexión** La aplicación continuó funcionando, pero mostró datos desactualizadps.
En ambos casos se logró restaurar el funcionamientos normal

Se obervó que la versión actual de ParkFlow Todavía no incorpora un mecanismo automatico para redirigir las lecturas hacia la primaria cuando la réplica es inaccesible.

Se implementrara un metodo de lectura de respaldo desde PostgreSQL primaria, identificando la base utilizada mediante la cabecera X-DB.


## Prueba 3 — Caída de primaria y promoción de réplica

Pendiente.
