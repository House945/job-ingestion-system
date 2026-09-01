from jobs.approval.policy import MarketPolicy
from jobs.models.canonical import CanonicalJob
from jobs.models.decision import RejectionReason
from jobs.models.enums import RejectionCode


class GeographyRule:
    """Posting must be remote-anywhere, or located in a market we publish to.

    A posting marked remote but tied to an identifiable foreign country is
    treated as remote within that country's market, not as remote-anywhere.
    """

    def __init__(self, policy: MarketPolicy) -> None:
        self._policy = policy

    def evaluate(self, job: CanonicalJob) -> RejectionReason | None:
        if self._policy.market_for(job) is not None:
            return None

        where = job.location.raw_country or "no location given"
        return RejectionReason(
            code=RejectionCode.GEO,
            message=f"not published in this market: {where}",
        )
