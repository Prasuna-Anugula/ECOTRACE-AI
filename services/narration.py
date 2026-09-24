"""
EcoTrace AI — Narration Generation Service (Stage 8 / 9)
─────────────────────────────────────────────────────────
THIS IS A PROTOTYPE MOCK.
No LLM or RAG pipeline is used. Narration text is template-generated to
demonstrate the EcoTrace compliance narration flow.

Future integration: replace generate_narration() with a real RAG + LLM call.
The narration_confidence scoring and hard-gate logic below will remain.

IMPORTANT: narration is only generated if Stage 7 (Processing Gate) PASSED.
"""

from __future__ import annotations
from config import (
    NARRATION_AUTO_BADGE_MIN,
    NARRATION_HITL_MIN,
    STATUS_AUTO_VERIFIED,
    STATUS_HITL,
    STATUS_REJECTED,
    STATUS_BLOCKED,
)


# ── Narration confidence soft-score sub-components ────────────────────────────
_NARRATION_WEIGHTS: dict[str, float] = {
    "regulatory_grounding":          0.35,
    "cross_document_consistency":    0.30,
    "chronological_consistency":     0.20,
    "threshold_conflict_flags":      0.15,
}


def generate_narration(record: dict) -> dict:
    """
    Generate a mock compliance narration for a verified record.

    Parameters
    ----------
    record : dict with keys from session state or a mock_transaction entry.
             Must include gate_result["passed"] == True to proceed.

    Returns
    -------
    dict:
        allowed           : bool (False if gate blocked narration)
        narration_text    : str | None
        narration_confidence : float | None
        narration_status  : str
        hard_gates        : list[{"label", "passed"}]
        soft_scores       : list[{"label", "weight", "value", "contribution"}]
        badge_decision    : str
        disclaimer        : str
    """
    gate_passed: bool = record.get("gate_passed", False)

    # ── Narration is blocked if the processing gate failed ──────────────────
    if not gate_passed:
        return {
            "allowed":              False,
            "narration_text":       None,
            "narration_confidence": None,
            "narration_status":     STATUS_BLOCKED,
            "hard_gates":           [],
            "soft_scores":          [],
            "badge_decision":       "NOT ISSUED — Processing Gate failed",
            "disclaimer":           "Prototype-generated narration",
            "block_reason": (
                "Processing completion evidence is required before "
                "compliance narration can be generated."
            ),
        }

    # ── Extract record fields ────────────────────────────────────────────────
    batch_id      = record.get("batch_id",      "BATCH-2026-00124")
    item_state    = record.get("item_state",    "dismantled")
    component     = record.get("component",     "PCB")
    serial        = record.get("serial",        "SN-ECOTRACE-92831")
    facility_name = record.get("facility_name", "GreenCycle Hyderabad")
    trust_score   = record.get("trust_score",   0.94)
    trust_status  = record.get("trust_status",  STATUS_AUTO_VERIFIED)
    conf          = record.get("component_confidence", record.get("ocr_confidence", 0.94))

    # ── Build template narration ─────────────────────────────────────────────
    if item_state == "dismantled":
        identity_sentence = (
            f"The item was classified as a {component} component with a "
            f"classification confidence of {int(conf * 100)}%."
        )
    else:
        identity_sentence = (
            f"The item was identified via OCR with serial number {serial}, "
            f"with a confidence of {int(conf * 100)}%."
        )

    narration_text = (
        f"EcoTrace verified that batch {batch_id} was received at the registered "
        f"processing facility ({facility_name}). "
        f"{identity_sentence} "
        f"The associated evidence passed the Evidence Trust Score threshold "
        f"(score: {trust_score:.3f}, status: {trust_status}). "
        f"Processing completion evidence was submitted within the required time window. "
        f"All mandatory verification conditions have been satisfied for this batch."
    )

    # ── Hard gates ───────────────────────────────────────────────────────────
    # For prototype: hard gates are derived from the trust score and duplicate check
    numeric_verification_passed = trust_score >= 0.55
    no_duplicate_claim          = record.get("serial_uniqueness", 1.0) >= 0.99 or item_state == "dismantled"

    hard_gates = [
        {"label": "Numeric verification",   "passed": numeric_verification_passed},
        {"label": "No duplicate item claim", "passed": no_duplicate_claim},
    ]
    hard_gates_ok = all(g["passed"] for g in hard_gates)

    # ── Soft scores (mock values, realistic range) ────────────────────────────
    # Values derived from trust_score to stay consistent with demo controls
    reg_grounding   = round(min(1.0, trust_score * 0.97), 3)
    cross_doc       = round(min(1.0, trust_score * 0.95), 3)
    chrono          = round(min(1.0, trust_score * 0.98), 3)
    threshold_flags = round(min(1.0, trust_score * 0.93), 3)

    soft_scores = [
        {
            "label":        "Regulatory Grounding",
            "weight":       _NARRATION_WEIGHTS["regulatory_grounding"],
            "value":        reg_grounding,
            "contribution": round(reg_grounding * _NARRATION_WEIGHTS["regulatory_grounding"], 4),
        },
        {
            "label":        "Cross-document Consistency",
            "weight":       _NARRATION_WEIGHTS["cross_document_consistency"],
            "value":        cross_doc,
            "contribution": round(cross_doc * _NARRATION_WEIGHTS["cross_document_consistency"], 4),
        },
        {
            "label":        "Chronological Consistency",
            "weight":       _NARRATION_WEIGHTS["chronological_consistency"],
            "value":        chrono,
            "contribution": round(chrono * _NARRATION_WEIGHTS["chronological_consistency"], 4),
        },
        {
            "label":        "Threshold / Version Conflict Flags",
            "weight":       _NARRATION_WEIGHTS["threshold_conflict_flags"],
            "value":        threshold_flags,
            "contribution": round(threshold_flags * _NARRATION_WEIGHTS["threshold_conflict_flags"], 4),
        },
    ]

    narration_confidence = round(sum(s["contribution"] for s in soft_scores), 4)

    # ── Narration status and badge decision ───────────────────────────────────
    if not hard_gates_ok:
        narration_status = STATUS_REJECTED
        badge_decision   = "REJECTED — Hard gate failure"
    elif narration_confidence >= NARRATION_AUTO_BADGE_MIN:
        narration_status = STATUS_AUTO_VERIFIED
        badge_decision   = "AUTO-ISSUED"
    elif narration_confidence >= NARRATION_HITL_MIN:
        narration_status = STATUS_HITL
        badge_decision   = "HITL REVIEW"
    else:
        narration_status = STATUS_REJECTED
        badge_decision   = "REJECTED — Low narration confidence"

    return {
        "allowed":               True,
        "narration_text":        narration_text,
        "narration_confidence":  narration_confidence,
        "narration_status":      narration_status,
        "hard_gates":            hard_gates,
        "soft_scores":           soft_scores,
        "badge_decision":        badge_decision,
        "disclaimer":            "Prototype-generated narration — no LLM or RAG pipeline used.",
    }
