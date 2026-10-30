"""
EcoTrace AI — Credit Ledger Service
─────────────────────────────────────
Manages the full lifecycle of Evidence Attestation (EA) credits:
    PENDING → ISSUED → LISTED → SOLD → RETIRED

Hash chain integrity:
    Each credit record contains a hash of its own content + prev_hash.
    Tampering with any record breaks the chain at that point.
    This makes fraud visible without requiring a blockchain node.

Basket recommendation:
    Given a producer's remaining obligation (kg), recommends the minimum
    set of recyclers (greedy, sorted by trust score descending) that can
    cover the shortfall, filtered by minimum trust score.
"""

from __future__ import annotations
import hashlib
import json
import os
from datetime import datetime

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

LIFECYCLE_ORDER = ["PENDING", "ISSUED", "LISTED", "SOLD", "RETIRED"]

STATUS_COLOURS = {
    "PENDING":  {"color": "#d97706", "bg": "#fffbeb", "border": "#fcd34d"},
    "ISSUED":   {"color": "#2563eb", "bg": "#eff6ff", "border": "#93c5fd"},
    "LISTED":   {"color": "#7c3aed", "bg": "#faf5ff", "border": "#c4b5fd"},
    "SOLD":     {"color": "#16a34a", "bg": "#f0fdf4", "border": "#86efac"},
    "RETIRED":  {"color": "#6b7280", "bg": "#f9fafb", "border": "#d1d5db"},
    "BLOCKED":  {"color": "#dc2626", "bg": "#fef2f2", "border": "#fca5a5"},
}


