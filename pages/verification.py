"""
EcoTrace AI — New Verification Page
Full interactive pipeline: Stages 0–10.

RULE: Every st.markdown() call must be a COMPLETE, self-contained HTML fragment.
      - No split open/close divs across separate calls.
      - No display:flex or display:grid (stripped by Streamlit sanitizer).
      - Use <table> or nested <div> blocks — all in ONE call.
"""

from __future__ import annotations
import streamlit as st

from services.mock_cv         import predict_component
from services.mock_ocr        import run_ocr
from services.trust_score     import calculate_score_from_params
from services.processing_gate import check_processing_gate
from services.narration       import generate_narration
from components.evidence_card   import render_evidence_card
from components.score_card      import render_score_card
from components.processing_gate import render_processing_gate
from components.badge           import render_trust_badge
from components.pipeline        import render_pipeline, build_stage_statuses
from utils.formatting           import status_colour, status_bg, fmt_score, item_state_label
from utils.demo_presets         import get_preset_names, apply_preset_to_state
from config                     import COMPONENT_CLASSES, PROCESSING_TIME_WINDOW_HOURS


# ── Session-state defaults ────────────────────────────────────────────────────

def _init_state() -> None:
    defaults = {
        "item_state":            "dismantled",
        "component":             "PCB",
        "component_confidence":  0.94,
        "material_plausibility": 0.90,
        "ocr_confidence":        0.92,
        "serial_uniqueness":     1.00,
        "facility_validity":     1.00,
        "gps_validity":          0.96,
        "image_quality":         0.88,
        "weight_consistency":    0.93,
        "completion_evidence":   True,
        "within_time_window":    True,
        "narration_hard_gate":   True,
        "batch_id":              "BATCH-2026-00124",
        "facility_name":         "GreenCycle Hyderabad",
        "serial":                "SN-ECOTRACE-92831",
        "trust_score":           None,
        "trust_status":          None,
        "gate_passed":           None,
        "badge_decision":        None,
        "narration_result":      None,
        "score_result":          None,
        "gate_result":           None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Main entry ────────────────────────────────────────────────────────────────

def render_verification() -> None:
    _init_state()
    _run_calculations()

    st.markdown("## New Verification")
    st.caption("Complete the pipeline to verify an e-waste item and determine Trust Badge eligibility.")

    main_col, ctrl_col = st.columns([3, 1], gap="large")
    with ctrl_col:
        _render_demo_controls()
    with main_col:
        _render_stages_0_1()
        st.markdown("---")
        _render_stage_2()
        st.markdown("---")
        _render_stage_3()
        st.markdown("---")
        _render_stages_4_5()
        st.markdown("---")
        _render_stage_6()
        st.markdown("---")
        _render_stage_7()
        st.markdown("---")
        _render_stage_8()
        st.markdown("---")
        _render_stage_9()
        st.markdown("---")
        _render_stage_10()
        st.markdown("---")
        _render_pipeline_summary()


# ── Calculations ──────────────────────────────────────────────────────────────

def _run_calculations() -> None:
    ss = st.session_state
    params = {
        "item_state":            ss["item_state"],
        "component_confidence":  ss["component_confidence"],
        "material_plausibility": ss["material_plausibility"],
        "ocr_confidence":        ss["ocr_confidence"],
        "serial_uniqueness":     ss["serial_uniqueness"],
        "facility_validity":     ss["facility_validity"],
        "gps_validity":          ss["gps_validity"],
        "image_quality":         ss["image_quality"],
        "weight_consistency":    ss["weight_consistency"],
    }
    score_result        = calculate_score_from_params(params)
    ss["score_result"]  = score_result
    ss["trust_score"]   = score_result.score
    ss["trust_status"]  = score_result.status

    gate_result        = check_processing_gate(
        completion_evidence_submitted = ss["completion_evidence"],
        within_time_window            = ss["within_time_window"],
        batch_id                      = ss["batch_id"],
        processing_timestamp          = "21 Sep 2026, 11:32 AM",
        time_window_hours             = PROCESSING_TIME_WINDOW_HOURS,
    )
    ss["gate_result"]  = gate_result
    ss["gate_passed"]  = gate_result["passed"]

    record = {
        "batch_id":             ss["batch_id"],
        "item_state":           ss["item_state"],
        "component":            ss["component"],
        "serial":               ss["serial"],
        "facility_name":        ss["facility_name"],
        "trust_score":          score_result.score,
        "trust_status":         score_result.status,
        "gate_passed":          gate_result["passed"],
        "component_confidence": ss["component_confidence"],
        "ocr_confidence":       ss["ocr_confidence"],
        "serial_uniqueness":    ss["serial_uniqueness"],
        "narration_hard_gate":  ss["narration_hard_gate"],
    }
    narration_result       = generate_narration(record)
    ss["narration_result"] = narration_result
    ss["badge_decision"]   = narration_result["badge_decision"]


# ── Stage renderers ───────────────────────────────────────────────────────────

def _render_stages_0_1() -> None:
    with st.expander("Stages 0–1: Picker Registration & Collection Event", expanded=False):
        c1, c2 = st.columns(2)
        c1.markdown(_info_table("Stage 0 — Picker Registration", [
            ("Picker ID", "PCK-0041"), ("Name", "Rajesh Kumar"),
            ("Zone", "Hyderabad South"), ("Onboarded", "15 Aug 2026"),
            ("Status", "ACTIVE"),
        ]), unsafe_allow_html=True)
        c2.markdown(_info_table("Stage 1 — Collection Event", [
            ("Event ID", "EVT-2026-09441"), ("Date", "21 Sep 2026, 09:14 AM"),
            ("Location", "Hyderabad, Telangana"), ("Items", "1"),
            ("Status", "COMPLETED"),
        ]), unsafe_allow_html=True)


def _render_stage_2() -> None:
    ss = st.session_state
    _section_label("STAGE 2 — IDENTITY & STATE CAPTURE")

    intact     = ss["item_state"] == "intact"
    dismantled = ss["item_state"] == "dismantled"

    col_a, col_b = st.columns(2)
    with col_a:
        _state_card("Intact Item",         "Serial/IMEI can be captured",   intact)
    with col_b:
        _state_card("Already Dismantled",  "Component classification used", dismantled)

    st.markdown("")

    if ss["item_state"] == "intact":
        _render_ocr_result()
    else:
        _render_cv_result()


def _state_card(label: str, sub: str, active: bool) -> None:
    border = "2px solid #16a34a" if active else "1px solid #d1d5db"
    bg     = "#f0fdf4"           if active else "#fff"
    col_t  = "#166534"           if active else "#374151"
    tick   = "✓ " if active else ""
    st.markdown(
        f'<div style="background:{bg};border:{border};border-radius:10px;padding:12px 14px;">'
        f'<div style="font-size:13px;font-weight:700;color:{col_t};">{tick}{label}</div>'
        f'<div style="font-size:11px;color:#6b7280;margin-top:2px;">{sub}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_ocr_result() -> None:
    ss  = st.session_state
    ocr = run_ocr(confidence=ss["ocr_confidence"], fixed_serial=ss["serial"])

    st.markdown(
        '<div style="background:#fef9c3;border:1px solid #fde68a;border-radius:6px;'
        'padding:7px 12px;font-size:11px;color:#92400e;font-weight:600;">'
        'Prototype OCR — mocked output. No real OCR model applied.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    uploaded = st.file_uploader("Upload Device Image (optional)", type=["jpg","jpeg","png"], key="ocr_image")
    if uploaded:
        st.image(uploaded, width=200)

    c1, c2, c3 = st.columns(3)
    _metric_cell(c1, "Serial / IMEI",    ocr["serial"])
    _metric_cell(c2, "OCR Confidence",   f"{int(ocr['confidence']*100)}%")
    _metric_cell(c3, "Serial Uniqueness",f"{int(ocr['serial_uniqueness']*100)}%")


def _render_cv_result() -> None:
    ss = st.session_state
    cv = predict_component(component=ss["component"], confidence=ss["component_confidence"])

    st.markdown(
        '<div style="background:#fef9c3;border:1px solid #fde68a;border-radius:6px;'
        'padding:7px 12px;font-size:11px;color:#92400e;font-weight:600;">'
        'Prototype CV — mocked output. No real computer vision model applied.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:6px;'
        'padding:8px 12px;font-size:11px;color:#0369a1;margin-top:6px;">'
        'Because the item was already dismantled at the first capture point, '
        'component evidence is used instead of serial/IMEI identity.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    uploaded = st.file_uploader("Upload Component Image (optional)", type=["jpg","jpeg","png"], key="cv_image")
    if uploaded:
        st.image(uploaded, width=200)

    c1, c2, c3 = st.columns(3)
    _metric_cell(c1, "Predicted Component", cv["component"])
    _metric_cell(c2, "CV Confidence",       f"{int(cv['confidence']*100)}%")
    _metric_cell(c3, "Possible Classes",    " · ".join(cv["possible_classes"]))
    st.caption("Component class is set via Demo Controls →")


def _render_stage_3() -> None:
    ss = st.session_state
    render_evidence_card(
        gps_validity        = ss["gps_validity"],
        image_quality       = ss["image_quality"],
        weight_consistency  = ss["weight_consistency"],
        facility_validity   = ss["facility_validity"],
        facility_name       = ss["facility_name"],
        item_state          = ss["item_state"],
        component_or_serial = (ss["component"] if ss["item_state"] == "dismantled"
                               else ss["serial"]),
    )


def _render_stages_4_5() -> None:
    with st.expander("Stages 4–5: Transport & Facility Intake", expanded=False):
        c1, c2 = st.columns(2)
        c1.markdown(_info_table("Stage 4 — Transport to Facility", [
            ("Carrier", "EcoLogistics Ltd"), ("Departed", "21 Sep 2026, 10:05 AM"),
            ("Arrived", "21 Sep 2026, 11:20 AM"), ("Seal Intact", "Yes"),
            ("Status", "COMPLETED"),
        ]), unsafe_allow_html=True)
        c2.markdown(_info_table("Stage 5 — Facility Intake Confirmation", [
            ("Intake Officer", "FAC-001-OPS"), ("Intake Time", "21 Sep 2026, 11:22 AM"),
            ("Evidence Check", "PASSED"), ("Weight Verified", "Yes"),
            ("Status", "COMPLETED"),
        ]), unsafe_allow_html=True)


def _render_stage_6() -> None:
    score_result = st.session_state.get("score_result")
    if score_result:
        render_score_card(score_result)


def _render_stage_7() -> None:
    gate_result = st.session_state.get("gate_result")
    if gate_result:
        render_processing_gate(gate_result)


def _render_stage_8() -> None:
    ss               = st.session_state
    narration_result = ss.get("narration_result") or {}
    _section_label("STAGE 8 — NARRATION GENERATION")

    if not narration_result.get("allowed", False):
        block_reason = narration_result.get(
            "block_reason",
            "Processing completion evidence is required before compliance narration can be generated."
        )
        st.markdown(
            f'<div style="background:#fef2f2;border:1px solid #fecaca;'
            f'border-left:4px solid #dc2626;border-radius:8px;padding:14px 16px;">'
            f'<p style="font-size:13px;font-weight:700;color:#991b1b;margin:0 0 4px 0;">'
            f'Narration Blocked</p>'
            f'<p style="font-size:12px;color:#b91c1c;margin:0;">{block_reason}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:6px;'
            'padding:7px 12px;font-size:11px;color:#166534;font-weight:600;">'
            'Prototype-generated narration — no LLM or RAG pipeline used.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("")
        narr_text = narration_result.get("narration_text", "")
        st.markdown(
            f'<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;'
            f'padding:16px;font-size:13px;color:#374151;line-height:1.7;">'
            f'{narr_text}</div>',
            unsafe_allow_html=True,
        )


def _render_stage_9() -> None:
    ss               = st.session_state
    narration_result = ss.get("narration_result") or {}
    _section_label("STAGE 9 — NARRATION CONFIDENCE")

    if not narration_result.get("allowed", False):
        st.caption("Not available — narration was blocked.")
        return

    hard_gates  = narration_result.get("hard_gates",  [])
    soft_scores = narration_result.get("soft_scores", [])
    n_conf      = narration_result.get("narration_confidence", 0) or 0
    n_status    = narration_result.get("narration_status", "—")

    # Score + status — all in ONE self-contained block
    sc = status_colour(n_status)
    sb = status_bg(n_status)
    st.markdown(
        f'<div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:18px 20px;">'
        f'<p style="font-size:10px;font-weight:600;color:#6b7280;'
        f'text-transform:uppercase;margin:0 0 2px 0;">Narration Confidence</p>'
        f'<p style="font-size:36px;font-weight:800;color:#111827;margin:0 0 8px 0;">{n_conf:.3f}</p>'
        f'<span style="background:{sb};color:{sc};border:1px solid {sc}44;'
        f'border-radius:6px;padding:4px 12px;font-size:13px;font-weight:700;">{n_status}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    # Hard gates — each is its own complete self-contained block
    st.markdown(
        '<p style="font-size:11px;font-weight:600;color:#6b7280;'
        'text-transform:uppercase;letter-spacing:0.06em;margin:0;">Hard Gates</p>',
        unsafe_allow_html=True,
    )
    for gate in hard_gates:
        g_col = "#16a34a" if gate["passed"] else "#dc2626"
        g_sym = "✓" if gate["passed"] else "✕"
        g_bg  = "#f0fdf4" if gate["passed"] else "#fef2f2"
        st.markdown(
            f'<div style="background:{g_bg};border:1px solid {g_col}33;'
            f'border-radius:6px;padding:7px 12px;margin-top:5px;">'
            f'<span style="color:{g_col};font-weight:700;font-size:13px;margin-right:8px;">{g_sym}</span>'
            f'<span style="font-size:12px;color:#374151;">{gate["label"]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("")
    st.markdown(
        '<p style="font-size:11px;font-weight:600;color:#6b7280;'
        'text-transform:uppercase;letter-spacing:0.06em;margin:0;">Soft Score Breakdown</p>',
        unsafe_allow_html=True,
    )

    # Build the entire breakdown table as ONE markdown call
    rows_html = ""
    for s in soft_scores:
        bar_pct = int(s["value"] * 100)
        bar_col = "#16a34a" if s["value"] >= 0.80 else "#d97706" if s["value"] >= 0.60 else "#dc2626"
        rows_html += (
            f'<tr>'
            f'<td style="font-size:11px;color:#374151;padding:5px 8px 5px 0;white-space:nowrap;">'
            f'{s["label"]}</td>'
            f'<td style="padding:5px 8px;width:50%;">'
            f'<div style="background:#f3f4f6;border-radius:4px;height:5px;">'
            f'<div style="background:{bar_col};width:{bar_pct}%;height:5px;border-radius:4px;"></div>'
            f'</div></td>'
            f'<td style="font-size:11px;color:#6b7280;padding:5px 0 5px 8px;'
            f'white-space:nowrap;text-align:right;">'
            f'{s["value"]:.2f} × {int(s["weight"]*100)}% = <strong>{s["contribution"]:.3f}</strong></td>'
            f'</tr>'
        )
    st.markdown(
        f'<table style="width:100%;border-collapse:collapse;margin-top:8px;">'
        f'{rows_html}'
        f'</table>'
        f'<p style="font-size:10px;color:#6b7280;margin-top:8px;">'
        f'Thresholds: ≥ 0.85 → AUTO-ISSUED · 0.60–0.84 → HITL REVIEW · &lt; 0.60 → REJECTED</p>',
        unsafe_allow_html=True,
    )


def _render_stage_10() -> None:
    ss = st.session_state
    _section_label("STAGE 10 — TRUST BADGE")

    narration_result = ss.get("narration_result") or {}
    render_trust_badge(
        badge_status         = ss.get("badge_decision") or "PENDING",
        trust_score          = ss.get("trust_score") or 0.0,
        narration_confidence = narration_result.get("narration_confidence"),
        gate_status          = "PASSED" if ss.get("gate_passed") else "FAILED",
        batch_id             = ss.get("batch_id",      "BATCH-2026-00124"),
        facility_name        = ss.get("facility_name", "GreenCycle Hyderabad"),
        item_state           = ss.get("item_state",    "dismantled"),
        component_or_serial  = (ss.get("component") if ss.get("item_state") == "dismantled"
                                else ss.get("serial", "—")),
    )


def _render_pipeline_summary() -> None:
    ss = st.session_state
    stage_statuses = build_stage_statuses(
        item_state        = ss.get("item_state", "dismantled"),
        trust_score       = ss.get("trust_score"),
        gate_passed       = ss.get("gate_passed"),
        badge_decision    = ss.get("badge_decision"),
        narration_allowed = bool(ss.get("gate_passed")),
    )
    active = 6
    if ss.get("gate_passed") is not None:
        active = 7
    if (ss.get("narration_result") or {}).get("allowed"):
        active = 10
    render_pipeline(stage_statuses, active_stage=active)


# ── Demo Controls ─────────────────────────────────────────────────────────────

def _render_demo_controls() -> None:
    ss = st.session_state

    st.markdown(
        '<div style="background:#1e293b;border-radius:12px;padding:14px 12px;margin-bottom:8px;">'
        '<p style="font-size:11px;font-weight:700;color:#94a3b8;'
        'letter-spacing:0.1em;text-transform:uppercase;margin:0 0 2px 0;">Demo Controls</p>'
        '<p style="font-size:10px;color:#64748b;margin:0;">Adjust to simulate scenarios</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    preset_name = st.selectbox("Load Preset", ["— select —"] + get_preset_names(), key="preset_selector")
    if preset_name != "— select —":
        apply_preset_to_state(preset_name, ss)
        st.rerun()

    st.markdown("---")

    state_val = st.radio("Item State", ["dismantled", "intact"],
                         index=0 if ss["item_state"] == "dismantled" else 1,
                         key="ctrl_item_state", horizontal=True)
    ss["item_state"] = state_val

    if state_val == "dismantled":
        ss["component"] = st.selectbox(
            "Component Class", COMPONENT_CLASSES,
            index=COMPONENT_CLASSES.index(ss.get("component", "PCB")),
            key="ctrl_component",
        )
        ss["component_confidence"]  = st.slider("Component Confidence",  0.0, 1.0, float(ss["component_confidence"]),  0.01, key="ctrl_comp_conf")
        ss["material_plausibility"] = st.slider("Material Plausibility", 0.0, 1.0, float(ss["material_plausibility"]), 0.01, key="ctrl_mat_plaus")
    else:
        ss["ocr_confidence"]   = st.slider("OCR Confidence",   0.0, 1.0, float(ss["ocr_confidence"]),   0.01, key="ctrl_ocr_conf")
        ss["serial_uniqueness"]= st.slider("Serial Uniqueness",0.0, 1.0, float(ss["serial_uniqueness"]), 0.01, key="ctrl_serial_uniq")

    st.markdown("---")
    st.caption("EVIDENCE METRICS")
    ss["facility_validity"]  = st.slider("Facility Validity",  0.0, 1.0, float(ss["facility_validity"]),  0.01, key="ctrl_fac")
    ss["gps_validity"]       = st.slider("GPS Validity",       0.0, 1.0, float(ss["gps_validity"]),       0.01, key="ctrl_gps")
    ss["image_quality"]      = st.slider("Image Quality",      0.0, 1.0, float(ss["image_quality"]),      0.01, key="ctrl_img")
    ss["weight_consistency"] = st.slider("Weight Consistency", 0.0, 1.0, float(ss["weight_consistency"]), 0.01, key="ctrl_wgt")

    st.markdown("---")
    st.caption("PROCESSING GATE")
    ss["completion_evidence"]  = st.toggle("Completion Evidence Submitted", value=bool(ss["completion_evidence"]),  key="ctrl_comp_ev")
    ss["within_time_window"]   = st.toggle("Within Time Window",            value=bool(ss["within_time_window"]),   key="ctrl_time_win")
    ss["narration_hard_gate"]  = st.toggle("Narration Hard Gate Pass",      value=bool(ss["narration_hard_gate"]),  key="ctrl_narr_gate")

    # Live score readout
    score = ss.get("trust_score")
    if score is not None:
        st.markdown("---")
        sc = status_colour(ss.get("trust_status", ""))
        sb = status_bg(ss.get("trust_status", ""))
        st.markdown(
            f'<div style="background:{sb};border:1px solid {sc}44;'
            f'border-radius:8px;padding:10px 12px;text-align:center;">'
            f'<p style="font-size:10px;color:#6b7280;font-weight:600;'
            f'text-transform:uppercase;margin:0 0 2px 0;">Trust Score</p>'
            f'<p style="font-size:26px;font-weight:800;color:{sc};margin:0;">{score:.3f}</p>'
            f'<p style="font-size:11px;font-weight:600;color:{sc};margin:0;">'
            f'{ss.get("trust_status","")}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ── Tiny HTML helpers — all return complete self-contained fragments ───────────

def _section_label(text: str) -> None:
    st.markdown(
        f'<p style="font-size:11px;font-weight:600;color:#6b7280;'
        f'letter-spacing:0.08em;text-transform:uppercase;margin:0 0 8px 0;">'
        f'{text}</p>',
        unsafe_allow_html=True,
    )


def _metric_cell(col, label: str, value: str) -> None:
    col.markdown(
        f'<div style="background:#f9fafb;border:1px solid #e5e7eb;'
        f'border-radius:8px;padding:12px;">'
        f'<p style="font-size:10px;color:#6b7280;font-weight:600;'
        f'text-transform:uppercase;letter-spacing:0.06em;margin:0 0 4px 0;">{label}</p>'
        f'<p style="font-size:14px;font-weight:700;color:#111827;margin:0;">{value}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _info_table(title: str, rows: list[tuple[str, str]]) -> str:
    """Returns a complete self-contained HTML card string for st.markdown."""
    row_html = "".join(
        f'<tr>'
        f'<td style="font-size:12px;color:#6b7280;padding:4px 8px 4px 0;">{k}</td>'
        f'<td style="font-size:12px;font-weight:600;color:#374151;padding:4px 0;">{v}</td>'
        f'</tr>'
        for k, v in rows
    )
    return (
        f'<div style="background:#fff;border:1px solid #e5e7eb;'
        f'border-radius:10px;padding:14px;">'
        f'<p style="font-size:12px;font-weight:700;color:#374151;margin:0 0 10px 0;">{title}</p>'
        f'<table style="width:100%;border-collapse:collapse;">{row_html}</table>'
        f'</div>'
    )
