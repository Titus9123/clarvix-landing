import logging

from fastapi import FastAPI

from backend.api.routers import internal, reports, requests, runs
from backend.core.errors import register_error_handlers
from backend.core.logging import configure_logging
from backend.db.database import init_db


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="Clarvix Ops Backend", version="0.1.0")

    register_error_handlers(app)

    @app.on_event("startup")
    def startup() -> None:
        init_db()
        logging.getLogger(__name__).info("backend_startup_ok")

    app.include_router(requests.router)
    app.include_router(runs.router)
    app.include_router(reports.router)
    app.include_router(internal.router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
