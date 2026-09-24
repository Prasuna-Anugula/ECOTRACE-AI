"""
EcoTrace AI — Recycler Trust Service
─────────────────────────────────────
Loads recycler company data, calculates trust tiers,
and provides lookup helpers for the Producer Marketplace.
"""

from __future__ import annotations
import json
import os
from datetime import datetime, date
from config import (
    MARKETPLACE_RECOMMENDED_MIN,
    MARKETPLACE_WARNING_THRESHOLD,
    MARKETPLACE_TRUST_SCORE_MIN,
    MARKETPLACE_HIGH_RISK_FLAGS,
)

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _load_recyclers() -> list[dict]:
    path = os.path.join(_DATA_DIR, "mock_recyclers.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["recyclers"]


def _load_credits() -> dict:
    path = os.path.join(_DATA_DIR, "mock_epr_credits.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_trust_tier(trust_score: float, anomaly_flags: list) -> dict:
    """Return tier label, colour, and icon based on trust score + anomaly flags."""
    flag_count = len(anomaly_flags)

    if flag_count >= MARKETPLACE_HIGH_RISK_FLAGS:
        return {"tier": "HIGH RISK",    "color": "#dc2626", "bg": "#fef2f2", "icon": "🔴", "border": "#fca5a5"}
    if trust_score >= MARKETPLACE_RECOMMENDED_MIN:
        return {"tier": "RECOMMENDED",  "color": "#166534", "bg": "#f0fdf4", "icon": "✅", "border": "#86efac"}
    if trust_score >= MARKETPLACE_WARNING_THRESHOLD:
        return {"tier": "VERIFIED",     "color": "#1d4ed8", "bg": "#eff6ff", "icon": "🔵", "border": "#93c5fd"}
    if trust_score >= MARKETPLACE_TRUST_SCORE_MIN:
        return {"tier": "CAUTION",      "color": "#d97706", "bg": "#fffbeb", "icon": "⚠️", "border": "#fcd34d"}
    return     {"tier": "NOT LISTED",   "color": "#6b7280", "bg": "#f9fafb", "icon": "⛔", "border": "#d1d5db"}


def days_until_expiry(valid_until: str) -> int:
    """Days until registration expires. Negative = already expired."""
    try:
        exp = datetime.strptime(valid_until, "%Y-%m-%d").date()
        return (exp - date.today()).days
    except Exception:
        return 0


def get_all_recyclers(
    min_trust: float = 0.0,
    min_gate_pass: float = 0.0,
    item_type_filter: str = "All",
    state_filter: str = "All",
    sort_by: str = "trust_score",
) -> list[dict]:
    """
    Return enriched recycler list with trust tier, expiry info,
    filtered and sorted as requested.
    """
    recyclers = _load_recyclers()
    enriched = []

    for r in recyclers:
        ts   = r.get("trust_score", 0)
        gpr  = r.get("gate_pass_rate", 0)
        flags = r.get("anomaly_flags", [])
        expiry_days = days_until_expiry(r.get("registration_valid_until", "2030-01-01"))

        # State filter — any facility in target state
        states = [f["state"] for f in r.get("facilities", [])]
        if state_filter != "All" and state_filter not in states:
            continue

        # Item type filter
        if item_type_filter != "All":
            all_types = []
            for fac in r.get("facilities", []):
                all_types += fac.get("item_handling", {}).get("component_types_accepted", [])
                all_types += fac.get("item_handling", {}).get("device_types_accepted", [])
            if item_type_filter not in all_types:
                continue

        # Score filters
        if ts < min_trust or gpr < min_gate_pass:
            continue

        tier = get_trust_tier(ts, flags)

        # Aggregate facility stats
        total_capacity = sum(
            f.get("capacity", {}).get("processing_capacity_tons_per_month", 0)
            for f in r.get("facilities", [])
        )
        total_workforce = sum(
            f.get("footprint", {}).get("workforce_total", 0)
            for f in r.get("facilities", [])
        )
        total_area = sum(
            f.get("footprint", {}).get("total_area_sqm", 0)
            for f in r.get("facilities", [])
        )
        total_monthly_items = sum(
            f.get("monthly_stats", {}).get("items_received", 0)
            for f in r.get("facilities", [])
        )
        total_dismantled = sum(
            f.get("monthly_stats", {}).get("items_dismantled", 0)
            for f in r.get("facilities", [])
        )
        total_intact = sum(
            f.get("monthly_stats", {}).get("items_intact_packaged", 0)
            for f in r.get("facilities", [])
        )

        enriched.append({
            **r,
            "tier":                     tier,
            "expiry_days":              expiry_days,
            "expiry_warning":           expiry_days < 30,
            "total_capacity_tpm":       total_capacity,
            "total_workforce":          total_workforce,
            "total_area_sqm":           total_area,
            "total_monthly_items":      total_monthly_items,
            "total_dismantled_monthly": total_dismantled,
            "total_intact_monthly":     total_intact,
            "facility_count":           len(r.get("facilities", [])),
        })

    # Sort
    reverse = True
    if sort_by == "trust_score":
        enriched.sort(key=lambda x: x["trust_score"], reverse=reverse)
    elif sort_by == "price_asc":
        enriched.sort(key=lambda x: x["price_per_kg_inr"], reverse=False)
    elif sort_by == "price_desc":
        enriched.sort(key=lambda x: x["price_per_kg_inr"], reverse=True)
    elif sort_by == "credits":
        enriched.sort(key=lambda x: x["available_credits_kg"], reverse=reverse)
    elif sort_by == "gate_pass_rate":
        enriched.sort(key=lambda x: x["gate_pass_rate"], reverse=reverse)
    elif sort_by == "capacity":
        enriched.sort(key=lambda x: x["total_capacity_tpm"], reverse=reverse)

    return enriched


def get_recycler_by_id(recycler_id: str) -> dict | None:
    """Return single enriched recycler dict by ID."""
    for r in get_all_recyclers():
        if r["recycler_id"] == recycler_id:
            return r
    return None


def get_all_states() -> list[str]:
    """Return sorted list of all facility states."""
    recyclers = _load_recyclers()
    states = set()
    for r in recyclers:
        for f in r.get("facilities", []):
            if f.get("state"):
                states.add(f["state"])
    return sorted(states)


def get_all_item_types() -> list[str]:
    """Return sorted list of all accepted item/component types."""
    recyclers = _load_recyclers()
    types = set()
    for r in recyclers:
        for f in r.get("facilities", []):
            ih = f.get("item_handling", {})
            types.update(ih.get("component_types_accepted", []))
            types.update(ih.get("device_types_accepted", []))
    return sorted(types)


def get_producers() -> list[dict]:
    return _load_credits().get("producers", [])


def get_credit_listings(recycler_id: str | None = None) -> list[dict]:
    listings = _load_credits().get("credit_listings", [])
    if recycler_id:
        listings = [l for l in listings if l["recycler_id"] == recycler_id]
    return listings
