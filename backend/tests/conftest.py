from collections.abc import Callable
from decimal import Decimal
from pathlib import Path

import pytest

from jobs.models.canonical import CanonicalJob, Location, Salary
from jobs.models.enums import (
    CompanyType,
    Country,
    Currency,
    EmploymentType,
    Language,
    SalaryUnit,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def feed_path() -> Path:
    return REPO_ROOT / "data" / "jobs.json"


@pytest.fixture
def make_job() -> Callable[..., CanonicalJob]:
    """Build a job that passes every rule, so each test can break exactly one thing."""

    def _make(**overrides: object) -> CanonicalJob:
        defaults: dict[str, object] = {
            "source_index": 0,
            "title": "Backend Engineer",
            "description": "Build APIs.",
            "company": "NextGen Systems",
            "location": Location(country=Country.UNITED_STATES, raw_country="USA", city="Austin"),
            "is_remote": False,
            "employment_type": EmploymentType.FULL_TIME,
            "company_type": CompanyType.DIRECT_EMPLOYER,
            "language": Language.ENGLISH,
            "salary": Salary(
                amount=Decimal("145000"), currency=Currency.USD, unit=SalaryUnit.ANNUAL
            ),
            "posting_date": None,
            "comparable_annual_usd": Decimal("145000"),
        }
        return CanonicalJob(**{**defaults, **overrides})

    return _make
