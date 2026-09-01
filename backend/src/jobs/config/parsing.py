from decimal import Decimal

from jobs.models.enums import Country, Currency

# A bare number below this value is read as an hourly rate rather than an
# annual figure. The feed does not always supply a unit. In the sample data
# annual salaries are five- and six-figure while hourly rates are two-figure,
# so the margin around this ceiling is wide. It would misread a day rate -
# that limitation is accepted and documented rather than hidden.
HOURLY_INFERENCE_CEILING = Decimal("1000")

# The feed does not always supply a currency. USD is assumed because the
# approval thresholds are denominated in USD. Currency is deliberately NOT
# inferred from the posting's country: that would be a silent heuristic capable
# of flipping a verdict with no trace in the data.
DEFAULT_CURRENCY = Currency.USD

# Used only to derive a sortable annual figure from an hourly rate. It is never
# used to evaluate the salary criterion - see DECISIONS.md, section 4.
ANNUAL_BILLABLE_HOURS = Decimal("2080")

# Country names as they appear in feeds, mapped to the only distinction the
# approval criteria care about. Anything unrecognized becomes OTHER.
COUNTRY_ALIASES: dict[str, Country] = {
    "usa": Country.UNITED_STATES,
    "us": Country.UNITED_STATES,
    "u.s.": Country.UNITED_STATES,
    "u.s.a.": Country.UNITED_STATES,
    "united states": Country.UNITED_STATES,
    "united states of america": Country.UNITED_STATES,
    "canada": Country.CANADA,
    "ca": Country.CANADA,
}

# Location text that denotes "no particular place" rather than a country.
REMOTE_MARKERS: frozenset[str] = frozenset({"remote", "anywhere", "worldwide"})
