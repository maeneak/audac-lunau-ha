from __future__ import annotations

import pytest

from custom_components.audac_luna_u.utils import (
    parse_bool,
    parse_float,
    parse_int,
    validate_snapshot_name,
)


def test_parse_bool() -> None:
    assert parse_bool("TRUE") is True
    assert parse_bool(" false ") is False
    assert parse_bool("x") is None
    assert parse_bool(None) is None


def test_parse_int() -> None:
    assert parse_int("10") == 10
    assert parse_int("  -5 ") == -5
    assert parse_int("abc") is None
    assert parse_int(None) is None


def test_parse_float() -> None:
    assert parse_float("10.5") == 10.5
    assert parse_float(" -1 ") == -1.0
    assert parse_float("abc") is None
    assert parse_float(None) is None


def test_validate_snapshot_name() -> None:
    assert validate_snapshot_name("Lobby Day_1") == "Lobby Day_1"
    assert validate_snapshot_name("A/B:C*D?") == "ABCD"

    with pytest.raises(ValueError):
        validate_snapshot_name("!!!")
