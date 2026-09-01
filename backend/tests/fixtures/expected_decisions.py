"""Manually calculated expectations for the feed from data/jobs.json.

This file is the single source of truth for the acceptance test. It was created BEFORE
implementation based on criteria analysis—it was not generated from
working code. If the implementation does not match it, first determine
which side is in error.
"""

from dataclasses import dataclass

from jobs.models.enums import RejectionCode


@dataclass(frozen=True)
class ExpectedDecision:
    index: int
    label: str
    approved: bool
    codes: frozenset[RejectionCode]


EXPECTED: tuple[ExpectedDecision, ...] = (
    ExpectedDecision(0, "NextGen - Backend Engineer", True, frozenset()),
    ExpectedDecision(
        1,
        "BrightStart - Frontend Developer Intern",
        False,
        frozenset({RejectionCode.EMPLOYMENT, RejectionCode.SALARY, RejectionCode.STAFFING}),
    ),
    ExpectedDecision(2, "DeepData - Machine Learning Engineer", True, frozenset()),
    ExpectedDecision(3, "Orbit Global - Agile Project Lead", False, frozenset({RejectionCode.GEO})),
    ExpectedDecision(
        4, "CloudWorks - DevOps Consultant", False, frozenset({RejectionCode.EMPLOYMENT})
    ),
    ExpectedDecision(5, "Tech Innovators - Senior Software Engineer", True, frozenset()),
    ExpectedDecision(
        6,
        "Staffing Solutions - Junior Developer",
        False,
        frozenset({RejectionCode.SALARY, RejectionCode.STAFFING, RejectionCode.LANGUAGE}),
    ),
    ExpectedDecision(7, "Analytics Corp - Data Scientist", True, frozenset()),
    ExpectedDecision(
        8,
        "Global Enterprises - Project Manager",
        False,
        frozenset({RejectionCode.GEO, RejectionCode.SALARY}),
    ),
    ExpectedDecision(9, "QualityLoop - QA Automation Engineer", True, frozenset()),
    ExpectedDecision(10, "PixelCraft - UX Designer", True, frozenset()),
    ExpectedDecision(11, "MetricMind - Product Analyst", True, frozenset()),
    ExpectedDecision(
        12,
        "AppForge - Mobile Engineer",
        False,
        frozenset({RejectionCode.GEO, RejectionCode.SALARY, RejectionCode.LANGUAGE}),
    ),
    ExpectedDecision(
        13,
        "DocuFlow - Technical Writer",
        False,
        frozenset({RejectionCode.EMPLOYMENT, RejectionCode.SALARY}),
    ),
    ExpectedDecision(14, "SecurePath - Cybersecurity Specialist", True, frozenset()),
    ExpectedDecision(15, "ScaleRocket - Growth Marketing Manager", True, frozenset()),
    ExpectedDecision(
        16,
        "DataCore - Database Administrator",
        False,
        frozenset({RejectionCode.GEO, RejectionCode.EMPLOYMENT, RejectionCode.STAFFING}),
    ),
    ExpectedDecision(
        17, "Northstar - Business Operations Associate", False, frozenset({RejectionCode.SALARY})
    ),
    ExpectedDecision(18, "ClientBridge - Customer Success Manager", True, frozenset()),
    ExpectedDecision(
        19,
        "OpsFlex - (no title)",
        False,
        frozenset(
            {
                RejectionCode.TITLE,
                RejectionCode.EMPLOYMENT,
                RejectionCode.SALARY,
                RejectionCode.STAFFING,
            }
        ),
    ),
)

APPROVED_COUNT = sum(1 for e in EXPECTED if e.approved)