from tests.fixtures.expected_decisions import APPROVED_COUNT, EXPECTED


def test_expectations_cover_whole_feed():
    assert len(EXPECTED) == 20
    assert [e.index for e in EXPECTED] == list(range(20))


def test_expected_approved_count():
    assert APPROVED_COUNT == 10


def test_approved_entries_have_no_rejection_codes():
    for entry in EXPECTED:
        if entry.approved:
            assert entry.codes == frozenset(), entry.label
        else:
            assert entry.codes, entry.label
