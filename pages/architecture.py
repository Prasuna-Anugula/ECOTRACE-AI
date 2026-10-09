"""
EcoTrace AI — System Architecture Page
RULE: No display:flex/grid. No split divs. Uses tables and native st.columns.
"""

from __future__ import annotations
import streamlit as st


def render_architecture() -> None:
    st.markdown("## System Architecture")
    st.caption("End-to-end architecture of the EcoTrace AI evidence-verification pipeline.")

    # ── Overview banner ───────────────────────────────────────────────────
    st.markdown(
        '<div style="background:#f0fdf4;border:1px solid #bbf7d0;'
        'border-left:4px solid #16a34a;border-radius:8px;padding:14px 16px;margin-bottom:20px;">'
        '<p style="font-size:13px;font-weight:700;color:#166534;margin:0 0 4px 0;">'
        'Prototype Architecture</p>'
        '<p style="font-size:12px;color:#374151;line-height:1.6;margin:0;">'
        'EcoTrace AI verifies e-waste collection and processing events through a 12-stage pipeline. '
        'Two critical decisions: (1) dismantled items use CV component classification — no score '
        'penalty for missing serial; and (2) the Processing Completion Gate is a hard gate that '
        'cannot be bypassed even with a perfect Trust Score.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Pipeline diagram + component details ──────────────────────────────
    st.markdown(
        '<p style="font-size:11px;font-weight:600;color:#6b7280;'
        'letter-spacing:0.08em;text-transform:uppercase;margin:0 0 12px 0;">'
        'PIPELINE ARCHITECTURE</p>',
        unsafe_allow_html=True,
    )

    diag_col, detail_col = st.columns([2, 1], gap="large")

    with diag_col:
        _render_pipeline_diagram()

    with detail_col:
        st.markdown(
            '<p style="font-size:11px;font-weight:600;color:#6b7280;'
            'letter-spacing:0.08em;text-transform:uppercase;margin:0 0 10px 0;">'
            'COMPONENT DETAILS</p>',
            unsafe_allow_html=True,
        )
        _render_component_details()

    st.markdown("---")

    # ── Trust Score formulas ──────────────────────────────────────────────
    st.markdown(
        '<p style="font-size:11px;font-weight:600;color:#6b7280;'
        'letter-spacing:0.08em;text-transform:uppercase;margin:0 0 12px 0;">'
        'TRUST SCORE FORMULAS</p>',
        unsafe_allow_html=True,
    )

    fa, fb = st.columns(2)
    with fa:
        _formula_card("Mode A — Intact Item", [
            ("Serial / IMEI OCR Confidence",  "30%"),
            ("Serial Uniqueness",              "15%"),
            ("Facility Registration Validity", "20%"),
            ("GPS Validity",                   "15%"),
            ("Image Quality",                  "10%"),
            ("Weight Consistency",             "10%"),
        ], "#2563eb", "#eff6ff")
    with fb:
        _formula_card("Mode B — Dismantled Item", [
            ("Component Classification Confidence", "30%"),
            ("Material Composition Plausibility",   "15%"),
            ("Facility Registration Validity",       "20%"),
            ("GPS Validity",                         "15%"),
            ("Image Quality",                        "10%"),
            ("Weight Consistency",                   "10%"),
        ], "#16a34a", "#f0fdf4")

    st.markdown("---")

    # ── Stage 7 explainer ─────────────────────────────────────────────────
    st.markdown(
        '<div style="background:#fff7ed;border:1px solid #fed7aa;'
        'border-left:4px solid #ea580c;border-radius:8px;padding:16px 18px;">'
        '<p style="font-size:13px;font-weight:700;color:#9a3412;margin:0 0 8px 0;">'
        'Stage 7 — Processing Completion Gate (Hard Gate)</p>'
        '<p style="font-size:12px;color:#374151;line-height:1.7;margin:0 0 8px 0;">'
        '<strong>The core architectural insight:</strong> A high Evidence Trust Score proves '
        'that collection evidence is reliable. It does NOT prove that the item was actually '
        'processed or destroyed. The gate requires independent evidence submitted within '
        'a 72-hour window. Both conditions must be true:</p>'
        '<ul style="font-size:12px;color:#374151;margin:0 0 8px 0;padding-left:20px;line-height:1.8;">'
        '<li>Processing completion evidence has been submitted</li>'
        '<li>Evidence was submitted within the 72-hour time window</li>'
        '</ul>'
        '<p style="font-size:12px;color:#92400e;font-weight:600;margin:0;">'
        'If either condition fails → badge issuance is blocked regardless of Trust Score.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── ML integration path ───────────────────────────────────────────────
    st.markdown(
        '<p style="font-size:11px;font-weight:600;color:#6b7280;'
        'letter-spacing:0.08em;text-transform:uppercase;margin:0 0 12px 0;">'
        'FUTURE ML INTEGRATION PATH</p>',
        unsafe_allow_html=True,
    )

    ml1, ml2, ml3 = st.columns(3)
    _ml_card(ml1, "Current (Prototype)", [
        "mock_ocr.py — returns fixed serial + confidence",
        "mock_cv.py — returns selected component + confidence",
        "Trust Score uses mocked values",
        "Narration is template-generated",
    ], "#6b7280", "#f9fafb")
    _ml_card(ml2, "Near-term Integration", [
        "Replace mock_ocr.py with real OCR service",
        "Replace mock_cv.py with trained CNN classifier",
        "Same input/output interface — no engine changes",
        "RAG pipeline for narration generation",
    ], "#2563eb", "#eff6ff")
    _ml_card(ml3, "Target Architecture", [
        "Fine-tuned OCR on e-waste label dataset",
        "Component classifier: PCB / Battery / Keyboard / Mouse",
        "LLM + RAG for regulatory-grounded narration",
        "Trained anomaly detection on facility patterns",
    ], "#16a34a", "#f0fdf4")

    render_limitations()


# ── Sub-renderers ─────────────────────────────────────────────────────────────

def _render_pipeline_diagram() -> None:
    """
    Pipeline rendered as a sequence of self-contained node blocks
    separated by arrow markers. No flex/grid.
    """
    def _node(label: str, sub: str, colour: str, bg: str) -> None:
        st.markdown(
            f'<div style="background:{bg};border:1.5px solid {colour};'
            f'border-radius:8px;padding:10px 14px;text-align:center;">'
            f'<p style="font-size:12px;font-weight:700;color:{colour};margin:0 0 2px 0;">'
            f'{label}</p>'
            f'<p style="font-size:10px;color:#6b7280;margin:0;">{sub}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    def _arrow() -> None:
        st.markdown(
            '<p style="text-align:center;color:#9ca3af;font-size:18px;margin:4px 0;">↓</p>',
            unsafe_allow_html=True,
        )

    _node("Data Capture", "Stage 0–1: Picker Registration + Collection", "#374151", "#f9fafb")
    _arrow()

    # Stage 2 split — use native columns
    st.markdown(
        '<p style="text-align:center;font-size:10px;font-weight:600;color:#6b7280;'
        'letter-spacing:0.06em;margin:2px 0;">STAGE 2 — IDENTITY &amp; STATE CAPTURE</p>',
        unsafe_allow_html=True,
    )
    s2a, s2b = st.columns(2)
    s2a.markdown(
        '<div style="background:#eff6ff;border:1.5px solid #2563eb;'
        'border-radius:8px;padding:10px;text-align:center;">'
        '<p style="font-size:12px;font-weight:700;color:#2563eb;margin:0 0 2px 0;">INTACT</p>'
        '<p style="font-size:10px;color:#6b7280;margin:0;">OCR / Serial IMEI</p>'
        '<p style="font-size:10px;color:#6b7280;margin:2px 0 0 0;">mock_ocr.py → serial + conf</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    s2b.markdown(
        '<div style="background:#f0fdf4;border:1.5px solid #16a34a;'
        'border-radius:8px;padding:10px;text-align:center;">'
        '<p style="font-size:12px;font-weight:700;color:#16a34a;margin:0 0 2px 0;">DISMANTLED</p>'
        '<p style="font-size:10px;color:#6b7280;margin:0;">Component CV Classification</p>'
        '<p style="font-size:10px;color:#6b7280;margin:2px 0 0 0;">mock_cv.py → PCB/Battery/…</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p style="text-align:center;color:#9ca3af;font-size:14px;margin:4px 0;">'
        '↓ (merge)</p>',
        unsafe_allow_html=True,
    )

    _node("Evidence Assembly", "Stage 3: GPS · Image Quality · Weight · Facility", "#374151", "#f9fafb")
    _arrow()
    _node("Trust Score Engine", "Stage 6: Weighted formula — Intact or Dismantled mode", "#7c3aed", "#f5f3ff")
    _arrow()

    # Stage 7 — highlighted
    st.markdown(
        '<div style="background:#fff7ed;border:2px solid #ea580c;'
        'border-radius:8px;padding:10px 14px;text-align:center;">'
        '<p style="font-size:12px;font-weight:700;color:#ea580c;margin:0 0 2px 0;">'
        'Processing Completion Gate</p>'
        '<p style="font-size:10px;color:#6b7280;margin:0;">'
        'Stage 7 — Hard gate. Both conditions required.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    _arrow()
    _node("RAG / Narration", "Stage 8–9: Compliance narration + confidence score", "#0891b2", "#ecfeff")
    _arrow()
    _node("Trust Badge", "Stage 10: AUTO-ISSUED · HITL REVIEW · REJECTED", "#16a34a", "#f0fdf4")
    _arrow()
    _node("Audit Dashboard", "Stage 11: Facility patterns · Anomaly detection", "#374151", "#f9fafb")


def _render_component_details() -> None:
    components = [
        ("Picker App",           "Mobile data capture — GPS, image, weight"),
        ("mock_ocr.py",          "Serial/IMEI extraction from device label"),
        ("mock_cv.py",           "Component classification (PCB/Battery/…)"),
        ("trust_score.py",       "Weighted scoring — intact or dismantled mode"),
        ("processing_gate.py",   "Hard gate — completion evidence check"),
        ("narration.py",         "Template → future RAG/LLM narration"),
        ("anomaly_detection.py", "Rule-based facility anomaly flags"),
        ("Audit Dashboard",      "Government / regulator view"),
    ]
    for label, desc in components:
        st.markdown(
            f'<div style="background:#fff;border:1px solid #e5e7eb;'
            f'border-radius:8px;padding:9px 12px;margin-bottom:5px;">'
            f'<p style="font-size:12px;font-weight:600;color:#374151;'
            f'font-family:monospace;margin:0 0 2px 0;">{label}</p>'
            f'<p style="font-size:11px;color:#6b7280;margin:0;">{desc}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )


def _formula_card(title: str, rows: list[tuple[str, str]], colour: str, bg: str) -> None:
    row_html = "".join(
        f'<tr><td style="font-size:11px;color:#374151;padding:5px 8px 5px 0;">{label}</td>'
        f'<td style="font-size:11px;font-weight:700;color:{colour};'
        f'padding:5px 0 5px 8px;text-align:right;">{weight}</td></tr>'
        for label, weight in rows
    )
    st.markdown(
        f'<div style="background:{bg};border:1px solid {colour}44;'
        f'border-radius:10px;padding:14px;">'
        f'<p style="font-size:12px;font-weight:700;color:{colour};margin:0 0 10px 0;">{title}</p>'
        f'<table style="width:100%;border-collapse:collapse;">{row_html}</table>'
        f'<p style="font-size:10px;color:#6b7280;margin:8px 0 0 0;">All weights sum to 100%</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _ml_card(col, title: str, points: list[str], colour: str, bg: str) -> None:
    items = "".join(
        f'<li style="margin-bottom:4px;">{p}</li>' for p in points
    )
    col.markdown(
        f'<div style="background:{bg};border:1px solid {colour}44;'
        f'border-radius:10px;padding:14px;">'
        f'<p style="font-size:12px;font-weight:700;color:{colour};margin:0 0 8px 0;">{title}</p>'
        f'<ul style="font-size:11px;color:#374151;padding-left:16px;'
        f'margin:0;line-height:1.7;">{items}</ul>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_limitations() -> None:
    """
    Standalone section rendering all known loopholes and their mitigations.
    Called at the bottom of render_architecture().
    """
    st.markdown("---")
    st.markdown(
        '<p style="font-size:11px;font-weight:600;color:#6b7280;'
        'letter-spacing:0.08em;text-transform:uppercase;margin:0 0 12px 0;">'
        'KNOWN LIMITATIONS &amp; MITIGATIONS</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="background:#fffbeb;border:1px solid #fde68a;'
        'border-left:4px solid #f59e0b;border-radius:8px;padding:12px 16px;margin-bottom:16px;">'
        '<p style="font-size:12px;font-weight:700;color:#92400e;margin:0 0 4px 0;">'
        'Academic Honesty Notice</p>'
        '<p style="font-size:11px;color:#78350f;line-height:1.7;margin:0;">'
        'EcoTrace is a functional prototype. The limitations below are acknowledged gaps '
        'between the prototype and a production-grade system. Each has a documented '
        'mitigation strategy. Panels are encouraged to ask about any of these.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    limitations = [
        {
            "id": "L1",
            "title": "Evidence submitted by recycler — GPS/photo integrity",
            "problem": "GPS spoofing apps, reused stock photos, and edited images are easy to produce. The recycler controls all evidence submission.",
            "mitigation": "In-app live capture only (no gallery uploads). EXIF metadata check (timestamp + GPS embedded at capture). pHash duplicate detection (same photo across submissions = instant flag). Geofence enforcement (GPS must fall within registered facility zone).",
            "status": "Production",
            "colour": "#d97706",
        },
        {
            "id": "L2",
            "title": "Hard veto rules (implemented in v0.2)",
            "problem": "Previously: a spoofed GPS could be hidden by a high OCR score in the weighted sum.",
            "mitigation": "VETO_FACILITY_MIN=0.50 and VETO_GPS_MIN=0.30 now applied BEFORE the weighted sum. Score is set to 0.0 regardless of other metrics if either veto fires. See trust_score.py.",
            "status": "Implemented",
            "colour": "#16a34a",
        },
        {
            "id": "L3",
            "title": "Stage 7 processing proof — photo is fakeable",
            "problem": "A photo of 'destruction' is trivially fakeable. Yes/no completion flag is insufficient.",
            "mitigation": "Mass balance check added: declared output weight must be ≥ 60% of input weight. In production: downstream smelter/recycler invoices must reconcile with input weight (copper, PCB, plastic yields). See processing_gate.py.",
            "status": "Partial (implemented in prototype)",
            "colour": "#d97706",
        },
        {
            "id": "L4",
            "title": "Cross-platform serial double-claiming",
            "problem": "Same device submitted at EcoTrace AND another platform → two EPR credits for one device.",
            "mitigation": "EcoTrace serial hashes are SHA-256 format, registry-compatible. When a national IMEI hash registry exists (CPCB or delegated body), the uniqueness check swaps from local DB to registry API — no architecture changes needed. Stated as a known limitation.",
            "status": "Future work",
            "colour": "#6b7280",
        },
        {
            "id": "L5",
            "title": "Ghost facilities — registration ≠ operational capacity",
            "problem": "A facility can be CPCB-registered with minimal infrastructure. Registration alone does not verify operational capacity.",
            "mitigation": "Rule 4 in anomaly_detection.py: daily_items_submitted / declared_daily_capacity > 1.20 triggers a ghost facility flag. Production: cross-reference with electricity meter data and equipment inspection records.",
            "status": "Implemented (Rule 4)",
            "colour": "#16a34a",
        },
        {
            "id": "L6",
            "title": "Picker–facility collusion",
            "problem": "Ghost pickers or inflated volumes — facility registers fake pickers and submits ghost collections.",
            "mitigation": "Rule 5 in anomaly_detection.py: per-picker volume > 3× median daily volume is flagged. Production: picker–facility network graph (facility where 90%+ of submissions come from 2 pickers who are employees = collusion signal).",
            "status": "Implemented (Rule 5)",
            "colour": "#16a34a",
        },
        {
            "id": "L7",
            "title": "Narration circular scoring (fixed in v0.2)",
            "problem": "Previously: soft scores were derived from trust_score, making narration confidence circular.",
            "mitigation": "Narration now generated from verified facts only. Soft scores measure structural properties (all fields present, cross-field consistency, chronological order) — not derived from trust_score. LLM role is phrasing only. See narration.py.",
            "status": "Implemented",
            "colour": "#16a34a",
        },
        {
            "id": "L8",
            "title": "Arbitrary thresholds",
            "problem": "0.80 / 0.55 / 72hr — a panel will ask where these came from.",
            "mitigation": "Initialised from domain expert heuristics (see config.py comments). Production: calibrated from precision/recall curve on labelled fraud dataset. Higher recall weight on REJECTED class — missing fraud costs more than a false HITL flag.",
            "status": "Documented in config.py",
            "colour": "#2563eb",
        },
        {
            "id": "L9",
            "title": "Synthetic data — circular evaluation",
            "problem": "Fraud cases in test data generated with same rules as detector → circular validation.",
            "mitigation": "Adversarial fraud generation required for production evaluation: fraud cases designed to fool the current system (high GPS + good OCR + impossible mass balance). Confirmed fraud labels from CPCB investigations needed for ground-truth validation.",
            "status": "Production requirement",
            "colour": "#6b7280",
        },
        {
            "id": "L10",
            "title": "EPR Certificate terminology (fixed in v0.2)",
            "problem": "Only CPCB can legally issue EPR certificates. EcoTrace calling outputs 'EPR certificates' is legally incorrect.",
            "mitigation": "Renamed throughout to 'Evidence Attestation' (EA). EcoTrace issues an EA — a cryptographically signed record supporting CPCB filing. Producers submit EAs as supporting evidence. Does not constitute an EPR certificate.",
            "status": "Implemented",
            "colour": "#16a34a",
        },
        {
            "id": "L11",
            "title": "Privacy — GPS and IMEI are personal data (DPDP Act 2023)",
            "problem": "Picker GPS tracks and device IMEIs are personal data. Storing in plaintext violates DPDP Act 2023.",
            "mitigation": "IMEI pseudonymised via SHA-256 hash immediately after OCR. Raw value discarded. Only masked hash stored and displayed. GPS abstracted to facility-zone flag in production. Picker IDs pseudonymised. Explicit consent at picker registration.",
            "status": "Implemented in mock_ocr.py",
            "colour": "#16a34a",
        },
    ]

    for lim in limitations:
        status_colour = lim["colour"]
        st.markdown(
            f'<div style="border:1px solid #e5e7eb;border-left:3px solid {status_colour};'
            f'border-radius:8px;padding:12px 14px;margin-bottom:8px;">'
            f'<table style="width:100%;border-collapse:collapse;">'
            f'<tr>'
            f'<td style="vertical-align:top;width:36px;">'
            f'<span style="font-size:10px;font-weight:800;color:{status_colour};'
            f'background:{status_colour}18;border-radius:4px;padding:2px 6px;">'
            f'{lim["id"]}</span></td>'
            f'<td style="vertical-align:top;padding-left:10px;">'
            f'<div style="font-size:12px;font-weight:700;color:#111827;margin-bottom:4px;">'
            f'{lim["title"]}</div>'
            f'<div style="font-size:11px;color:#6b7280;margin-bottom:4px;">'
            f'<strong>Problem:</strong> {lim["problem"]}</div>'
            f'<div style="font-size:11px;color:#374151;margin-bottom:4px;">'
            f'<strong>Mitigation:</strong> {lim["mitigation"]}</div>'
            f'<span style="font-size:10px;font-weight:700;color:{status_colour};'
            f'background:{status_colour}18;border-radius:4px;padding:1px 7px;">'
            f'{lim["status"]}</span>'
            f'</td></tr></table>'
            f'</div>',
            unsafe_allow_html=True,
        )
