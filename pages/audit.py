"""
EcoTrace AI — Audit Dashboard (Stage 11)
RULE: No display:flex/grid. No split divs. Tables for multi-column layouts.
"""

from __future__ import annotations
import json
import os
import streamlit as st

from components.charts import (
    chart_badge_by_facility, chart_intake_vs_processing,
    chart_trust_score_distribution, chart_completion_failures,
    chart_anomaly_indicator,
)
from services.anomaly_detection import detect_anomalies_all


def _load(filename: str) -> list:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        with open(os.path.join(base, "data", filename)) as f:
            return json.load(f)
    except Exception:
        return []


def render_audit() -> None:
    st.markdown("## Audit Dashboard")
    st.caption("Facility-level compliance patterns, badge issuance, and anomaly indicators.")
    st.markdown(
        '<p style="font-size:12px;color:#d97706;font-weight:600;margin:0 0 16px 0;">'
        'Synthetic data — not real-world statistics.</p>',
        unsafe_allow_html=True,
    )

    facilities = _load("mock_facilities.json")
    txns       = _load("mock_transactions.json")

    total_txns    = len(txns)
    auto_verified = sum(1 for t in txns if t.get("trust_status")    == "AUTO-VERIFIED")
    hitl_review   = sum(1 for t in txns if t.get("trust_status")    == "HITL REVIEW")
    rejected      = sum(1 for t in txns if t.get("trust_status")    == "REJECTED")
    gate_failures = sum(1 for t in txns if t.get("processing_gate") == "FAILED")

    # ── KPIs ──────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    _kpi(k1, "Total Items",    str(total_txns),    "#374151")
    _kpi(k2, "Auto-Verified",  str(auto_verified), "#16a34a")
    _kpi(k3, "HITL Reviews",   str(hitl_review),   "#d97706")
    _kpi(k4, "Rejected",       str(rejected),      "#dc2626")
    _kpi(k5, "Gate Failures",  str(gate_failures), "#dc2626")

    st.markdown("")

    # ── Charts ────────────────────────────────────────────────────────────
    c1, c2 = st.columns(2)
    c1.plotly_chart(chart_badge_by_facility(),    use_container_width=True)
    c2.plotly_chart(chart_intake_vs_processing(), use_container_width=True)

    c3, c4 = st.columns(2)
    c3.plotly_chart(chart_trust_score_distribution(), use_container_width=True)
    c4.plotly_chart(chart_completion_failures(),      use_container_width=True)

    st.plotly_chart(chart_anomaly_indicator(), use_container_width=True)

    # ── Facility detail table ─────────────────────────────────────────────
    st.markdown(
        '<p style="font-size:11px;font-weight:600;color:#6b7280;'
        'letter-spacing:0.08em;text-transform:uppercase;margin:8px 0 12px 0;">'
        'FACILITY DETAIL TABLE</p>',
        unsafe_allow_html=True,
    )

    enriched = detect_anomalies_all(facilities)

    # Table header — one complete self-contained block
    st.markdown(
        '<table style="width:100%;border-collapse:collapse;">'
        '<thead><tr style="background:#f9fafb;border-bottom:2px solid #e5e7eb;">'
        + "".join(
            f'<th style="font-size:10px;font-weight:700;color:#6b7280;'
            f'text-transform:uppercase;letter-spacing:0.05em;'
            f'padding:8px 12px;text-align:{align};">{h}</th>'
            for h, align in [
                ("Facility",        "left"),
                ("Received",        "right"),
                ("Processed",       "right"),
                ("Badges",          "right"),
                ("Gate Failures",   "right"),
                ("Anomaly Status",  "center"),
            ]
        )
        + '</tr></thead></table>',
        unsafe_allow_html=True,
    )

    # Each facility row — one complete self-contained block per row
    for fac in enriched:
        status    = fac.get("anomaly_status", "NORMAL")
        flags     = fac.get("anomaly_flags",  [])
        reg_stat  = fac.get("registration_status", "REGISTERED")
        received  = fac["items_received"]
        processed = fac["items_processed"]
        badges    = fac["badges_issued"]
        failures  = fac["completion_failures"]

        proc_ratio = processed / max(received, 1)
        ratio_col  = "#16a34a" if proc_ratio >= 0.90 else "#d97706" if proc_ratio >= 0.70 else "#dc2626"
        fail_col   = "#dc2626" if failures > 20 else "#374151"
        reg_col    = "#16a34a" if reg_stat == "REGISTERED" else "#d97706"
        anom_col   = "#16a34a" if status == "NORMAL" else "#d97706"
        anom_bg    = "#f0fdf4" if status == "NORMAL" else "#fffbeb"

        flags_html = ""
        if flags:
            items = "".join(f"<li>{f}</li>" for f in flags)
            flags_html = (
                f'<ul style="font-size:10px;color:#92400e;margin:4px 0 0 0;'
                f'padding-left:14px;">{items}</ul>'
            )

        st.markdown(
            f'<table style="width:100%;border-collapse:collapse;">'
            f'<tbody><tr style="border-bottom:1px solid #f3f4f6;background:#fff;">'

            # Facility name
            f'<td style="padding:10px 12px;min-width:180px;">'
            f'<p style="font-size:13px;font-weight:600;color:#111827;margin:0 0 2px 0;">'
            f'{fac["name"]}</p>'
            f'<p style="font-size:10px;color:#6b7280;margin:0;">'
            f'{fac.get("location","—")} &nbsp;·&nbsp; '
            f'<span style="color:{reg_col};">{reg_stat}</span></p>'
            f'{flags_html}</td>'

            # Received
            f'<td style="padding:10px 12px;text-align:right;">'
            f'<span style="font-size:14px;font-weight:600;color:#374151;">'
            f'{received}</span></td>'

            # Processed + ratio
            f'<td style="padding:10px 12px;text-align:right;">'
            f'<span style="font-size:14px;font-weight:600;color:{ratio_col};">'
            f'{processed}</span>'
            f'<p style="font-size:10px;color:{ratio_col};margin:0;">'
            f'{proc_ratio:.0%}</p></td>'

            # Badges
            f'<td style="padding:10px 12px;text-align:right;">'
            f'<span style="font-size:14px;font-weight:600;color:#374151;">'
            f'{badges}</span></td>'

            # Gate failures
            f'<td style="padding:10px 12px;text-align:right;">'
            f'<span style="font-size:14px;font-weight:600;color:{fail_col};">'
            f'{failures}</span></td>'

            # Anomaly badge
            f'<td style="padding:10px 12px;text-align:center;">'
            f'<span style="background:{anom_bg};color:{anom_col};'
            f'border:1px solid {anom_col}44;border-radius:6px;'
            f'padding:3px 10px;font-size:11px;font-weight:700;">'
            f'{status}</span></td>'

            f'</tr></tbody></table>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<p style="font-size:11px;color:#9ca3af;font-style:italic;margin-top:10px;">'
        'Anomaly detection is rule-based — not a trained model. All data is synthetic.</p>',
        unsafe_allow_html=True,
    )


def _kpi(col, label: str, value: str, colour: str) -> None:
    col.markdown(
        f'<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:14px 16px;">'
        f'<p style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;'
        f'letter-spacing:0.06em;margin:0 0 4px 0;">{label}</p>'
        f'<p style="font-size:26px;font-weight:800;color:{colour};line-height:1;margin:0;">'
        f'{value}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
