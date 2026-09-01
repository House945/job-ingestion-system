import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from jobs.api.routes import jobs as jobs_routes
from jobs.config.defaults import build_pipeline
from jobs.config.settings import Settings
from jobs.ingestion.loader import load_feed
from jobs.service import JobService
from jobs.storage.rejection_log import RejectionLog
from jobs.storage.repository import InMemoryJobRepository

logger = logging.getLogger(__name__)


def build_service(settings: Settings) -> JobService:
    """Wire the service and run ingestion once."""
    service = JobService(
        pipeline=build_pipeline(),
        repository=InMemoryJobRepository(),
        rejection_log=RejectionLog(),
    )

    summary = service.ingest(load_feed(settings.feed_path))
    logger.info(
        "ingested %s records: %s approved, %s rejected",
        summary.processed,
        summary.approved,
        summary.rejected,
    )
    return service


def create_app(service: JobService | None = None) -> FastAPI:
    """Build the application.

    Accepts a prepared service so tests can supply their own feed without
    touching the environment. When none is given, ingestion runs at startup
    from the configured path - see DECISIONS.md, section 16.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.service = service or build_service(Settings.from_env())
        yield

    app = FastAPI(title="Job Ingestion API", version="1.0.0", lifespan=lifespan)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(jobs_routes.router)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    return app


app = create_app()