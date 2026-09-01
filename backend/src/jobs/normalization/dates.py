from datetime import date

from jobs.normalization.result import Normalized


def parse_posting_date(value: str | None) -> Normalized[date | None]:
    """Parse an ISO date, tolerating absence.

    Posting date is not an approval criterion, so a missing or malformed date
    never rejects a posting. It only affects how the posting sorts.
    """
    if value is None or not value.strip():
        return Normalized(None)

    try:
        return Normalized(date.fromisoformat(value.strip()))
    except ValueError:
        return Normalized(None, (f"posting date could not be parsed: {value}",))
