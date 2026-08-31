from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RawJob(BaseModel):
    """An offer as received from the feed—after standardizing the structure, before
    normalizing the values.

    Every field is optional because the scraper might have found nothing. Source
    adapters produce this exact type, regardless of whether the feed had
    'location' as an object or as a string.
    """

    model_config = ConfigDict(frozen=True)

    source_index: int
    title: str | None = None
    description: str | None = None
    company: str | None = None
    city: str | None = None
    region: str | None = None
    country: str | None = None
    location_text: str | None = None
    salary_value: float | str | None = None
    salary_currency: str | None = None
    salary_unit: str | None = None
    employment_type: str | None = None
    posting_date: str | None = None
    company_type: str | None = None
    language: str | None = None
    remote: bool | None = None
    original: dict[str, Any] = Field(default_factory=dict)