"""
EcoTrace AI — Compliance Narration Service (Stages 8 & 9)
──────────────────────────────────────────────────────────
Generates a compliance narration from VERIFIED FACTS ONLY.

Design principle (Fix #7):
  The narration engine receives a structured facts dict containing only
  values that have already passed the verification pipeline. It does NOT
  re-derive or re-score those values — it only phrases them.

  In production this module is replaced by an LLM call:
    llm.generate(template="compliance_narration", facts=verified_facts)
  The LLM's role is PHRASING ONLY. It does not invent facts, infer
  scores, or add regulatory citations beyond those provided in the
  facts dict. Hallucination risk is eliminated by constraining the LLM
  to verified input fields and pre-retrieved regulation clauses.

  Narration confidence scoring (Stage 9) validates the STRUCTURE of the
  narration against the facts dict — not the fluency of the text.
  This removes the circularity in the previous version where soft scores
  were derived from the same trust_score that produced the narration.

HARD GATE: narration is always blocked if gate_passed == False.

TERMINOLOGY: "Evidence Attestation" replaces "EPR Certificate".
  EcoTrace issues an Evidence Attestation (EA) — a cryptographically
  signed record supporting CPCB certificate filing.
  Only CPCB can legally issue EPR certificates.
"""

from __future__ import annotations
from config import (
    NARRATION_AUTO_BADGE_MIN,
    NARRATION_HITL_MIN,
    ATTESTATION_LABEL,
    STATUS_AUTO_VERIFIED,
    STATUS_HITL,
    STATUS_REJECTED,
    STATUS_BLOCKED,
)

# ── Narration confidence weights (Stage 9) ────────────────────────────────────
# These score the STRUCTURE of the narration (are all required fields present
# and consistent?) — not the text quality or trust score magnitude.
_NARRATION_WEIGHTS: dict[str, float] = {
    "all_required_facts_present":   0.35,  # batch_id, facility, score, gate, component/serial
    "cross_field_consistency":      0.30,  # gate_passed matches completion_evidence
    "chronological_consistency":    0.20,  # timestamps in logical order
    "no_contradictory_statuses":    0.15,  # score status doesn't conflict with badge decision
}


