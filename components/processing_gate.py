"""
EcoTrace AI — Processing Completion Gate Component (Stage 7)

RULE: Every st.markdown() call is a complete, self-contained HTML fragment.
No display:flex / display:grid. No split open/close divs.
Uses <table> for multi-column layouts.
"""

from __future__ import annotations
import streamlit as st


def render_processing_gate(gate_result: dict) -> None:
    passed     = gate_result.get("passed", False)
    status     = gate_result.get("status", "FAILED")
    reason     = gate_result.get("reason", "")
    batch_id   = gate_result.get("batch_id", "—")
    ts         = gate_result.get("processing_timestamp", "—")
    window     = gate_result.get("time_window_hours", 72)
    conditions = gate_result.get("conditions", [])

    border_col = "#16a34a" if passed else "#dc2626"
    bg_col     = "#f0fdf4" if passed else "#fef2f2"
    badge_col  = "#16a34a" if passed else "#dc2626"
    badge_bg   = "#dcfce7" if passed else "#fee2e2"
    icon       = "✓" if passed else "✕"

    # ── Stage label ───────────────────────────────────────────────────────
    st.markdown(
        '<p style="font-size:11px;font-weight:600;color:#6b7280;'
        'letter-spacing:0.08em;text-transform:uppercase;margin:0 0 8px 0;">'
        'STAGE 7 — PROCESSING COMPLETION GATE</p>',
        unsafe_allow_html=True,
    )

    # ── Title + badge using native columns ────────────────────────────────
    title_col, badge_col_area = st.columns([3, 1])
    with title_col:
        st.markdown(
            f'<p style="font-size:15px;font-weight:700;color:#111827;margin:0 0 2px 0;">'
            f'Processing Completion Gate</p>'
            f'<p style="font-size:12px;color:#6b7280;margin:0;">'
            f'High intake confidence does not prove that the item was actually processed.</p>',
            unsafe_allow_html=True,
        )
    with badge_col_area:
        st.markdown(
            f'<div style="text-align:right;padding-top:4px;">'
            f'<span style="background:{badge_bg};color:{badge_col};'
            f'border:2px solid {badge_col};border-radius:8px;padding:6px 14px;'
            f'font-size:13px;font-weight:800;">{icon} {status}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<hr style="border:none;border-top:2px solid {border_col}33;margin:10px 0;">',
        unsafe_allow_html=True,
    )

    # ── Conditions — each is one complete self-contained block ────────────
    for cond in conditions:
        c_passed = cond.get("passed", False)
        c_icon   = "✓" if c_passed else "✕"
        c_col    = "#16a34a" if c_passed else "#dc2626"
        c_bg     = "#f0fdf4" if c_passed else "#fef2f2"
        st.markdown(
            f'<div style="background:{c_bg};border:1px solid {c_col}33;'
            f'border-radius:8px;padding:10px 14px;margin-bottom:6px;">'
            f'<p style="font-size:12px;font-weight:600;color:#374151;margin:0 0 2px 0;">'
            f'<span style="color:{c_col};font-weight:700;font-size:14px;margin-right:8px;">'
            f'{c_icon}</span>{cond.get("label","")}</p>'
            f'<p style="font-size:11px;color:#6b7280;margin:0;padding-left:22px;">'
            f'{cond.get("detail","")}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Metadata row as a table ───────────────────────────────────────────
    st.markdown(
        f'<table style="width:100%;border-collapse:collapse;margin-top:6px;">'
        f'<tr>'
        f'<td style="font-size:12px;color:#374151;padding:6px 16px 6px 0;white-space:nowrap;">'
        f'<span style="color:#6b7280;">Batch ID:</span> <strong>{batch_id}</strong></td>'
        f'<td style="font-size:12px;color:#374151;padding:6px 16px;white-space:nowrap;">'
        f'<span style="color:#6b7280;">Timestamp:</span> <strong>{ts}</strong></td>'
        f'<td style="font-size:12px;color:#374151;padding:6px 0;white-space:nowrap;">'
        f'<span style="color:#6b7280;">Window:</span> <strong>{window} hours</strong></td>'
        f'</tr></table>',
        unsafe_allow_html=True,
    )

    # ── Reason ────────────────────────────────────────────────────────────
    st.markdown(
        f'<p style="font-size:12px;color:{badge_col};font-weight:500;margin:8px 0 0 0;">'
        f'{reason}</p>',
        unsafe_allow_html=True,
    )

    # ── Failure warning ───────────────────────────────────────────────────
    if not passed:
        st.markdown(
            '<div style="background:#fff7ed;border:1px solid #fed7aa;'
            'border-left:4px solid #ea580c;border-radius:8px;'
            'padding:12px 16px;margin-top:10px;">'
            '<p style="font-size:12px;font-weight:700;color:#9a3412;margin:0 0 3px 0;">'
            'Trust Badge cannot be issued.</p>'
            '<p style="font-size:12px;color:#c2410c;margin:0;">'
            'A high Evidence Trust Score does not substitute for processing completion proof. '
            'Both conditions must pass for badge issuance.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
