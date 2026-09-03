from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EvidenceGrade(str, Enum):
    UNKNOWN = "UNKNOWN"
    ESTIMATED = "ESTIMATED"
    VERIFIED = "VERIFIED"


class EvidenceKind(str, Enum):
    DIRECT = "DIRECT"
    DERIVED = "DERIVED"
    MODELED = "MODELED"


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


class Eligibility(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


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
    kind: EvidenceKind = EvidenceKind.DIRECT
    method: str | None = None
    lineage: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.grade == EvidenceGrade.VERIFIED and not self.source:
            raise ValueError("VERIFIED evidence requires a source")
        if self.kind == EvidenceKind.MODELED and self.grade == EvidenceGrade.VERIFIED:
            raise ValueError("MODELED evidence cannot be VERIFIED")


@dataclass(frozen=True)
class ObservedValue:
    value: Any
    evidence: Evidence = field(default_factory=Evidence)
    unit: str | None = None


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
    term_months: ObservedValue | None = None
    annual_km: ObservedValue | None = None
    upfront_payment: ObservedValue | None = None
    recurring_payment: ObservedValue | None = None
    mandatory_fees: ObservedValue | None = None
    overage_cost_per_km: ObservedValue | None = None
    attributes: dict[str, ObservedValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.currency:
            raise ValueError("currency is required")
        _validate_observed_number(self.term_months, "term_months", strictly_positive=True)
        _validate_observed_number(self.annual_km, "annual_km", non_negative=True)
        _validate_observed_number(self.upfront_payment, "upfront_payment", non_negative=True)
        _validate_observed_number(self.recurring_payment, "recurring_payment", non_negative=True)
        _validate_observed_number(self.mandatory_fees, "mandatory_fees", non_negative=True)
        _validate_observed_number(self.overage_cost_per_km, "overage_cost_per_km", non_negative=True)
        _validate_unit(self.term_months, "term_months", "month")
        _validate_unit(self.annual_km, "annual_km", "km/year")
        _validate_unit(self.upfront_payment, "upfront_payment", self.currency)
        _validate_unit(self.recurring_payment, "recurring_payment", f"{self.currency}/month")
        _validate_unit(self.mandatory_fees, "mandatory_fees", self.currency)
        _validate_unit(self.overage_cost_per_km, "overage_cost_per_km", f"{self.currency}/km")


@dataclass(frozen=True)
class UtilityAnchors:
    floor: float
    need: float
    stretch: float
    need_utility: float
    direction: UtilityDirection = UtilityDirection.HIGHER_IS_BETTER

    def __post_init__(self) -> None:
        if not (0.0 < self.need_utility < 1.0):
            raise ValueError("need_utility must be strictly between 0 and 1")


@dataclass(frozen=True)
class GateDefinition:
    operator: str
    threshold: Any
    minimum_evidence: EvidenceGrade = EvidenceGrade.ESTIMATED
    decision_critical: bool = True


@dataclass(frozen=True)
class Criterion:
    criterion_id: str
    attribute: str
    preference: PreferenceLabel
    anchors: UtilityAnchors | None = None
    gate: GateDefinition | None = None
    minimum_evidence: EvidenceGrade = EvidenceGrade.ESTIMATED
    active: bool = True
    dimension: str | None = None
    base_weight: float = 1.0
    subweight: float = 1.0
    weight_cap: float | None = None
    unit: str | None = None

    def __post_init__(self) -> None:
        if self.base_weight < 0 or self.subweight < 0:
            raise ValueError("criterion weights must be non-negative")
        if self.weight_cap is not None and self.weight_cap < 0:
            raise ValueError("weight_cap must be non-negative")
        if self.preference == PreferenceLabel.MUST_HAVE:
            if self.gate is None:
                raise ValueError(f"Must-have criterion {self.criterion_id} requires a gate")
            if not self.gate.decision_critical:
                raise ValueError(f"Must-have criterion {self.criterion_id} requires a decision-critical gate")
            if self.anchors is None:
                raise ValueError(
                    f"Must-have criterion {self.criterion_id} requires utility anchors; "
                    "use a zero-weight gate-only criterion if weighting is not intended"
                )
        if self.active and self.anchors is None and self.base_weight > 0:
            raise ValueError(
                f"Active weighted criterion {self.criterion_id} requires utility anchors; "
                "set base_weight=0 for an explicit gate-only criterion"
            )
        if self.active and self.anchors is None and self.gate is None:
            raise ValueError(f"Active unscored criterion {self.criterion_id} requires a gate")


@dataclass(frozen=True)
class UserProfile:
    profile_id: str
    criteria: tuple[Criterion, ...]
    expected_annual_km: int | None = None
    unused_km_value_per_km: ObservedValue | None = None
    dimension_weights: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.expected_annual_km is not None and self.expected_annual_km < 0:
            raise ValueError("expected_annual_km must be non-negative")
        for dimension, weight in self.dimension_weights.items():
            if weight < 0:
                raise ValueError(f"dimension weight must be non-negative: {dimension}")
        _validate_observed_number(self.unused_km_value_per_km, "unused_km_value_per_km", non_negative=True)


@dataclass(frozen=True)
class CriterionResult:
    criterion_id: str
    utility: float | None
    weight: float
    gate_state: GateState | None
    data_present: bool
    evidence_sufficient: bool
    active: bool
    scorable: bool
    normalized_weight: float = 0.0
    reason: str | None = None


@dataclass(frozen=True)
class CandidateResult:
    candidate_id: str
    vehicle_id: str
    offer_id: str
    mode: AcquisitionMode
    currency: str
    score: float | None
    data_coverage: float
    evidence_coverage: float
    readiness: Readiness
    eligibility: Eligibility
    criterion_results: tuple[CriterionResult, ...]
    economics: dict[str, Any] | None = None
    close_call: bool = False
    reasons: tuple[str, ...] = ()


def _validate_observed_number(
    observed: ObservedValue | None,
    field_name: str,
    *,
    non_negative: bool = False,
    strictly_positive: bool = False,
) -> None:
    if observed is None or observed.value is None:
        return
    if not isinstance(observed.value, (int, float)) or isinstance(observed.value, bool):
        raise TypeError(f"{field_name} must be numeric")
    value = float(observed.value)
    if strictly_positive and value <= 0:
        raise ValueError(f"{field_name} must be > 0")
    if non_negative and value < 0:
        raise ValueError(f"{field_name} must be >= 0")


def _validate_unit(observed: ObservedValue | None, field_name: str, expected_unit: str) -> None:
    if observed is None or observed.value is None:
        return
    if observed.unit != expected_unit:
        raise ValueError(f"{field_name} requires canonical unit {expected_unit!r}, got {observed.unit!r}")
