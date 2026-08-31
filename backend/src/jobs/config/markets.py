from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Market:
    """A place we publish to, with its own compensation thresholds.

    Markets are how a future rule like "remote UK postings qualify at 90k USD"
    gets expressed: it is one entry in the map below, not a change to any rule.
    """

    name: str
    annual_threshold_usd: Decimal
    hourly_threshold_usd: Decimal


# Thresholds from the brief. Applied to postings whose market is not published,
# so that such a posting is still evaluated on salary and reports every reason
# it failed rather than only the geographic one.
DEFAULT_MARKET = Market(
    name="default",
    annual_threshold_usd=Decimal("100000"),
    hourly_threshold_usd=Decimal("45"),
)

_STANDARD_THRESHOLDS = {
    "annual_threshold_usd": Decimal("100000"),
    "hourly_threshold_usd": Decimal("45"),
}

# Markets we currently publish to. Adding one is a single entry here.
#
# Keys: "us" and "canada" for in-person postings; "remote_anywhere" for postings
# with no identifiable location; "remote_<country>" for remote postings tied to
# a specific foreign market. The last form is what the brief's forward-looking
# example needs - adding "remote_uk" with a 90000 threshold would approve remote
# UK postings without touching a single rule.
PUBLISHED_MARKETS: dict[str, Market] = {
    "us": Market(name="United States", **_STANDARD_THRESHOLDS),
    "canada": Market(name="Canada", **_STANDARD_THRESHOLDS),
    "remote_anywhere": Market(name="Remote (anywhere)", **_STANDARD_THRESHOLDS),
}