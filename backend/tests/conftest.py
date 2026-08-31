from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def feed_path() -> Path:
    return REPO_ROOT / "data" / "jobs.json"