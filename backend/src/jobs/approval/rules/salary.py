from jobs.approval.policy import MarketPolicy
from jobs.models.canonical import CanonicalJob
from jobs.models.decision import RejectionReason
from jobs.models.enums import RejectionCode, SalaryUnit
from jobs.normalization.currency import CurrencyConverter


class SalaryRule:
    """Compensation must clear the threshold for the posting's market.

    The two thresholds are applied separately by unit and are deliberately not
    equivalent: 45/hour over 2080 hours is 93,600, below the annual threshold.
    Converting hourly to annual before comparing would reject postings the
    brief intends to approve - see DECISIONS.md, section 4.

    This rule never reads CanonicalJob.comparable_annual_usd. That field exists
    for sorting and mixes the two units on purpose.
    """

    def __init__(self, policy: MarketPolicy, converter: CurrencyConverter) -> None:
        self._policy = policy
        self._converter = converter

    def evaluate(self, job: CanonicalJob) -> RejectionReason | None:
        if job.salary is None:
            return self._reject("no salary information")

        in_usd = self._converter.to_usd(job.salary.amount, job.salary.currency)
        if in_usd is None:
            return self._reject(f"cannot convert {job.salary.currency.value} to USD")

        market = self._policy.thresholds_for(job)

        match job.salary.unit:
            case SalaryUnit.ANNUAL:
                if in_usd > market.annual_threshold_usd:
                    return None
                return self._reject(
                    f"annual {in_usd:.0f} USD does not exceed "
                    f"{market.annual_threshold_usd:.0f} for {market.name}"
                )
            case SalaryUnit.HOURLY:
                if in_usd > market.hourly_threshold_usd:
                    return None
                return self._reject(
                    f"hourly {in_usd:.2f} USD does not exceed "
                    f"{market.hourly_threshold_usd:.2f} for {market.name}"
                )
            case _:
                return self._reject("salary unit could not be determined")

    @staticmethod
    def _reject(message: str) -> RejectionReason:
        return RejectionReason(code=RejectionCode.SALARY, message=message)