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

