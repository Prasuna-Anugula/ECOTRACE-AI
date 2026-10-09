"""
EcoTrace AI — Facility Anomaly Detection (Stage 11)
────────────────────────────────────────────────────
Rule-based anomaly detection for facility-level patterns.

Six rules implemented (Fixes #4, #5, #6):

  Rule 1 — Processing ratio (original)
    processed / received < threshold → under-processing flag

  Rule 2 — Completion failure rate (original)
    failures / received > threshold → high failure rate flag

  Rule 3 — Badge overflow (original)
    badges / received > 1.05 → physically impossible, data integrity flag

  Rule 4 — Ghost facility capacity check (Fix #5)
    daily_items_submitted / declared_daily_capacity > 1.20
    A facility claiming to process 120% of its declared capacity is
    either under-declaring capacity (to avoid scrutiny) or submitting
    ghost records. Cross-reference with electricity meter data in production.

  Rule 5 — Picker volume anomaly (Fix #6)
    Any picker submitting > 3× their median daily volume is flagged.
    In production: feeds a picker–facility network graph to detect
    collusion clusters (a facility where 90%+ of submissions come from
    2 pickers who are also employees is a collusion signal).

  Rule 6 — Cross-platform serial flag (Fix #4)
    Placeholder for national IMEI hash registry integration.
    When a serial hash matches a record on an external registry,
    it indicates possible cross-platform double-claiming.
    Currently returns a caveat — not a hard block.

THIS IS NOT A TRAINED MODEL.
Production replacement: Isolation Forest or Autoencoder trained on
historical facility patterns with confirmed fraud labels.
"""

from __future__ import annotations
from config import (
    ANOMALY_PROCESSING_RATIO_MIN,
    ANOMALY_COMPLETION_FAILURE_MAX,
    ANOMALY_BADGE_OVERFLOW_MAX,
    ANOMALY_GHOST_FACILITY_MAX,
    ANOMALY_PICKER_VOLUME_MULTIPLIER,
)


def detect_anomaly(facility: dict) -> dict:
    """
    Evaluate a single facility for anomaly indicators.

    Parameters
    ----------
    facility : dict with keys:
        items_received, items_processed, badges_issued,
        completion_failures, declared_daily_capacity (optional),
        daily_items_submitted (optional),
        picker_daily_volumes (optional — list of per-picker daily counts)

    Returns
    -------
    dict:
        anomaly_status : "NORMAL" | "REVIEW"
        flags          : list[str] of triggered rule descriptions
        disclaimer     : str
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
            "disclaimer":     _disclaimer(),
        }

    # ── Rule 1: Processing ratio ──────────────────────────────────────────────
    processing_ratio = processed / received
    if processing_ratio < ANOMALY_PROCESSING_RATIO_MIN:
        flags.append(
            f"Rule 1 — Processing ratio {processing_ratio:.0%} is below "
            f"threshold ({ANOMALY_PROCESSING_RATIO_MIN:.0%}). "
            f"Under-processing or stockpiling suspected."
        )

    # ── Rule 2: Completion failure rate ───────────────────────────────────────
    failure_rate = failures / received
    if failure_rate > ANOMALY_COMPLETION_FAILURE_MAX:
        flags.append(
            f"Rule 2 — Completion failure rate {failure_rate:.0%} exceeds "
            f"threshold ({ANOMALY_COMPLETION_FAILURE_MAX:.0%}). "
            f"Review processing gate submissions."
        )

    # ── Rule 3: Badge overflow ────────────────────────────────────────────────
    badge_ratio = badges / received
    if badge_ratio > ANOMALY_BADGE_OVERFLOW_MAX:
        flags.append(
            f"Rule 3 — Badge overflow: {badges} badges issued for "
            f"{received} items received (ratio {badge_ratio:.2f}). "
            f"Issuing more badges than items received is physically impossible. "
            f"Possible data integrity issue or duplicate submissions."
        )

    # ── Rule 4: Ghost facility capacity check ─────────────────────────────────
    declared_cap   = facility.get("declared_daily_capacity", 0)
    daily_submitted = facility.get("daily_items_submitted", 0)
    if declared_cap > 0 and daily_submitted > 0:
        cap_ratio = daily_submitted / declared_cap
        if cap_ratio > ANOMALY_GHOST_FACILITY_MAX:
            flags.append(
                f"Rule 4 — Ghost facility risk: {daily_submitted} items/day submitted "
                f"vs declared capacity {declared_cap} items/day "
                f"(ratio {cap_ratio:.2f}, threshold {ANOMALY_GHOST_FACILITY_MAX:.2f}). "
                f"Facility may be under-declaring capacity or submitting ghost records. "
                f"Verify against electricity meter data and equipment records."
            )

    # ── Rule 5: Picker volume anomaly ─────────────────────────────────────────
    picker_volumes: list[float] = facility.get("picker_daily_volumes", [])
    if len(picker_volumes) >= 3:
        sorted_vols = sorted(picker_volumes)
        median_vol  = sorted_vols[len(sorted_vols) // 2]
        threshold   = median_vol * ANOMALY_PICKER_VOLUME_MULTIPLIER
        outliers    = [v for v in picker_volumes if v > threshold and threshold > 0]
        if outliers:
            flags.append(
                f"Rule 5 — Picker volume anomaly: {len(outliers)} picker(s) submitted "
                f"more than {ANOMALY_PICKER_VOLUME_MULTIPLIER:.0f}× the median daily volume "
                f"({median_vol:.0f} items/day). "
                f"Review for ghost pickers or volume inflation. "
                f"Production: run picker-facility network graph analysis."
            )

    # ── Rule 6: Cross-platform serial flag ────────────────────────────────────
    cross_platform_hits = int(facility.get("cross_platform_serial_hits", 0))
    if cross_platform_hits > 0:
        flags.append(
            f"Rule 6 — Cross-platform alert: {cross_platform_hits} serial hash(es) "
            f"found in external registry. Possible cross-platform double-claiming. "
            f"Requires national IMEI hash registry for full enforcement. "
            f"EcoTrace is registry-compatible (SHA-256 hash format)."
        )

    status = "REVIEW" if flags else "NORMAL"
    return {
        "anomaly_status": status,
        "flags":          flags,
        "disclaimer":     _disclaimer(),
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


def _disclaimer() -> str:
    return (
        "Rule-based anomaly detection — not a trained model. "
        "Production: Isolation Forest or Autoencoder on labelled historical data. "
        "Rules 4–6 require declared_daily_capacity, picker_daily_volumes, "
        "and cross_platform_serial_hits fields from the facility record."
    )
