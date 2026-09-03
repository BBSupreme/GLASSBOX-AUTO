import pytest

from glassbox_auto.models import (
    Criterion,
    Evidence,
    EvidenceGrade,
    GateDefinition,
    ObservedValue,
    PreferenceLabel,
    UtilityAnchors,
)
from glassbox_auto.scoring import score_candidate


def verified(value):
    return ObservedValue(value, Evidence(EvidenceGrade.VERIFIED, source="must-have-falsifier"))


def must_have(**kwargs):
    return Criterion(
        "critical",
        "critical",
        PreferenceLabel.MUST_HAVE,
        UtilityAnchors(0, 1, 2, 0.8),
        GateDefinition(">=", 1),
        **kwargs,
    )


@pytest.mark.parametrize(
    "criterion, dimensions",
    [
        (must_have(base_weight=0), {}),
        (must_have(subweight=0), {}),
        (must_have(weight_cap=0), {}),
        (must_have(dimension="family"), {"family": 0}),
    ],
)
def test_must_have_must_retain_positive_effective_weight(criterion, dimensions):
    with pytest.raises(ValueError, match="positive effective weight"):
        score_candidate((criterion,), {"critical": verified(2)}, dimensions)
