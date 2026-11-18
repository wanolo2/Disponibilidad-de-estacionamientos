
-- ParkFlow - Esquema de base de datos

CREATE TABLE IF NOT EXISTS estacionamientos (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    ubicacion VARCHAR(200),
    capacidad INTEGER NOT NULL CHECK (capacidad > 0)
);

CREATE TABLE IF NOT EXISTS espacios (
    id BIGSERIAL PRIMARY KEY,
    estacionamiento_id BIGINT NOT NULL
        REFERENCES estacionamientos(id),
    numero INTEGER NOT NULL CHECK (numero > 0),
    ocupado BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (estacionamiento_id, numero)
);

CREATE TABLE IF NOT EXISTS movimientos (
    id BIGSERIAL PRIMARY KEY,
    espacio_id BIGINT NOT NULL REFERENCES espacios(id),
    tipo VARCHAR(10) NOT NULL
        CHECK (tipo IN ('entrada', 'salida')),
    patente VARCHAR(12) NOT NULL,
    fecha TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Crear estacionamiento inicial
INSERT INTO estacionamientos (nombre, ubicacion, capacidad)
VALUES ('Estacionamiento Principal', 'Campus', 200)
ON CONFLICT (nombre) DO NOTHING;

-- Crear 200 espacios inicialmente libres
INSERT INTO espacios (estacionamiento_id, numero)
SELECT e.id, n
FROM estacionamientos e
CROSS JOIN generate_series(1, 200) AS n
WHERE e.nombre = 'Estacionamiento Principal'
ON CONFLICT (estacionamiento_id, numero) DO NOTHING;
