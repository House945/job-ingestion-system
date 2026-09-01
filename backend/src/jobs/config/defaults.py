from jobs.approval.engine import RuleEngine
from jobs.approval.policy import MarketPolicy
from jobs.approval.rules.base import Rule
from jobs.approval.rules.company import CompanyTypeRule
from jobs.approval.rules.employment import EmploymentTypeRule
from jobs.approval.rules.geography import GeographyRule
from jobs.approval.rules.language import LanguageRule
from jobs.approval.rules.salary import SalaryRule
from jobs.approval.rules.title import TitleRule
from jobs.ingestion.adapters.registry import AdapterRegistry
from jobs.ingestion.pipeline import IngestionPipeline
from jobs.normalization.currency import CurrencyConverter, StaticRateConverter
from jobs.normalization.normalizer import JobNormalizer


def build_rules(policy: MarketPolicy, converter: CurrencyConverter) -> list[Rule]:
    """The publication criteria, in the order their reasons are reported."""
    return [
        TitleRule(),
        GeographyRule(policy),
        EmploymentTypeRule(),
        SalaryRule(policy, converter),
        CompanyTypeRule(),
        LanguageRule(),
    ]


def build_pipeline(
    policy: MarketPolicy | None = None,
    converter: CurrencyConverter | None = None,
) -> IngestionPipeline:
    """Wire the default pipeline. Every dependency is overridable for tests."""
    policy = policy or MarketPolicy()
    converter = converter or StaticRateConverter()

    return IngestionPipeline(
        registry=AdapterRegistry(),
        normalizer=JobNormalizer(converter),
        engine=RuleEngine(build_rules(policy, converter)),
    )
