import json
import logging
from collections.abc import Callable

from jobs.models.canonical import CanonicalJob
from jobs.models.decision import Decision, RejectionReason
from jobs.models.enums import RejectionCode
from jobs.storage.rejection_log import LoggingSink, RejectionLog


def _rejected(make_job: Callable[..., CanonicalJob], index: int = 0) -> Decision:
    return Decision(
        source_index=index,
        job=make_job(title="Junior Developer"),
        raw=None,
        reasons=(
            RejectionReason(code=RejectionCode.SALARY, message="below threshold"),
            RejectionReason(code=RejectionCode.STAFFING, message="staffing firm"),
        ),
    )


def test_entries_are_retained(make_job):
    log = RejectionLog(sinks=[])

    log.record(_rejected(make_job))

    assert log.count() == 1


def test_logging_sink_emits_structured_json(make_job, caplog):
    """The log line is the contract from the brief - it must be parseable."""
    with caplog.at_level(logging.WARNING, logger="jobs.rejections"):
        RejectionLog(sinks=[LoggingSink()]).record(_rejected(make_job))

    assert len(caplog.records) == 1
    payload = json.loads(caplog.records[0].getMessage().split("job rejected: ", 1)[1])
    assert {reason["code"] for reason in payload["reasons"]} == {"SALARY", "STAFFING"}


def test_logging_and_retention_both_happen(make_job):
    """The UI tab is an addition to logging, never a replacement for it."""
    log = RejectionLog(sinks=[LoggingSink()])

    log.record(_rejected(make_job))

    assert log.count() == 1


def test_parse_error_decision_without_a_job_is_loggable():
    """A record that failed to parse has no title and no company."""
    decision = Decision(
        source_index=4,
        job=None,
        raw=None,
        reasons=(RejectionReason(code=RejectionCode.PARSE_ERROR, message="broken"),),
    )

    RejectionLog(sinks=[LoggingSink()]).record(decision)