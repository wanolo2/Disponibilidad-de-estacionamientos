
# ParkFlow — Sistema de disponibilidad de estacionamientos

**Asignatura:** ISI601 — Taller de Diseño de Sistemas
**Proyecto:** Individual
**Estado:** Fase 3 — Aplicación funcional
**Fecha:** 20 de noviembre de 2026

## 1. Descripción del proyecto

ParkFlow es un sistema que permite consultar la disponibilidad de estacionamientos y registrar las entradas y salidas de vehículos.

Está orientado a conductores, operadores y sistemas de información que necesitan conocer la ocupación de los espacios.

El proyecto utiliza una arquitectura distribuida con dos instancias FastAPI, un balanceador de carga, un API Gateway y dos bases de datos PostgreSQL con replicación asíncrona.

La aplicación permite:

- Consultar espacios libres y ocupados.
- Revisar el estado individual de los espacios.
- Registrar entradas y salidas de vehículos.
- Consultar el historial de movimientos.
- Filtrar movimientos por tipo, fecha y hora.
- Identificar qué instancia y base de datos atendieron cada solicitud.

## 2. Arquitectura del sistema

| Componente | Tecnología | Función |
|---|---|---|
| API Gateway | Kong 3.9.4 | Enrutamiento y límite de solicitudes |
| Balanceador | NGINX | Distribuye solicitudes entre instancias |
| Aplicación | FastAPI × 2 | Ejecuta la lógica de ParkFlow |
| Base primaria | PostgreSQL 16 | Registra movimientos y actualiza espacios |
| Base réplica | PostgreSQL 16 | Atiende consultas mediante replicación WAL |
| Contenedores | Docker Compose | Configura y levanta los servicios |

### 2.1. Flujo de solicitudes

Cliente → Kong → NGINX → FastAPI

Las dos instancias FastAPI utilizan la siguiente separación:

- **POST:** escribe en PostgreSQL primaria.
- **GET:** consulta PostgreSQL réplica.

Las respuestas incluyen:

- `X-Instance`: identifica la instancia FastAPI.
- `X-DB`: indica la conexión de base de datos utilizada.

### 2.2. Replicación

PostgreSQL utiliza replicación asíncrona mediante streaming WAL.

Las escrituras se realizan en la primaria y los cambios se transmiten a la réplica.

Debido a la naturaleza asíncrona, puede existir un retraso entre una escritura confirmada y su disponibilidad en las consultas de lectura.

## 3. Requisitos previos

Para ejecutar el sistema se necesita:

- Docker y Docker Compose.
- Git.
- Una terminal compatible con Linux o Windows.
- Puertos locales 8000 y 5433 disponibles.

El proyecto puede ejecutarse desde Docker Desktop o GitHub Codespaces.

## 4. Instalación desde un clon limpio

### 4.1. Clonar el repositorio

```bash
git clone https://github.com/wanolo2/Disponibilidad-de-estacionamientos.git
cd Disponibilidad-de-estacionamientos
```

### 4.2. Configurar las variables de entorno

En Linux o GitHub Codespaces:

```bash
cp .env.example .env
```

En PowerShell:

```powershell
Copy-Item .env.example .env
```

Editar `.env` y comprobar que las siguientes variables tengan valores no vacíos:

- `POSTGRES_PASSWORD`
- `REPLICATION_PASSWORD`

Las contraseñas deben corresponder a las utilizadas por el entorno de pruebas.

El archivo `.env` está excluido de Git para evitar publicar credenciales.

### 4.3. Iniciar ParkFlow

```bash
docker compose up -d --build
```

Docker Compose construye las aplicaciones y levanta los seis contenedores.

En una instalación nueva, PostgreSQL configura la replicación mediante `db/init-primary.sh` y crea las tablas iniciales mediante `db/schema.sql`.

El sistema inicializa un estacionamiento con 200 espacios.

### 4.4. Comprobar los servicios

```bash
docker compose ps -a
```

Servicios esperados:

- `parkflow-kong`
- `parkflow-nginx`
- `parkflow-app-1`
- `parkflow-app-2`
- `parkflow-db-primary`
- `parkflow-db-replica`

Las bases de datos deben alcanzar el estado `healthy`.

## 5. Endpoints de ParkFlow

| Método | Endpoint | Función | Base |
|---|---|---|---|
| GET | `/health` | Estado de FastAPI | No requiere BD |
| GET | `/api/v1/estacionamientos` | Disponibilidad general | Réplica |
| GET | `/api/v1/estacionamientos/{id}/espacios` | Estado de espacios | Réplica |
| POST | `/api/v1/movimientos` | Registrar entrada o salida | Primaria |
| GET | `/api/v1/movimientos` | Historial de movimientos | Réplica |

