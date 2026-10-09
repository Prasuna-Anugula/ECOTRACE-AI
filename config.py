"""
EcoTrace AI — Central Configuration
All weights, thresholds, and application constants live here.
No business logic; pure configuration values.
"""

# ─────────────────────────────────────────────
# APPLICATION META
# ─────────────────────────────────────────────
APP_NAME    = "EcoTrace AI"
APP_TAGLINE = "Evidence-based e-waste traceability and compliance verification"
APP_VERSION = "v0.2"
PROTOTYPE_MODE = True

# ─────────────────────────────────────────────
# TRUST SCORE — INTACT ITEM WEIGHTS
# Must sum to 1.0
#
# Weight justification (domain-expert heuristics):
#   ocr_confidence    30% — Primary identity signal. OCR/CV confidence
#                           directly measures how reliably the item was
#                           identified. Highest weight because identity
#                           fraud (fake serials) is the most common attack.
#   facility_validity 20% — Primary compliance signal. An unregistered
#                           facility is a hard disqualifier (see VETO below).
#                           20% weight reflects its compliance importance
#                           beyond the binary veto.
#   serial_uniqueness 15% — Corroborating identity check. Prevents the same
#                           device being claimed twice within this system.
#   gps_validity      15% — Spatial corroboration. GPS spoofing is detectable
#                           via geofence checks (production: in-app capture
#                           with EXIF validation).
#   image_quality     10% — Supporting evidence. Poor image quality reduces
#                           verifiability but is not independently fraudulent.
#   weight_consistency 10% — Supporting evidence. Weight anomalies flag
#                            substitution or under-reporting.
#
# Production calibration: weights are re-estimated via logistic regression
# on a labelled fraud/legitimate dataset. Higher recall weight is applied
# to the REJECTED class — missing fraud costs more than a false HITL flag.
# ─────────────────────────────────────────────
INTACT_WEIGHTS: dict[str, float] = {
    "ocr_confidence":    0.30,
    "serial_uniqueness": 0.15,
    "facility_validity": 0.20,
    "gps_validity":      0.15,
    "image_quality":     0.10,
    "weight_consistency":0.10,
}

# ─────────────────────────────────────────────
# TRUST SCORE — DISMANTLED ITEM WEIGHTS
# Must sum to 1.0
#
# Same rationale as INTACT_WEIGHTS above.
# component_confidence replaces ocr_confidence (CV replaces OCR).
# material_plausibility replaces serial_uniqueness (mass-based check
# replaces ID-based uniqueness for dismantled parts).
# ─────────────────────────────────────────────
DISMANTLED_WEIGHTS: dict[str, float] = {
    "component_confidence": 0.30,
    "material_plausibility":0.15,
    "facility_validity":    0.20,
    "gps_validity":         0.15,
    "image_quality":        0.10,
    "weight_consistency":   0.10,
}

# ─────────────────────────────────────────────
# HARD VETO THRESHOLDS
# Applied BEFORE weighted scoring.
# A score below these values is a binary disqualifier —
# no weighted sum can compensate for it.
#
# VETO_FACILITY_MIN: facility_validity below this → REJECTED outright.
#   Rationale: An unregistered or suspended facility cannot legally
#   process e-waste under E-Waste Rules 2022. This is a compliance
#   requirement, not an evidence quality indicator.
#
# VETO_GPS_MIN: gps_validity below this → REJECTED outright.
#   Rationale: GPS coordinates that fall outside any registered facility
#   geofence, or that are clearly spoofed (0,0 or identical across many
#   submissions), invalidate the entire collection event. A high OCR score
#   cannot verify where an item was collected.
# ─────────────────────────────────────────────
VETO_FACILITY_MIN: float = 0.50
VETO_GPS_MIN:      float = 0.30

