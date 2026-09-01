from decimal import Decimal, InvalidOperation

from jobs.config.parsing import DEFAULT_CURRENCY, HOURLY_INFERENCE_CEILING
from jobs.models.canonical import Salary
from jobs.models.enums import Currency, SalaryUnit
from jobs.models.raw import RawJob
from jobs.normalization.result import Normalized


def normalize_salary(raw: RawJob) -> Normalized[Salary | None]:
    """Build a salary with an explicit unit and currency, guessing where needed.

    Every guess is recorded. A salary that cannot be parsed at all yields None,
    which the salary rule then rejects with a reason - normalization does not
    decide whether a posting qualifies.
    """
    warnings: list[str] = []

    amount = _to_decimal(raw.salary_value)
    if amount is None:
        if raw.salary_value is not None:
            warnings.append(f"salary value could not be parsed: {raw.salary_value!r}")
        return Normalized(None, tuple(warnings))

    currency = _resolve_currency(raw.salary_currency, warnings)
    unit = _resolve_unit(raw.salary_unit, amount, warnings)

    return Normalized(Salary(amount=amount, currency=currency, unit=unit), tuple(warnings))


def _to_decimal(value: float | str | None) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.replace(",", "").replace("$", "").strip()
        if not cleaned:
            return None
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            return None
    if isinstance(value, float) and value.is_integer():
        return Decimal(int(value))
    return Decimal(str(value))


def _resolve_currency(raw_currency: str | None, warnings: list[str]) -> Currency:
    if raw_currency is None:
        warnings.append(f"currency missing; defaulted to {DEFAULT_CURRENCY.name}")
        return DEFAULT_CURRENCY

    currency = Currency(raw_currency)
    if currency is Currency.UNKNOWN:
        warnings.append(f"currency not recognized: {raw_currency}")
    return currency


def _resolve_unit(raw_unit: str | None, amount: Decimal, warnings: list[str]) -> SalaryUnit:
    if raw_unit is not None:
        unit = SalaryUnit(raw_unit)
        if unit is SalaryUnit.UNKNOWN:
            warnings.append(f"salary unit not recognized: {raw_unit}")
        return unit

    inferred = SalaryUnit.HOURLY if amount < HOURLY_INFERENCE_CEILING else SalaryUnit.ANNUAL
    warnings.append(f"salary unit missing; inferred {inferred.value} from magnitude")
    return inferred
