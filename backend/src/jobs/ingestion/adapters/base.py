from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from jobs.models.raw import RawJob


@dataclass(frozen=True)
class LocationFields:
    """Location as extracted from a feed record, before any interpretation."""

    city: str | None = None
    region: str | None = None
    country: str | None = None
    text: str | None = None


@dataclass(frozen=True)
class SalaryFields:
    """Salary as extracted from a feed record, before any interpretation."""

    value: float | str | None = None
    currency: str | None = None
    unit: str | None = None


class SourceAdapter(ABC):
    """Turns one feed record into a RawJob.

    Adapters unify shape, not meaning. They decide which key holds the city;
    they do not decide whether a country counts as North America, or whether
    a bare number is an hourly rate. That is normalization's job.

    Fields common to both layouts are extracted once here, so the two adapters
    cannot drift apart on anything except the two polymorphic fields.
    """

    def to_raw_job(self, index: int, record: Mapping[str, Any]) -> RawJob:
        location = self._extract_location(record)
        salary = self._extract_salary(record)
        return RawJob(
            source_index=index,
            title=_as_str(record.get("title")),
            description=_as_str(record.get("description")),
            company=_as_str(record.get("company")),
            city=location.city,
            region=location.region,
            country=location.country,
            location_text=location.text,
            salary_value=salary.value,
            salary_currency=salary.currency,
            salary_unit=salary.unit,
            employment_type=_as_str(record.get("employment_type")),
            posting_date=_as_str(record.get("posting_date")),
            company_type=_as_str(record.get("company_type")),
            language=_as_str(record.get("language")),
            remote=_as_bool(record.get("remote")),
            original=dict(record),
        )

    @abstractmethod
    def _extract_location(self, record: Mapping[str, Any]) -> LocationFields: ...

    @abstractmethod
    def _extract_salary(self, record: Mapping[str, Any]) -> SalaryFields: ...


def _as_str(value: object) -> str | None:
    """Coerce a feed value to a string, collapsing blanks to None."""
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return str(value)


def _as_bool(value: object) -> bool | None:
    return value if isinstance(value, bool) else None