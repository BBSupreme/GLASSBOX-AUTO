from glassbox_auto.release_integrity import check_release_integrity


def test_release_integrity_v0_2_0_is_green():
    assert check_release_integrity("0.2.0") == []


def test_release_integrity_fails_wrong_expected_version():
    errors = check_release_integrity("9.9.9")
    assert any("expected" in error for error in errors)
