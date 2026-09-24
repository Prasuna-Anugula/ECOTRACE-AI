"""
EcoTrace AI — Evidence Assembly Card Component (Stage 3)

RULE: Every st.markdown() call must be fully self-contained HTML.
No split open/close div tags across calls. No display:flex or display:grid
(stripped by Streamlit's sanitizer). Use tables or block elements instead.
"""

from __future__ import annotations
import streamlit as st
from utils.formatting import fmt_pct_int, evidence_indicator


def render_evidence_card(
    gps_validity:        float,
    image_quality:       float,
    weight_consistency:  float,
    facility_validity:   float,
    latitude:            float = 17.385,
    longitude:           float = 78.4867,
    actual_weight:       float = 4.2,
    expected_weight:     float = 4.5,
    facility_name:       str   = "GreenCycle Hyderabad",
    facility_status:     str   = "REGISTERED",
    item_state:          str   = "dismantled",
    component_or_serial: str   = "PCB",
) -> None:
    st.markdown(
        '<p style="font-size:11px;font-weight:600;color:#6b7280;'
        'letter-spacing:0.08em;text-transform:uppercase;margin:0 0 8px 0;">'
        'STAGE 3 — EVIDENCE ASSEMBLY</p>',
        unsafe_allow_html=True,
    )

    # ── Four metric cards using native columns ────────────────────────────
    cols = st.columns(4)
    _metric_card(cols[0], "GPS Location",   gps_validity,
                 f"{latitude:.4f}° N",      f"{longitude:.4f}° E")
    _metric_card(cols[1], "Image Quality",  image_quality,
                 "Sharpness score",         fmt_pct_int(image_quality))
    _metric_card(cols[2], "Weight",         weight_consistency,
                 f"Actual: {actual_weight} kg", f"Expected: {expected_weight} kg")
    _metric_card(cols[3], "Facility",       facility_validity,
                 facility_name,             facility_status)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Summary table — uses <table> which Streamlit allows ───────────────
    metrics = [
        ("GPS Validity",       gps_validity),
        ("Image Quality",      image_quality),
        ("Weight Consistency", weight_consistency),
        ("Facility Validity",  facility_validity),
    ]

    rows_html = ""
    for label, value in metrics:
        symbol, colour = evidence_indicator(value)
        bar_pct = int(value * 100)
        bar_html = (
            f'<div style="background:#e5e7eb;border-radius:4px;height:6px;width:100%;">'
            f'<div style="background:{colour};width:{bar_pct}%;height:6px;'
            f'border-radius:4px;"></div></div>'
        )
        rows_html += (
            f'<tr>'
            f'<td style="padding:4px 8px 4px 0;width:16px;text-align:center;">'
            f'<span style="color:{colour};font-weight:700;font-size:13px;">{symbol}</span></td>'
            f'<td style="padding:4px 8px;font-size:12px;color:#374151;white-space:nowrap;">'
            f'{label}</td>'
            f'<td style="padding:4px 8px;width:60%;">{bar_html}</td>'
            f'<td style="padding:4px 0 4px 8px;font-size:12px;font-weight:600;'
            f'color:#374151;white-space:nowrap;text-align:right;">'
            f'{fmt_pct_int(value)}</td>'
            f'</tr>'
        )

    st.markdown(
        f'<div style="background:#f9fafb;border:1px solid #e5e7eb;'
        f'border-radius:10px;padding:14px 16px;">'
        f'<p style="font-size:11px;font-weight:600;color:#6b7280;'
        f'letter-spacing:0.06em;text-transform:uppercase;margin:0 0 10px 0;">'
        f'Evidence Summary</p>'
        f'<table style="width:100%;border-collapse:collapse;">'
        f'{rows_html}'
        f'</table>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _metric_card(col, title: str, value: float, line1: str, line2: str) -> None:
    """Single evidence metric card — fully self-contained HTML block."""
    symbol, colour = evidence_indicator(value)
    col.markdown(
        f'<div style="background:#fff;border:1px solid #e5e7eb;'
        f'border-radius:10px;padding:12px;min-height:100px;">'
        f'<div style="font-size:10px;font-weight:600;color:#6b7280;'
        f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;">'
        f'{title}</div>'
        f'<div style="font-size:13px;font-weight:600;color:#111827;margin-bottom:2px;">'
        f'{line1}</div>'
        f'<div style="font-size:11px;color:#6b7280;margin-bottom:8px;">{line2}</div>'
        f'<span style="color:{colour};font-weight:700;font-size:12px;">{symbol}</span>'
        f'<span style="font-size:11px;font-weight:600;color:{colour};margin-left:4px;">'
        f'{fmt_pct_int(value)}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
