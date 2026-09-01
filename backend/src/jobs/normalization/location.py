from jobs.config.parsing import COUNTRY_ALIASES, REMOTE_MARKERS
from jobs.models.canonical import Location
from jobs.models.enums import Country
from jobs.models.raw import RawJob
from jobs.normalization.result import Normalized


def normalize_location(raw: RawJob) -> Normalized[Location]:
    """Resolve a country string into the only distinction the criteria need.

    Splitting the location text already happened in the adapter. All that is
    left here is classification: United States, Canada, somewhere else, or
    nowhere identifiable.
    """
    text = (raw.country or "").strip()
    key = text.casefold()
    warnings: list[str] = []

    if not text:
        country = Country.UNKNOWN
    elif key in REMOTE_MARKERS:
        country = Country.UNKNOWN
    elif key in COUNTRY_ALIASES:
        country = COUNTRY_ALIASES[key]
    else:
        country = Country.OTHER
        warnings.append(f"country not recognized as US or Canada: {text}")

    return Normalized(
        Location(
            country=country,
            raw_country=text or None,
            city=raw.city,
            region=raw.region,
        ),
        tuple(warnings),
    )
