from jobs.models.canonical import CanonicalJob
from jobs.models.decision import RejectionReason
from jobs.models.enums import RejectionCode


class TitleRule:
    """Title must not be null or empty."""

    def evaluate(self, job: CanonicalJob) -> RejectionReason | None:
        if job.title:
            return None
        return RejectionReason(code=RejectionCode.TITLE, message="title is missing or empty")