El historial admite los parámetros `pagina`, `tipo`, `fecha_desde` y `fecha_hasta`.

La paginación utiliza un máximo de 50 registros por página.

## 6. Pruebas de funcionamiento

Los siguientes ejemplos utilizan `curl` desde una terminal Linux o GitHub Codespaces.

En Windows PowerShell se puede utilizar `curl.exe`.

### 6.1. Verificar FastAPI

```bash
curl -i http://localhost:8000/health
```

Resultado esperado:

- HTTP 200 OK.
- `X-Instance: app-1` o `app-2`.
- Cabecera `Via` correspondiente a Kong.

### 6.2. Consultar disponibilidad

```bash
curl -i http://localhost:8000/api/v1/estacionamientos
```

Respuesta esperada:

- HTTP 200 OK.
- `X-DB: replica`.
- Cantidad de espacios libres y ocupados.

La disponibilidad depende de los movimientos almacenados.

### 6.3. Consultar espacios individuales

```bash
curl -i http://localhost:8000/api/v1/estacionamientos/1/espacios
```

Devuelve los espacios registrados para el estacionamiento 1 y su estado de ocupación.

### 6.4. Registrar entrada de vehículo

Primero se debe comprobar que el espacio seleccionado esté libre.

Ejemplo de entrada al espacio 10:

```bash
curl -i -X POST http://localhost:8000/api/v1/movimientos \
  -H "Content-Type: application/json" \
  -d '{"espacio_id":10,"tipo":"entrada","patente":"DEMO10"}'
```

Si el espacio está libre, se espera:

- HTTP 201 Created.
- `X-DB: primary`.
- Movimiento de entrada registrado.
- Espacio actualizado a ocupado.

Si el espacio ya está ocupado, la API devuelve HTTP 409.

### 6.5. Registrar salida de vehículo

```bash
curl -i -X POST http://localhost:8000/api/v1/movimientos \
  -H "Content-Type: application/json" \
  -d '{"espacio_id":10,"tipo":"salida","patente":"DEMO10"}'
```

Si el espacio estaba ocupado, se espera:

- HTTP 201 Created.
- `X-DB: primary`.
- Movimiento de salida registrado.
- Espacio actualizado a libre.

### 6.6. Consultar historial

```bash
curl -i http://localhost:8000/api/v1/movimientos
```

La respuesta incluye los movimientos ordenados por fecha descendente.

### 6.7. Filtrar movimientos

Consultar entradas:

```bash
curl -i "http://localhost:8000/api/v1/movimientos?tipo=entrada"
```

Consultar la segunda página:

```bash
curl -i "http://localhost:8000/api/v1/movimientos?pagina=2"
```

También es posible utilizar filtros de fecha y hora mediante `fecha_desde` y `fecha_hasta`, con valores ISO 8601.

## 7. API Gateway y balanceador

### 7.1. Enrutamiento mediante Kong

Kong tiene configuradas rutas para:

- `/health`
- `/api/v1/...`

Ejemplo de ruta válida:

```bash
curl -i http://localhost:8000/health
```

Ejemplo de ruta no registrada:

```bash
curl -i http://localhost:8000/no-existe
```

Resultado esperado para la segunda consulta:

HTTP 404 Not Found, generado por Kong.

### 7.2. Rate limiting

Kong utiliza un límite de 20 solicitudes por minuto por IP.

Si se supera el límite, devuelve HTTP 429 Too Many Requests.

Esta función evita que un cliente realice una cantidad excesiva de solicitudes dentro de una ventana de tiempo.

### 7.3. Balanceo de carga

NGINX distribuye las peticiones entre `app-1` y `app-2`.

La cabecera `X-Instance` permite comprobar cuál instancia respondió.

Durante las pruebas se verificó la distribución de solicitudes entre ambas aplicaciones.

## 8. PostgreSQL primaria y réplica

### 8.1. Verificar la primaria

```bash
docker compose exec db-primary psql -U parkflow -d parkflow -c "SELECT pg_is_in_recovery();"
```

Resultado esperado: `f`.

### 8.2. Verificar la réplica

```bash
docker compose exec db-replica psql -U parkflow -d parkflow -c "SELECT pg_is_in_recovery();"
```

Resultado esperado: `t`.

### 8.3. Comprobar streaming

```bash
docker compose exec db-primary psql -U parkflow -d parkflow -c "SELECT state, sync_state FROM pg_stat_replication;"
```

Resultado esperado:

`streaming | async`

### 8.4. Comprobar los datos

