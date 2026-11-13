# ParkFlow — Sistema de disponibilidad de estacionamientos

**Asignatura:** ISI601 — Taller de Diseño de Sistemas
**Proyecto:** Individual
**Estado:** Fase 2 — Arquitectura funcionando en Docker

## 1. Descripción del proyecto

ParkFlow es un sistema diseñado para consultar la disponibilidad de espacios de estacionamiento y registrar entradas y salidas de vehículos.

El proyecto considera tres tipos de clientes: conductores, pantallas informativas y operadores.

En la Fase 2 se implementó y verificó la arquitectura técnica mediante Docker Compose. La lógica real de gestión de estacionamientos corresponde a la Fase 3.

## 2. Arquitectura

La arquitectura utiliza los siguientes componentes:

| Componente | Tecnología | Función |
|---|---|---|
| API Gateway | Kong 3.9.4 | Entrada a la API, enrutamiento y límite de solicitudes |
| Balanceador | NGINX | Distribución de solicitudes entre instancias |
| Aplicación | FastAPI × 2 | Servicio de prueba con identificación de instancia |
| Base primaria | PostgreSQL 16 | Almacenamiento y escrituras |
| Base réplica | PostgreSQL 16 | Réplica de lectura mediante streaming replication |
| Contenedores | Docker Compose | Orquestación de la arquitectura |

El flujo de solicitudes es:

**Cliente → Kong → NGINX → FastAPI**

PostgreSQL utiliza una base primaria y una réplica que recibe los cambios mediante streaming de registros WAL.

## 3. Requisitos previos

Para ejecutar el proyecto se necesita:

- Docker Desktop funcionando.
- Docker Compose.
- Git.
- PowerShell o una terminal compatible.
- Puertos 8000 y 5433 disponibles en el equipo.

## 4. Instalación desde un clon limpio

### 4.1. Clonar el repositorio

```powershell
git clone https://github.com/wanolo2/Disponibilidad-de-estacionamientos.git
cd Disponibilidad-de-estacionamientos
```

### 4.2. Configurar variables de entorno

Crear el archivo `.env` a partir del ejemplo:

```powershell
Copy-Item .env.example .env
```

El archivo contiene las variables necesarias para PostgreSQL y la replicación.

Las contraseñas de `.env.example` son valores de demostración. Para otros entornos se deben reemplazar por contraseñas propias.

El archivo `.env` está excluido de Git para evitar publicar contraseñas reales.

### 4.3. Levantar la arquitectura

Con Docker Desktop funcionando y el archivo `.env` preparado, ejecutar:

```powershell
docker compose up -d
```

Docker Compose crea los contenedores y los volúmenes necesarios.

En una inicialización nueva, el script `db/init-primary.sh` configura automáticamente el usuario de replicación. Posteriormente, la réplica obtiene una copia inicial de la primaria y comienza a recibir los cambios.

### 4.4. Verificar contenedores

```powershell
docker compose ps -a
```

Deben aparecer seis servicios:

- `parkflow-kong`
- `parkflow-nginx`
- `parkflow-app-1`
- `parkflow-app-2`
- `parkflow-db-primary`
- `parkflow-db-replica`

## 5. Pruebas de funcionamiento

### 5.1. API Gateway

Ejecutar:

```powershell
curl.exe -i http://localhost:8000/health
```

Respuesta esperada:

```http
HTTP/1.1 200 OK
x-instance: app-1
Via: 1.1 kong/3.9.4
```

También puede responder `app-2`.

La cabecera `Via` confirma el paso por Kong, mientras que `X-Instance` identifica la instancia FastAPI.

Las instancias de aplicación y NGINX no publican sus puertos directamente en el equipo anfitrión.

### 5.2. Balanceo de carga

Ejecutar:

```powershell
1..10 | ForEach-Object {
    curl.exe -s -D - -o NUL http://localhost:8000/health |
        Select-String -Pattern '^HTTP/', '^x-instance:', '^Via:'
}
```

En las pruebas realizadas se obtuvieron diez respuestas HTTP 200, distribuidas entre las dos instancias:

- `app-1`: cinco solicitudes.
- `app-2`: cinco solicitudes.

### 5.3. Límite de solicitudes de Kong

Kong utiliza el plugin Rate Limiting con un límite de 20 solicitudes por minuto por IP.

Ejecutar:

```powershell
1..25 | ForEach-Object {
    curl.exe -s -o NUL -w '%{http_code}\n' http://localhost:8000/health
}
```

En la prueba realizada se obtuvieron:

- 20 solicitudes aceptadas: HTTP 200.
- 5 solicitudes rechazadas: HTTP 429.

La cantidad puede variar si existen peticiones anteriores dentro de la misma ventana de tiempo.

### 5.4. Comprobar primaria y réplica

Verificar la primaria:

```powershell
docker compose exec db-primary psql -U parkflow -d parkflow -c "SELECT pg_is_in_recovery();"
```

Resultado esperado: `f`.

Verificar la réplica:

```powershell
docker compose exec db-replica psql -U parkflow -d parkflow -c "SELECT pg_is_in_recovery();"
```

Resultado esperado: `t`.

### 5.5. Comprobar replicación de datos

Crear una tabla e insertar un registro en la primaria:

```powershell
docker compose exec db-primary psql -U parkflow -d parkflow -c "CREATE TABLE IF NOT EXISTS prueba_replicacion (id SERIAL PRIMARY KEY, mensaje TEXT); INSERT INTO prueba_replicacion (mensaje) VALUES ('Prueba de replicacion ParkFlow');"
```

Consultar la réplica:

```powershell
docker compose exec db-replica psql -U parkflow -d parkflow -c "SELECT * FROM prueba_replicacion;"
```

El mensaje insertado debe aparecer en la consulta. Como la replicación es asíncrona, puede existir un pequeño retraso.

## 6. Prueba desde un clon limpio

El 13 de noviembre de 2026 se clonó el repositorio en una carpeta independiente denominada `ParkFlow-Prueba-limpia`.

Se ejecutó `docker compose up -d` utilizando nuevos volúmenes.

Resultados comprobados:

- Se crearon y levantaron los seis contenedores.
- PostgreSQL primaria y réplica alcanzaron estado saludable.
- La réplica inició streaming WAL desde la primaria.
- Se insertó un registro nuevo en la primaria y se consultó correctamente desde la réplica.
- Kong respondió HTTP 200 y permitió acceder a FastAPI mediante NGINX.

Esto verificó la inicialización automática de la arquitectura en un entorno limpio.

## 7. Evidencias

Las capturas, comandos ejecutados y resultados de la Fase 2 se encuentran en:

`docs/fase2/EVIDENCIAS.md`

## 8. Detener el sistema

Para detener los contenedores sin eliminar los volúmenes de PostgreSQL:

```powershell
docker compose down
```

No utilizar `docker compose down -v` si se desean conservar los datos almacenados.

## 9. Limitaciones y trabajo pendiente

La Fase 2 utiliza una aplicación FastAPI de prueba que responde a `GET /health`.

En la Fase 3 se implementarán los endpoints reales de estacionamientos y movimientos, incluyendo:

- Escrituras en PostgreSQL primaria.
- Lecturas desde PostgreSQL réplica.
- Cabeceras `X-DB`.
- Segunda función del API Gateway.
- Pruebas de fallas y medición de RPO y RTO.

La replicación asíncrona puede presentar retrasos entre una escritura y su lectura desde la réplica.