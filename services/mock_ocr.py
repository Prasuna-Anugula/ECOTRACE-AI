"""
EcoTrace AI — Mock OCR Service
──────────────────────────────
THIS IS A PROTOTYPE MOCK.
No real OCR model is used. Outputs are synthetically generated to demonstrate
the EcoTrace pipeline architecture.

Future integration: replace this module with a real OCR service that accepts
an image and returns {"serial": "...", "confidence": 0.xx}.
The Trust Score engine (trust_score.py) will not need to change.
"""

from __future__ import annotations
import random


# ── Mock serial pool ──────────────────────────────────────────────────────────
_MOCK_SERIALS: list[str] = [
    "SN-ECOTRACE-92831",
    "SN-ECOTRACE-77412",
    "SN-ECOTRACE-44019",
    "SN-ECOTRACE-29944",
    "SN-ECOTRACE-61823",
    "SN-ECOTRACE-50017",
    "SN-ECOTRACE-83421",
    "SN-ECOTRACE-11092",
    "SN-ECOTRACE-92831",  # intentional duplicate for demo uniqueness logic
]


def run_ocr(image=None, fixed_serial: str | None = None, confidence: float = 0.92) -> dict:
    """
    Simulate an OCR scan of a device label / IMEI sticker.

    Parameters
    ----------
    image       : uploaded image object (ignored in mock — kept for API parity)
    fixed_serial: if provided, return this serial (used by demo controls)
    confidence  : OCR confidence to simulate (0.0 – 1.0)

    Returns
    -------
    dict with keys: serial, confidence, serial_uniqueness, mode, disclaimer
    """
    serial = fixed_serial if fixed_serial else random.choice(_MOCK_SERIALS[:7])

    # Uniqueness: check against the mock pool (simple demo logic)
    occurrences = _MOCK_SERIALS.count(serial)
    serial_uniqueness = 1.0 if occurrences == 1 else max(0.0, 1.0 - (occurrences - 1) * 0.25)

    return {
        "serial":           serial,
        "confidence":       round(float(confidence), 4),
        "serial_uniqueness": round(serial_uniqueness, 4),
        "mode":             "MOCK",
        "disclaimer":       (
            "Prototype OCR — mocked output. "
            "No real OCR model has been applied. "
            "For architecture validation only."
        ),
    }
