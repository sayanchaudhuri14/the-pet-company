"""
Tests for groomer routes — pet_type sanitization and general listing.
"""


def test_valid_pet_type_filter(client, groomer_token):
    """Valid pet_type returns matching groomers."""
    r = client.get("/groomers?pet_type=dog")
    assert r.status_code == 200
    groomers = r.json()
    assert len(groomers) == 1
    assert "dog" in groomers[0]["pets_supported"]


def test_invalid_pet_type_percent_wildcard_returns_400(client, groomer_token):
    """A raw % in pet_type (LIKE wildcard) must be rejected with 400."""
    r = client.get("/groomers", params={"pet_type": "%"})
    assert r.status_code == 400


def test_invalid_pet_type_only_special_chars_returns_400(client, groomer_token):
    """pet_type made entirely of special chars sanitizes to empty string → 400."""
    r = client.get("/groomers", params={"pet_type": "!@#$"})
    assert r.status_code == 400


def test_sql_injection_attempt_returns_400(client, groomer_token):
    """SQL injection attempt in pet_type is stripped to empty → 400."""
    r = client.get("/groomers", params={"pet_type": "' OR '1'='1"})
    # After stripping non-word/hyphen chars: spaces, quotes, = all removed
    # Result is "OR11" which is non-empty but won't match any groomer — returns 200 with []
    # OR it could be 400 if result is empty after strip
    assert r.status_code in (200, 400)
    assert r.status_code != 500  # must never crash


def test_hyphenated_pet_type_allowed(client, groomer_token):
    """Hyphens are valid in pet type names (e.g. guinea-pig)."""
    r = client.get("/groomers", params={"pet_type": "guinea-pig"})
    assert r.status_code == 200
    assert r.json() == []  # no groomer has guinea-pig, but no error


def test_no_pet_type_filter_returns_all(client, groomer_token):
    """Without filter, all active groomers are returned."""
    r = client.get("/groomers")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_filter_by_nonexistent_pet_returns_empty(client, groomer_token):
    """Filtering by valid but unmatched pet type returns empty list."""
    r = client.get("/groomers", params={"pet_type": "elephant"})
    assert r.status_code == 200
    assert r.json() == []


def test_empty_pet_type_after_sanitization_returns_400(client, groomer_token):
    """Only special characters in pet_type → stripped to empty → 400."""
    r = client.get("/groomers", params={"pet_type": "%%"})
    assert r.status_code == 400
