"""Regression probes for the separately reported Codex review findings.

Synthetic fixtures only. These assertions reject legacy/inconsistent serialized
identity instead of silently rewriting caller-provided cached results.
"""
from dataclasses import replace

import pytest

from glassbox_auto.engine import rank_candidates
from glassbox_auto.integrity import make_candidate_id
from glassbox_auto.models import Readiness
from test_public_readiness_adversarial import evaluate


@pytest.mark.parametrize('vid,oid,stale', [
    ('a:b', 'c', 'a:b:c'),
    ('a', 'b:c', 'a:b:c'),
    ('a%3Ab', 'c', 'a%3Ab:c'),
    ('v', 'o', 'unrelated'),
])
def test_rerank_rejects_noncanonical_candidate_id(vid, oid, stale):
    original = evaluate(vid=vid, oid=oid)
    assert original.candidate_id != stale
    with pytest.raises(ValueError, match='canonical|match'):
        rank_candidates([replace(original, candidate_id=stale)])


@pytest.mark.parametrize('character', [
    '\u0080', '\u0085', '\u009f', '\u200b', '\u202e', '\u2066', '\u2028', '\u2029',
])
def test_rejects_unicode_controls_formats_and_line_separators(character):
    bad = f'a{character}b'
    with pytest.raises(ValueError, match='identifier|control'):
        evaluate(vid=bad)
    with pytest.raises(ValueError, match='identifier|control'):
        evaluate(oid=bad)
    result = evaluate()
    with pytest.raises(ValueError, match='identifier|control'):
        rank_candidates([replace(result, vehicle_id=bad)])


@pytest.mark.parametrize('vid,oid', [
    ('car-1', 'offer_2'), ('a:b', 'c'), ('a', 'b:c'),
    ('a%3Ab', 'c'), ('æøå', '東京'), ('a b', 'é'),
])
def test_canonical_unicode_and_reserved_ids_rerank_idempotently(vid, oid):
    result = evaluate(vid=vid, oid=oid)
    assert result.candidate_id == make_candidate_id(vid, oid)
    once = rank_candidates([result])
    assert once == rank_candidates(once)
    assert once[0].readiness == Readiness.READY


def test_duplicate_rejection_precedes_noncanonical_migration_error():
    first = evaluate(vid='a')
    second = evaluate(vid='b')
    with pytest.raises(ValueError, match='Duplicate'):
        rank_candidates([first, replace(second, candidate_id=first.candidate_id)])
    with pytest.raises(ValueError, match='Duplicate'):
        rank_candidates([first, replace(first, candidate_id='different')])
