import json
import logging
from collections.abc import Sequence
from typing import Protocol

from jobs.models.decision import Decision

logger = logging.getLogger("jobs.rejections")


class RejectionSink(Protocol):
    """Somewhere a rejection is written to."""

    def write(self, decision: Decision) -> None: ...


class LoggingSink:
    """Emits one structured JSON line per rejection.

    This is the requirement from the brief and the machine-readable contract:
    it works with no UI running and survives the process that produced it.
    """

    def write(self, decision: Decision) -> None:
        job = decision.job
        payload = {
            "source_index": decision.source_index,
            "title": job.title if job else None,
            "company": job.company if job else None,
            "reasons": [
                {"code": reason.code.value, "message": reason.message}
                for reason in decision.reasons
            ],
        }
        logger.warning("job rejected: %s", json.dumps(payload, ensure_ascii=False))


class RejectionLog:
    """Records rejected postings and keeps them available for inspection.

    Logging satisfies the brief's requirement. Retention is an addition: the
    reasons a feed fails are the most useful artifact this system produces, and
    leaving them only in stdout wastes them. Retention never replaces the log -
    both happen, from one call - see DECISIONS.md, section 12.
    """

    def __init__(self, sinks: Sequence[RejectionSink] | None = None) -> None:
        self._sinks: tuple[RejectionSink, ...] = (
            tuple(sinks) if sinks is not None else (LoggingSink(),)
        )
        self._entries: list[Decision] = []

    def record(self, decision: Decision) -> None:
        self._entries.append(decision)
        for sink in self._sinks:
            sink.write(decision)

    def entries(self) -> Sequence[Decision]:
        return tuple(self._entries)

    def count(self) -> int:
        return len(self._entries)