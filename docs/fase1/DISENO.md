# ParkFlow - Sistema de disponibilidad de estacionamientos

**Asignatura:** ISI601 - Taller de Diseño de Sistemas  
**Fecha:** miércoles 4 de noviembre de 2026  
**Modalidad:** Proyecto individual

## Problemática

En estacionamientos de centros comerciales o instituciones, los conductores muchas veces desconocen cuántos espacios libres existen antes de ingresar. Esto puede provocar recorridos innecesarios, congestión en los accesos y consultas repetitivas al personal. Además, los encargados necesitan registrar las entradas y salidas para mantener actualizada la información.

Se propone desarrollar **ParkFlow**, una aplicación que permita consultar los espacios disponibles de un estacionamiento y registrar los movimientos de vehículos. Los conductores podrán ver la disponibilidad desde una página web; las pantallas informativas la consultarán automáticamente; y los operadores registrarán entradas y salidas.

## Verificación de los cinco criterios del proyecto

### 1. Más lecturas que escrituras (mínimo 10:1)

Como supuesto inicial se considera un estacionamiento de **200 espacios** y la siguiente actividad diaria:

- **7.200 lecturas** desde cinco pantallas que consultan cada 30 segundos durante 12 horas.
- **2.800 lecturas** adicionales desde la página web.
- **500 escrituras** de movimientos, aproximadamente 250 entradas y 250 salidas.

La relación sería **10.000 lecturas / 500 escrituras = 20:1**. La disponibilidad se consulta continuamente, pero solo cambia cuando entra o sale un vehículo.

### 2. Más de un tipo de cliente

- **Sitio web:** conductores que consultan la disponibilidad.
- **Pantallas informativas:** cliente automatizado que consulta periódicamente la API.
- **Panel del operador:** personal que registra entradas y salidas.

Todos los clientes accederán mediante un API Gateway.

### 3. Posibilidad de crecimiento

Se parte con **un estacionamiento de 200 espacios**, con una meta de crecimiento de **cinco estacionamientos y 1.000 espacios en total**. Suponiendo una actividad similar en cada uno, la carga pasaría de 10.000 a **50.000 lecturas diarias**, y de 500 a **2.500 escrituras diarias**. Esta escala justifica distribuir las solicitudes entre varias instancias de la aplicación.

### 4. Dato importante y tolerancia a fallas

El dato crítico es el **registro de entrada o salida**: si se pierde o se replica con retraso, el número de espacios disponibles podría ser incorrecto. Como objetivos iniciales se proponen **RPO máximo de 30 segundos** y **RTO máximo de 5 minutos**. Son metas que deberán comprobarse en las pruebas, no garantías actuales. La aplicación debe advertir cuando la información de disponibilidad pueda estar desactualizada.

### 5. Alcance reducido

Se trabajará con **tres entidades**:

1. **Estacionamiento:** nombre, ubicación y capacidad.
2. **Espacio:** estacionamiento al que pertenece y estado libre/ocupado.
3. **Movimiento:** registro de entrada o salida con fecha y hora.

Los endpoints mínimos serán consultar estacionamientos, consultar espacios disponibles, registrar movimientos y comprobar el estado de la aplicación (`/health`). No se implementarán pagos, reservas ni sensores físicos.

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



# ParkFlow - Justificación de componentes

**Asignatura:** ISI601 - Taller de Diseño de Sistemas  
**Fecha:** 6 de noviembre de 2026


## 1.- Kong API Gateway

**¿Que problema resuelve?** Permite centralizar el acceso a la API, dirigir las solicitudes a las rutas correspondientes y controla el acceso mediante una API key o límites de peticiones

**¿Que pasaria sin él?** Los clientes tendrian que acceder directamente al balanceador o a la app, perdiendo el control centralizado de acceso y solicitudes

**¿Qué costo agrega** Incorpora un servicio adicional que necesita configuración, recursos del sistema y mantenimiento. Tambíen puede aumentar ligeramente el tiempo de espera.


## 2.- NGINX - Balanceador de carga 

**¿Que problema resuelve?** Distribuye las solicitudes de los usuarios entre las dos instancias, evitando que todo el trafico dependa de una sola instancia. Además, permite continuar recibiendo solicitudes si fallara una de ellas.

**¿Que pasaria sin él?** Las solicitudes podrian centrarse en una sola instancia, aumentado su carga y provocando interrupciones si deja de funcionar. Necesitariamos otro mecanismo para distribuir el trafico y gestionar fallas.

**¿Qué costo agrega** Requiere configuración, mantenimiento y recursos adicionales. Tambien introduce una pequeña latencia y representa un posible punto unico de falla.