# ─────────────────────────────────────────────
# TRUST SCORE THRESHOLDS
#
# Threshold justification:
#   0.80 (AUTO-VERIFIED): At this score, all major evidence channels
#     contribute high values. The probability of a false positive
#     (fraudulent submission scoring ≥ 0.80) is low under the current
#     weight distribution. In production, this threshold is set at the
#     point where precision ≥ 0.95 on the labelled test set.
#
#   0.55 (HITL boundary): Below this, at least two major evidence
#     channels show significant weakness. Human review is warranted.
#     In production, set at the F1-optimal threshold on the test set,
#     with higher weight on recall for the REJECTED class.
#
#   < 0.55 → REJECTED: Evidence quality is too low to proceed. This
#     threshold is intentionally conservative — false rejections can be
#     appealed, but false approvals generate fraudulent EPR credits.
# ─────────────────────────────────────────────
TRUST_SCORE_AUTO_VERIFIED_MIN: float = 0.80
TRUST_SCORE_HITL_MIN:          float = 0.55

# ─────────────────────────────────────────────
# NARRATION CONFIDENCE THRESHOLDS
# Same calibration rationale as Trust Score thresholds above.
# ─────────────────────────────────────────────
NARRATION_AUTO_BADGE_MIN: float = 0.85
NARRATION_HITL_MIN:       float = 0.60

# ─────────────────────────────────────────────
# STAGE 7 — PROCESSING COMPLETION GATE
# ─────────────────────────────────────────────
PROCESSING_TIME_WINDOW_HOURS: int = 72

# ─────────────────────────────────────────────
# MASS BALANCE — EXPECTED MATERIAL YIELD
# Used in Stage 7 processing gate to verify that declared
# output weights are plausible given input weight.
# Rationale: 10 tonnes of mixed e-waste should yield roughly
# predictable quantities of copper, PCB, plastic, and steel.
# A recycler claiming 10 t in and 0.1 t out is a red flag.
#
# Values are approximate industry averages (UNEP e-waste stats).
# Production: calibrate per item type from downstream smelter records.
#
# Each entry: expected_yield_fraction (output_kg / input_kg)
# tolerance: acceptable deviation before flagging
# ─────────────────────────────────────────────
MASS_BALANCE_PROFILES: dict[str, dict] = {
    "PCB": {
        "copper_fraction":  0.20,
        "precious_fraction":0.003,
        "plastic_fraction": 0.30,
        "steel_fraction":   0.05,
        "residue_fraction": 0.30,
        "tolerance":        0.40,
    },
    "Battery": {
        "copper_fraction":  0.05,
        "lithium_fraction": 0.07,
        "plastic_fraction": 0.20,
        "steel_fraction":   0.25,
        "residue_fraction": 0.30,
        "tolerance":        0.40,
    },
    "Mobile": {
        "copper_fraction":  0.10,
        "precious_fraction":0.001,
        "plastic_fraction": 0.35,
        "steel_fraction":   0.10,
        "residue_fraction": 0.25,
        "tolerance":        0.40,
    },
    "Laptop": {
        "copper_fraction":  0.12,
        "precious_fraction":0.001,
        "plastic_fraction": 0.30,
        "steel_fraction":   0.15,
        "residue_fraction": 0.25,
        "tolerance":        0.40,
    },
    "default": {
        "copper_fraction":  0.08,
        "plastic_fraction": 0.30,
        "steel_fraction":   0.15,
        "residue_fraction": 0.30,
        "tolerance":        0.45,
    },
}

# Minimum declared output as fraction of input weight.
# If declared_output_kg < input_weight_kg * MASS_BALANCE_MIN_OUTPUT_FRACTION
# the gate flags a possible under-reporting anomaly.
MASS_BALANCE_MIN_OUTPUT_FRACTION: float = 0.60

# ─────────────────────────────────────────────
# COMPONENT CLASSES (CV)
# ─────────────────────────────────────────────
COMPONENT_CLASSES: list[str] = ["PCB", "Battery", "Keyboard", "Mouse"]

# ─────────────────────────────────────────────
# STATUS LABELS
# ─────────────────────────────────────────────
STATUS_AUTO_VERIFIED = "AUTO-VERIFIED"
STATUS_HITL          = "HITL REVIEW"
STATUS_REJECTED      = "REJECTED"
STATUS_PASSED        = "PASSED"
STATUS_FAILED        = "FAILED"
STATUS_BLOCKED       = "BLOCKED"
STATUS_COMPLETED     = "COMPLETED"
STATUS_IN_PROGRESS   = "IN PROGRESS"
STATUS_PENDING       = "PENDING"
STATUS_VETOED        = "VETOED"

