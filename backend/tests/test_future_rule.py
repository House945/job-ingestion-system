from decimal import Decimal

from jobs.approval.policy import MarketPolicy
from jobs.config.defaults import build_pipeline
from jobs.config.markets import PUBLISHED_MARKETS, Market
from jobs.ingestion.loader import load_feed

ORBIT_GLOBAL = 3  # remote UK posting, 85,000 GBP


def test_remote_uk_is_rejected_today(feed_path):
    decisions = build_pipeline().process(load_feed(feed_path))

    assert decisions[ORBIT_GLOBAL].approved is False


def test_adding_a_market_approves_it(feed_path):
    """The brief's forward-looking example: remote UK at 90k USD or more.

    Adding it requires one market entry. No rule, no engine and no pipeline
    code changes - which is the whole point of routing geography and
    compensation through a shared policy.
    """
    markets = {
        **PUBLISHED_MARKETS,
        "remote_uk": Market(
            name="United Kingdom (remote)",
            annual_threshold_usd=Decimal("90000"),
            hourly_threshold_usd=Decimal("45"),
        ),
    }

    decisions = build_pipeline(policy=MarketPolicy(markets)).process(load_feed(feed_path))

    assert decisions[ORBIT_GLOBAL].approved is True