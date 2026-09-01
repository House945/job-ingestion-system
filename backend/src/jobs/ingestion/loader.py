import json
from collections.abc import Sequence
from pathlib import Path


class FeedLoadError(Exception):
    """Raised when a feed file cannot be read or does not contain a job list."""


def load_feed(path: Path) -> Sequence[object]:
    """Read a feed file and return its records.

    Failures here are fatal because they leave nothing to process: an
    unreadable file, malformed JSON, or a top level that is not an array.

    A bad individual entry is not one of them. Entries are returned as they
    came, including ones that are not objects at all, and the pipeline isolates
    each failure into a rejected decision with a parse error. One unusable
    record must not cost the others.
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

    return parsed