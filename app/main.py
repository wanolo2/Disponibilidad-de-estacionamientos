
import os
from fastapi import FastAPI

app = FastAPI(title="ParkFlow")

INSTANCE_ID = os.getenv("INSTANCE_ID", "app-1")


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
