from pydantic import BaseModel, ConfigDict

from jobs.models.canonical import CanonicalJob
from jobs.models.enums import RejectionCode
from jobs.models.raw import RawJob


class RejectionReason(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: RejectionCode
    message: str


class Decision(BaseModel):
    """The result of evaluating a single offer.

    Rejection carries ALL violated criteria, not just the first one encountered—the
    engine does not fail fast, because the list of reasons is the most valuable artifact
    when debugging feed quality.
    """

    model_config = ConfigDict(frozen=True)

    source_index: int
    job: CanonicalJob | None
    raw: RawJob | None
    reasons: tuple[RejectionReason, ...] = ()

    @property
    def approved(self) -> bool:
        return not self.reasons

    @property
    def codes(self) -> frozenset[RejectionCode]:
        return frozenset(reason.code for reason in self.reasons)
