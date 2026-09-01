from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from jobs.api.dependencies import get_service
from jobs.api.schemas import COUNTRY_LABELS, CountryOut, JobOut, RejectedJobOut
from jobs.models.enums import Country
from jobs.service import JobService
from jobs.storage.query import JobQuery, SortField, SortOrder

router = APIRouter()


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(
    service: Annotated[JobService, Depends(get_service)],
    search: Annotated[str | None, Query(description="Case-insensitive title match")] = None,
    country: Annotated[str | None, Query()] = None,
    sort_by: Annotated[SortField | None, Query()] = None,
    order: Annotated[SortOrder, Query()] = SortOrder.DESC,
) -> list[JobOut]:
    query = JobQuery(
        search=search,
        country=_parse_country(country),
        sort_by=sort_by,
        order=order,
    )
    return [JobOut.from_job(job) for job in service.search(query)]


def _parse_country(value: str | None) -> Country | None:
    """Reject unknown country values instead of silently coercing them.

    The enum degrades to UNKNOWN by design, because scraped feed data must not
    abort a batch. A query parameter is not scraped data: a typo here is a
    client error and should say so rather than return an empty list.
    """
    if value is None:
        return None

    country = Country(value)
    if country is Country.UNKNOWN and value.casefold() != Country.UNKNOWN.value:
        raise HTTPException(status_code=422, detail=f"unknown country: {value}")
    return country


@router.get("/jobs/rejected", response_model=list[RejectedJobOut])
def list_rejected_jobs(
    service: Annotated[JobService, Depends(get_service)],
) -> list[RejectedJobOut]:
    """Rejected postings with their reasons.

    Exposes what the rejection log already recorded. The log remains the
    contract; this endpoint just makes it readable.
    """
    return [RejectedJobOut.from_decision(decision) for decision in service.rejected()]


@router.get("/countries", response_model=list[CountryOut])
def list_countries(
    service: Annotated[JobService, Depends(get_service)],
) -> list[CountryOut]:
    """Countries present in approved postings - derived from data, not hard-coded."""
    return [
        CountryOut(value=country.value, label=COUNTRY_LABELS.get(country, "Unknown"))
        for country in service.countries()
    ]