import uuid
from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from httpx import AsyncClient

from poshub_api.demo.router import router as demo_router
from poshub_api.orders.constants import EXTERNAL_API_URL
from poshub_api.orders.router import router as orders_router
from mangum import Mangum

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = AsyncClient(base_url=EXTERNAL_API_URL, verify=False)
    yield
    await app.state.http.aclose()


app = FastAPI(lifespan=lifespan)

app.include_router(orders_router)
app.include_router(demo_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "path": request.url.path,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "path": request.url.path,
            "status_code": 500,
        },
    )


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id

    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


@app.get("/health")
def health():
    return {"status": "ok"}



handler = Mangum(app)

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
