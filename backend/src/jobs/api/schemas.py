from datetime import date

from pydantic import BaseModel

from jobs.models.canonical import CanonicalJob
from jobs.models.decision import Decision
from jobs.models.enums import Country

COUNTRY_LABELS: dict[Country, str] = {
    Country.UNITED_STATES: "United States",
    Country.CANADA: "Canada",
    Country.OTHER: "Other",
    Country.UNKNOWN: "Remote / unspecified",
}


class SalaryOut(BaseModel):
    """Salary as the UI needs it: an amount, a currency and an explicit unit.

    Amounts cross the wire as JSON numbers. Decimal is used for every
    computation; these magnitudes are exact in IEEE-754, so the conversion is
    lossless and the frontend gets something it can format directly.
    """

    amount: float
    currency: str
    unit: str


class JobOut(BaseModel):
    source_index: int
    title: str
    company: str
    description: str
    city: str | None
    region: str | None
    country: str
    country_label: str
    is_remote: bool
    employment_type: str
    salary: SalaryOut | None
    comparable_annual_usd: float | None
    posting_date: date | None
    warnings: list[str]

    @classmethod
    def from_job(cls, job: CanonicalJob) -> "JobOut":
        return cls(
            source_index=job.source_index,
            title=job.title,
            company=job.company,
            description=job.description,
            city=job.location.city,
            region=job.location.region,
            country=job.location.country.value,
            country_label=COUNTRY_LABELS.get(job.location.country, "Unknown"),
            is_remote=job.is_remote,
            employment_type=job.employment_type.value,
            salary=(
                SalaryOut(
                    amount=float(job.salary.amount),
                    currency=job.salary.currency.value.upper(),
                    unit=job.salary.unit.value,
                )
                if job.salary
                else None
            ),
            comparable_annual_usd=(
                float(job.comparable_annual_usd) if job.comparable_annual_usd else None
            ),
            posting_date=job.posting_date,
            warnings=list(job.warnings),
        )


class RejectionReasonOut(BaseModel):
    code: str
    message: str


class RejectedJobOut(BaseModel):
    """A rejected posting.

    Every field except the reasons is optional: a rejected posting may have no
    title, no location and no parseable salary. That is why it cannot share a
    response shape with an approved one.
    """

    source_index: int
    title: str | None
    company: str | None
    country_label: str | None
    salary_text: str | None
    reasons: list[RejectionReasonOut]
    warnings: list[str]

    @classmethod
    def from_decision(cls, decision: Decision) -> "RejectedJobOut":
        job = decision.job
        salary_text = None
        if job and job.salary:
            unit = "hr" if job.salary.unit.value == "hourly" else "yr"
            salary_text = f"{job.salary.amount:,.0f} {job.salary.currency.value.upper()}/{unit}"

        return cls(
            source_index=decision.source_index,
            title=job.title or None if job else None,
            company=job.company or None if job else None,
            country_label=(
                COUNTRY_LABELS.get(job.location.country) if job else None
            ),
            salary_text=salary_text,
            reasons=[
                RejectionReasonOut(code=reason.code.value, message=reason.message)
                for reason in decision.reasons
            ],
            warnings=list(job.warnings) if job else [],
        )


class CountryOut(BaseModel):
    value: str
    label: str