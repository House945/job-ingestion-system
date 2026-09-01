from decimal import Decimal

from jobs.models.enums import Currency
from jobs.normalization.currency import StaticRateConverter


def test_usd_is_unchanged():
    assert StaticRateConverter().to_usd(Decimal("100000"), Currency.USD) == Decimal("100000.00")


def test_gbp_salary_clears_the_annual_threshold():
    """The UK posting is the acceptance test for conversion actually running."""
    converted = StaticRateConverter().to_usd(Decimal("85000"), Currency.GBP)

    assert converted is not None
    assert converted > Decimal("100000")


def test_unknown_currency_yields_none():
    assert StaticRateConverter().to_usd(Decimal("100"), Currency.UNKNOWN) is None


def test_rates_are_injectable():
    converter = StaticRateConverter(rates={Currency.EUR: Decimal("2")})

    assert converter.to_usd(Decimal("10"), Currency.EUR) == Decimal("20")
