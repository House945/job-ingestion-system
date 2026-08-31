from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from jobs.models.enums import (
    CompanyType,
    Country,
    Currency,
    EmploymentType,
    Language,
    SalaryUnit,
)


class Location(BaseModel):
    model_config = ConfigDict(frozen=True)

    country: Country
    raw_country: str | None = None
    city: str | None = None
    region: str | None = None


class Salary(BaseModel):
    """Salary with an explicit unit and currency.

    The unit is NOT normalized to annual, because the task criteria specify
    two non-equivalent thresholds: 100,000 USD/year AND 45 USD/h. 45 * 2080h
    is 93,600, so converting hourly to annual would yield different verdicts.
    The salary rule branches on the unit.
    """

    model_config = ConfigDict(frozen=True)

    amount: Decimal
    currency: Currency
    unit: SalaryUnit


class CanonicalJob(BaseModel):
    """An offer ready to be evaluated by the rules.

    'Canonical' means 'parsable', not 'meets the criteria'.
    Therefore, title can be empty and salary can be None—these are cases
    that should be rejected by RULES with a specific reason, rather than a validation exception.
    Fields that were guessed rather than read are recorded in `warnings`. The
    distinction between what the feed stated and what we inferred survives all
    the way to the UI, which matters when the input is scraped.
    """

    model_config = ConfigDict(frozen=True)

    source_index: int
    title: str
    description: str
    company: str
    location: Location
    is_remote: bool
    employment_type: EmploymentType
    company_type: CompanyType
    language: Language
    salary: Salary | None
    posting_date: date | None
    comparable_annual_usd: Decimal | None
    warnings: tuple[str, ...] = ()