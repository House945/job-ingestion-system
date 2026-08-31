from enum import StrEnum


class RejectionCode(StrEnum):
    """Reason for rejecting the offer. One code per violated criterion."""

    TITLE = "TITLE"
    GEO = "GEO"
    EMPLOYMENT = "EMPLOYMENT"
    SALARY = "SALARY"
    STAFFING = "STAFFING"
    LANGUAGE = "LANGUAGE"
    PARSE_ERROR = "PARSE_ERROR"