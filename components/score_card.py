"""
EcoTrace AI — Trust Score Card Component (Stage 6)

RULE: Every st.markdown() call is a complete, self-contained HTML fragment.
No display:flex / display:grid. No split open/close divs.
"""

from __future__ import annotations
import streamlit as st
from services.trust_score import TrustScoreResult
from utils.formatting import status_colour, status_bg


def render_score_card(result: TrustScoreResult) -> None:
    sc = status_colour(result.status)
    sb = status_bg(result.status)

    # ── Stage label ───────────────────────────────────────────────────────
    st.markdown(
        f'<p style="font-size:11px;font-weight:600;color:#6b7280;'
        f'letter-spacing:0.08em;text-transform:uppercase;margin:0 0 8px 0;">'
        f'STAGE 6 — EVIDENCE TRUST SCORE'
        f'&nbsp;&nbsp;<span style="font-size:10px;background:#fef9c3;color:#92400e;'
        f'border:1px solid #fde68a;border-radius:4px;padding:1px 7px;font-weight:600;">'
        f'MODE: {result.mode}</span></p>',
        unsafe_allow_html=True,
    )

    # ── Score + ring using native columns (no flex needed) ────────────────
    ring_col, label_col = st.columns([1, 2])

    with ring_col:
        st.markdown(_score_ring(result.score, sc), unsafe_allow_html=True)

    with label_col:
        st.markdown(
            f'<p style="font-size:48px;font-weight:800;color:#111827;'
            f'line-height:1;letter-spacing:-2px;margin:8px 0 8px 0;">'
            f'{result.score:.3f}</p>'
            f'<span style="background:{sb};color:{sc};border:1px solid {sc}44;'
            f'border-radius:6px;padding:4px 14px;font-size:14px;font-weight:700;">'
            f'{result.status}</span>'
            f'<p style="font-size:11px;color:#6b7280;margin:8px 0 0 0;">'
            f'≥ 0.80 → AUTO-VERIFIED &nbsp;·&nbsp; '
            f'0.55–0.79 → HITL REVIEW &nbsp;·&nbsp; &lt; 0.55 → REJECTED</p>',
            unsafe_allow_html=True,
        )

    st.markdown("")

    # ── Score breakdown as one self-contained table ───────────────────────
    st.markdown(
        '<p style="font-size:11px;font-weight:600;color:#6b7280;'
        'letter-spacing:0.08em;text-transform:uppercase;margin:0 0 8px 0;">'
        'SCORE BREAKDOWN</p>',
        unsafe_allow_html=True,
    )

    rows_html = ""
    for comp in result.components:
        bar_pct = int(comp.raw_value * 100)
        bar_col = _bar_colour(comp.raw_value)
        rows_html += (
            f'<tr>'
            f'<td style="font-size:12px;color:#374151;padding:6px 8px 6px 0;'
            f'white-space:nowrap;width:45%;">{comp.label}</td>'
            f'<td style="padding:6px 8px;width:40%;">'
            f'<div style="background:#f3f4f6;border-radius:4px;height:6px;">'
            f'<div style="background:{bar_col};width:{bar_pct}%;height:6px;border-radius:4px;"></div>'
            f'</div></td>'
            f'<td style="font-size:11px;color:#6b7280;padding:6px 0 6px 8px;'
            f'white-space:nowrap;text-align:right;font-family:monospace;">'
            f'{comp.raw_value:.2f} × {comp.weight_pct} = '
            f'<strong style="color:#111827;">{comp.contribution:.3f}</strong></td>'
            f'</tr>'
        )

    # Total row
    rows_html += (
        f'<tr style="border-top:2px solid #e5e7eb;">'
        f'<td style="font-size:13px;font-weight:700;color:#111827;'
        f'padding:8px 8px 4px 0;">Final Score</td>'
        f'<td></td>'
        f'<td style="font-size:16px;font-weight:800;color:{sc};'
        f'text-align:right;font-family:monospace;padding:8px 0 4px 8px;">'
        f'{result.score:.4f}</td>'
        f'</tr>'
    )

    st.markdown(
        f'<div style="background:#fff;border:1px solid #e5e7eb;'
        f'border-radius:10px;padding:14px 16px;">'
        f'<table style="width:100%;border-collapse:collapse;">'
        f'{rows_html}'
        f'</table></div>',
        unsafe_allow_html=True,
    )


def _score_ring(score: float, colour: str) -> str:
    r    = 44
    cx   = cy = 52
    circ = 2 * 3.14159 * r
    dash = circ * min(1.0, max(0.0, score))
    gap  = circ - dash
    return (
        f'<svg width="104" height="104" viewBox="0 0 104 104">'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#e5e7eb" stroke-width="8"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{colour}" stroke-width="8"'
        f' stroke-linecap="round" stroke-dasharray="{dash:.1f} {gap:.1f}"'
        f' transform="rotate(-90 {cx} {cy})"/>'
        f'<text x="{cx}" y="{cy}" text-anchor="middle" dy="0.35em"'
        f' font-size="16" font-weight="700" fill="#111827">{int(score * 100)}%</text>'
        f'</svg>'
    )


def _bar_colour(value: float) -> str:
    if value >= 0.80:
        return "#16a34a"
    elif value >= 0.60:
        return "#d97706"
    return "#dc2626"
