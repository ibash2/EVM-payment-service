import time
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.blockchain.runer import run_daemons
from src.payment.router import router as payment_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_daemons()
    yield


app = FastAPI(title="Payment Service", lifespan=lifespan)


@app.get("/")
async def root():
    return {"status": "ok", "time": time.time()}


app.include_router(payment_router, tags=["payment"])
