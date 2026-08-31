import pytest

from jobs.ingestion.adapters.flat import FlatAdapter
from jobs.ingestion.adapters.registry import AdapterRegistry
from jobs.ingestion.adapters.structured import StructuredAdapter
from jobs.ingestion.shapes import FeedShape, detect_shape

STRUCTURED_RECORD = {
    "title": "Backend Engineer",
    "description": "Build APIs.",
    "company": "NextGen Systems",
    "location": {"city": "Austin", "state": "TX", "country": "USA"},
    "salary": {"value": 145000, "currency": "USD"},
    "employment_type": "Full-Time",
    "posting_date": "2023-10-03",
    "company_type": "Direct Employer",
    "language": "English",
    "remote": False,
}

FLAT_RECORD = {
    "title": "Backend Engineer",
    "description": "Build APIs.",
    "company": "NextGen Systems",
    "location": "Austin, TX, USA",
    "salary": 145000,
    "employment_type": "Full-Time",
    "posting_date": "2023-10-03",
    "company_type": "Direct Employer",
    "language": "English",
    "remote": False,
}


def test_both_shapes_produce_equivalent_raw_jobs():
    """The whole point of the adapter layer: shape stops mattering here."""
    registry = AdapterRegistry()

    structured = registry.to_raw_job(0, STRUCTURED_RECORD)
    flat = registry.to_raw_job(0, FLAT_RECORD)

    ignored = {"original", "salary_currency"}
    structured_fields = structured.model_dump(exclude=ignored)
    flat_fields = flat.model_dump(exclude=ignored)

    assert structured_fields == flat_fields


def test_flat_shape_carries_no_currency():
    """The flat feed omits currency entirely - inventing one is not the adapter's job."""
    raw = FlatAdapter().to_raw_job(0, FLAT_RECORD)

    assert raw.salary_currency is None
    assert raw.salary_unit is None


@pytest.mark.parametrize(
    ("location", "expected"),
    [
        ("New York, NY, USA", ("New York", "NY", "USA")),
        ("London, UK", ("London", None, "UK")),
        ("Remote", (None, None, "Remote")),
        ("Toronto, ON, Canada", ("Toronto", "ON", "Canada")),
    ],
)
def test_flat_location_split(location, expected):
    raw = FlatAdapter().to_raw_job(0, {**FLAT_RECORD, "location": location})

    assert (raw.city, raw.region, raw.country) == expected


def test_null_location_is_tolerated():
    raw = FlatAdapter().to_raw_job(0, {**FLAT_RECORD, "location": None})

    assert raw.city is None
    assert raw.country is None


def test_empty_city_becomes_none():
    """A present-but-blank field is the same situation as a missing one."""
    record = {**STRUCTURED_RECORD, "location": {"city": "", "state": "CA", "country": "USA"}}

    raw = StructuredAdapter().to_raw_job(0, record)

    assert raw.city is None
    assert raw.region == "CA"


def test_boolean_salary_is_not_treated_as_a_number():
    raw = FlatAdapter().to_raw_job(0, {**FLAT_RECORD, "salary": True})

    assert raw.salary_value is None


def test_record_with_null_location_and_object_salary_is_structured():
    """The OpsFlex record: shape is not uniform within a record."""
    record = {"location": None, "salary": {"value": 40, "currency": "USD", "unit": "hourly"}}

    assert detect_shape(record) is FeedShape.STRUCTURED


def test_original_record_is_preserved():
    raw = StructuredAdapter().to_raw_job(7, STRUCTURED_RECORD)

    assert raw.original == STRUCTURED_RECORD
    assert raw.source_index == 7