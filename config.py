"""
EcoTrace AI — Central Configuration
All weights, thresholds, and application constants live here.
No business logic; pure configuration values.
"""

# ─────────────────────────────────────────────
# APPLICATION META
# ─────────────────────────────────────────────
APP_NAME = "EcoTrace AI"
APP_TAGLINE = "Evidence-based e-waste traceability and compliance verification"
APP_VERSION = "v0.1"
PROTOTYPE_MODE = True

# ─────────────────────────────────────────────
# TRUST SCORE — INTACT ITEM WEIGHTS
# Must sum to 1.0
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
# TRUST SCORE THRESHOLDS
# ─────────────────────────────────────────────
TRUST_SCORE_AUTO_VERIFIED_MIN:  float = 0.80
TRUST_SCORE_HITL_MIN:           float = 0.55
# < TRUST_SCORE_HITL_MIN  → REJECTED

# ─────────────────────────────────────────────
# NARRATION CONFIDENCE THRESHOLDS
# ─────────────────────────────────────────────
NARRATION_AUTO_BADGE_MIN:  float = 0.85
NARRATION_HITL_MIN:        float = 0.60
# < NARRATION_HITL_MIN → REJECTED

# ─────────────────────────────────────────────
# STAGE 7 — PROCESSING COMPLETION GATE
# ─────────────────────────────────────────────
PROCESSING_TIME_WINDOW_HOURS: int = 72   # evidence must be within this window

# ─────────────────────────────────────────────
# COMPONENT CLASSES (CV)
# ─────────────────────────────────────────────
COMPONENT_CLASSES: list[str] = ["PCB", "Battery", "Casing", "Cable"]

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

# ─────────────────────────────────────────────
# EVIDENCE VALIDITY THRESHOLDS (for indicators)
# ─────────────────────────────────────────────
EVIDENCE_VALID_MIN:   float = 0.80   # >= green tick
EVIDENCE_WARNING_MIN: float = 0.60   # >= amber warning
# < EVIDENCE_WARNING_MIN → red cross

# ─────────────────────────────────────────────
# ANOMALY DETECTION RULES
# (rule-based, not a trained model)
# ─────────────────────────────────────────────
ANOMALY_PROCESSING_RATIO_MIN:    float = 0.70   # processed/received
ANOMALY_COMPLETION_FAILURE_MAX:  float = 0.15   # failures/received
ANOMALY_BADGE_OVERFLOW_MAX:      float = 1.05   # badges/received (>1 = suspicious)

# ─────────────────────────────────────────────
# USER ROLES / PORTALS
# ─────────────────────────────────────────────
ROLE_RECYCLER  = "recycler"
ROLE_PRODUCER  = "producer"
ROLE_REGULATOR = "regulator"

# ─────────────────────────────────────────────
# MARKETPLACE THRESHOLDS
# ─────────────────────────────────────────────
MARKETPLACE_TRUST_SCORE_MIN:    float = 0.60   # minimum to appear in marketplace
MARKETPLACE_RECOMMENDED_MIN:    float = 0.85   # "EcoTrace Recommended" badge
MARKETPLACE_WARNING_THRESHOLD:  float = 0.70   # show warning below this
MARKETPLACE_GATE_PASS_MIN:      float = 0.70   # minimum gate pass rate
MARKETPLACE_HIGH_RISK_FLAGS:    int   = 2      # num anomaly flags = high risk

# ─────────────────────────────────────────────
# EPR CREDIT MULTIPLIERS (by component type)
# Credit = weight_kg × multiplier
# ─────────────────────────────────────────────
EPR_MULTIPLIERS: dict[str, float] = {
    "PCB":              1.5,
    "Battery":          2.0,
    "Screen":           1.2,
    "Motherboard":      1.5,
    "HDD":              1.1,
    "Casing":           0.8,
    "Cable":            0.9,
    "Mobile":           1.3,
    "Laptop":           1.4,
    "Television":       1.1,
    "Desktop":          1.2,
    "Printer":          1.0,
    "Mixed E-Waste":    1.0,
}
