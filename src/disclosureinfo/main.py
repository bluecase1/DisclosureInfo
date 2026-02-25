from fastapi import FastAPI
from .settings import Settings
from .routers import health, disclosures

settings = Settings()

app = FastAPI(
    title="DisclosureInfo API",
    version="0.1.0",
)

app.include_router(health.router, tags=["system"])
app.include_router(disclosures.router, prefix="/api/v1", tags=["disclosures"])
