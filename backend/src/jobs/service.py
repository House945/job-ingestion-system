from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from jobs.ingestion.pipeline import IngestionPipeline
from jobs.models.canonical import CanonicalJob
from jobs.models.decision import Decision
from jobs.models.enums import Country
from jobs.storage.query import JobQuery
from jobs.storage.rejection_log import RejectionLog
from jobs.storage.repository import JobRepository


@dataclass(frozen=True)
class IngestionSummary:
    processed: int
    approved: int
    rejected: int


class JobService:
    """Application service: runs ingestion, then answers queries.

    Holds no HTTP knowledge, which is what lets the query semantics be tested
    without a web layer and lets ingestion run from anywhere.
    """

    def __init__(
        self,
        pipeline: IngestionPipeline,
        repository: JobRepository,
        rejection_log: RejectionLog,
    ) -> None:
        self._pipeline = pipeline
        self._repository = repository
        self._rejection_log = rejection_log

    def ingest(self, records: Iterable[object]) -> IngestionSummary:
        decisions = self._pipeline.process(records)

        approved = [d.job for d in decisions if d.approved and d.job is not None]
        self._repository.add_all(approved)

        for decision in decisions:
            if not decision.approved:
                self._rejection_log.record(decision)

        return IngestionSummary(
            processed=len(decisions),
            approved=len(approved),
            rejected=len(decisions) - len(approved),
        )

    def search(self, query: JobQuery) -> Sequence[CanonicalJob]:
        return self._repository.search(query)

    def countries(self) -> Sequence[Country]:
        return self._repository.countries()

    def rejected(self) -> Sequence[Decision]:
        return self._rejection_log.entries()
