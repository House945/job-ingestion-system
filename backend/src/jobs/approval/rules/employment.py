from jobs.models.canonical import CanonicalJob
from jobs.models.decision import RejectionReason
from jobs.models.enums import EmploymentType, RejectionCode


class EmploymentTypeRule:
    """Posting must be full-time.

    An unrecognized employment type is not full-time, so it is rejected with a
    reason rather than passed through or raised on.
    """

    def evaluate(self, job: CanonicalJob) -> RejectionReason | None:
        if job.employment_type is EmploymentType.FULL_TIME:
            return None
        return RejectionReason(
            code=RejectionCode.EMPLOYMENT,
            message=f"not a full-time position: {job.employment_type.value}",
        )
