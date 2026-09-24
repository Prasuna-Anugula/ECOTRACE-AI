"""
EcoTrace AI — Pipeline Visualization Component
Renders the 12-stage evidence-verification pipeline (Stage 0 – Stage 11).
"""

from __future__ import annotations
import streamlit as st
from utils.formatting import status_colour, status_bg


# ── Stage definitions ─────────────────────────────────────────────────────────
PIPELINE_STAGES = [
    {"id": 0,  "label": "Picker Registration",     "icon": "👤", "desc": "Picker onboarding & registration"},
    {"id": 1,  "label": "Collection Event",         "icon": "📦", "desc": "Collection event initiated"},
    {"id": 2,  "label": "Identity & State",         "icon": "🔍", "desc": "OCR or CV component capture"},
    {"id": 3,  "label": "Evidence Assembly",        "icon": "📷", "desc": "GPS · Image · Weight · Facility"},
    {"id": 4,  "label": "Transport",                "icon": "🚛", "desc": "Item in transit to facility"},
    {"id": 5,  "label": "Facility Intake",          "icon": "🏭", "desc": "Evidence cross-check at intake"},
    {"id": 6,  "label": "Trust Score",              "icon": "🛡", "desc": "Weighted evidence trust calculation"},
    {"id": 7,  "label": "Processing Gate",          "icon": "⚙", "desc": "Completion evidence hard gate"},
    {"id": 8,  "label": "Narration",                "icon": "📄", "desc": "Compliance narration generation"},
    {"id": 9,  "label": "Narration Confidence",     "icon": "📊", "desc": "Regulatory & consistency scoring"},
    {"id": 10, "label": "Trust Badge",              "icon": "✅", "desc": "Auto-issued · HITL · Rejected"},
    {"id": 11, "label": "Audit Dashboard",          "icon": "📈", "desc": "Facility patterns & anomalies"},
]


def render_pipeline(stage_statuses: dict[int, str], active_stage: int = 6) -> None:
    """
    Render the full 12-stage pipeline.

    Parameters
    ----------
    stage_statuses : dict mapping stage_id → status string
                     e.g. {0: "COMPLETED", 6: "IN PROGRESS", 7: "PENDING"}
    active_stage   : the currently highlighted stage id
    """
    st.markdown(
        '<p style="font-size:11px;font-weight:600;color:#6b7280;'
        'letter-spacing:0.08em;text-transform:uppercase;margin-bottom:12px;">'
        'VERIFICATION PIPELINE</p>',
        unsafe_allow_html=True,
    )

    # Render in two rows of 6 for compact display
    rows = [PIPELINE_STAGES[:6], PIPELINE_STAGES[6:]]

    for row in rows:
        cols = st.columns(len(row))
        for col, stage in zip(cols, row):
            sid     = stage["id"]
            status  = stage_statuses.get(sid, "PENDING")
            is_active = (sid == active_stage)

            sc = status_colour(status)
            sb = status_bg(status)

            border = f"2px solid {sc}" if is_active else f"1px solid #e5e7eb"
            bg     = sb if is_active else "#fafafa"
            shadow = "0 2px 8px rgba(0,0,0,0.10)" if is_active else "none"

            col.markdown(
                f"""
                <div style="background:{bg};border:{border};border-radius:10px;
                            padding:10px 8px;text-align:center;
                            box-shadow:{shadow};min-height:110px;
                            display:flex;flex-direction:column;
                            align-items:center;justify-content:flex-start;gap:4px;">
                    <div style="font-size:20px;line-height:1.2;">{stage['icon']}</div>
                    <div style="font-size:10px;font-weight:700;color:#374151;
                                letter-spacing:0.02em;line-height:1.3;margin-top:2px;">
                        <span style="color:#9ca3af;font-weight:400;">S{sid} </span>{stage['label']}
                    </div>
                    <div style="font-size:9px;color:#6b7280;line-height:1.3;
                                text-align:center;">{stage['desc']}</div>
                    <div style="margin-top:auto;padding-top:6px;">
                        <span style="background:{sb};color:{sc};
                                     border:1px solid {sc}44;border-radius:4px;
                                     padding:1px 6px;font-size:9px;font-weight:700;
                                     letter-spacing:0.04em;">{status}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Connector arrow between rows
        if row is rows[0]:
            st.markdown(
                '<div style="text-align:center;color:#9ca3af;font-size:18px;'
                'margin:6px 0;">↓</div>',
                unsafe_allow_html=True,
            )


def build_stage_statuses(
    item_state: str,
    trust_score: float | None,
    gate_passed: bool | None,
    badge_decision: str | None,
    narration_allowed: bool,
) -> dict[int, str]:
    """
    Build a stage_statuses dict from the current verification state.
    Used by dashboard and verification pages.
    """
    s: dict[int, str] = {}

    # Stages 0–3 are always shown as COMPLETED once we're in verification
    s[0] = "COMPLETED"
    s[1] = "COMPLETED"
    s[2] = "COMPLETED" if item_state else "IN PROGRESS"
    s[3] = "COMPLETED" if trust_score is not None else "IN PROGRESS"
    s[4] = "COMPLETED"
    s[5] = "COMPLETED"

    # Stage 6 — Trust Score
    if trust_score is None:
        s[6] = "PENDING"
    elif trust_score >= 0.80:
        s[6] = "AUTO-VERIFIED"
    elif trust_score >= 0.55:
        s[6] = "HITL REVIEW"
    else:
        s[6] = "REJECTED"

    # Stage 7 — Processing Gate
    if gate_passed is None:
        s[7] = "PENDING"
    elif gate_passed:
        s[7] = "PASSED"
    else:
        s[7] = "BLOCKED"

    # Stage 8 — Narration
    if not narration_allowed:
        s[8] = "BLOCKED"
    elif gate_passed:
        s[8] = "COMPLETED"
    else:
        s[8] = "PENDING"

    # Stage 9 — Narration confidence
    s[9] = "COMPLETED" if narration_allowed and gate_passed else "PENDING"

    # Stage 10 — Trust Badge
    if badge_decision is None:
        s[10] = "PENDING"
    else:
        bd = badge_decision.upper()
        if "AUTO" in bd:
            s[10] = "AUTO-ISSUED"
        elif "HITL" in bd:
            s[10] = "HITL REVIEW"
        else:
            s[10] = "REJECTED"

    s[11] = "COMPLETED"

    return s
