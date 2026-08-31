from collections.abc import Mapping
from typing import Any

from jobs.ingestion.adapters.base import LocationFields, SalaryFields, SourceAdapter, _as_str


class FlatAdapter(SourceAdapter):
    """Handles records where location is a comma-separated string and salary a number.

    The location split is deliberately naive - the brief explicitly says not to
    invest in location parsing. Anything that is not a recognized country name
    ends up classified as OTHER during normalization, which is the correct
    outcome for the approval criteria regardless of how the text was split.
    """

    def _extract_location(self, record: Mapping[str, Any]) -> LocationFields:
        text = _as_str(record.get("location"))
        if text is None:
            return LocationFields()

        parts = [part.strip() for part in text.split(",") if part.strip()]
        match parts:
            case []:
                return LocationFields(text=text)
            case [country]:
                return LocationFields(country=country, text=text)
            case [city, country]:
                return LocationFields(city=city, country=country, text=text)
            case [city, *middle, country]:
                return LocationFields(
                    city=city,
                    region=", ".join(middle),
                    country=country,
                    text=text,
                )
            case _:
                return LocationFields(text=text)

    def _extract_salary(self, record: Mapping[str, Any]) -> SalaryFields:
        value = record.get("salary")
        if not isinstance(value, (int, float, str)) or isinstance(value, bool):
            return SalaryFields()
        return SalaryFields(value=value)