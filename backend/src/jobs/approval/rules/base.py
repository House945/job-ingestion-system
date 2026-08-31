from typing import Protocol

from jobs.models.canonical import CanonicalJob
from jobs.models.decision import RejectionReason


class Rule(Protocol):
    """One publication criterion.

    Returns None when the posting satisfies the criterion, or a reason when it
    does not. A rule never raises and never inspects other rules' outcomes:
    every rule sees every posting, so a rejection can report all of its causes.
    """

    def evaluate(self, job: CanonicalJob) -> RejectionReason | None: ...