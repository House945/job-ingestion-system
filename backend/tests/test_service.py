from jobs.config.defaults import build_pipeline
from jobs.ingestion.loader import load_feed
from jobs.service import JobService
from jobs.storage.query import JobQuery
from jobs.storage.rejection_log import RejectionLog
from jobs.storage.repository import InMemoryJobRepository
from tests.fixtures.expected_decisions import APPROVED_COUNT, EXPECTED


def _service() -> JobService:
    return JobService(build_pipeline(), InMemoryJobRepository(), RejectionLog(sinks=[]))


def test_ingestion_splits_approved_from_rejected(feed_path):
    service = _service()

    summary = service.ingest(load_feed(feed_path))

    assert summary.processed == len(EXPECTED)
    assert summary.approved == APPROVED_COUNT
    assert summary.rejected == len(EXPECTED) - APPROVED_COUNT


def test_only_approved_jobs_are_searchable(feed_path):
    service = _service()
    service.ingest(load_feed(feed_path))

    assert len(service.search(JobQuery())) == APPROVED_COUNT


def test_every_rejected_record_carries_reasons(feed_path):
    service = _service()
    service.ingest(load_feed(feed_path))

    assert all(decision.reasons for decision in service.rejected())