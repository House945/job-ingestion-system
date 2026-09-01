import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_FEED_PATH = Path(__file__).resolve().parents[3].parent / "data" / "jobs.json"


@dataclass(frozen=True)
class Settings:
    feed_path: Path

    @classmethod
    def from_env(cls) -> "Settings":
        raw = os.environ.get("JOBS_FEED_PATH")
        return cls(feed_path=Path(raw) if raw else DEFAULT_FEED_PATH)