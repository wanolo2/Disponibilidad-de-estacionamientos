
import os
import psycopg

from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException, Response
from typing import Literal
from pydantic import BaseModel, Field
from datetime import datetime
from fastapi import Query
app = FastAPI(title="ParkFlow")

INSTANCE_ID = os.getenv("INSTANCE_ID", "app-1")
DB_REPLICA_URL = os.getenv("DB_REPLICA_URL")
DB_PRIMARY_URL = os.getenv("DB_PRIMARY_URL")


class MovimientoCrear(BaseModel):
    espacio_id: int = Field(gt=0)
    tipo: Literal["entrada", "salida"]
    patente: str = Field(min_length=4, max_length=12)


@app.middleware("http")
async def add_instance_header(request, call_next):
    response = await call_next(request)
    response.headers["X-Instance"] = INSTANCE_ID
    return response


@app.get("/health")
def health():
    return {
        "status": "ok",
        "instance_id": INSTANCE_ID
    }


@app.get("/api/v1/estacionamientos")
def consultar_estacionamientos(response: Response):
    with psycopg.connect(
        DB_REPLICA_URL,
        row_factory=dict_row
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    e.id,
                    e.nombre,
                    e.ubicacion,
                    e.capacidad,
                    COUNT(s.id) FILTER (
                        WHERE s.ocupado = FALSE
                    ) AS libres,
                    COUNT(s.id) FILTER (
                        WHERE s.ocupado = TRUE
                    ) AS ocupados
                FROM estacionamientos e
                LEFT JOIN espacios s
                    ON s.estacionamiento_id = e.id
                GROUP BY e.id
                ORDER BY e.id;
            """)

            datos = cur.fetchall()

    response.headers["X-DB"] = "replica"
    return datos


@app.get("/api/v1/estacionamientos/{estacionamiento_id}/espacios")
def consultar_espacios(
    estacionamiento_id: int,
    response: Response
):
    with psycopg.connect(
        DB_REPLICA_URL,
        row_factory=dict_row
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, numero, ocupado
                FROM espacios
                WHERE estacionamiento_id = %s
                ORDER BY numero;
            """, (estacionamiento_id,))

            espacios = cur.fetchall()

    response.headers["X-DB"] = "replica"
    return espacios

@app.post("/api/v1/movimientos", status_code=201)
def registrar_movimiento(
    movimiento: MovimientoCrear,
    response: Response
):
    with psycopg.connect(
        DB_PRIMARY_URL,
        row_factory=dict_row
    ) as conn:
        with conn.cursor() as cur:

            # Bloquear el espacio durante la transacción
            cur.execute("""
                SELECT id, ocupado
                FROM espacios
                WHERE id = %s
                FOR UPDATE;
            """, (movimiento.espacio_id,))

            espacio = cur.fetchone()

            if not espacio:
                raise HTTPException(
                    status_code=404,
                    detail="Espacio no encontrado"
                )

            if movimiento.tipo == "entrada" and espacio["ocupado"]:
                raise HTTPException(
                    status_code=409,
                    detail="El espacio ya está ocupado"
                )

            if movimiento.tipo == "salida" and not espacio["ocupado"]:
                raise HTTPException(
                    status_code=409,
                    detail="El espacio ya está libre"
                )

            nuevo_estado = movimiento.tipo == "entrada"

            # Actualizar disponibilidad
            cur.execute("""
                UPDATE espacios
                SET ocupado = %s
                WHERE id = %s;
            """, (
                nuevo_estado,
                movimiento.espacio_id
            ))

            # Registrar el movimiento
            cur.execute("""
                INSERT INTO movimientos (
                    espacio_id, tipo, patente
                )
                VALUES (%s, %s, %s)
                RETURNING id, espacio_id, tipo, patente, fecha;
            """, (
                movimiento.espacio_id,
                movimiento.tipo,
                movimiento.patente.strip().upper()
            ))

            registro = cur.fetchone()

    # La transacción se confirma al salir sin errores
    response.headers["X-DB"] = "primary"

    return registro


@app.get("/api/v1/movimientos")
def consultar_movimientos(
    response: Response,
    pagina: int = Query(default=1, ge=1),
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
    tipo: Literal["entrada", "salida"] | None = None
):
    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        raise HTTPException(
            status_code=422,
            detail="La fecha inicial no puede superar la final"
        )

    consulta = """
        SELECT
            m.id,
            m.espacio_id,
            s.numero AS numero_espacio,
            m.tipo,
            m.patente,
            m.fecha
        FROM movimientos m
        JOIN espacios s ON s.id = m.espacio_id
        WHERE 1=1
    """

    parametros = []

    if fecha_desde:
        consulta += " AND m.fecha >= %s"
        parametros.append(fecha_desde)

    if fecha_hasta:
        consulta += " AND m.fecha <= %s"
        parametros.append(fecha_hasta)

    if tipo:
        consulta += " AND m.tipo = %s"
        parametros.append(tipo)

    consulta += """
        ORDER BY m.fecha DESC, m.id DESC
        LIMIT 50 OFFSET %s
    """

    parametros.append((pagina - 1) * 50)

    with psycopg.connect(
        DB_REPLICA_URL,
        row_factory=dict_row
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(consulta, parametros)
            movimientos = cur.fetchall()

    response.headers["X-DB"] = "replica"

    return {
        "pagina": pagina,
        "limite": 50,
        "movimientos": movimientos
    }
