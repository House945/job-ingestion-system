from decimal import Decimal

import pytest
from pydantic import ValidationError

from jobs.models.canonical import CanonicalJob, Location, Salary
from jobs.models.decision import Decision, RejectionReason
from jobs.models.enums import (
    CompanyType,
    Country,
    Currency,
    EmploymentType,
    Language,
    RejectionCode,
    SalaryUnit,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Full-Time", EmploymentType.FULL_TIME),
        ("full time", EmploymentType.FULL_TIME),
        ("FULL_TIME", EmploymentType.FULL_TIME),
        ("  Internship  ", EmploymentType.INTERNSHIP),
        ("Freelance", EmploymentType.UNKNOWN),
        ("", EmploymentType.UNKNOWN),
    ],
)
def test_employment_type_normalizes_feed_variants(raw, expected):
    assert EmploymentType(raw) is expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Staffing Firm", CompanyType.STAFFING_FIRM),
        ("Direct Employer", CompanyType.DIRECT_EMPLOYER),
        ("Consulting Agency", CompanyType.CONSULTING_AGENCY),
        ("Recruitment Partner", CompanyType.UNKNOWN),
    ],
)
def test_company_type_normalizes_feed_variants(raw, expected):
    assert CompanyType(raw) is expected


def test_unknown_language_does_not_raise():
    assert Language("Valyrian") is Language.UNKNOWN


def test_canonical_job_allows_empty_title():
    """An empty title should be rejected by a rule, not by model validation."""
    job = _build_job(title="")

    assert job.title == ""


def test_canonical_job_is_immutable():
    job = _build_job()

    with pytest.raises(ValidationError):
        job.title = "changed"  # type: ignore[misc]


def test_decision_without_reasons_is_approved():
    decision = Decision(source_index=0, job=_build_job(), raw=None)

    assert decision.approved is True
    assert decision.codes == frozenset()


def test_decision_with_reasons_is_rejected():
    decision = Decision(
        source_index=0,
        job=_build_job(),
        raw=None,
        reasons=(
            RejectionReason(code=RejectionCode.SALARY, message="below treshold"),
            RejectionReason(code=RejectionCode.GEO, message="outside US/CA"),
        ),
    )

    assert decision.approved is False
    assert decision.codes == {RejectionCode.SALARY, RejectionCode.GEO}


def _build_job(title: str = "Backend Engineer") -> CanonicalJob:
    return CanonicalJob(
        source_index=0,
        title=title,
        description="Description",
        company="NextGen Systems",
        location=Location(country=Country.UNITED_STATES, city="Austin", region="TX"),
        is_remote=False,
        employment_type=EmploymentType.FULL_TIME,
        company_type=CompanyType.DIRECT_EMPLOYER,
        language=Language.ENGLISH,
        salary=Salary(
            amount=Decimal("145000"), currency=Currency.USD, unit=SalaryUnit.ANNUAL
        ),
        posting_date=None,
        comparable_annual_usd=Decimal("145000"),
    )