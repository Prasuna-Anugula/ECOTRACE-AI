"""
EcoTrace AI — Processing Completion Gate (Stage 7)
──────────────────────────────────────────────────
Hard gate: a high Trust Score does NOT prove that the item was actually
processed. This gate requires independent processing completion evidence
before narration or badge issuance can proceed.

Three conditions checked (all must pass):
  1. Completion evidence has been submitted.
  2. Evidence was submitted within the allowed time window.
  3. Mass balance is plausible — declared output weight is within
     acceptable range given input weight and item type.

Mass balance rationale:
  A photo of "destruction" is trivially fakeable. Mass balance adds a
  quantitative check: 10 kg of PCB in should yield approximately 2 kg of
  copper, 3 kg of plastic, 0.5 kg of steel, etc. If declared output is
  less than MASS_BALANCE_MIN_OUTPUT_FRACTION × input, the gate flags it.
  In production this is verified against downstream smelter/recycler invoices.
"""

from __future__ import annotations
from config import (
    STATUS_PASSED,
    STATUS_HITL,
    MASS_BALANCE_PROFILES,
    MASS_BALANCE_MIN_OUTPUT_FRACTION,
)


def check_mass_balance(
    input_weight_kg:    float,
    declared_output_kg: float,
    item_type:          str = "default",
) -> dict:
    """
    Check whether declared output weight is plausible for the given input.

    Parameters
    ----------
    input_weight_kg    : total weight of items received (kg)
    declared_output_kg : total weight of processed outputs declared (kg)
    item_type          : component/device type key for MASS_BALANCE_PROFILES

    Returns
    -------
    dict:
        passed          : bool
        input_kg        : float
        declared_kg     : float
        min_expected_kg : float
        ratio           : float  (declared / input)
        profile_used    : str
        flag            : str | None  (human-readable issue if failed)
    """
    profile = MASS_BALANCE_PROFILES.get(item_type, MASS_BALANCE_PROFILES["default"])
    min_expected = round(input_weight_kg * MASS_BALANCE_MIN_OUTPUT_FRACTION, 2)
    ratio = round(declared_output_kg / input_weight_kg, 3) if input_weight_kg > 0 else 0.0

    passed = declared_output_kg >= min_expected
    flag = None if passed else (
        f"Declared output {declared_output_kg:.1f} kg is below minimum expected "
        f"{min_expected:.1f} kg ({int(MASS_BALANCE_MIN_OUTPUT_FRACTION*100)}% of "
        f"input {input_weight_kg:.1f} kg). Possible under-reporting or "
        f"incomplete processing. Verify against downstream invoices."
    )

    return {
        "passed":           passed,
        "input_kg":         input_weight_kg,
        "declared_kg":      declared_output_kg,
        "min_expected_kg":  min_expected,
        "ratio":            ratio,
        "profile_used":     item_type,
        "flag":             flag,
    }


def check_processing_gate(
    completion_evidence_submitted: bool,
    within_time_window:            bool,
    batch_id:                      str   = "BATCH-2026-00124",
    processing_timestamp:          str   = "21 Sep 2026, 11:32 AM",
    time_window_hours:             int   = 72,
    input_weight_kg:               float = 0.0,
    declared_output_kg:            float = 0.0,
    item_type:                     str   = "default",
) -> dict:
    """
    Evaluate the Processing Completion Gate.

    Parameters
    ----------
    completion_evidence_submitted : True if destruction/dismantling proof exists
    within_time_window            : True if evidence was submitted within window
    batch_id                      : batch identifier
    processing_timestamp          : human-readable timestamp
    time_window_hours             : maximum hours allowed (from config)
    input_weight_kg               : total input weight for mass balance check
    declared_output_kg            : declared processed output weight
    item_type                     : component type for mass balance profile

    Returns
    -------
    dict with keys:
        passed, status, reason, batch_id, processing_timestamp,
        time_window_hours, within_window, evidence_submitted,
        mass_balance, conditions
    """
    # ── Mass balance check ────────────────────────────────────────────────────
    if input_weight_kg > 0:
        mb = check_mass_balance(input_weight_kg, declared_output_kg, item_type)
    else:
        # Weight not provided in prototype demo — skip mass balance
        mb = {
            "passed":          True,
            "input_kg":        0.0,
            "declared_kg":     0.0,
            "min_expected_kg": 0.0,
            "ratio":           0.0,
            "profile_used":    "not checked",
            "flag":            None,
        }

    mass_balance_ok = mb["passed"]

    # ── Conditions list for UI ────────────────────────────────────────────────
    conditions = [
        {
            "label":  "Processing completion evidence submitted",
            "passed": completion_evidence_submitted,
            "detail": (
                "Destruction / dismantling proof received"
                if completion_evidence_submitted
                else "No processing completion evidence on record"
            ),
        },
        {
            "label":  f"Evidence within {time_window_hours}-hour time window",
            "passed": within_time_window,
            "detail": (
                f"Submitted within the required {time_window_hours}-hour window"
                if within_time_window
                else f"Evidence submitted outside the {time_window_hours}-hour window"
            ),
        },
        {
            "label":  "Mass balance plausible",
            "passed": mass_balance_ok,
            "detail": (
                mb["flag"] if not mass_balance_ok
                else (
                    f"Declared output {mb['declared_kg']:.1f} kg meets minimum "
                    f"{mb['min_expected_kg']:.1f} kg"
                    if mb["input_kg"] > 0
                    else "Mass balance not checked (weight not provided in prototype)"
                )
            ),
        },
    ]

    gate_passed = completion_evidence_submitted and within_time_window and mass_balance_ok

    # ── Reason message ────────────────────────────────────────────────────────
    if gate_passed:
        status = STATUS_PASSED
        reason = (
            "All three processing completion conditions satisfied. "
            "Evidence Attestation and badge issuance may proceed."
        )
    elif not completion_evidence_submitted:
        status = STATUS_HITL
        reason = (
            "Processing completion evidence has not been submitted. "
            "A high Evidence Trust Score does not substitute for "
            "actual processing proof. Badge issuance is blocked."
        )
    elif not within_time_window:
        status = STATUS_HITL
        reason = (
            f"Processing evidence was submitted outside the {time_window_hours}-hour window. "
            "Held for HITL review. Badge issuance is blocked."
        )
    else:
        status = STATUS_HITL
        reason = (
            "Mass balance check failed. Declared output weight is below the "
            "minimum expected yield for the declared input weight. "
            "Verify against downstream smelter / recycler invoices."
        )

    return {
        "passed":               gate_passed,
        "status":               status,
        "reason":               reason,
        "batch_id":             batch_id,
        "processing_timestamp": processing_timestamp,
        "time_window_hours":    time_window_hours,
        "within_window":        within_time_window,
        "evidence_submitted":   completion_evidence_submitted,
        "mass_balance":         mb,
        "conditions":           conditions,
    }
