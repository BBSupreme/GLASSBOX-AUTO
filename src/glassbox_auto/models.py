from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EvidenceGrade(str, Enum):
    UNKNOWN = "UNKNOWN"
    ESTIMATED = "ESTIMATED"
    VERIFIED = "VERIFIED"


class AcquisitionMode(str, Enum):
    LEASE_NEW = "LEASE_NEW"
    BUY_NEW = "BUY_NEW"
    BUY_USED = "BUY_USED"


class PreferenceLabel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    MUST_HAVE = "MUST_HAVE"


class UtilityDirection(str, Enum):
    HIGHER_IS_BETTER = "HIGHER_IS_BETTER"
    LOWER_IS_BETTER = "LOWER_IS_BETTER"


class GateState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class Readiness(str, Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"


GRADE_RANK = {
    EvidenceGrade.UNKNOWN: 0,
    EvidenceGrade.ESTIMATED: 1,
    EvidenceGrade.VERIFIED: 2,
}

PREFERENCE_MULTIPLIERS = {
    PreferenceLabel.LOW: 0.5,
    PreferenceLabel.MEDIUM: 1.0,
    PreferenceLabel.HIGH: 1.5,
    PreferenceLabel.VERY_HIGH: 2.0,
    PreferenceLabel.MUST_HAVE: 2.0,
}


@dataclass(frozen=True)
class Evidence:
    grade: EvidenceGrade = EvidenceGrade.UNKNOWN
    source: str | None = None
    as_of: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class ObservedValue:
    value: Any
    evidence: Evidence = field(default_factory=Evidence)


@dataclass(frozen=True)
class Vehicle:
    vehicle_id: str
    make: str
    model: str
    variant: str
    attributes: dict[str, ObservedValue] = field(default_factory=dict)


@dataclass(frozen=True)
class AcquisitionOffer:
    offer_id: str
    vehicle_id: str
    mode: AcquisitionMode
    currency: str = "DKK"
    term_months: int | None = None
    annual_km: int | None = None
    upfront_payment: float = 0.0
    recurring_payment: float = 0.0
    mandatory_fees: float = 0.0
    overage_cost_per_km: float | None = None
    attributes: dict[str, ObservedValue] = field(default_factory=dict)


@dataclass(frozen=True)
class UtilityAnchors:
    floor: float
    need: float
    stretch: float
    direction: UtilityDirection = UtilityDirection.HIGHER_IS_BETTER


@dataclass(frozen=True)
class GateDefinition:
    operator: str
    threshold: Any
    minimum_evidence: EvidenceGrade = EvidenceGrade.ESTIMATED


@dataclass(frozen=True)
class Criterion:
    criterion_id: str
    attribute: str
    preference: PreferenceLabel
    anchors: UtilityAnchors | None = None
    gate: GateDefinition | None = None
    minimum_evidence: EvidenceGrade = EvidenceGrade.ESTIMATED
    active: bool = True


@dataclass(frozen=True)
class UserProfile:
    profile_id: str
    criteria: tuple[Criterion, ...]
    expected_annual_km: int | None = None
    unused_km_value_per_km: float | None = None


@dataclass(frozen=True)
class CriterionResult:
    criterion_id: str
    utility: float | None
    weight: float
    gate_state: GateState | None
    covered: bool
    reason: str | None = None


@dataclass(frozen=True)
class CandidateResult:
    candidate_id: str
    vehicle_id: str
    offer_id: str
    mode: AcquisitionMode
    score: float | None
    evidence_coverage: float
    readiness: Readiness
    criterion_results: tuple[CriterionResult, ...]
    economics: dict[str, float] | None = None
    close_call: bool = False
    reasons: tuple[str, ...] = ()
