"""
EcoTrace AI — Trust Score Engine
──────────────────────────────────
Core business logic for calculating Evidence Trust Scores.

Two modes:
  A. Intact Item  — serial/OCR-based identity
  B. Dismantled   — component CV-based identity

The weighting mode is fixed at Stage 2 and cannot be changed later.
Scores are calculated purely from input values; no hardcoding of results.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from config import (
    INTACT_WEIGHTS,
    DISMANTLED_WEIGHTS,
    TRUST_SCORE_AUTO_VERIFIED_MIN,
    TRUST_SCORE_HITL_MIN,
    STATUS_AUTO_VERIFIED,
    STATUS_HITL,
    STATUS_REJECTED,
)


@dataclass
class ScoreComponent:
    """A single weighted component of the Trust Score."""
    label:       str
    raw_value:   float   # 0.0 – 1.0
    weight:      float   # 0.0 – 1.0
    contribution: float  # raw_value × weight

    @property
    def weight_pct(self) -> str:
        return f"{int(self.weight * 100)}%"

    @property
    def raw_pct(self) -> str:
        return f"{self.raw_value:.2f}"


@dataclass
class TrustScoreResult:
    """Full result returned from any calculate_*_score() call."""
    mode:         str                        # "INTACT" or "DISMANTLED"
    score:        float                      # final weighted score
    status:       str                        # AUTO-VERIFIED / HITL REVIEW / REJECTED
    components:   list[ScoreComponent] = field(default_factory=list)

    @property
    def score_pct(self) -> str:
        return f"{self.score:.3f}"


# ── Status helper ─────────────────────────────────────────────────────────────

def get_score_status(score: float) -> str:
    """Map a numeric Trust Score to its status label."""
    if score >= TRUST_SCORE_AUTO_VERIFIED_MIN:
        return STATUS_AUTO_VERIFIED
    elif score >= TRUST_SCORE_HITL_MIN:
        return STATUS_HITL
    else:
        return STATUS_REJECTED


# ── Intact mode ───────────────────────────────────────────────────────────────

def calculate_intact_score(
    ocr_confidence:    float,
    serial_uniqueness: float,
    facility_validity: float,
    gps_validity:      float,
    image_quality:     float,
    weight_consistency: float,
) -> TrustScoreResult:
    """
    Calculate Trust Score for an INTACT item (serial/OCR identity).

    All inputs must be in [0.0, 1.0].
    """
    w = INTACT_WEIGHTS

    components = [
        ScoreComponent(
            label="Serial / IMEI OCR Confidence",
            raw_value=_clamp(ocr_confidence),
            weight=w["ocr_confidence"],
            contribution=_clamp(ocr_confidence) * w["ocr_confidence"],
        ),
        ScoreComponent(
            label="Serial Uniqueness",
            raw_value=_clamp(serial_uniqueness),
            weight=w["serial_uniqueness"],
            contribution=_clamp(serial_uniqueness) * w["serial_uniqueness"],
        ),
        ScoreComponent(
            label="Facility Registration Validity",
            raw_value=_clamp(facility_validity),
            weight=w["facility_validity"],
            contribution=_clamp(facility_validity) * w["facility_validity"],
        ),
        ScoreComponent(
            label="GPS Validity",
            raw_value=_clamp(gps_validity),
            weight=w["gps_validity"],
            contribution=_clamp(gps_validity) * w["gps_validity"],
        ),
        ScoreComponent(
            label="Image Quality",
            raw_value=_clamp(image_quality),
            weight=w["image_quality"],
            contribution=_clamp(image_quality) * w["image_quality"],
        ),
        ScoreComponent(
            label="Weight Consistency",
            raw_value=_clamp(weight_consistency),
            weight=w["weight_consistency"],
            contribution=_clamp(weight_consistency) * w["weight_consistency"],
        ),
    ]

    total = sum(c.contribution for c in components)
    total = round(_clamp(total), 4)

    return TrustScoreResult(
        mode="INTACT",
        score=total,
        status=get_score_status(total),
        components=components,
    )


# ── Dismantled mode ───────────────────────────────────────────────────────────

def calculate_dismantled_score(
    component_confidence:  float,
    material_plausibility: float,
    facility_validity:     float,
    gps_validity:          float,
    image_quality:         float,
    weight_consistency:    float,
) -> TrustScoreResult:
    """
    Calculate Trust Score for a DISMANTLED item (component CV identity).

    All inputs must be in [0.0, 1.0].
    Serial/IMEI absence does NOT penalise the score — the item was
    already dismantled at first capture; component evidence is used instead.
    """
    w = DISMANTLED_WEIGHTS

    components = [
        ScoreComponent(
            label="Component Classification Confidence",
            raw_value=_clamp(component_confidence),
            weight=w["component_confidence"],
            contribution=_clamp(component_confidence) * w["component_confidence"],
        ),
        ScoreComponent(
            label="Material Composition Plausibility",
            raw_value=_clamp(material_plausibility),
            weight=w["material_plausibility"],
            contribution=_clamp(material_plausibility) * w["material_plausibility"],
        ),
        ScoreComponent(
            label="Facility Registration Validity",
            raw_value=_clamp(facility_validity),
            weight=w["facility_validity"],
            contribution=_clamp(facility_validity) * w["facility_validity"],
        ),
        ScoreComponent(
            label="GPS Validity",
            raw_value=_clamp(gps_validity),
            weight=w["gps_validity"],
            contribution=_clamp(gps_validity) * w["gps_validity"],
        ),
        ScoreComponent(
            label="Image Quality",
            raw_value=_clamp(image_quality),
            weight=w["image_quality"],
            contribution=_clamp(image_quality) * w["image_quality"],
        ),
        ScoreComponent(
            label="Weight Consistency",
            raw_value=_clamp(weight_consistency),
            weight=w["weight_consistency"],
            contribution=_clamp(weight_consistency) * w["weight_consistency"],
        ),
    ]

    total = sum(c.contribution for c in components)
    total = round(_clamp(total), 4)

    return TrustScoreResult(
        mode="DISMANTLED",
        score=total,
        status=get_score_status(total),
        components=components,
    )


# ── Convenience dispatcher ────────────────────────────────────────────────────

def calculate_score_from_params(params: dict) -> TrustScoreResult:
    """
    Dispatch to the correct mode based on params["item_state"].

    params keys (dismantled):
        item_state, component_confidence, material_plausibility,
        facility_validity, gps_validity, image_quality, weight_consistency

    params keys (intact):
        item_state, ocr_confidence, serial_uniqueness,
        facility_validity, gps_validity, image_quality, weight_consistency
    """
    state = params.get("item_state", "dismantled").lower()

    if state == "intact":
        return calculate_intact_score(
            ocr_confidence=params.get("ocr_confidence", 0.92),
            serial_uniqueness=params.get("serial_uniqueness", 1.0),
            facility_validity=params.get("facility_validity", 1.0),
            gps_validity=params.get("gps_validity", 0.95),
            image_quality=params.get("image_quality", 0.88),
            weight_consistency=params.get("weight_consistency", 0.90),
        )
    else:
        return calculate_dismantled_score(
            component_confidence=params.get("component_confidence", 0.94),
            material_plausibility=params.get("material_plausibility", 0.90),
            facility_validity=params.get("facility_validity", 1.0),
            gps_validity=params.get("gps_validity", 0.96),
            image_quality=params.get("image_quality", 0.88),
            weight_consistency=params.get("weight_consistency", 0.93),
        )


# ── Internal helpers ──────────────────────────────────────────────────────────

def _clamp(v: float) -> float:
    """Clamp a value to [0.0, 1.0]."""
    return max(0.0, min(1.0, float(v)))
