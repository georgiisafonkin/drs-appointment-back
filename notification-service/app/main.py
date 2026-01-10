from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from app.core.kafka import start_consumer, stop_consumer

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(start_consumer())
    yield
    task.cancel()
    await stop_consumer()

app = FastAPI(
    title="Notification Service",
    lifespan=lifespan
)

@app.get("/health")
async def health():
    return {"status": "ok"}
