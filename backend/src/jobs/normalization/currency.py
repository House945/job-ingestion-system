from collections.abc import Mapping
from decimal import Decimal
from typing import Protocol

from jobs.models.enums import Currency


class CurrencyConverter(Protocol):
    """Converts an amount into USD.

    Returns None when no rate is available, rather than raising: an unknown
    rate is a normal condition for scraped data, not an exceptional one.
    """

    def to_usd(self, amount: Decimal, currency: Currency) -> Decimal | None: ...


class StaticRateConverter:
    """Converter backed by hard-coded rates.

    Mocked deliberately and named for what it is. In production this would call
    a rate service; the protocol above is the seam where that implementation
    attaches, and nothing upstream would change.
    """

    def __init__(self, rates: Mapping[Currency, Decimal] | None = None) -> None:
        self._rates: Mapping[Currency, Decimal] = rates or {
            Currency.USD: Decimal("1.00"),
            Currency.CAD: Decimal("0.74"),
            Currency.GBP: Decimal("1.27"),
            Currency.EUR: Decimal("1.08"),
        }

    def to_usd(self, amount: Decimal, currency: Currency) -> Decimal | None:
        rate = self._rates.get(currency)
        if rate is None:
            return None
        return amount * rate
