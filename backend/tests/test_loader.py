import json

import pytest

from jobs.ingestion.loader import FeedLoadError, load_feed


def test_loads_records(tmp_path):
    path = tmp_path / "feed.json"
    path.write_text(json.dumps([{"title": "A"}, {"title": "B"}]), encoding="utf-8")

    records = load_feed(path)

    assert len(records) == 2


def test_missing_file_raises(tmp_path):
    with pytest.raises(FeedLoadError, match="cannot read feed"):
        load_feed(tmp_path / "nope.json")


def test_invalid_json_raises(tmp_path):
    path = tmp_path / "feed.json"
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(FeedLoadError, match="not valid JSON"):
        load_feed(path)


def test_non_array_raises(tmp_path):
    path = tmp_path / "feed.json"
    path.write_text(json.dumps({"title": "A"}), encoding="utf-8")

    with pytest.raises(FeedLoadError, match="must contain a JSON array"):
        load_feed(path)


def test_non_object_entries_pass_through(tmp_path):
    """The loader does not judge individual entries - the pipeline isolates them."""
    path = tmp_path / "feed.json"
    path.write_text(json.dumps([{"title": "A"}, "oops", None, 42]), encoding="utf-8")

    records = load_feed(path)

    assert len(records) == 4


def test_real_feed_parses(feed_path):
    records = load_feed(feed_path)

    assert len(records) == 20
