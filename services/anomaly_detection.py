"""
EcoTrace AI — Facility Anomaly Detection (Stage 11)
────────────────────────────────────────────────────
Rule-based anomaly detection for facility-level patterns.

THIS IS NOT A TRAINED MODEL.
Anomaly flags are derived from configurable business rules comparing:
  - items_received vs items_processed
  - completion_failures / items_received
  - badges_issued / items_received

Future integration: replace rule logic with a trained anomaly-detection model
while keeping the same input/output contract.
"""

from __future__ import annotations
from config import (
    ANOMALY_PROCESSING_RATIO_MIN,
    ANOMALY_COMPLETION_FAILURE_MAX,
    ANOMALY_BADGE_OVERFLOW_MAX,
)


def detect_anomaly(facility: dict) -> dict:
    """
    Evaluate a single facility record for anomaly indicators.

    Parameters
    ----------
    facility : dict with keys:
        items_received, items_processed, badges_issued, completion_failures

    Returns
    -------
    dict:
        anomaly_status : "NORMAL" | "REVIEW"
        flags          : list of triggered rule descriptions
        disclaimer     : always present
    """
    received   = int(facility.get("items_received",   0))
    processed  = int(facility.get("items_processed",  0))
    badges     = int(facility.get("badges_issued",     0))
    failures   = int(facility.get("completion_failures", 0))

    flags: list[str] = []

    if received == 0:
        return {
            "anomaly_status": "NORMAL",
            "flags":          [],
            "disclaimer":     "Rule-based anomaly detection — not a trained model.",
        }

    # Rule 1: Processing ratio too low
    processing_ratio = processed / received
    if processing_ratio < ANOMALY_PROCESSING_RATIO_MIN:
        flags.append(
            f"Processing ratio {processing_ratio:.0%} is below "
            f"threshold ({ANOMALY_PROCESSING_RATIO_MIN:.0%})"
        )

    # Rule 2: Completion failure rate too high
    failure_rate = failures / received
    if failure_rate > ANOMALY_COMPLETION_FAILURE_MAX:
        flags.append(
            f"Completion failure rate {failure_rate:.0%} exceeds "
            f"threshold ({ANOMALY_COMPLETION_FAILURE_MAX:.0%})"
        )

    # Rule 3: Badges issued exceed received (data integrity concern)
    badge_ratio = badges / received
    if badge_ratio > ANOMALY_BADGE_OVERFLOW_MAX:
        flags.append(
            f"Badges issued ({badges}) exceed items received ({received}) — "
            "possible data integrity issue"
        )

    status = "REVIEW" if flags else "NORMAL"

    return {
        "anomaly_status": status,
        "flags":          flags,
        "disclaimer":     "Rule-based anomaly detection — not a trained model.",
    }


def detect_anomalies_all(facilities: list[dict]) -> list[dict]:
    """
    Run anomaly detection across all facilities.
    Returns each facility dict enriched with anomaly_status and flags.
    """
    enriched = []
    for fac in facilities:
        result = detect_anomaly(fac)
        enriched.append({
            **fac,
            "anomaly_status": result["anomaly_status"],
            "anomaly_flags":  result["flags"],
        })
    return enriched
