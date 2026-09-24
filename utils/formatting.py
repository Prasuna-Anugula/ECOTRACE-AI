"""
EcoTrace AI — Formatting Utilities
────────────────────────────────────
Pure helper functions for display formatting.
No Streamlit imports — kept framework-agnostic for testability.
"""

from __future__ import annotations
from config import EVIDENCE_VALID_MIN, EVIDENCE_WARNING_MIN


# ── Score / percentage formatting ─────────────────────────────────────────────

def fmt_score(value: float) -> str:
    """Format a 0-1 score to 3 decimal places: '0.942'"""
    return f"{float(value):.3f}"


def fmt_pct(value: float, decimals: int = 1) -> str:
    """Format a 0-1 value as percentage string: '94.0%'"""
    return f"{float(value) * 100:.{decimals}f}%"


def fmt_pct_int(value: float) -> str:
    """Format a 0-1 value as integer percentage: '94%'"""
    return f"{int(round(float(value) * 100))}%"


def fmt_contribution(raw: float, weight: float) -> str:
    """Format a score component line: '0.94 × 30% = 0.282'"""
    contribution = raw * weight
    return f"{raw:.2f} × {int(weight * 100)}% = {contribution:.3f}"


# ── Status badge colours ───────────────────────────────────────────────────────

STATUS_COLOURS: dict[str, str] = {
    "AUTO-VERIFIED":  "#16a34a",   # green-600
    "AUTO-ISSUED":    "#16a34a",
    "PASSED":         "#16a34a",
    "COMPLETED":      "#16a34a",
    "HITL REVIEW":    "#d97706",   # amber-600
    "IN PROGRESS":    "#2563eb",   # blue-600
    "PENDING":        "#6b7280",   # gray-500
    "BLOCKED":        "#dc2626",   # red-600
    "REJECTED":       "#dc2626",
    "FAILED":         "#dc2626",
    "NOT ISSUED":     "#6b7280",
    "NORMAL":         "#16a34a",
    "REVIEW":         "#d97706",
    "PROVISIONAL":    "#d97706",
    "REGISTERED":     "#16a34a",
}

STATUS_BG: dict[str, str] = {
    "AUTO-VERIFIED":  "#f0fdf4",
    "AUTO-ISSUED":    "#f0fdf4",
    "PASSED":         "#f0fdf4",
    "COMPLETED":      "#f0fdf4",
    "HITL REVIEW":    "#fffbeb",
    "IN PROGRESS":    "#eff6ff",
    "PENDING":        "#f9fafb",
    "BLOCKED":        "#fef2f2",
    "REJECTED":       "#fef2f2",
    "FAILED":         "#fef2f2",
    "NOT ISSUED":     "#f9fafb",
    "NORMAL":         "#f0fdf4",
    "REVIEW":         "#fffbeb",
}


def status_colour(status: str) -> str:
    return STATUS_COLOURS.get(status.upper(), "#6b7280")


def status_bg(status: str) -> str:
    return STATUS_BG.get(status.upper(), "#f9fafb")


def status_html(status: str, small: bool = False) -> str:
    """Return an inline HTML badge for a status string."""
    colour = status_colour(status)
    bg     = status_bg(status)
    size   = "11px" if small else "12px"
    pad    = "2px 7px" if small else "3px 10px"
    return (
        f'<span style="background:{bg};color:{colour};border:1px solid {colour}33;'
        f'border-radius:4px;padding:{pad};font-size:{size};'
        f'font-weight:600;letter-spacing:0.03em;">{status}</span>'
    )


# ── Evidence indicator ────────────────────────────────────────────────────────

def evidence_indicator(value: float) -> tuple[str, str]:
    """
    Return (symbol, colour) for an evidence metric value.
    >= EVIDENCE_VALID_MIN   → checkmark, green
    >= EVIDENCE_WARNING_MIN → warning,   amber
    <  EVIDENCE_WARNING_MIN → cross,     red
    """
    if value >= EVIDENCE_VALID_MIN:
        return "✓", "#16a34a"
    elif value >= EVIDENCE_WARNING_MIN:
        return "!", "#d97706"
    else:
        return "✕", "#dc2626"


def evidence_indicator_label(value: float) -> str:
    symbol, _ = evidence_indicator(value)
    if symbol == "✓":
        return "Valid"
    elif symbol == "!":
        return "Warning"
    else:
        return "Invalid"


# ── Misc helpers ───────────────────────────────────────────────────────────────

def truncate(text: str, max_len: int = 40) -> str:
    return text if len(text) <= max_len else text[:max_len - 1] + "…"


def item_state_label(state: str) -> str:
    return "Intact Device" if state.lower() == "intact" else "Dismantled Item"


def badge_decision_to_status(decision: str) -> str:
    """Normalise a badge_decision string to a display status."""
    d = decision.upper()
    if "AUTO" in d:
        return "AUTO-ISSUED"
    elif "HITL" in d:
        return "HITL REVIEW"
    else:
        return "REJECTED"
