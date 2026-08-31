from decimal import Decimal

import pytest

from jobs.models.enums import Currency, SalaryUnit
from jobs.models.raw import RawJob
from jobs.normalization.salary import normalize_salary


def _raw(**kwargs) -> RawJob:
    return RawJob(source_index=0, **kwargs)


def test_explicit_fields_are_used_as_given():
    result = normalize_salary(_raw(salary_value=145000, salary_currency="USD"))

    assert result.value is not None
    assert result.value.amount == Decimal("145000")
    assert result.value.currency is Currency.USD


def test_hourly_unit_is_respected():
    result = normalize_salary(
        _raw(salary_value=65, salary_currency="USD", salary_unit="hourly")
    )

    assert result.value is not None
    assert result.value.unit is SalaryUnit.HOURLY
    assert not result.warnings


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (62.5, SalaryUnit.HOURLY),
        (45, SalaryUnit.HOURLY),
        (999, SalaryUnit.HOURLY),
        (1000, SalaryUnit.ANNUAL),
        (80000, SalaryUnit.ANNUAL),
    ],
)
def test_missing_unit_is_inferred_from_magnitude(value, expected):
    result = normalize_salary(_raw(salary_value=value))

    assert result.value is not None
    assert result.value.unit is expected


def test_inference_is_recorded_as_a_warning():
    """The record must carry the fact that its unit was guessed, not read."""
    result = normalize_salary(_raw(salary_value=62.5))

    assert any("inferred" in warning for warning in result.warnings)


def test_missing_currency_defaults_to_usd_and_warns():
    result = normalize_salary(_raw(salary_value=80000))

    assert result.value is not None
    assert result.value.currency is Currency.USD
    assert any("currency missing" in warning for warning in result.warnings)


def test_missing_salary_yields_none_without_warning():
    result = normalize_salary(_raw())

    assert result.value is None
    assert result.warnings == ()


def test_unparseable_salary_yields_none_with_warning():
    result = normalize_salary(_raw(salary_value="negotiable"))

    assert result.value is None
    assert result.warnings


def test_formatted_string_amount_is_recovered():
    """Defensive: not in the sample feed, but plausible from a scraper."""
    result = normalize_salary(_raw(salary_value="$145,000"))

    assert result.value is not None
    assert result.value.amount == Decimal("145000")


def test_float_amount_does_not_carry_binary_artifacts():
    result = normalize_salary(_raw(salary_value=62.5))

    assert result.value is not None
    assert result.value.amount == Decimal("62.5")