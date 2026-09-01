from collections.abc import Callable, Iterable
from datetime import date
from decimal import Decimal

import pytest

from jobs.models.canonical import CanonicalJob, Location
from jobs.models.enums import Country
from jobs.storage.query import JobQuery, SortField, SortOrder
from jobs.storage.repository import InMemoryJobRepository


@pytest.fixture
def repository(make_job: Callable[..., CanonicalJob]) -> InMemoryJobRepository:
    repo = InMemoryJobRepository()
    repo.add_all(
        [
            make_job(
                title="Backend Engineer",
                location=Location(country=Country.UNITED_STATES, raw_country="USA"),
                comparable_annual_usd=Decimal("145000"),
                posting_date=date(2023, 10, 3),
            ),
            make_job(
                title="Senior Backend Developer",
                location=Location(country=Country.CANADA, raw_country="Canada"),
                comparable_annual_usd=Decimal("110000"),
                posting_date=date(2023, 10, 23),
            ),
            make_job(
                title="Data Scientist",
                location=Location(country=Country.CANADA, raw_country="Canada"),
                comparable_annual_usd=Decimal("130000"),
                posting_date=date(2023, 10, 10),
            ),
            make_job(
                title="Growth Marketing Manager",
                location=Location(country=Country.UNITED_STATES, raw_country="USA"),
                comparable_annual_usd=Decimal("125000"),
                posting_date=None,
            ),
        ]
    )
    return repo


def _titles(jobs: Iterable[CanonicalJob]) -> list[str]:
    return [job.title for job in jobs]


class TestSearch:
    def test_empty_query_returns_everything(self, repository):
        assert len(repository.search(JobQuery())) == 4

    def test_search_is_case_insensitive(self, repository):
        results = repository.search(JobQuery(search="BACKEND"))

        assert len(results) == 2

    def test_search_matches_partial_words(self, repository):
        results = repository.search(JobQuery(search="scien"))

        assert _titles(results) == ["Data Scientist"]

    def test_search_ignores_surrounding_whitespace(self, repository):
        assert len(repository.search(JobQuery(search="  backend  "))) == 2

    def test_search_with_no_matches_returns_empty(self, repository):
        assert repository.search(JobQuery(search="plumber")) == []


class TestFilter:
    def test_filter_by_country(self, repository):
        results = repository.search(JobQuery(country=Country.CANADA))

        assert len(results) == 2

    def test_filter_combines_with_search(self, repository):
        results = repository.search(JobQuery(search="backend", country=Country.CANADA))

        assert _titles(results) == ["Senior Backend Developer"]

    def test_countries_come_from_stored_data(self, repository):
        assert set(repository.countries()) == {Country.UNITED_STATES, Country.CANADA}


class TestSort:
    def test_salary_descending(self, repository):
        results = repository.search(
            JobQuery(sort_by=SortField.SALARY, order=SortOrder.DESC)
        )

        assert _titles(results)[0] == "Backend Engineer"

    def test_salary_ascending(self, repository):
        results = repository.search(JobQuery(sort_by=SortField.SALARY, order=SortOrder.ASC))

        assert _titles(results)[0] == "Senior Backend Developer"

    def test_date_descending(self, repository):
        results = repository.search(
            JobQuery(sort_by=SortField.POSTING_DATE, order=SortOrder.DESC)
        )

        assert _titles(results)[0] == "Senior Backend Developer"

    @pytest.mark.parametrize("order", [SortOrder.ASC, SortOrder.DESC])
    def test_missing_date_sorts_last_in_both_directions(self, repository, order):
        """Toggling direction must never surface a block of blanks at the top."""
        results = repository.search(JobQuery(sort_by=SortField.POSTING_DATE, order=order))

        assert _titles(results)[-1] == "Growth Marketing Manager"