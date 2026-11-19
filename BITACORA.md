# Bitácora del proyecto ParkFlow - ISI601

## Miércoles 4 de noviembre de 2026

- **Qué hice hoy:** Elegí la problemática de disponibilidad de estacionamientos y preparé `docs/fase1/PROBLEMA.md` con la justificación de los cinco criterios, luego cree el repositorio en GitHub agregando a la profesora
- **Dónde me trabé:** No tuve bloqueos técnicos; todavía debo completar los requisitos y los cálculos detallados de la siguiente clase.
- **Qué haré la próxima clase:** Definir los requisitos funcionales y no funcionales, y preparar la estimación de carga.
- **Uso de IA:** Solicité ayuda para estructurar y revisar la problemática. Decidí trabajar con estacionamientos y revisaré los supuestos antes de presentarlos.

## Jueves 5 de noviembre de 2026

- **Qué hice hoy:** Definí cuatro requisitos funcionales, cuatro requisitos no funcionales y las estimaciones de lecturas, escrituras, hora punta y almacenamiento a cinco años en `docs/fase1/`.
- **Dónde me trabé:** Al principio habían varias requisitos que repetian más o menos lo mismo para consultar espacios y para registrar entradas/salidas; los unifiqué.
- **Qué haré la próxima clase:** Preparar los borradores de los diagramas lógico y físico de la arquitectura en draw.io y exportarlos a PNG.
- **Uso de IA:** Pedí  apoyo para calcular la carga y  para redactar los objetivos de rendimiento, disponibilidad, RPO y RTO.

## Jueves 12 de noviembre de 2026

- **Que hice hoy** Configure PostgreSQL primaria y réplica mediante Docker Compose, comprobando la replicación de datos. También levanté dos instancias FastAPI y configuré NGINX para distribuir las solicitudes. Finalmente, comprobé que el sistema continúa respondiendo cuando se detiene una instancia

- *Dónde me trabé:** Tuve problemas con la autenticación del usuario de replicación y con la distribución de solicitudes NGINX. Ambos problemas fueron solucionados

- **Que haré la próxima clase:** Integrar Kong API Gateway, automatizar la configuración de PostgreSQL y documentar las evidencias de funcionamiento

- *Uso de IA:*Utilice ChatGPT para el diagnostico de errores y la preparación de pruebas. Las configuraciones fueron ejecutadas y verificadas por mi

## Viernes 13 de noviembre de 2026 — Entrega Fase 2

**¿Qué hice hoy?** Integré Kong API Gateway con NGINX y FastAPI. Configuré el límite de solicitudes, automaticé la inicialización de la replicación de PostgreSQL y comprobé que los seis contenedores funcionan desde un clon limpio. Documenté las pruebas y actualicé el README.

**¿Dónde me trabé?** Tuve problemas con la configuración de Docker Compose, los saltos de línea del script de PostgreSQL. Logré resolverlos y verificar el funcionamiento.

**¿Qué haré la próxima clase?** Comenzar la Fase 3, implementando los endpoints reales de estacionamientos y movimientos, con escrituras en la primaria y lecturas desde la réplica.

**Uso de IA:** Utilicé ChatGPT como apoyo para configurar los servicios, comprender los errores y preparar las pruebas. Ejecuté los comandos, comprobé los resultados y realicé los ajustes necesarios.

## Miercoles 18 de noviembre de 2026 - Avance Fase 3

**¿Qué hice hoy?** Implementé los endpoints de la app utilizando FastAPI y PostgreSQL. Creé las tablas de estacionamientos, espacios y movimientos, junto con 200 espacios iniciales. Comprobé el registro de entrada y salida mediante POST en la base primaria y las consultas de disponibilidad mediante GET en la replica. Se configuro las rutas de Api Gateway Kong y verifiqué su funcionamiento

**¿Dónde me trabé?** Tuve problemas con la librería Psycopg, lo que provocaba errores 504 al consultar la API. Se soluciono corrigiendo las dependencias y reconstruyendo los contenedores de Docker.

**¿Que haré la proxima clase?** Realizar y documentar las tres pruebas de fallos de la Fase 3, completar las evidencias, actualizar README.

**Uso de IA** Utilice chatGPT como apoyo para el diagnisto de errores de pyhton, Docker y para configurar las rutas de Kong-

## Jueves 19 de noviembre de 2026 - Avance Fase 3

**¿Qué hice hoy?** Realicé las primeras dos pruebas de fallos de ParkFlow. Primero detuve una instancia FastAPI y comprobé que el sistema continuaba funcionando mediante la segunda instancia. Después simulé un retraso en la replicación de PostgreSQL, comprobando que la primaria mostraba 199 espacios libres mientras la réplica mostraba 200. También desconecté la réplica de la red Docker, observé un error HTTP 500 y comprobé que las consultas se recuperaban al restablecer la conexión. Registré los resultados y preparé capturas de pantalla como evidencia.

**¿Dónde me trabe?** Al desconectar PostgreSQL réplica, FastAPI devolvió un error HTTP 500 porque no existe un mecanismo de respaldo para las lecturas. 

**¿Qué haré la próxima clase?** Realizar la tercera prueba de fallos, simulando la caída de PostgreSQL primaria y la promoción de la réplica. Medir RPO y RTO, completar la documentación, actualizar el README y preparar la entrega de la Fase 3.

**Uso de IA** Utilice ChatGPT como apoyo para preparar los procedimientos de prueba, interpretar las respuestas HTTPP y realizar la documentación de los resultados obtenidos.
