from collections.abc import Mapping
from typing import Any

from jobs.ingestion.adapters.base import LocationFields, SalaryFields, SourceAdapter, _as_str


class StructuredAdapter(SourceAdapter):
    """Handles records where location and salary are nested objects."""

    def _extract_location(self, record: Mapping[str, Any]) -> LocationFields:
        location = record.get("location")
        if not isinstance(location, Mapping):
            return LocationFields()

        city = _as_str(location.get("city"))
        region = _as_str(location.get("region") or location.get("state"))
        country = _as_str(location.get("country"))
        parts = [part for part in (city, region, country) if part]
        return LocationFields(
            city=city,
            region=region,
            country=country,
            text=", ".join(parts) or None,
        )

    def _extract_salary(self, record: Mapping[str, Any]) -> SalaryFields:
        salary = record.get("salary")
        if not isinstance(salary, Mapping):
            return SalaryFields()

        value = salary.get("value")
        return SalaryFields(
            value=value if isinstance(value, (int, float, str)) else None,
            currency=_as_str(salary.get("currency")),
            unit=_as_str(salary.get("unit")),
        )