# ─────────────────────────────────────────────
# EVIDENCE VALIDITY THRESHOLDS
# ─────────────────────────────────────────────
EVIDENCE_VALID_MIN:   float = 0.80
EVIDENCE_WARNING_MIN: float = 0.60

# ─────────────────────────────────────────────
# ANOMALY DETECTION RULES
# Rule 1 — Processing ratio: processed / received
# Rule 2 — Completion failure rate: failures / received
# Rule 3 — Badge overflow: badges / received (> 1 is physically impossible)
# Rule 4 — Ghost facility: daily_items_submitted / declared_daily_capacity
# Rule 5 — Picker volume anomaly: per-picker daily items vs 3× median
# Rule 6 — Cross-platform serial: flagged if serial appears in external registry
# ─────────────────────────────────────────────
ANOMALY_PROCESSING_RATIO_MIN:    float = 0.70
ANOMALY_COMPLETION_FAILURE_MAX:  float = 0.15
ANOMALY_BADGE_OVERFLOW_MAX:      float = 1.05
ANOMALY_GHOST_FACILITY_MAX:      float = 1.20  # > 120% of declared capacity → ghost flag
ANOMALY_PICKER_VOLUME_MULTIPLIER:float = 3.0   # > 3× median daily volume → flag

# ─────────────────────────────────────────────
# PRIVACY — DPDP Act 2023 compliance
# ─────────────────────────────────────────────
# In production: IMEI/serial stored as SHA-256 hash only.
# GPS stored as facility-zone flag, not raw coordinates.
# Picker ID pseudonymised — internal random ID only.
PRIVACY_HASH_SERIALS: bool = True    # enable serial pseudonymisation
PRIVACY_ABSTRACT_GPS: bool = True    # store zone flag, not raw coords

# ─────────────────────────────────────────────
# USER ROLES / PORTALS
# ─────────────────────────────────────────────
ROLE_RECYCLER  = "recycler"
ROLE_PRODUCER  = "producer"
ROLE_REGULATOR = "regulator"

# ─────────────────────────────────────────────
# MARKETPLACE THRESHOLDS
# ─────────────────────────────────────────────
MARKETPLACE_TRUST_SCORE_MIN:   float = 0.60
MARKETPLACE_RECOMMENDED_MIN:   float = 0.85
MARKETPLACE_WARNING_THRESHOLD: float = 0.70
MARKETPLACE_GATE_PASS_MIN:     float = 0.70
MARKETPLACE_HIGH_RISK_FLAGS:   int   = 2

# ─────────────────────────────────────────────
# EVIDENCE ATTESTATION (replaces "EPR Certificate")
# EcoTrace issues an Evidence Attestation — a cryptographically
# signed record that supports (but does not replace) the EPR
# certificate issued by CPCB. Producers submit EcoTrace
# attestations as supporting evidence for CPCB filings.
# ─────────────────────────────────────────────
ATTESTATION_LABEL       = "Evidence Attestation"
ATTESTATION_LABEL_SHORT = "EA"
ATTESTATION_ISSUER      = "EcoTrace AI"

# ─────────────────────────────────────────────
# EPR CREDIT MULTIPLIERS (by component type)
# ─────────────────────────────────────────────
EPR_MULTIPLIERS: dict[str, float] = {
    "PCB":           1.5,
    "Battery":       2.0,
    "Screen":        1.2,
    "Motherboard":   1.5,
    "HDD":           1.1,
    "Casing":        0.8,
    "Cable":         0.9,
    "Mobile":        1.3,
    "Laptop":        1.4,
    "Television":    1.1,
    "Desktop":       1.2,
    "Printer":       1.0,
    "Mixed E-Waste": 1.0,
    "Keyboard":      0.9,
    "Mouse":         0.8,
}
