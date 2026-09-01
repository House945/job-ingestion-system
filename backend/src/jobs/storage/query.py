from dataclasses import dataclass
from enum import StrEnum

from jobs.models.enums import Country


class SortField(StrEnum):
    SALARY = "salary"
    POSTING_DATE = "posting_date"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True)
class JobQuery:
    """A search request, independent of how it arrived.

    The repository accepts this type rather than loose HTTP parameters, so
    query semantics can be tested without a web layer and the same query can
    later come from a scheduled job or a CLI.
    """

    search: str | None = None
    country: Country | None = None
    sort_by: SortField | None = None
    order: SortOrder = SortOrder.DESC