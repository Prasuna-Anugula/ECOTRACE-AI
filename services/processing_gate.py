"""
EcoTrace AI — Processing Completion Gate (Stage 7)
──────────────────────────────────────────────────
Hard gate: a high Trust Score does NOT prove that the item was actually
processed. This gate requires independent processing completion evidence
before narration or badge issuance can proceed.

Both conditions must be true for the gate to PASS:
  1. Completion evidence has been submitted.
  2. Evidence was submitted within the allowed time window.
"""

from __future__ import annotations
from config import STATUS_PASSED, STATUS_HITL


def check_processing_gate(
    completion_evidence_submitted: bool,
    within_time_window: bool,
    batch_id: str = "BATCH-2026-00124",
    processing_timestamp: str = "21 Sep 2026, 11:32 AM",
    time_window_hours: int = 72,
) -> dict:
    """
    Evaluate the Processing Completion Gate.

    Parameters
    ----------
    completion_evidence_submitted : True if destruction/dismantling proof exists
    within_time_window            : True if evidence was submitted within the allowed window
    batch_id                      : identifier linked to this processing event
    processing_timestamp          : human-readable timestamp of the processing event
    time_window_hours             : configured maximum hours allowed (from config)

    Returns
    -------
    dict:
        passed              : bool
        status              : "PASSED" | "HITL"  (HITL means hold for human review)
        reason              : human-readable explanation
        batch_id            : echoed back
        processing_timestamp: echoed back
        time_window_hours   : echoed back
        within_window       : bool
        evidence_submitted  : bool
        conditions          : list of {"label", "passed", "detail"} for UI display
    """
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
    ]

    gate_passed = completion_evidence_submitted and within_time_window

    if gate_passed:
        status = STATUS_PASSED
        reason = (
            "Both processing completion conditions satisfied. "
            "Narration generation and badge issuance may proceed."
        )
    elif not completion_evidence_submitted:
        status = STATUS_HITL
        reason = (
            "Processing completion evidence has not been submitted. "
            "A high Evidence Trust Score does not substitute for "
            "actual processing proof. Badge issuance is blocked."
        )
    else:
        status = STATUS_HITL
        reason = (
            f"Processing evidence was submitted outside the {time_window_hours}-hour window. "
            "Held for HITL review. Badge issuance is blocked."
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
        "conditions":           conditions,
    }
