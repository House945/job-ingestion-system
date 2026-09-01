from jobs.approval.engine import RuleEngine
from jobs.models.decision import RejectionReason
from jobs.models.enums import RejectionCode


class _AlwaysFails:
    def __init__(self, code: RejectionCode) -> None:
        self._code = code

    def evaluate(self, job):
        return RejectionReason(code=self._code, message="nope")


class _AlwaysPasses:
    def evaluate(self, job):
        return None


def test_collects_every_reason_not_just_the_first(make_job):
    engine = RuleEngine(
        [
            _AlwaysFails(RejectionCode.TITLE),
            _AlwaysPasses(),
            _AlwaysFails(RejectionCode.SALARY),
        ]
    )

    reasons = engine.evaluate(make_job())

    assert {r.code for r in reasons} == {RejectionCode.TITLE, RejectionCode.SALARY}


def test_no_rules_means_no_reasons(make_job):
    assert RuleEngine([]).evaluate(make_job()) == ()
