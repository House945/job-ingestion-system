from decimal import Decimal

from jobs.models.enums import CompanyType, Country, EmploymentType, Language, SalaryUnit
from jobs.models.raw import RawJob
from jobs.normalization.currency import StaticRateConverter
from jobs.normalization.normalizer import JobNormalizer


def _normalizer() -> JobNormalizer:
    return JobNormalizer(StaticRateConverter())


def test_full_record_normalizes():
    raw = RawJob(
        source_index=0,
        title="  Backend Engineer  ",
        description="Build APIs.",
        company="NextGen Systems",
        city="Austin",
        region="TX",
        country="USA",
        salary_value=145000,
        salary_currency="USD",
        employment_type="Full-Time",
        posting_date="2023-10-03",
        company_type="Direct Employer",
        language="English",
        remote=False,
    )

    job = _normalizer().normalize(raw)

    assert job.title == "Backend Engineer"
    assert job.location.country is Country.UNITED_STATES
    assert job.employment_type is EmploymentType.FULL_TIME
    assert job.company_type is CompanyType.DIRECT_EMPLOYER
    assert job.language is Language.ENGLISH
    assert job.posting_date is not None


def test_empty_record_normalizes_without_raising():
    """A record with nothing in it must still produce a job for the rules to reject."""
    job = _normalizer().normalize(RawJob(source_index=0))

    assert job.title == ""
    assert job.salary is None
    assert job.employment_type is EmploymentType.UNKNOWN
    assert job.posting_date is None


def test_hourly_rate_gets_a_comparable_annual_figure():
    raw = RawJob(source_index=0, salary_value=65, salary_currency="USD", salary_unit="hourly")

    job = _normalizer().normalize(raw)

    assert job.salary is not None
    assert job.salary.unit is SalaryUnit.HOURLY
    assert job.salary.amount == Decimal("65")
    assert job.comparable_annual_usd == Decimal("135200")


def test_comparable_figure_is_converted_to_usd():
    raw = RawJob(source_index=0, salary_value=85000, salary_currency="GBP")

    job = _normalizer().normalize(raw)

    assert job.comparable_annual_usd is not None
    assert job.comparable_annual_usd > Decimal("100000")


def test_warnings_are_collected_from_every_parser():
    raw = RawJob(source_index=0, salary_value=62.5, country="Germany", posting_date="not-a-date")

    job = _normalizer().normalize(raw)

    assert len(job.warnings) >= 3


def test_missing_currency_rate_leaves_comparable_figure_empty():
    raw = RawJob(source_index=0, salary_value=1000, salary_currency="JPY")

    job = _normalizer().normalize(raw)

    assert job.comparable_annual_usd is None
