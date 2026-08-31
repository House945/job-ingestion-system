import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any


class FeedLoadError(Exception):
    """Raised when a feed file cannot be read or does not contain a job list."""


def load_feed(path: Path) -> Sequence[dict[str, Any]]:
    """Read a feed file and return its records.

    Failures here are fatal for the whole batch, unlike per-record failures
    later in the pipeline: if the file is missing or is not a JSON array, there
    is nothing to process and the caller needs to know immediately.
    """
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise FeedLoadError(f"cannot read feed at {path}: {exc}") from exc

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise FeedLoadError(f"feed at {path} is not valid JSON: {exc}") from exc

    if not isinstance(parsed, list):
        raise FeedLoadError(
          f"feed at {path} must contain a JSON array, got {type(parsed).__name__}"
          )

    records: list[dict[str, Any]] = []
    for position, entry in enumerate(parsed):
        if not isinstance(entry, dict):
            raise FeedLoadError(f"feed entry at position {position} is not an object")
        records.append(entry)

    return records