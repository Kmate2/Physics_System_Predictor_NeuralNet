from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CollectorRegistry, Counter, Histogram, CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response
from time import perf_counter
from project.backend.routers import predict, health

app = FastAPI(title="Physics Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

reg = CollectorRegistry()
REQS = Counter("http_requests_total", "Count of requests", ["route","method","code"], registry=reg)
LAT  = Histogram("http_request_duration_seconds", "Request latency", ["route","method"], registry=reg)

@app.middleware("http")
async def metrics_mw(request: Request, call_next):
    start = perf_counter()
    resp = await call_next(request)
    LAT.labels(request.url.path, request.method).observe(perf_counter() - start)
    REQS.labels(request.url.path, request.method, str(resp.status_code)).inc()
    return resp

@app.get("/metrics")
def metrics():
    return Response(generate_latest(reg), media_type=CONTENT_TYPE_LATEST)


app.include_router(predict.router)
app.include_router(health.router)
