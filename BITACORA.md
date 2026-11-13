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