from collections.abc import Sequence

from jobs.approval.rules.base import Rule
from jobs.models.canonical import CanonicalJob
from jobs.models.decision import RejectionReason


class RuleEngine:
    """Applies every rule to every posting.

    Deliberately not fail-fast. A posting that violates three criteria reports
    three reasons, because the rejection log's value is diagnostic: knowing that
    a feed fails on salary AND language AND geography says something about the
    source that "failed on salary" does not.

    The rule set is a constructor argument, so adding a criterion means writing
    a rule and registering it - the engine itself never changes.
    """

    def __init__(self, rules: Sequence[Rule]) -> None:
        self._rules = tuple(rules)

    def evaluate(self, job: CanonicalJob) -> tuple[RejectionReason, ...]:
        reasons = (rule.evaluate(job) for rule in self._rules)
        return tuple(reason for reason in reasons if reason is not None)
