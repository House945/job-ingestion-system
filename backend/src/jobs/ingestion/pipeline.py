import logging
from collections.abc import Iterable, Mapping, Sequence

from jobs.approval.engine import RuleEngine
from jobs.ingestion.adapters.registry import AdapterRegistry
from jobs.models.decision import Decision, RejectionReason
from jobs.models.enums import RejectionCode
from jobs.normalization.normalizer import JobNormalizer

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Adapt, normalize, evaluate - once per record.

    A record that cannot be processed at all becomes a rejected Decision with a
    parse-error reason, never an exception that escapes. One malformed record
    out of twenty must not cost the other nineteen.
    """

    def __init__(
        self,
        registry: AdapterRegistry,
        normalizer: JobNormalizer,
        engine: RuleEngine,
    ) -> None:
        self._registry = registry
        self._normalizer = normalizer
        self._engine = engine

    def process(self, records: Iterable[object]) -> Sequence[Decision]:
        return [self._process_one(index, record) for index, record in enumerate(records)]

    def _process_one(self, index: int, record: object) -> Decision:
        try:
            if not isinstance(record, Mapping):
                raise TypeError(f"expected a JSON object, got {type(record).__name__}")
            raw = self._registry.to_raw_job(index, record)
            job = self._normalizer.normalize(raw)
        except Exception as exc:
            logger.warning("record %s could not be processed: %s", index, exc)
            return Decision(
                source_index=index,
                job=None,
                raw=None,
                reasons=(
                    RejectionReason(
                        code=RejectionCode.PARSE_ERROR,
                        message="record could not be read as a job posting",
                    ),
                ),
            )

        return Decision(
            source_index=index,
            job=job,
            raw=raw,
            reasons=self._engine.evaluate(job),
        )
