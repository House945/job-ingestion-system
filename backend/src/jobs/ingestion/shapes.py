from collections.abc import Mapping
from enum import StrEnum
from typing import Any


class FeedShape(StrEnum):
    """Layout of a single feed record.

    The sample feed mixes two layouts. STRUCTURED nests location and salary as
    objects; FLAT provides them as a comma-separated string and a bare number.
    """

    STRUCTURED = "structured"
    FLAT = "flat"


def detect_shape(record: Mapping[str, Any]) -> FeedShape:
    """Classify a record by the shape of its polymorphic fields.

    Salary is the primary discriminator because it is present in every sample
    record, including one whose location is null. Location is checked as a
    fallback so that a record missing salary entirely can still be classified.
    """
    if isinstance(record.get("salary"), Mapping):
        return FeedShape.STRUCTURED
    if isinstance(record.get("location"), Mapping):
        return FeedShape.STRUCTURED
    return FeedShape.FLAT