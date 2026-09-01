import pytest
from fastapi.testclient import TestClient

from jobs.api.main import create_app
from jobs.config.defaults import build_pipeline
from jobs.ingestion.loader import load_feed
from jobs.service import JobService
from jobs.storage.rejection_log import RejectionLog
from jobs.storage.repository import InMemoryJobRepository
from tests.fixtures.expected_decisions import APPROVED_COUNT, EXPECTED


@pytest.fixture
def client(feed_path):
    service = JobService(build_pipeline(), InMemoryJobRepository(), RejectionLog(sinks=[]))
    service.ingest(load_feed(feed_path))

    with TestClient(create_app(service=service)) as test_client:
        yield test_client


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_lists_approved_jobs(client):
    body = client.get("/jobs").json()

    assert len(body) == APPROVED_COUNT


def test_search_by_title(client):
    body = client.get("/jobs", params={"search": "engineer"}).json()

    assert body
    assert all("engineer" in job["title"].casefold() for job in body)


def test_search_with_no_matches_returns_empty_list(client):
    assert client.get("/jobs", params={"search": "zzzz"}).json() == []


def test_filter_by_country(client):
    body = client.get("/jobs", params={"country": "canada"}).json()

    assert body
    assert all(job["country"] == "canada" for job in body)


def test_invalid_country_is_rejected(client):
    assert client.get("/jobs", params={"country": "atlantis"}).status_code == 422


def test_sort_by_salary_descending(client):
    body = client.get(
        "/jobs", params={"sort_by": "salary", "order": "desc"}
    ).json()
    figures = [job["comparable_annual_usd"] for job in body]

    assert figures == sorted(figures, reverse=True)


def test_sort_by_date_puts_missing_last(client):
    body = client.get("/jobs", params={"sort_by": "posting_date", "order": "asc"}).json()

    assert body[-1]["posting_date"] is None


def test_hourly_posting_keeps_its_unit(client):
    """An hourly rate must not be presented as an annual salary."""
    body = client.get("/jobs").json()
    hourly = [job for job in body if job["salary"] and job["salary"]["unit"] == "hourly"]

    assert hourly
    assert hourly[0]["salary"]["amount"] < 1000


def test_rejected_endpoint_lists_reasons(client):
    body = client.get("/jobs/rejected").json()

    assert len(body) == len(EXPECTED) - APPROVED_COUNT
    assert all(job["reasons"] for job in body)


def test_rejected_posting_without_a_title_is_returned(client):
    body = client.get("/jobs/rejected").json()
    untitled = [job for job in body if job["title"] is None]

    assert untitled
    assert any(reason["code"] == "TITLE" for reason in untitled[0]["reasons"])


def test_countries_are_derived_from_data(client):
    body = client.get("/countries").json()
    values = {country["value"] for country in body}

    assert values == {"united_states", "canada"}


def test_startup_ingests_the_configured_feed(feed_path, monkeypatch):
    """Without an injected service, the app ingests from JOBS_FEED_PATH."""
    monkeypatch.setenv("JOBS_FEED_PATH", str(feed_path))

    with TestClient(create_app()) as test_client:
        assert len(test_client.get("/jobs").json()) == APPROVED_COUNT