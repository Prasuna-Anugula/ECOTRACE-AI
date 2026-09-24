"""
EcoTrace AI — Verification History Page
RULE: No display:flex/grid. No split divs. Uses <table> for row layouts.
"""

from __future__ import annotations
import json
import os
import streamlit as st
from utils.formatting import status_colour, status_bg, fmt_score, item_state_label


def _load_transactions() -> list[dict]:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "data", "mock_transactions.json")
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []


def render_history() -> None:
    st.markdown("## Verification History")
    st.caption("All mock verification records from the synthetic dataset.")

    txns = _load_transactions()
    if not txns:
        st.info("No verification records found.")
        return

    # ── Filters ───────────────────────────────────────────────────────────
    f1, f2, f3 = st.columns(3)
    filter_state  = f1.selectbox("Item State",       ["All", "Dismantled", "Intact"],                  key="hist_fs")
    filter_status = f2.selectbox("Trust Status",     ["All", "AUTO-VERIFIED", "HITL REVIEW", "REJECTED"], key="hist_fst")
    filter_gate   = f3.selectbox("Processing Gate",  ["All", "PASSED", "FAILED"],                      key="hist_fg")

    filtered = txns
    if filter_state  != "All":
        filtered = [t for t in filtered if t.get("item_state","").lower() == filter_state.lower()]
    if filter_status != "All":
        filtered = [t for t in filtered if t.get("trust_status","") == filter_status]
    if filter_gate   != "All":
        filtered = [t for t in filtered if t.get("processing_gate","") == filter_gate]

    st.markdown(
        f'<p style="font-size:12px;color:#6b7280;margin:6px 0 12px 0;">'
        f'Showing {len(filtered)} of {len(txns)} records &nbsp;·&nbsp;'
        f'<span style="color:#d97706;font-weight:600;">Synthetic data</span></p>',
        unsafe_allow_html=True,
    )

    # ── Summary KPIs ──────────────────────────────────────────────────────
    if filtered:
        scores    = [t["trust_score"] for t in filtered if t.get("trust_score") is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Records",         len(filtered))
        k2.metric("Avg Trust Score", f"{avg_score:.3f}")
        k3.metric("Gates Passed",    sum(1 for t in filtered if t.get("processing_gate") == "PASSED"))
        k4.metric("Badges Issued",   sum(1 for t in filtered if t.get("badge_status")    == "AUTO-ISSUED"))

    st.markdown("")

    # ── Table header ──────────────────────────────────────────────────────
    st.markdown(
        '<table style="width:100%;border-collapse:collapse;">'
        '<thead><tr style="background:#f9fafb;border-bottom:2px solid #e5e7eb;">'
        '<th style="font-size:10px;font-weight:700;color:#6b7280;text-transform:uppercase;'
        'letter-spacing:0.06em;padding:8px 12px;text-align:left;">Batch ID</th>'
        '<th style="font-size:10px;font-weight:700;color:#6b7280;text-transform:uppercase;'
        'letter-spacing:0.06em;padding:8px 12px;text-align:left;">Item State</th>'
        '<th style="font-size:10px;font-weight:700;color:#6b7280;text-transform:uppercase;'
        'letter-spacing:0.06em;padding:8px 12px;text-align:left;">Component / Serial</th>'
        '<th style="font-size:10px;font-weight:700;color:#6b7280;text-transform:uppercase;'
        'letter-spacing:0.06em;padding:8px 12px;text-align:left;">Trust Score</th>'
        '<th style="font-size:10px;font-weight:700;color:#6b7280;text-transform:uppercase;'
        'letter-spacing:0.06em;padding:8px 12px;text-align:left;">Processing Gate</th>'
        '<th style="font-size:10px;font-weight:700;color:#6b7280;text-transform:uppercase;'
        'letter-spacing:0.06em;padding:8px 12px;text-align:left;">Badge Status</th>'
        '<th style="font-size:10px;font-weight:700;color:#6b7280;text-transform:uppercase;'
        'letter-spacing:0.06em;padding:8px 12px;text-align:left;">Date / Facility</th>'
        '</tr></thead></table>',
        unsafe_allow_html=True,
    )

    # ── Rows ──────────────────────────────────────────────────────────────
    for txn in filtered:
        _render_row(txn)

    st.markdown(
        '<p style="font-size:11px;color:#9ca3af;font-style:italic;margin-top:8px;">'
        'All records are synthetic demo data. Not real-world statistics.</p>',
        unsafe_allow_html=True,
    )


def _render_row(txn: dict) -> None:
    state    = txn.get("item_state", "dismantled")
    score    = txn.get("trust_score", 0) or 0
    gate     = txn.get("processing_gate", "—")
    badge    = txn.get("badge_status", "—")
    identity = txn.get("component", "—") if state == "dismantled" else txn.get("serial", "—")

    # Score colour
    score_col = "#16a34a" if score >= 0.80 else "#d97706" if score >= 0.55 else "#dc2626"

    # Gate badge
    gate_col = "#16a34a" if gate == "PASSED" else "#dc2626"
    gate_bg  = "#f0fdf4" if gate == "PASSED" else "#fef2f2"

    # Badge
    bc = status_colour(badge)
    bb = status_bg(badge)

    st.markdown(
        f'<table style="width:100%;border-collapse:collapse;">'
        f'<tbody><tr style="border-bottom:1px solid #f3f4f6;'
        f'background:#fff;">'

        # Batch ID
        f'<td style="padding:10px 12px;min-width:140px;">'
        f'<span style="font-size:13px;font-weight:700;color:#111827;'
        f'font-family:monospace;">{txn.get("batch_id","—")}</span></td>'

        # Item State
        f'<td style="padding:10px 12px;">'
        f'<span style="font-size:12px;font-weight:600;color:#374151;">'
        f'{item_state_label(state)}</span></td>'

        # Component / Serial
        f'<td style="padding:10px 12px;">'
        f'<span style="font-size:12px;color:#374151;">{identity}</span></td>'

        # Trust Score
        f'<td style="padding:10px 12px;">'
        f'<span style="font-size:16px;font-weight:800;color:{score_col};">'
        f'{fmt_score(score)}</span></td>'

        # Processing Gate
        f'<td style="padding:10px 12px;">'
        f'<span style="background:{gate_bg};color:{gate_col};'
        f'border:1px solid {gate_col}33;border-radius:4px;'
        f'padding:2px 8px;font-size:11px;font-weight:600;">{gate}</span></td>'

        # Badge Status
        f'<td style="padding:10px 12px;">'
        f'<span style="background:{bb};color:{bc};border:1px solid {bc}44;'
        f'border-radius:4px;padding:2px 8px;font-size:11px;font-weight:600;">'
        f'{badge}</span></td>'

        # Date / Facility
        f'<td style="padding:10px 12px;">'
        f'<span style="font-size:11px;color:#9ca3af;display:block;">'
        f'{txn.get("collection_date","—")}</span>'
        f'<span style="font-size:11px;color:#9ca3af;">'
        f'{txn.get("facility_name","—")}</span></td>'

        f'</tr></tbody></table>',
        unsafe_allow_html=True,
    )
