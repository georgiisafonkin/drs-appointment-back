from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router
from app.core.kafka import start_kafka, stop_kafka

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await start_kafka()
    yield
    # shutdown
    await stop_kafka()

app = FastAPI(
    title="Auth Service",
    lifespan=lifespan
)

app.include_router(router)