```bash
docker compose exec db-primary psql -U parkflow -d parkflow -c "SELECT COUNT(*) FROM espacios; SELECT COUNT(*) FROM movimientos;"
```

El número de movimientos depende de las operaciones realizadas.

## 9. Pruebas de fallos — Fase 3

Se realizaron tres experimentos para evaluar la tolerancia a fallos.

### 9.1. Caída de FastAPI

Se detuvo `app-2` y se verificó que ParkFlow continuó respondiendo mediante `app-1`.

Resultado: HTTP 200 OK y continuidad de las consultas.

### 9.2. Fallo de PostgreSQL réplica

Se ejecutaron dos experimentos:

- Pausa de reproducción WAL: se observaron lecturas desactualizadas.
- Desconexión de la réplica: la API devolvió HTTP 500.

En ambos casos se restauró posteriormente el funcionamiento.

### 9.3. Caída de PostgreSQL primaria

Se detuvo la primaria y se promovió manualmente la réplica.

Después de actualizar la conexión de FastAPI y recargar NGINX, se recuperaron las escrituras.

**Resultados del ensayo final:**

| Indicador | Resultado |
|---|---|
| Promoción de réplica | Exitosa |
| Escritura posterior a promoción | HTTP 201 Created |
| RTO manual observado | 266 segundos |
| Objetivo RTO | 300 segundos |
| Pérdida del registro de control | 0 registros |
| RPO temporal exacto | No determinado |

El RTO incluye la ejecución manual del procedimiento. El objetivo se cumplió en este ensayo, pero no representa una garantía para futuras fallas.

La conservación del registro de control no demuestra que todas las transacciones confirmadas hayan sobrevivido.

La documentación completa, comandos y evidencias están en:

`docs/fase3/PRUEBAS_DE_FALLA.md`

## 10. Prueba desde un clon limpio

El 13 de noviembre se verificó la inicialización automática de la arquitectura de la Fase 2 desde un clon limpio.

Se levantaron los seis contenedores y se comprobó la replicación primaria-réplica.

Para la Fase 3, la prueba de clon limpio debe confirmar también los endpoints reales, la inicialización de las tablas y las escrituras y lecturas mediante la API.

## 11. Decisiones de diseño

**Kong API Gateway:** centraliza el acceso, administra las rutas y limita la cantidad de solicitudes.

**NGINX:** distribuye la carga entre las instancias FastAPI y permite continuar respondiendo si una de ellas falla.

**Dos instancias FastAPI:** proporcionan redundancia y separan la lógica de aplicación de los demás componentes.

**PostgreSQL primaria:** centraliza las operaciones de escritura y mantiene la consistencia de las actualizaciones transaccionales.

**PostgreSQL réplica:** atiende consultas para separar la carga de lectura y escritura.

**Docker Compose:** permite configurar y levantar los componentes de manera reproducible.

## 12. Limitaciones

- La replicación es asíncrona, por lo que pueden existir lecturas desactualizadas.
- Si la réplica se desconecta, las consultas pueden devolver HTTP 500.
- No existe un mecanismo automático de lectura de respaldo hacia la primaria.
- La promoción de réplica y redirección de conexiones son manuales.
- El RPO temporal exacto no fue determinado.
- La aplicación no dispone todavía de una interfaz web para usuarios finales.
- El failover modifica los roles de las bases; la antigua primaria no debe reiniciarse sin una reintegración correcta.

Como mejoras futuras se propone automatizar el failover, incorporar respaldo de lectura y desarrollar una interfaz web de administración y consulta.

## 13. Documentación

- `docs/fase1/`: problemática, requisitos y diseño.
- `docs/fase2/EVIDENCIAS.md`: pruebas de arquitectura.
- `docs/fase3/PRUEBAS_DE_FALLA.md`: pruebas de fallos y resultados.
- `docs/fase3/evidencias/`: capturas de los experimentos.
- `BITACORA.md`: registro de avances del proyecto.

## 14. Detener el sistema

Para detener los contenedores sin borrar los volúmenes:

```bash
docker compose down
```

Para iniciar nuevamente la arquitectura normal:

```bash
docker compose up -d --build
```

**Precaución:** después de una promoción de PostgreSQL, no reiniciar la antigua primaria sin restaurar previamente una arquitectura coherente. No usar `docker compose down -v` si se necesitan conservar los datos.

## 15. Estado final

ParkFlow integra una API funcional de estacionamientos, dos instancias FastAPI, Kong, NGINX y replicación PostgreSQL.

Se implementaron operaciones reales de lectura y escritura, se verificaron las dos funciones de Kong y se documentaron las tres pruebas de fallos correspondientes a la Fase 3.
