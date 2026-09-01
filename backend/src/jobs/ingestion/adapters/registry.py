from collections.abc import Mapping
from typing import Any

from jobs.ingestion.adapters.base import SourceAdapter
from jobs.ingestion.adapters.flat import FlatAdapter
from jobs.ingestion.adapters.structured import StructuredAdapter
from jobs.ingestion.shapes import FeedShape, detect_shape
from jobs.models.raw import RawJob


class AdapterRegistry:
    """Routes each record to the adapter matching its shape.

    Adding a third feed layout means writing an adapter, adding a FeedShape
    member and a detection branch - no existing adapter changes.
    """

    def __init__(self, adapters: Mapping[FeedShape, SourceAdapter] | None = None) -> None:
        self._adapters: Mapping[FeedShape, SourceAdapter] = adapters or {
            FeedShape.STRUCTURED: StructuredAdapter(),
            FeedShape.FLAT: FlatAdapter(),
        }

    def to_raw_job(self, index: int, record: Mapping[str, Any]) -> RawJob:
        shape = detect_shape(record)
        adapter = self._adapters.get(shape)
        if adapter is None:
            raise KeyError(f"no adapter registered for shape {shape}")
        return adapter.to_raw_job(index, record)
