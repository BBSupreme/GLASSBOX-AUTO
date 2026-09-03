import pytest

from glassbox_auto.compat.v3 import SourceTrack
from glassbox_auto.compat.v3_report import ParityStatus, compare_exact, compare_numeric, unresolved


def test_exact_comparison_reports_match_or_difference():
    assert compare_exact(
        finding_id="x",
        topic="gate",
        source_track=SourceTrack.RECOVERED_V3_2,
        observed="PASS",
        canonical="PASS",
    ).status == ParityStatus.MATCH
    assert compare_exact(
        finding_id="x",
        topic="gate",
        source_track=SourceTrack.RECOVERED_V3_2,
        observed="PASS",
        canonical="FAIL",
    ).status == ParityStatus.DIFFERENCE


def test_numeric_comparison_requires_declared_tolerance():
    assert compare_numeric(
        finding_id="x",
        topic="score",
        source_track=SourceTrack.RECOVERED_V3_2,
        observed=8.50001,
        canonical=8.5,
        tolerance=0.001,
    ).status == ParityStatus.MATCH
    assert compare_numeric(
        finding_id="x",
        topic="score",
        source_track=SourceTrack.RECOVERED_V3_2,
        observed=8.51,
        canonical=8.5,
        tolerance=0.001,
    ).status == ParityStatus.DIFFERENCE
    with pytest.raises(ValueError):
        compare_numeric(
            finding_id="x",
            topic="score",
            source_track=SourceTrack.RECOVERED_V3_2,
            observed=8.5,
            canonical=8.5,
            tolerance=-1,
        )


def test_unresolved_cannot_be_silent():
    finding = unresolved(
        finding_id="PC-01",
        topic="close-call coverage",
        source_track=SourceTrack.RECOVERED_V3_2,
        observed="critical4",
        canonical="weight coverage",
        notes="Exact v3.2.1 fixture has not been recovered.",
    )
    assert finding.status == ParityStatus.UNRESOLVED
    with pytest.raises(ValueError):
        unresolved(
            finding_id="x",
            topic="x",
            source_track=SourceTrack.RECOVERED_V3_2,
            notes="",
        )