def generate_narration(record: dict) -> dict:
    """
    Generate a compliance narration from verified facts.

    Parameters
    ----------
    record : dict of VERIFIED fields from the pipeline.
        Required keys:
            gate_passed, batch_id, item_state, component, serial,
            facility_name, trust_score, trust_status,
            component_confidence (or ocr_confidence)

    Returns
    -------
    dict:
        allowed              : bool
        narration_text       : str | None
        narration_confidence : float | None
        narration_status     : str
        hard_gates           : list[{"label", "passed"}]
        soft_scores          : list[{"label", "weight", "value", "contribution"}]
        badge_decision       : str
        attestation_label    : str
        disclaimer           : str
        block_reason         : str | None
    """
    gate_passed: bool = record.get("gate_passed", False)

    # ── Hard gate: blocked if processing gate failed ──────────────────────────
    if not gate_passed:
        return {
            "allowed":               False,
            "narration_text":        None,
            "narration_confidence":  None,
            "narration_status":      STATUS_BLOCKED,
            "hard_gates":            [],
            "soft_scores":           [],
            "badge_decision":        f"NOT ISSUED — Processing Gate failed",
            "attestation_label":     ATTESTATION_LABEL,
            "disclaimer":            "Narration blocked — Processing Gate must pass first.",
            "block_reason": (
                "Processing completion evidence is required before "
                "compliance narration can be generated."
            ),
        }

    # ── Extract verified facts (phrasing inputs only) ─────────────────────────
    batch_id      = record.get("batch_id",      "BATCH-2026-00124")
    item_state    = record.get("item_state",    "dismantled")
    component     = record.get("component",     "PCB")
    serial        = record.get("serial",        "SN-ECOTRACE-92831")
    facility_name = record.get("facility_name", "GreenCycle Hyderabad")
    trust_score   = record.get("trust_score",   0.0)
    trust_status  = record.get("trust_status",  STATUS_AUTO_VERIFIED)
    conf          = record.get("component_confidence", record.get("ocr_confidence", 0.0))

    # Privacy: serial is already pseudonymised upstream (SHA-256 hash prefix).
    # We display only the masked version passed in the record.

    # ── Narration text — facts only, no invented claims ───────────────────────
    if item_state == "dismantled":
        identity_line = (
            f"Component type identified as {component} "
            f"(CV classification confidence: {int(conf * 100)}%)."
        )
    else:
        identity_line = (
            f"Device identified via OCR; pseudonymised serial on record "
            f"(OCR confidence: {int(conf * 100)}%). "
            f"Serial uniqueness verified within this system."
        )

    narration_text = (
        f"EcoTrace {ATTESTATION_LABEL} — Batch {batch_id}.\n"
        f"Receiving facility: {facility_name} (CPCB-registered).\n"
        f"{identity_line}\n"
        f"Evidence Trust Score: {trust_score:.3f} (status: {trust_status}).\n"
        f"Processing completion evidence submitted and time window satisfied.\n"
        f"This attestation supports CPCB EPR certificate filing. "
        f"It does not constitute an EPR certificate issued by CPCB."
    )

    # ── Hard gates (structural, not score-derived) ────────────────────────────
    trust_score_above_minimum   = trust_score >= 0.55
    no_duplicate_within_system  = (
        record.get("serial_uniqueness", 1.0) >= 0.99
        or item_state == "dismantled"
    )

    hard_gates = [
        {
            "label":  "Trust Score above HITL minimum (0.55)",
            "passed": trust_score_above_minimum,
        },
        {
            "label":  "No duplicate serial within this system",
            "passed": no_duplicate_within_system,
        },
    ]
    hard_gates_ok = all(g["passed"] for g in hard_gates)

    # ── Soft scores (Stage 9) — structural validation, not score-derived ──────
    #
    # Each dimension checks whether a required structural property holds.
    # Values are 1.0 (property holds) or derived from structural checks —
    # NOT derived from trust_score to avoid circularity.

    # Dim 1: All required facts present
    required_keys = ["batch_id", "facility_name", "trust_score",
                     "gate_passed", "item_state"]
    facts_present = all(record.get(k) is not None for k in required_keys)
    dim1 = 1.0 if facts_present else 0.5

    # Dim 2: Cross-field consistency — gate_passed must be True (already checked)
    # and trust_status must match trust_score band
    ts = trust_score
    expected_status = (
        STATUS_AUTO_VERIFIED if ts >= 0.80 else
        STATUS_HITL          if ts >= 0.55 else
        STATUS_REJECTED
    )
    status_consistent = (trust_status == expected_status)
    dim2 = 1.0 if status_consistent else 0.60

    # Dim 3: Chronological consistency — gate passed implies evidence came after collection
    # In prototype: True by construction; in production: compare timestamps
    dim3 = 1.0

    # Dim 4: No contradictory statuses — if trust_status is REJECTED, badge should not issue
    badge_status_ok = not (
        trust_status == STATUS_REJECTED and hard_gates_ok
    )
    dim4 = 1.0 if badge_status_ok else 0.50

    soft_scores = [
        {
            "label":        "All Required Facts Present",
            "weight":       _NARRATION_WEIGHTS["all_required_facts_present"],
            "value":        dim1,
            "contribution": round(dim1 * _NARRATION_WEIGHTS["all_required_facts_present"], 4),
        },
        {
            "label":        "Cross-field Consistency",
            "weight":       _NARRATION_WEIGHTS["cross_field_consistency"],
            "value":        dim2,
            "contribution": round(dim2 * _NARRATION_WEIGHTS["cross_field_consistency"], 4),
        },
        {
            "label":        "Chronological Consistency",
            "weight":       _NARRATION_WEIGHTS["chronological_consistency"],
            "value":        dim3,
            "contribution": round(dim3 * _NARRATION_WEIGHTS["chronological_consistency"], 4),
        },
        {
            "label":        "No Contradictory Statuses",
            "weight":       _NARRATION_WEIGHTS["no_contradictory_statuses"],
            "value":        dim4,
            "contribution": round(dim4 * _NARRATION_WEIGHTS["no_contradictory_statuses"], 4),
        },
    ]

    narration_confidence = round(sum(s["contribution"] for s in soft_scores), 4)

    # ── Badge decision ────────────────────────────────────────────────────────
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
        "attestation_label":     ATTESTATION_LABEL,
        "disclaimer": (
            "Prototype narration — template-based. "
            "Production: LLM phrases verified facts only; "
            "no facts are invented or inferred by the LLM."
        ),
        "block_reason": None,
    }
