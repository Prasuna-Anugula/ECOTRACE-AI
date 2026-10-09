"""
EcoTrace AI — Mock OCR Service
──────────────────────────────
THIS IS A PROTOTYPE MOCK.
No real OCR model is used. Outputs are synthetically generated.

Privacy compliance — DPDP Act 2023 (Fix #11):
  Raw IMEI/serial numbers are personal data. EcoTrace never stores
  raw serials in the database. Instead:
    1. OCR reads the raw serial from the device label.
    2. The raw serial is immediately hashed (SHA-256 with a fixed salt).
    3. Only the pseudonymised hash is stored and displayed.
    4. The hash prefix (first 12 chars) is shown in the UI as the
       "masked serial" — enough for display, not enough to reverse.
    5. Uniqueness checks run on the hash — not the raw value.

  This prototype demonstrates the pseudonymisation step even though
  the input serials are synthetic.

Cross-platform limitation (Fix #4):
  Serial uniqueness is checked WITHIN this system only.
  Cross-platform double-claiming (same device submitted to two platforms)
  requires a national IMEI hash registry operated by CPCB or a delegated
  neutral body. EcoTrace's hash format is registry-compatible:
    SHA-256(salt + raw_serial) → 64-char hex
  When a national registry exists, the uniqueness check replaces
  the local DB lookup with a registry API call. No other code changes needed.
"""

from __future__ import annotations
import hashlib
import random

from config import PRIVACY_HASH_SERIALS


# Salt for serial hashing — in production this is a secret per-deployment value
_SERIAL_SALT = "ecotrace-2026-prototype-salt"

# ── Mock serial pool (synthetic — never real IMEI values) ────────────────────
_MOCK_SERIALS: list[str] = [
    "SN-ECOTRACE-92831",
    "SN-ECOTRACE-77412",
    "SN-ECOTRACE-44019",
    "SN-ECOTRACE-29944",
    "SN-ECOTRACE-61823",
    "SN-ECOTRACE-50017",
    "SN-ECOTRACE-83421",
    "SN-ECOTRACE-11092",
    "SN-ECOTRACE-92831",   # intentional duplicate for demo uniqueness logic
]


def _pseudonymise(raw_serial: str) -> str:
    """
    Return SHA-256 hash of (salt + serial).
    Only the hash is stored — raw serial is discarded after this call.
    """
    payload = (_SERIAL_SALT + raw_serial).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _masked_display(hash_hex: str) -> str:
    """
    Return a display-safe masked version of the hash.
    Shows first 8 chars + '...' — enough to identify in UI, not reversible.
    """
    return f"EA-{hash_hex[:8].upper()}..."


def run_ocr(
    image=None,
    fixed_serial: str | None = None,
    confidence:   float = 0.92,
) -> dict:
    """
    Simulate an OCR scan of a device label / IMEI sticker.

    Parameters
    ----------
    image        : uploaded image (ignored in mock — kept for API parity)
    fixed_serial : if provided, use this serial (demo controls)
    confidence   : OCR confidence to simulate (0.0 – 1.0)

    Returns
    -------
    dict:
        serial_hash      : str   — pseudonymised serial (SHA-256, stored)
        serial_display   : str   — masked version for UI display
        confidence       : float
        serial_uniqueness: float — 1.0 if hash unique in local DB
        cross_platform_note : str — limitation caveat
        mode             : "MOCK"
        privacy_note     : str
        disclaimer       : str
    """
    raw_serial = fixed_serial if fixed_serial else random.choice(_MOCK_SERIALS[:7])

    # Pseudonymise immediately — raw serial not returned or stored
    serial_hash    = _pseudonymise(raw_serial) if PRIVACY_HASH_SERIALS else raw_serial
    serial_display = _masked_display(serial_hash) if PRIVACY_HASH_SERIALS else raw_serial

    # Uniqueness check runs on raw serial here (prototype).
    # In production: uniqueness check runs on the hash against the local DB.
    occurrences       = _MOCK_SERIALS.count(raw_serial)
    serial_uniqueness = 1.0 if occurrences == 1 else max(0.0, 1.0 - (occurrences - 1) * 0.25)

    return {
        "serial_hash":       serial_hash,
        "serial_display":    serial_display,
        "confidence":        round(float(confidence), 4),
        "serial_uniqueness": round(serial_uniqueness, 4),
        "cross_platform_note": (
            "Uniqueness verified within EcoTrace only. "
            "Cross-platform double-claiming requires a national IMEI hash "
            "registry (CPCB or delegated body). EcoTrace is registry-compatible."
        ),
        "mode": "MOCK",
        "privacy_note": (
            "Raw serial pseudonymised via SHA-256. "
            "Only the hash is stored. DPDP Act 2023 compliant."
        ),
        "disclaimer": (
            "Prototype OCR — mocked output. "
            "No real OCR model applied. Architecture validation only."
        ),
    }
