from decimal import Decimal

import pytest

from jobs.approval.policy import MarketPolicy
from jobs.approval.rules.company import CompanyTypeRule
from jobs.approval.rules.employment import EmploymentTypeRule
from jobs.approval.rules.geography import GeographyRule
from jobs.approval.rules.language import LanguageRule
from jobs.approval.rules.salary import SalaryRule
from jobs.approval.rules.title import TitleRule
from jobs.models.canonical import Location, Salary
from jobs.models.enums import (
    CompanyType,
    Country,
    Currency,
    EmploymentType,
    Language,
    RejectionCode,
    SalaryUnit,
)
from jobs.normalization.currency import StaticRateConverter


def _salary(
    amount: str,
    currency: Currency = Currency.USD,
    unit: SalaryUnit = SalaryUnit.ANNUAL,
) -> Salary:
    return Salary(amount=Decimal(amount), currency=currency, unit=unit)


class TestTitleRule:
    def test_passes_with_a_title(self, make_job):
        assert TitleRule().evaluate(make_job()) is None

    @pytest.mark.parametrize("title", ["", "   "])
    def test_rejects_blank_title(self, make_job, title):
        reason = TitleRule().evaluate(make_job(title=title.strip()))

        assert reason is not None
        assert reason.code is RejectionCode.TITLE


class TestGeographyRule:
    @pytest.fixture
    def rule(self) -> GeographyRule:
        return GeographyRule(MarketPolicy())

    @pytest.mark.parametrize(
        "country", [Country.UNITED_STATES, Country.CANADA]
    )
    def test_accepts_north_america_in_person(self, rule, make_job, country):
        job = make_job(location=Location(country=country), is_remote=False)

        assert rule.evaluate(job) is None

    def test_accepts_remote_with_no_identifiable_location(self, rule, make_job):
        job = make_job(location=Location(country=Country.UNKNOWN), is_remote=True)

        assert rule.evaluate(job) is None

    def test_rejects_remote_tied_to_a_foreign_market(self, rule, make_job):
        """The decisive interpretation: remote UK is the UK market, not anywhere."""
        job = make_job(
            location=Location(country=Country.OTHER, raw_country="UK"), is_remote=True
        )

        reason = rule.evaluate(job)

        assert reason is not None
        assert reason.code is RejectionCode.GEO

    def test_rejects_in_person_abroad(self, rule, make_job):
        job = make_job(
            location=Location(country=Country.OTHER, raw_country="Germany"), is_remote=False
        )

        assert rule.evaluate(job) is not None

    def test_rejects_unknown_location_when_not_remote(self, rule, make_job):
        job = make_job(location=Location(country=Country.UNKNOWN), is_remote=False)

        assert rule.evaluate(job) is not None


class TestEmploymentTypeRule:
    def test_accepts_full_time(self, make_job):
        assert EmploymentTypeRule().evaluate(make_job()) is None

    @pytest.mark.parametrize(
        "employment_type",
        [
            EmploymentType.PART_TIME,
            EmploymentType.CONTRACT,
            EmploymentType.INTERNSHIP,
            EmploymentType.UNKNOWN,
        ],
    )
    def test_rejects_everything_else(self, make_job, employment_type):
        reason = EmploymentTypeRule().evaluate(make_job(employment_type=employment_type))

        assert reason is not None
        assert reason.code is RejectionCode.EMPLOYMENT


class TestCompanyTypeRule:
    def test_rejects_staffing_firm(self, make_job):
        reason = CompanyTypeRule().evaluate(make_job(company_type=CompanyType.STAFFING_FIRM))

        assert reason is not None
        assert reason.code is RejectionCode.STAFFING

    @pytest.mark.parametrize(
        "company_type",
        [CompanyType.DIRECT_EMPLOYER, CompanyType.CONSULTING_AGENCY, CompanyType.UNKNOWN],
    )
    def test_accepts_other_company_types(self, make_job, company_type):
        """Consulting agencies are not staffing firms - read literally."""
        assert CompanyTypeRule().evaluate(make_job(company_type=company_type)) is None


class TestLanguageRule:
    def test_accepts_english_anywhere(self, make_job):
        assert LanguageRule().evaluate(make_job(language=Language.ENGLISH)) is None

    def test_accepts_french_in_canada(self, make_job):
        job = make_job(language=Language.FRENCH, location=Location(country=Country.CANADA))

        assert LanguageRule().evaluate(job) is None

    def test_rejects_french_outside_canada(self, make_job):
        job = make_job(
            language=Language.FRENCH, location=Location(country=Country.UNITED_STATES)
        )

        reason = LanguageRule().evaluate(job)

        assert reason is not None
        assert reason.code is RejectionCode.LANGUAGE

    @pytest.mark.parametrize("language", [Language.GERMAN, Language.UNKNOWN])
    def test_rejects_other_languages(self, make_job, language):
        assert LanguageRule().evaluate(make_job(language=language)) is not None


class TestSalaryRule:
    @pytest.fixture
    def rule(self) -> SalaryRule:
        return SalaryRule(MarketPolicy(), StaticRateConverter())

    def test_accepts_annual_above_threshold(self, rule, make_job):
        assert rule.evaluate(make_job(salary=_salary("100001"))) is None

    def test_rejects_annual_at_threshold(self, rule, make_job):
        """'over $100,000' is read as strictly greater."""
        assert rule.evaluate(make_job(salary=_salary("100000"))) is not None

    def test_accepts_hourly_above_threshold(self, rule, make_job):
        job = make_job(salary=_salary("46", unit=SalaryUnit.HOURLY))

        assert rule.evaluate(job) is None

    def test_hourly_threshold_is_not_derived_from_the_annual_one(self, rule, make_job):
        """46/hour is 95,680 a year - below the annual threshold, yet it qualifies."""
        job = make_job(salary=_salary("46", unit=SalaryUnit.HOURLY))

        assert rule.evaluate(job) is None

    def test_rejects_hourly_at_threshold(self, rule, make_job):
        assert rule.evaluate(make_job(salary=_salary("45", unit=SalaryUnit.HOURLY))) is not None

    def test_converts_before_comparing(self, rule, make_job):
        """85,000 GBP is roughly 108k USD and clears the threshold."""
        job = make_job(salary=_salary("85000", currency=Currency.GBP))

        assert rule.evaluate(job) is None

    def test_rejects_missing_salary(self, rule, make_job):
        reason = rule.evaluate(make_job(salary=None))

        assert reason is not None
        assert reason.code is RejectionCode.SALARY

    def test_rejects_unknown_unit(self, rule, make_job):
        job = make_job(salary=_salary("50", unit=SalaryUnit.UNKNOWN))

        assert rule.evaluate(job) is not None

    def test_rejects_unconvertible_currency(self, rule, make_job):
        job = make_job(salary=_salary("500000", currency=Currency.UNKNOWN))

        assert rule.evaluate(job) is not None