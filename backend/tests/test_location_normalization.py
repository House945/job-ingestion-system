import pytest

from jobs.models.enums import Country
from jobs.models.raw import RawJob
from jobs.normalization.location import normalize_location


@pytest.mark.parametrize(
    ("country_text", "expected"),
    [
        ("USA", Country.UNITED_STATES),
        ("usa", Country.UNITED_STATES),
        ("United States", Country.UNITED_STATES),
        ("Canada", Country.CANADA),
        ("UK", Country.OTHER),
        ("Germany", Country.OTHER),
        ("Ireland", Country.OTHER),
        ("Remote", Country.UNKNOWN),
        ("", Country.UNKNOWN),
        (None, Country.UNKNOWN),
    ],
)
def test_country_classification(country_text, expected):
    raw = RawJob(source_index=0, country=country_text)

    assert normalize_location(raw).value.country is expected


def test_remote_marker_is_not_a_foreign_country():
    """'Remote' means no identifiable place, which is not the same as elsewhere."""
    assert normalize_location(RawJob(source_index=0, country="Remote")).value.country is (
        Country.UNKNOWN
    )
    assert normalize_location(RawJob(source_index=0, country="UK")).value.country is Country.OTHER


def test_unrecognized_country_is_flagged():
    result = normalize_location(RawJob(source_index=0, country="Germany"))

    assert result.warnings


def test_city_and_region_pass_through():
    raw = RawJob(source_index=0, city="Austin", region="TX", country="USA")

    location = normalize_location(raw).value

    assert location.city == "Austin"
    assert location.region == "TX"
    assert location.raw_country == "USA"