def _load_ledger() -> dict:
    path = os.path.join(_DATA_DIR, "mock_credit_ledger.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_onboarding() -> dict:
    path = os.path.join(_DATA_DIR, "mock_onboarding.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_recyclers() -> list[dict]:
    path = os.path.join(_DATA_DIR, "mock_recyclers.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["recyclers"]


# ── Hash chain verification ────────────────────────────────────────────────────

def _compute_hash(credit: dict) -> str:
    """Compute a deterministic hash of the credit's key fields + prev_hash."""
    payload = (
        f"{credit.get('credit_id','')}|"
        f"{credit.get('batch_id','')}|"
        f"{credit.get('recycler_id','')}|"
        f"{credit.get('weight_kg',0)}|"
        f"{credit.get('credit_kg',0)}|"
        f"{credit.get('trust_score',0)}|"
        f"{credit.get('status','')}|"
        f"{credit.get('prev_hash','')}"
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


def verify_hash_chain(credits: list[dict]) -> list[dict]:
    """
    Verify the hash chain across all credits in order.
    Returns each credit enriched with chain_ok: bool.
    """
    results = []
    for credit in credits:
        expected = _compute_hash(credit)
        chain_ok = (credit.get("hash", "") == expected)
        results.append({**credit, "chain_ok": chain_ok})
    return results


# ── Credit getters ─────────────────────────────────────────────────────────────

def get_all_credits(status_filter: str | None = None) -> list[dict]:
    credits = _load_ledger()["credits"]
    if status_filter and status_filter != "All":
        credits = [c for c in credits if c["status"] == status_filter]
    return verify_hash_chain(credits)


def get_credits_for_recycler(recycler_id: str) -> list[dict]:
    return [c for c in get_all_credits() if c["recycler_id"] == recycler_id]


def get_credits_for_producer(producer_id: str) -> list[dict]:
    return [c for c in get_all_credits() if c.get("buyer_producer_id") == producer_id]


def get_audit_outcomes() -> list[dict]:
    return _load_ledger().get("audit_outcomes", [])


# ── Lifecycle stats ────────────────────────────────────────────────────────────

def get_lifecycle_summary() -> dict:
    credits = get_all_credits()
    summary = {s: {"count": 0, "credit_kg": 0.0} for s in LIFECYCLE_ORDER}
    summary["BLOCKED"] = {"count": 0, "credit_kg": 0.0}

    for c in credits:
        status = c["status"] if c["gate_passed"] else "BLOCKED"
        if status in summary:
            summary[status]["count"]     += 1
            summary[status]["credit_kg"] += c.get("credit_kg", 0.0)

    total_credits = sum(s["credit_kg"] for s in summary.values())
    for s in summary.values():
        s["pct"] = round((s["credit_kg"] / total_credits * 100) if total_credits > 0 else 0, 1)

    return summary


def get_chain_integrity_status(credits: list[dict]) -> dict:
    broken = [c for c in credits if not c.get("chain_ok", True)]
    return {
        "total":   len(credits),
        "ok":      len(credits) - len(broken),
        "broken":  len(broken),
        "intact":  len(broken) == 0,
        "broken_ids": [c["credit_id"] for c in broken],
    }


# ── Obligation & basket ────────────────────────────────────────────────────────

def get_producer_obligation(producer_id: str) -> dict:
    """
    Return obligation data for a producer including fulfilled, shortfall, deadline.
    """
    onboarding   = _load_onboarding()
    prod         = next(
        (p for p in onboarding["registered_producers"] if p["producer_id"] == producer_id),
        None,
    )
    if not prod:
        return {}

    sold_credits = get_credits_for_producer(producer_id)
    fulfilled_kg = sum(c["credit_kg"] for c in sold_credits if c["status"] in ("SOLD", "RETIRED"))
    obligation   = prod.get("annual_obligation_kg", 0.0)
    shortfall    = max(obligation - fulfilled_kg, 0.0)
    pct_done     = min((fulfilled_kg / obligation * 100) if obligation > 0 else 0.0, 100.0)

    # Deadline countdown
    try:
        deadline_date = datetime.strptime(prod["deadline"], "%Y-%m-%d").date()
        days_left     = (deadline_date - datetime.today().date()).days
    except Exception:
        days_left = 0

    status = (
        "COMPLIANT"   if shortfall == 0 else
        "ON_TRACK"    if pct_done >= 60 else
        "AT_RISK"     if pct_done >= 30 else
        "CRITICAL"
    )

    return {
        "producer":      prod,
        "obligation_kg": obligation,
        "fulfilled_kg":  round(fulfilled_kg, 2),
        "shortfall_kg":  round(shortfall, 2),
        "pct_done":      round(pct_done, 1),
        "days_left":     days_left,
        "status":        status,
        "credits":       sold_credits,
    }


def recommend_basket(
    remaining_kg:   float,
    min_trust:      float = 0.85,
    producer_id:    str   = "",
) -> dict:
    """
    Recommend the minimum set of recyclers to cover remaining_kg obligation.
    Greedy: sorted by trust_score descending.

    Returns:
        basket        : list of dicts (recycler, credits_to_buy, cost_inr)
        total_covered : float (kg)
        total_cost    : float (INR)
        can_fulfil    : bool
        recycler_count: int
    """
    recyclers = _load_recyclers()
    recyclers = [r for r in recyclers if r.get("trust_score", 0) >= min_trust]
    recyclers = sorted(recyclers, key=lambda x: x.get("trust_score", 0), reverse=True)

    basket        = []
    running       = 0.0
    total_cost    = 0.0

    for r in recyclers:
        if running >= remaining_kg:
            break
        available = r.get("available_credits_kg", 0.0)
        to_buy    = min(available, remaining_kg - running)
        cost      = round(to_buy * r.get("price_per_kg_inr", 0), 2)

        basket.append({
            "recycler_id":   r["recycler_id"],
            "company_name":  r["company_name"],
            "trust_score":   r["trust_score"],
            "gate_pass_rate":r["gate_pass_rate"],
            "available_kg":  available,
            "to_buy_kg":     round(to_buy, 2),
            "price_per_kg":  r["price_per_kg_inr"],
            "cost_inr":      cost,
        })
        running    += to_buy
        total_cost += cost

    return {
        "basket":         basket,
        "total_covered":  round(running, 2),
        "total_cost":     round(total_cost, 2),
        "can_fulfil":     running >= remaining_kg,
        "recycler_count": len(basket),
        "shortfall_remaining": round(max(remaining_kg - running, 0), 2),
    }


# ── Onboarding helpers ─────────────────────────────────────────────────────────

def get_all_producers() -> list[dict]:
    return _load_onboarding()["registered_producers"]


def get_all_registered_recyclers() -> list[dict]:
    return _load_onboarding()["registered_recyclers"]


def compute_obligation(
    products: list[dict],
    epr_rate_percent: float = 30.0,
) -> dict:
    """
    Given a list of product dicts (category, units_sold_per_year, avg_weight_kg),
    compute total placed on market and EPR obligation.
    """
    total_kg    = sum(p["units_sold_per_year"] * p["avg_weight_kg"] for p in products)
    obligation  = round(total_kg * epr_rate_percent / 100, 2)
    return {
        "total_placed_kg": round(total_kg, 2),
        "epr_rate_pct":    epr_rate_percent,
        "obligation_kg":   obligation,
        "obligation_t":    round(obligation / 1000, 2),
        "by_product": [
            {
                "category":   p["category"],
                "units":      p["units_sold_per_year"],
                "avg_kg":     p["avg_weight_kg"],
                "total_kg":   round(p["units_sold_per_year"] * p["avg_weight_kg"], 2),
                "obligation_kg": round(p["units_sold_per_year"] * p["avg_weight_kg"] * epr_rate_percent / 100, 2),
            }
            for p in products
        ],
    }
