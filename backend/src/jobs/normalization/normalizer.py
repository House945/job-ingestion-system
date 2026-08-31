from decimal import Decimal

from jobs.config.parsing import ANNUAL_BILLABLE_HOURS
from jobs.models.canonical import CanonicalJob, Salary
from jobs.models.enums import CompanyType, EmploymentType, Language, SalaryUnit
from jobs.models.raw import RawJob
from jobs.normalization.currency import CurrencyConverter
from jobs.normalization.dates import parse_posting_date
from jobs.normalization.location import normalize_location
from jobs.normalization.salary import normalize_salary


class JobNormalizer:
    """Turns a RawJob into a CanonicalJob.

    This is the single boundary between "whatever the feed said" and "something
    the rules can evaluate". Nothing downstream deals with missing structure.
    """

    def __init__(self, converter: CurrencyConverter) -> None:
        self._converter = converter

    def normalize(self, raw: RawJob) -> CanonicalJob:
        warnings: list[str] = []

        location = normalize_location(raw)
        warnings.extend(location.warnings)

        salary = normalize_salary(raw)
        warnings.extend(salary.warnings)

        posting_date = parse_posting_date(raw.posting_date)
        warnings.extend(posting_date.warnings)

        return CanonicalJob(
            source_index=raw.source_index,
            title=(raw.title or "").strip(),
            description=(raw.description or "").strip(),
            company=(raw.company or "").strip(),
            location=location.value,
            is_remote=bool(raw.remote),
            employment_type=EmploymentType(raw.employment_type or ""),
            company_type=CompanyType(raw.company_type or ""),
            language=Language(raw.language or ""),
            salary=salary.value,
            posting_date=posting_date.value,
            comparable_annual_usd=self._comparable_annual_usd(salary.value),
            warnings=tuple(warnings),
        )

    def _comparable_annual_usd(self, salary: Salary | None) -> Decimal | None:
        """Produce a single figure usable for sorting a mixed list.

        Used ONLY for ordering. The salary rule never reads this value - see
        DECISIONS.md, sections 4 and 5.
        """
        if salary is None:
            return None

        in_usd = self._converter.to_usd(salary.amount, salary.currency)
        if in_usd is None:
            return None

        match salary.unit:
            case SalaryUnit.ANNUAL:
                return in_usd
            case SalaryUnit.HOURLY:
                return in_usd * ANNUAL_BILLABLE_HOURS
            case _:
                return None