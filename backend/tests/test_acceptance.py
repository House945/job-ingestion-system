from typing import Any

import pytest

from jobs.config.defaults import build_pipeline
from jobs.ingestion.loader import load_feed
from tests.fixtures.expected_decisions import APPROVED_COUNT, EXPECTED


@pytest.fixture(scope="module")
def decisions(feed_path):
    return build_pipeline().process(load_feed(feed_path))


def test_every_record_yields_a_decision(decisions):
    assert len(decisions) == len(EXPECTED)


@pytest.mark.parametrize("expected", EXPECTED, ids=lambda e: f"{e.index:02d}-{e.label}")
def test_decision_matches_expectation(decisions, expected):
    decision = decisions[expected.index]

    assert decision.approved is expected.approved, decision.reasons
    assert decision.codes == expected.codes


def test_approved_count(decisions):
    assert sum(1 for d in decisions if d.approved) == APPROVED_COUNT


def test_no_record_produced_a_parse_error(decisions):
    """Every sample record is processable; a parse error here means a real bug."""
    from jobs.models.enums import RejectionCode

    assert not any(RejectionCode.PARSE_ERROR in d.codes for d in decisions)


def test_malformed_record_does_not_abort_the_batch():
    records: list[dict[str, Any]] = [
        {"title": "Fine", "salary": 200000},
        {"salary": object()},
        {"title": "Also fine"},
    ]

    decisions = build_pipeline().process(records)

    assert len(decisions) == 3