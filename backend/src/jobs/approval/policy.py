from collections.abc import Mapping

from jobs.config.markets import DEFAULT_MARKET, PUBLISHED_MARKETS, Market
from jobs.models.canonical import CanonicalJob
from jobs.models.enums import Country


class MarketPolicy:
    """Resolves which market a posting belongs to, if any.

    This is the single place where geography and compensation meet. Keeping the
    two rules independent would be cleaner in isolation, but then a condition
    that spans both - the brief's remote-UK example - could not be expressed
    without rewriting the engine.
    """

    def __init__(self, markets: Mapping[str, Market] | None = None) -> None:
        self._markets: Mapping[str, Market] = (
            markets if markets is not None else PUBLISHED_MARKETS
        )

    def market_for(self, job: CanonicalJob) -> Market | None:
        """Return the market this posting publishes to, or None if we do not publish it."""
        match job.location.country:
            case Country.UNITED_STATES:
                return self._markets.get("us")
            case Country.CANADA:
                return self._markets.get("canada")
            case Country.UNKNOWN if job.is_remote:
                return self._markets.get("remote_anywhere")
            case Country.OTHER if job.is_remote:
                key = (job.location.raw_country or "").casefold().replace(" ", "_")
                return self._markets.get(f"remote_{key}")
            case _:
                return None

    def thresholds_for(self, job: CanonicalJob) -> Market:
        """Return the thresholds to judge this posting's salary by.

        Falls back to the brief's standard thresholds when the posting's market
        is not published, so that a posting rejected on geography still reports
        a salary failure when it has one. Rejection reasons are diagnostic; a
        posting that fails on two counts should say so.
        """
        return self.market_for(job) or DEFAULT_MARKET