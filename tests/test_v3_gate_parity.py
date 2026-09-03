from glassbox_auto.compat.v3_gates import (
    FamilyTestState,
    HistoricalCheck,
    canonical_family_gate,
    canonical_terms_gate,
    derive_ncap_gate,
    observed_recovered_v3_family_gate,
    observed_recovered_v3_terms_gate,
)
from glassbox_auto.models import Evidence, EvidenceGrade, ObservedValue


def verified(value, source):
    return ObservedValue(value, Evidence(EvidenceGrade.VERIFIED, source=source))


def test_ncap_composite_reproduces_recovered_thresholds_with_lineage():
    result = derive_ncap_gate(verified(2021, "ncap-year"), verified(5, "ncap-stars"))
    assert result.value is True
    assert result.evidence.grade == EvidenceGrade.VERIFIED
    assert "ncap-year" in result.evidence.lineage
    assert "ncap-stars" in result.evidence.lineage


def test_ncap_missing_component_is_unknown():
    result = derive_ncap_gate(verified(2021, "ncap-year"), None)
    assert result.value is None
    assert result.evidence.grade == EvidenceGrade.UNKNOWN


def test_pc08_observed_formula_ignores_actual_dealbreaker_row():
    # Observed recovered formula reads the Date row instead of Dealbreaker.
    observed = observed_recovered_v3_family_gate(
        date_field="2026-09-03",
        child_seat=FamilyTestState.PASS,
        stroller=FamilyTestState.PASS,
    )
    canonical = canonical_family_gate(
        dealbreaker=True,
        child_seat=FamilyTestState.PASS,
        stroller=FamilyTestState.PASS,
    )
    assert observed == HistoricalCheck.PASS
    assert canonical == HistoricalCheck.FAIL


def test_family_gate_concern_and_missing_states():
    assert canonical_family_gate(
        dealbreaker=False,
        child_seat=FamilyTestState.CONCERN,
        stroller=FamilyTestState.PASS,
    ) == HistoricalCheck.CHECK
    assert canonical_family_gate(
        dealbreaker=False,
        child_seat=FamilyTestState.UNKNOWN,
        stroller=FamilyTestState.PASS,
    ) == HistoricalCheck.TO_TEST


def test_pc09_observed_terms_gate_can_pass_without_exit_terms():
    observed = observed_recovered_v3_terms_gate(minimum_price_in_binding=100000)
    canonical = canonical_terms_gate(
        binding_period_known=True,
        minimum_price_in_binding=100000,
        termination_terms_known=False,
        return_terms_known=False,
    )
    assert observed == HistoricalCheck.PASS
    assert canonical == HistoricalCheck.UNKNOWN


def test_canonical_terms_gate_requires_all_operational_evidence():
    assert canonical_terms_gate(
        binding_period_known=True,
        minimum_price_in_binding=100000,
        termination_terms_known=True,
        return_terms_known=True,
    ) == HistoricalCheck.PASS
    assert canonical_terms_gate(
        binding_period_known=True,
        minimum_price_in_binding=None,
        termination_terms_known=True,
        return_terms_known=True,
    ) == HistoricalCheck.UNKNOWN
