"""
EcoTrace AI — Dashboard Page
Evidence Verification Overview with summary cards and pipeline status.

IMPORTANT: Never split an HTML tag across two st.markdown() calls.
Streamlit renders each call into an isolated DOM fragment — unclosed tags
and orphaned closing tags will render as literal text.
All HTML in this file is self-contained within a single st.markdown() call.
"""

from __future__ import annotations
import json
import os
import streamlit as st

from components.pipeline import render_pipeline, build_stage_statuses
from utils.formatting import status_colour, status_bg, fmt_score, item_state_label


def _load_transactions() -> list[dict]:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "data", "mock_transactions.json")
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []


def render_dashboard() -> None:

    st.markdown("## Evidence Verification Overview")
    st.caption("Real-time summary of active and completed verification records.")

    txns = _load_transactions()

    # ── Aggregate stats ───────────────────────────────────────────────────
    total         = len(txns)
    auto_verified = sum(1 for t in txns if t.get("trust_status") == "AUTO-VERIFIED")
    hitl          = sum(1 for t in txns if t.get("trust_status") == "HITL REVIEW")
    gate_passed_n = sum(1 for t in txns if t.get("processing_gate") == "PASSED")
    badges_issued = sum(1 for t in txns if t.get("badge_status") == "AUTO-ISSUED")
    gate_failures = sum(1 for t in txns if t.get("processing_gate") == "FAILED")

    # Active verification from session state
    ss            = st.session_state
    active_score  = ss.get("trust_score")
    active_batch  = ss.get("batch_id",       "BATCH-2026-00124")
    active_state  = ss.get("item_state",     "dismantled")
    active_comp   = ss.get("component",      "PCB")
    active_serial = ss.get("serial",         "SN-ECOTRACE-92831")
    active_fac    = ss.get("facility_name",  "GreenCycle Hyderabad")
    active_gate   = ss.get("gate_passed",    None)
    active_badge  = ss.get("badge_decision", None)

    # ── KPI row 1 ─────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    _kpi(c1, "Active Verification",
         "1", "#2563eb", "Current session")
    _kpi(c2, "Current Trust Score",
         fmt_score(active_score) if active_score else "—",
         "#16a34a" if active_score and active_score >= 0.80 else "#d97706",
         "Live calculation")
    _kpi(c3, "Gates Passed",
         str(gate_passed_n), "#16a34a", f"of {total} records")
    _kpi(c4, "Badges Issued",
         str(badges_issued), "#16a34a", "Auto-issued")

    st.markdown("")

    # ── KPI row 2 ─────────────────────────────────────────────────────────
    d1, d2, d3, d4 = st.columns(4)
    _kpi(d1, "Total Records",
         str(total), "#374151", "In mock dataset")
    _kpi(d2, "Auto-Verified",
         str(auto_verified), "#16a34a",
         f"{int(auto_verified / max(total, 1) * 100)}% of total")
    _kpi(d3, "HITL Reviews",
         str(hitl), "#d97706", "Awaiting review")
    _kpi(d4, "Gate Failures",
         str(gate_failures), "#dc2626", "Processing proof missing")

    st.markdown("---")

    # ── Current Verification — fully native Streamlit, zero raw HTML ──────
    st.markdown(
        '<p style="font-size:11px;font-weight:600;color:#6b7280;'
        'letter-spacing:0.08em;text-transform:uppercase;margin:0 0 8px 0;">'
        'CURRENT VERIFICATION</p>',
        unsafe_allow_html=True,
    )

    identity_val = active_comp if active_state == "dismantled" else active_serial
    gate_label   = ("PASSED"  if active_gate is True
                    else "FAILED" if active_gate is False
                    else "PENDING")
    badge_label  = active_badge if active_badge else "PENDING"
    score_str    = fmt_score(active_score) if active_score else "—"

    # Use st.columns directly — no wrapper div
    r1a, r1b, r1c = st.columns(3)
    _field(r1a, "Batch ID",            active_batch)
    _field(r1b, "Item State",          item_state_label(active_state))
    _field(r1c, "Component / Serial",  identity_val)

    st.markdown("<br>", unsafe_allow_html=True)

    r2a, r2b, r2c = st.columns(3)
    score_col = ("#16a34a" if active_score and active_score >= 0.80
                 else "#d97706" if active_score else "#374151")
    _field(r2a, "Facility",        active_fac)
    _field(r2b, "Trust Score",     score_str,   colour=score_col)
    _field_status(r2c, "Processing Gate", gate_label)

    st.markdown("<br>", unsafe_allow_html=True)

    badge_col_left, _ = st.columns([1, 3])
    _field_status(badge_col_left, "Badge Status", badge_label)

    st.markdown("---")

    # ── Pipeline ──────────────────────────────────────────────────────────
    stage_statuses = build_stage_statuses(
        item_state        = active_state,
        trust_score       = active_score,
        gate_passed       = active_gate,
        badge_decision    = active_badge,
        narration_allowed = bool(active_gate),
    )
    render_pipeline(stage_statuses, active_stage=_current_active_stage(stage_statuses))

    st.markdown("")
    if st.button("+ Start New Verification", type="primary"):
        st.session_state["current_page"] = "New Verification"
        st.rerun()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _kpi(col, label: str, value: str, colour: str, sub: str = "") -> None:
    """KPI card using a single self-contained st.markdown block."""
    col.markdown(
        f'<div style="background:#fff;border:1px solid #e5e7eb;'
        f'border-radius:10px;padding:14px 16px;">'
        f'<div style="font-size:10px;font-weight:600;color:#6b7280;'
        f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">'
        f'{label}</div>'
        f'<div style="font-size:26px;font-weight:800;color:{colour};line-height:1;">'
        f'{value}</div>'
        f'<div style="font-size:11px;color:#9ca3af;margin-top:4px;">{sub}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _field(col, label: str, value: str, colour: str = "#111827") -> None:
    """Label + value rendered with native st.markdown — no wrapping div."""
    col.markdown(
        f'<p style="font-size:10px;font-weight:600;color:#6b7280;'
        f'text-transform:uppercase;letter-spacing:0.05em;margin:0 0 2px 0;">'
        f'{label}</p>'
        f'<p style="font-size:13px;font-weight:600;color:{colour};margin:0 0 8px 0;">'
        f'{value}</p>',
        unsafe_allow_html=True,
    )


def _field_status(col, label: str, status: str) -> None:
    """Label + inline status badge — single self-contained block."""
    sc = status_colour(status)
    sb = status_bg(status)
    col.markdown(
        f'<p style="font-size:10px;font-weight:600;color:#6b7280;'
        f'text-transform:uppercase;letter-spacing:0.05em;margin:0 0 4px 0;">'
        f'{label}</p>'
        f'<span style="background:{sb};color:{sc};'
        f'border:1px solid {sc}44;border-radius:5px;'
        f'padding:3px 10px;font-size:12px;font-weight:700;">'
        f'{status}</span>',
        unsafe_allow_html=True,
    )


def _current_active_stage(statuses: dict) -> int:
    for sid in range(11, -1, -1):
        if statuses.get(sid) == "IN PROGRESS":
            return sid
    for sid in range(12):
        if statuses.get(sid) in ("PENDING", "BLOCKED"):
            return sid
    return 10
