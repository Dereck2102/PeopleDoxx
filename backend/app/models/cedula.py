from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, field_validator

from app.models.report import ScraperResult


def _validate_ecuadorian_cedula(cedula: str) -> str:
    """
    Validate an Ecuadorian national ID (cédula) number.

    Rules:
      - Must be exactly 10 digits.
      - Province code (digits 1-2) must be 01-24 or 30.
      - Third digit must be 0-5 (natural person).
      - Luhn-like Módulo 10 check: coefficients [2,1,2,1,2,1,2,1,2],
        multiply each of the first 9 digits by its coefficient; if product ≥ 10,
        subtract 9; sum all results; check digit = (10 - (total % 10)) % 10
        and must equal the 10th digit.

    Raises ValueError with a descriptive message on failure.
    """
    if not cedula.isdigit() or len(cedula) != 10:
        raise ValueError("La cédula debe contener exactamente 10 dígitos numéricos.")

    province = int(cedula[:2])
    valid_provinces = set(range(1, 25)) | {30}
    if province not in valid_provinces:
        raise ValueError(
            f"Código de provincia inválido '{cedula[:2]}'. Debe ser 01-24 o 30."
        )

    third_digit = int(cedula[2])
    if third_digit >= 6:
        raise ValueError(
            "El tercer dígito debe ser menor que 6 (persona natural)."
        )

    coefficients = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    digits = [int(d) for d in cedula]
    total = 0
    for i, coeff in enumerate(coefficients):
        product = digits[i] * coeff
        if product >= 10:
            product -= 9
        total += product

    expected_check = (10 - (total % 10)) % 10
    if expected_check != digits[9]:
        raise ValueError(
            f"Dígito verificador inválido. Se esperaba {expected_check}, "
            f"se obtuvo {digits[9]}."
        )

    return cedula


class CedulaRequest(BaseModel):
    """Request model for a cédula lookup."""

    cedula: str

    @field_validator("cedula")
    @classmethod
    def validate_cedula(cls, value: str) -> str:
        value = value.strip()
        return _validate_ecuadorian_cedula(value)


class CedulaResponse(BaseModel):
    """Response model for a cédula lookup."""

    cedula: str
    results: list[ScraperResult]
    generated_at: datetime
    total_sources: int
    successful_sources: int

    @classmethod
    def from_results(cls, cedula: str, results: list[ScraperResult]) -> "CedulaResponse":
        return cls(
            cedula=cedula,
            results=results,
            generated_at=datetime.now(tz=timezone.utc),
            total_sources=len(results),
            successful_sources=sum(1 for r in results if r.success),
        )
