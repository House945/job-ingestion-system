from collections.abc import Callable, Iterable, Sequence
from datetime import date
from decimal import Decimal
from typing import Protocol

from jobs.models.canonical import CanonicalJob
from jobs.models.enums import Country
from jobs.storage.query import JobQuery, SortField, SortOrder


class JobRepository(Protocol):
    """Storage for approved postings.

    Query operations live here rather than in the HTTP layer, so that swapping
    the implementation for a database-backed one changes nothing above it. In
    that implementation these methods become SQL; the callers do not move.
    """

    def add_all(self, jobs: Iterable[CanonicalJob]) -> None: ...

    def search(self, query: JobQuery) -> Sequence[CanonicalJob]: ...

    def countries(self) -> Sequence[Country]: ...

    def count(self) -> int: ...


class InMemoryJobRepository:
    """Repository backed by a list.

    Adequate because the feed is static and processing is deterministic: a
    restart re-ingests the same file and reproduces the same state.
    """

    def __init__(self) -> None:
        self._jobs: list[CanonicalJob] = []

    def add_all(self, jobs: Iterable[CanonicalJob]) -> None:
        self._jobs.extend(jobs)

    def count(self) -> int:
        return len(self._jobs)

    def countries(self) -> Sequence[Country]:
        """Countries actually present in stored postings, not a hard-coded list."""
        seen = {job.location.country for job in self._jobs}
        return sorted(seen, key=lambda country: country.value)

    def search(self, query: JobQuery) -> Sequence[CanonicalJob]:
        results = list(self._jobs)

        if query.search:
            needle = query.search.strip().casefold()
            results = [job for job in results if needle in job.title.casefold()]

        if query.country is not None:
            results = [job for job in results if job.location.country is query.country]

        if query.sort_by is not None:
            results = _sorted(results, query.sort_by, query.order)

        return results



def _sorted(
    jobs: list[CanonicalJob], field: SortField, order: SortOrder
) -> list[CanonicalJob]:
    key: Callable[[CanonicalJob], Decimal | date | None]
    match field:
        case SortField.SALARY:
            key = _salary_key
        case SortField.POSTING_DATE:
            key = _date_key

    present = [job for job in jobs if key(job) is not None]
    missing = [job for job in jobs if key(job) is None]

    present.sort(key=lambda job: key(job), reverse=order is SortOrder.DESC)  # type: ignore[arg-type, return-value]
    return present + missing


def _salary_key(job: CanonicalJob) -> Decimal | None:
    """Sort by the comparable annual figure, never by the raw amount.

    The list mixes annual salaries and hourly rates. Ordering by raw amount
    would put every hourly posting below every annual one regardless of what
    they are actually worth - see DECISIONS.md, section 5.
    """
    return job.comparable_annual_usd


def _date_key(job: CanonicalJob) -> date | None:
    return job.posting_date