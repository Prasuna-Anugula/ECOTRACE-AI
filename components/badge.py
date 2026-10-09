"""
EcoTrace AI — Evidence Attestation Badge Component (Stage 10)
──────────────────────────────────────────────────────────────
Renders the EcoTrace Evidence Attestation (EA) decision.

TERMINOLOGY (Fix #10):
  "EPR Certificate" → "Evidence Attestation"

  EcoTrace issues an Evidence Attestation — a cryptographically signed
  record documenting that a specific item passed all 12 verification stages.
  This attestation SUPPORTS (but does not replace) the EPR certificate
  issued by CPCB. Only CPCB can legally issue EPR certificates.
  Producers submit EcoTrace attestations as supporting evidence for
  their CPCB filings.

RULE: No display:grid/flex. No split divs. Every st.markdown is self-contained.
Uses native st.columns for multi-column layout.
"""

from __future__ import annotations
import streamlit as st
from config import ATTESTATION_LABEL, ATTESTATION_LABEL_SHORT


def render_trust_badge(
    badge_status:         str,
    trust_score:          float,
    narration_confidence: float | None,
    gate_status:          str,
    batch_id:             str,
    facility_name:        str,
    item_state:           str,
    component_or_serial:  str,
) -> None:
    bs = badge_status.upper()

    if "AUTO" in bs:
        border_col = "#16a34a"
        bg_col     = "#f0fdf4"
        title_col  = "#166534"
        badge_text = f"ECOTRACE {ATTESTATION_LABEL_SHORT} — VERIFIED"
        sub_text   = f"{ATTESTATION_LABEL.upper()} — AUTO-ISSUED"
        icon       = "✓"
        note       = (
            f"This {ATTESTATION_LABEL} supports CPCB EPR certificate filing. "
            f"It does not constitute an EPR certificate issued by CPCB."
        )
    elif "HITL" in bs:
        border_col = "#d97706"
        bg_col     = "#fffbeb"
        title_col  = "#92400e"
        badge_text = f"ECOTRACE {ATTESTATION_LABEL_SHORT} — PENDING REVIEW"
        sub_text   = f"{ATTESTATION_LABEL.upper()} — HELD FOR HITL REVIEW"
        icon       = "⏸"
        note       = f"A human reviewer must verify this record before the {ATTESTATION_LABEL} is issued."
    else:
        border_col = "#dc2626"
        bg_col     = "#fef2f2"
        title_col  = "#991b1b"
        badge_text = f"ECOTRACE {ATTESTATION_LABEL_SHORT} — NOT ISSUED"
        sub_text   = f"STATUS: {badge_status}"
        icon       = "✕"
        note       = f"Evidence or processing conditions were not met. {ATTESTATION_LABEL} cannot be issued."

    narr_display = f"{narration_confidence:.3f}" if narration_confidence is not None else "N/A"

    # ── Header — fully self-contained ─────────────────────────────────────
    st.markdown(
        f'<div style="background:{bg_col};border:2px solid {border_col};'
        f'border-radius:14px;padding:24px;">'
        f'<p style="text-align:center;font-size:28px;margin:0 0 6px 0;">{icon}</p>'
        f'<p style="text-align:center;font-size:16px;font-weight:800;color:{title_col};'
        f'letter-spacing:0.08em;text-transform:uppercase;margin:0 0 4px 0;">{badge_text}</p>'
        f'<p style="text-align:center;font-size:12px;font-weight:600;color:{border_col};'
        f'letter-spacing:0.08em;text-transform:uppercase;margin:0;">{sub_text}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<hr style="border:none;border-top:2px solid {border_col}44;margin:10px 0;">',
        unsafe_allow_html=True,
    )

    # ── Score metrics using native columns ────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    _score_cell(m1, "Evidence Score",  f"{trust_score:.3f}", border_col, bg_col)
    _score_cell(m2, "Narration Score", narr_display,         border_col, bg_col)
    _score_cell(m3, "Processing Gate", gate_status,          border_col, bg_col)
    _score_cell(m4, "Item State",      item_state.title(),   border_col, bg_col)

    st.markdown(
        f'<hr style="border:none;border-top:1px solid {border_col}44;margin:10px 0;">',
        unsafe_allow_html=True,
    )

    # ── IDs ───────────────────────────────────────────────────────────────
    id1, id2, id3 = st.columns(3)
    _id_cell(id1, "Batch",              batch_id)
    _id_cell(id2, "Facility",           facility_name)
    _id_cell(id3, "Component / Serial", component_or_serial)

    # ── Note ──────────────────────────────────────────────────────────────
    if note:
        st.markdown(
            f'<p style="font-size:11px;color:{border_col};font-weight:500;margin:10px 0 0 0;">'
            f'{note}</p>',
            unsafe_allow_html=True,
        )

    # ── Legal disclaimer ──────────────────────────────────────────────────
    st.markdown(
        f'<p style="font-size:10px;color:#9ca3af;margin:8px 0 0 0;">'
        f'EcoTrace {ATTESTATION_LABEL}s are supporting evidence for CPCB filings. '
        f'Only CPCB can legally issue EPR certificates under E-Waste Management Rules 2022.'
        f'</p>',
        unsafe_allow_html=True,
    )


def _score_cell(col, label: str, value: str, colour: str, bg: str) -> None:
    col.markdown(
        f'<div style="background:{bg};border:1px solid {colour}22;'
        f'border-radius:8px;padding:8px 10px;text-align:center;">'
        f'<p style="font-size:10px;color:#6b7280;font-weight:600;'
        f'text-transform:uppercase;letter-spacing:0.05em;margin:0 0 4px 0;">{label}</p>'
        f'<p style="font-size:15px;font-weight:700;color:#111827;margin:0;">{value}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _id_cell(col, label: str, value: str) -> None:
    col.markdown(
        f'<p style="font-size:10px;font-weight:600;color:#6b7280;'
        f'text-transform:uppercase;letter-spacing:0.05em;margin:0 0 2px 0;">{label}</p>'
        f'<p style="font-size:13px;font-weight:600;color:#111827;margin:0 0 6px 0;">{value}</p>',
        unsafe_allow_html=True,
    )
