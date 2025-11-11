import os

if os.getenv("DD_ENABLED", "false").lower() == "true":
    # Auto-instrumentation should be imported as early as possible.
    import ddtrace.auto  # noqa: F401

from fastapi import FastAPI

from .routers import capabilities, health, manifest

app = FastAPI(
    title="Manifest Server",
    description="A service for running low-code Airbyte connectors",
    version="0.2.0",
    contact={
        "name": "Airbyte",
        "url": "https://airbyte.com",
    },
)

app.include_router(health.router)
app.include_router(capabilities.router)
app.include_router(manifest.router, prefix="/v1")
