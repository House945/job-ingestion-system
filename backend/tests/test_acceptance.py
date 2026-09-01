from typing import Any

import pytest

from jobs.config.defaults import build_pipeline
from jobs.ingestion.loader import load_feed
from jobs.models.enums import RejectionCode
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

    assert not any(RejectionCode.PARSE_ERROR in d.codes for d in decisions)


def test_malformed_record_does_not_abort_the_batch():
    records: list[dict[str, Any]] = [
        {"title": "Fine", "salary": 200000},
        {"salary": object()},
        {"title": "Also fine"},
    ]

    decisions = build_pipeline().process(records)

    assert len(decisions) == 3

def test_non_object_entry_does_not_abort_the_batch():
    """A scraped feed can contain anything. Two good records must survive one bad one."""
    records: list[Any] = [
        {"title": "Fine", "salary": 200000},
        "oops",
        {"title": "Also fine", "salary": 300000},
    ]

    decisions = build_pipeline().process(records)

    assert len(decisions) == 3
    assert RejectionCode.PARSE_ERROR in decisions[1].codes
    assert RejectionCode.PARSE_ERROR not in decisions[0].codes