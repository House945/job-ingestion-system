from jobs.models.canonical import CanonicalJob
from jobs.models.decision import RejectionReason
from jobs.models.enums import CompanyType, RejectionCode


class CompanyTypeRule:
    """Posting must not come from a staffing firm.

    Read literally: only STAFFING_FIRM disqualifies. Consulting agencies are a
    separate category in the feed and the brief names staffing firms
    specifically - see DECISIONS.md, section 9.
    """

    def evaluate(self, job: CanonicalJob) -> RejectionReason | None:
        if job.company_type is not CompanyType.STAFFING_FIRM:
            return None
        return RejectionReason(
            code=RejectionCode.STAFFING,
            message="posting is from a staffing firm",
        )