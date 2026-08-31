from jobs.models.canonical import CanonicalJob
from jobs.models.decision import RejectionReason
from jobs.models.enums import Country, Language, RejectionCode


class LanguageRule:
    """Description must be in English, or in French for Canadian postings.

    The only rule whose verdict depends on two fields at once. That coupling is
    in the criteria themselves, not an artifact of the design.
    """

    def evaluate(self, job: CanonicalJob) -> RejectionReason | None:
        if job.language is Language.ENGLISH:
            return None
        if job.language is Language.FRENCH and job.location.country is Country.CANADA:
            return None

        return RejectionReason(
            code=RejectionCode.LANGUAGE,
            message=f"unsupported language for this location: {job.language.value}",
        )