## 3.- FastAPI. Instancias de la App

**¿Que problema resuelve?** Permite ejectuar la lógica, procesando las consultas de disponibilidad y los registros de movimientos. Al utilizar dos instancias identicas, el sistema puede continuar atendiendo solicitudes si una deja de funcionar.

**¿Que pasaria sin él?** Sin la app, no podriamos procesar las solicitudes de los usuarios. Si utilizaramos una sola instancia, su caida interrumpiria el serivicio totalmente.

**¿Qué costo agrega**Ejecutar dos instancias requiere más memoria, procesamiento y configuración. Tambien debemos mantener ambas instancias funcionando con la misma versión de la aplicación.

## 4.- PostgreSQL 16 - Base de datos primaria

**¿Que problema resuelve?** Permite almacenar y administrar los datos de la app, registrando las entradas y salidas de vehiculos y actualizando el estado de los espacios de manera consistente.

**¿Que pasaria sin él?**
No tendriamos una base central donde guardar los movimientos y estados del estacionamiento. Además, si la base de datos primaria falla, no podremos registrar nuevos movimientos.
**¿Qué costo agrega**
Requiere almacenamiento, recursos del sistema, configuración y mantenimiento y tambien representa un punto critico de fallas para las ecrituras.

## 5.- PostgreSQL 16 - Base de datos réplica.

**¿Que problema resuelve?**
Permite atender consultas de disponibilidad e historial sin sobrecargar la base primaria. Recibe continuamente los cambios de la primaria mediante la función de Streaming Replication y puede utilizarse para recuperar las operaciones en caso de que fallara la principal
**¿Que pasaria sin él?**
Todas las consultas y escrituras dependerían de la base de datos primaria, aumentando su carga. Además, ante una falla de esta misma, no contariamos con una réplica preparada para asumir sus funciones

**¿Qué costo agrega**
Requiere almacenamiento, recursos adicionales y configuración de replicación. Tambien puede existir un pequeño retraso en la sincronización de datos entre ambas bases.

## 6.- Docker Compose - Administración de contenedores

**¿Que problema resuelve?**
Permite configurar y ejectuar todos los componentes mediante un solo comando, facilitando su despliegue y funcionamiento en diferentes computadores.

**¿Que pasaria sin él?**
Tendriamos que iniciar y configurar cada servicio por separado, aumentad la dificultdad de instalación y el riesgo de error

**¿Qué costo agrega**
Requiere crear y mantener archivos de configuración, administrar redes y volúmenes, y disponer de los recursos necesarios para ejecutar todos los contenedores.


## Riesgo y mitigaciones

 ## Riesgo 1 — Falla de la base de datos primaria
 ## ¿Cuál es el riesgo?

Si PostgreSQL primaria deja de funcionar, ParkFlow no podrá registrar entradas ni salidas de vehículos. Esto podría provocar que la información de ocupación quede desactualizada.

**¿Cómo lo mitigaremos?**

Utilizaremos una réplica de PostgreSQL que mantiene una copia de los datos mediante Streaming Replication. Ante una falla de la primaria, podremos promover manualmente la réplica y configurar las aplicaciones para utilizarla como nueva primaria.

**Objetivos de recuperación:**
- RPO: 30 segundos como máximo objetivo de pérdida de información.
- RTO: 5 minutos como máximo objetivo para restablecer las escrituras.
Estos tiempos se verificarán mediante pruebas y no están garantizados automáticamente por la replicación.


##  Riesgo 2 — Retraso en la replicación de datos
**¿Cuál es el riesgo?**

La réplica de PostgreSQL podría presentar retrasos en la sincronización, provocando que ParkFlow muestre espacios disponibles que realmente están ocupados.

**¿Cómo lo mitigaremos?**

Se supervisará el retraso de replicación y, cuando la información no sea confiable, las consultas podrán redirigirse temporalmente a la base primaria. Además, las operaciones de entrada y salida verificarán el estado actualizado del espacio en la primaria antes de registrar cambios.


## Riesgo 3 — Falla del API Gateway o balanceador
## ¿Cuál es el riesgo?

Si Kong o NGINX dejan de funcionar, las solicitudes de los clientes no podrán llegar a las instancias de ParkFlow, aunque estas continúen operativas.

## ¿Cómo lo mitigaremos?

Se utilizarán verificaciones del estado de los servicios, políticas de reinicio de contenedores y procedimientos documentados para restablecer los componentes afectados.

Estas medidas ayudan a recuperar el servicio, aunque no eliminan completamente los puntos únicos de falla.
