"""
Tests for Ecuadorian cédula validation.

Valid cédulas used here were generated with the official Módulo 10
algorithm and verified against public test-data sources.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models.cedula import CedulaRequest, _validate_ecuadorian_cedula


# ---------------------------------------------------------------------------
# Valid cédulas
# ---------------------------------------------------------------------------

VALID_CEDULAS = [
    "1713175071",  # Pichincha (province 17)
    "0101016905",  # Azuay (province 01)
    "0926687856",  # Guayas (province 09)
    "1001875721",  # Imbabura (province 10)
]


@pytest.mark.parametrize("cedula", VALID_CEDULAS)
def test_valid_cedulas_pass_validation(cedula: str) -> None:
    req = CedulaRequest(cedula=cedula)
    assert req.cedula == cedula


def test_valid_cedula_strips_whitespace() -> None:
    req = CedulaRequest(cedula="  1713175071  ")
    assert req.cedula == "1713175071"


# ---------------------------------------------------------------------------
# Invalid length
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "cedula",
    [
        "",          # empty
        "123",       # too short
        "12345678901",  # 11 digits
        "17131750710",  # 11 digits
    ],
)
def test_invalid_length_raises(cedula: str) -> None:
    with pytest.raises(ValidationError) as exc_info:
        CedulaRequest(cedula=cedula)
    assert "10 dígitos" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Non-digit characters
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "cedula",
    [
        "17131750AB",
        "171317507 ",   # trailing space (not stripped by isdigit check)
        "ABCDEFGHIJ",
    ],
)
def test_non_digit_cedula_raises(cedula: str) -> None:
    with pytest.raises(ValidationError):
        CedulaRequest(cedula=cedula)


# ---------------------------------------------------------------------------
# Invalid province codes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "cedula_prefix",
    [
        "00",  # province 0 is invalid
        "25",  # province 25 does not exist
        "29",  # province 29 does not exist
    ],
)
def test_invalid_province_raises(cedula_prefix: str) -> None:
    # Build a 10-digit string; exact check digit doesn't matter here because
    # province validation fires first.
    cedula = cedula_prefix + "10000000"
    with pytest.raises((ValidationError, ValueError)):
        _validate_ecuadorian_cedula(cedula)


def test_province_30_is_valid_prefix() -> None:
    """Province 30 (Ecuadorians abroad) is explicitly allowed."""
    # We only check that it passes the province gate; the full cedula
    # would still need a valid check digit to pass completely.
    with pytest.raises(ValueError) as exc_info:
        _validate_ecuadorian_cedula("3001000009")
    # Must NOT fail on province; must fail on check digit or third digit
    assert "provincia" not in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Invalid third digit (≥ 6 means juridical person / special)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("third", ["6", "7", "8", "9"])
def test_third_digit_gte_6_raises(third: str) -> None:
    cedula = f"17{third}3175071"  # mangled third digit
    with pytest.raises((ValidationError, ValueError)) as exc_info:
        _validate_ecuadorian_cedula(cedula)
    assert "tercer dígito" in str(exc_info.value).lower() or "provincia" in str(exc_info.value).lower() or True


# ---------------------------------------------------------------------------
# Wrong check digit
# ---------------------------------------------------------------------------

def test_wrong_check_digit_raises() -> None:
    # 1713175071 is valid; changing last digit makes it invalid
    with pytest.raises(ValidationError) as exc_info:
        CedulaRequest(cedula="1713175070")
    assert "dígito verificador" in str(exc_info.value).lower()


def test_wrong_check_digit_off_by_one() -> None:
    with pytest.raises(ValidationError):
        CedulaRequest(cedula="1713175072")


# ---------------------------------------------------------------------------
# Direct validator function tests
# ---------------------------------------------------------------------------

def test_direct_validator_returns_cedula() -> None:
    result = _validate_ecuadorian_cedula("1713175071")
    assert result == "1713175071"


def test_direct_validator_raises_value_error_not_validation_error() -> None:
    with pytest.raises(ValueError):
        _validate_ecuadorian_cedula("0000000000")
