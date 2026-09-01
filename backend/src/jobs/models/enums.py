from enum import StrEnum
from typing import Any


class _NormalizingEnum(StrEnum):
    """Enum that tolerates various formatting variants from the feed.

    The feed is scraped, so 'Full-Time', 'full time', and 'FULL_TIME' mean
    the same thing. An unknown value does not raise an exception—it maps to UNKNOWN,
    ensuring that a single weird record doesn't crash the entire batch. The decision on
    whether UNKNOWN is acceptable is made by rules, not the model.
    """

    @classmethod
    def _missing_(cls, value: Any) -> "_NormalizingEnum": # noqa: ANN401
        if isinstance(value, str):
            normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
            for member in cls:
                if member.value == normalized:
                    return member
        return cls["UNKNOWN"]


class EmploymentType(_NormalizingEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    UNKNOWN = "unknown"


class CompanyType(_NormalizingEnum):
    DIRECT_EMPLOYER = "direct_employer"
    STAFFING_FIRM = "staffing_firm"
    CONSULTING_AGENCY = "consulting_agency"
    UNKNOWN = "unknown"


class Language(_NormalizingEnum):
    ENGLISH = "english"
    FRENCH = "french"
    GERMAN = "german"
    UNKNOWN = "unknown"


class Currency(_NormalizingEnum):
    USD = "usd"
    CAD = "cad"
    GBP = "gbp"
    EUR = "eur"
    UNKNOWN = "unknown"


class SalaryUnit(_NormalizingEnum):
    ANNUAL = "annual"
    HOURLY = "hourly"
    UNKNOWN = "unknown"


class Country(_NormalizingEnum):
    UNITED_STATES = "united_states"
    CANADA = "canada"
    OTHER = "other"
    UNKNOWN = "unknown"



class RejectionCode(StrEnum):
    """Reason for rejecting the offer. One code per violated criterion."""

    TITLE = "TITLE"
    GEO = "GEO"
    EMPLOYMENT = "EMPLOYMENT"
    SALARY = "SALARY"
    STAFFING = "STAFFING"
    LANGUAGE = "LANGUAGE"
    PARSE_ERROR = "PARSE_ERROR"
