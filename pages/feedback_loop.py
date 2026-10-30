"""
EcoTrace AI — Feedback Loop Page
──────────────────────────────────
Shows how audit outcomes become training labels that feed back into
model retraining — closing the loop from auditor → ML → better detection.

Sections:
  1. The feedback loop concept
  2. Current training label pool
  3. Feature importance (what the model learns from)
  4. Retraining pipeline diagram
  5. Model performance improvement tracking

NO display:flex/grid. All layout via st.columns() and <table>.
"""

from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
from services.credit_ledger import get_audit_outcomes, get_all_credits


def render_feedback_loop() -> None:
    st.markdown("## Feedback Loop — Audit Outcomes to Model Retraining")
    st.caption(
        "Every auditor outcome becomes a labelled training record. "
        "EcoTrace uses these labels to continuously improve the Trust Score and anomaly detection."
    )

    tab_concept, tab_labels, tab_pipeline, tab_performance = st.tabs([
        "How It Works",
        "Training Label Pool",
        "Retraining Pipeline",
        "Model Performance",
    ])

    with tab_concept:
        _render_concept()

    with tab_labels:
        _render_label_pool()

    with tab_pipeline:
        _render_pipeline()

    with tab_performance:
        _render_performance()


# ── Concept ───────────────────────────────────────────────────────────────────

def _render_concept() -> None:
    st.markdown(
        '<div style="background:#f0fdf4;border:1px solid #bbf7d0;'
        'border-left:4px solid #16a34a;border-radius:8px;'
        'padding:14px 16px;margin-bottom:20px;">'
        '<div style="font-size:14px;font-weight:700;color:#166534;margin-bottom:6px;">'
        'The EcoTrace Feedback Loop</div>'
        '<div style="font-size:12px;color:#374151;line-height:1.8;">'
        'EcoTrace starts with rule-based thresholds and heuristic weights. '
        'As auditors confirm or reject verification outcomes, those decisions '
        'become ground-truth labels. The labels retrain the Trust Score model '
        'and anomaly detector — making the system progressively harder to fool.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    steps = [
        ("1", "Verification Pipeline",    "Item passes Stages 0–11. Trust Score + badge decision made.", "#2563eb", "#eff6ff"),
        ("2", "Auditor Physical Inspection","Auditor visits facility, checks records, confirms legitimacy or fraud.", "#7c3aed", "#faf5ff"),
        ("3", "Outcome Recorded",          "Auditor logs CONFIRMED_LEGITIMATE (1) or CONFIRMED_FRAUD (0) in EcoTrace.", "#d97706", "#fffbeb"),
        ("4", "Feature Extraction",        "System extracts: trust_score, gate_passed, GPS, weight, facility_id, picker_id.", "#166534", "#f0fdf4"),
        ("5", "Model Retraining",          "Logistic regression / Random Forest retrained on new labelled batch.", "#374151", "#f9fafb"),
        ("6", "Threshold Recalibration",   "Precision/recall curve recalculated. AUTO-VERIFIED threshold updated.", "#374151", "#f9fafb"),
        ("7", "Weight Redistribution",     "Evidence component weights updated from feature importances.", "#374151", "#f9fafb"),
        ("8", "Adversarial Testing",       "New fraud patterns injected to test updated model before deployment.", "#dc2626", "#fef2f2"),
        ("9", "Deployment",               "Updated model deployed. Loop restarts with next audit cycle.", "#166534", "#f0fdf4"),
    ]

    for step in steps:
        num, title, desc, colour, bg = step
        st.markdown(
            f'<div style="border:1px solid #e5e7eb;border-left:3px solid {colour};'
            f'background:{bg};border-radius:8px;padding:10px 14px;margin-bottom:8px;">'
            f'<table style="width:100%;border-collapse:collapse;"><tr>'
            f'<td style="width:36px;vertical-align:top;">'
            f'<div style="width:28px;height:28px;background:{colour};border-radius:50%;'
            f'text-align:center;line-height:28px;font-size:12px;font-weight:800;color:#fff;">'
            f'{num}</div></td>'
            f'<td style="vertical-align:top;padding-left:10px;">'
            f'<div style="font-size:12px;font-weight:700;color:#111827;">{title}</div>'
            f'<div style="font-size:11px;color:#6b7280;margin-top:2px;">{desc}</div>'
            f'</td></tr></table></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div style="background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;'
        'padding:10px 16px;margin-top:8px;font-size:11px;color:#78350f;">'
        '<strong>Circular evaluation risk:</strong> If fraud cases in the training set are '
        'generated with the same rules as the detector, evaluation is circular. '
        'EcoTrace mitigates this by: (a) using only real auditor-confirmed labels, '
        'and (b) generating adversarial fraud cases independently of the current ruleset '
        'before each retraining cycle.'
        '</div>',
        unsafe_allow_html=True,
    )


# ── Training label pool ───────────────────────────────────────────────────────

def _render_label_pool() -> None:
    outcomes = get_audit_outcomes()
    credits  = get_all_credits()

    total_credits  = len(credits)
    labelled       = len(outcomes)
    unlabelled     = total_credits - labelled
    legitimate     = sum(1 for o in outcomes if o["label_for_training"] == 1)
    fraud          = sum(1 for o in outcomes if o["label_for_training"] == 0)
    label_rate     = round(labelled / total_credits * 100, 1) if total_credits else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Total Credits",     total_credits)
    with k2:
        st.metric("Labelled",          labelled, delta=f"{label_rate}% coverage")
    with k3:
        st.metric("Unlabelled",        unlabelled, delta="Pending audit", delta_color="off")
    with k4:
        st.metric("Legitimate (1)",    legitimate)
    with k5:
        st.metric("Fraud (0)",         fraud, delta="Adversarial cases" if fraud else None, delta_color="off")

    # Label imbalance warning
    if legitimate > 0 and fraud > 0:
        ratio = legitimate / fraud
        if ratio > 5:
            st.warning(
                f"Class imbalance: {legitimate} legitimate vs {fraud} fraud labels "
                f"(ratio {ratio:.1f}:1). Apply SMOTE or class weights during retraining "
                f"to avoid the model defaulting to 'legitimate' prediction."
            )

    # Pie chart
    if outcomes:
        fig = go.Figure(go.Pie(
            labels=["Confirmed Legitimate", "Confirmed Fraud", "Unlabelled"],
            values=[legitimate, fraud, unlabelled],
            marker_colors=["#16a34a", "#dc2626", "#d1d5db"],
            hole=0.5,
        ))
        fig.update_layout(
            height=250, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Label table
    st.markdown("#### Labelled Records")
    hdr = st.columns([1.8, 1.5, 1.0, 2.0, 1.5])
    for col, h in zip(hdr, ["Credit ID", "Batch", "Label", "Outcome", "Auditor"]):
        with col:
            st.markdown(
                f'<div style="font-size:11px;font-weight:700;color:#374151;'
                f'padding:6px 0;border-bottom:2px solid #e5e7eb;">{h}</div>',
                unsafe_allow_html=True,
            )
    for o in outcomes:
        label   = o["label_for_training"]
        lc      = "#16a34a" if label == 1 else "#dc2626" if label == 0 else "#6b7280"
        l_text  = "1 — Legitimate" if label == 1 else "0 — Fraud" if label == 0 else "-1 — Inconclusive"
        row     = st.columns([1.8, 1.5, 1.0, 2.0, 1.5])
        for col, val in zip(row, [
            o["credit_id"],
            o["batch_id"],
            f'<span style="font-weight:700;color:{lc};">{l_text}</span>',
            o["outcome"].replace("_"," "),
            o["auditor_id"],
        ]):
            with col:
                st.markdown(
                    f'<div style="font-size:11px;padding:5px 0;">{val}</div>',
                    unsafe_allow_html=True,
                )


# ── Retraining pipeline diagram ───────────────────────────────────────────────

def _render_pipeline() -> None:
    st.markdown("#### Retraining Pipeline Architecture")

    stages = [
        ("Raw Labels", "Auditor outcomes stored with credit_id, label, features", "#6b7280", "#f9fafb"),
        ("Feature Extraction", "trust_score, gate_passed, gps_validity, facility_id, weight_kg, picker_id, processing_time_hrs", "#2563eb", "#eff6ff"),
        ("Data Validation", "Remove duplicates. Check label balance. Flag circular cases (same rule generated label).", "#d97706", "#fffbeb"),
        ("Adversarial Injection", "Inject adversarial fraud cases (high GPS + good OCR + impossible mass balance) not present in training data.", "#dc2626", "#fef2f2"),
        ("Model Training", "Logistic Regression for Trust Score weights. Isolation Forest for anomaly detection. Cross-validation on hold-out set.", "#166534", "#f0fdf4"),
        ("Threshold Calibration", "Precision/recall curve. Set AUTO-VERIFIED threshold where precision ≥ 0.95. Higher recall weight on REJECTED class.", "#166534", "#f0fdf4"),
        ("Evaluation", "Evaluate on adversarial test set (not training set). Report F1, precision, recall, confusion matrix.", "#374151", "#f9fafb"),
        ("Deployment Gate", "New model only deployed if F1 ≥ current model F1. Rollback if any adversarial case passes.", "#374151", "#f9fafb"),
        ("Production", "Updated Trust Score weights + thresholds live in config.py. Loop restarts.", "#16a34a", "#f0fdf4"),
    ]

    for stage, (title, desc, colour, bg) in enumerate(stages):
        st.markdown(
            f'<div style="background:{bg};border:1px solid {colour}44;'
            f'border-radius:8px;padding:10px 14px;margin-bottom:4px;">'
            f'<table style="width:100%;border-collapse:collapse;"><tr>'
            f'<td style="width:36px;vertical-align:top;">'
            f'<span style="font-size:10px;font-weight:700;color:{colour};">S{stage+1}</span>'
            f'</td>'
            f'<td style="vertical-align:top;padding-left:8px;">'
            f'<div style="font-size:12px;font-weight:700;color:#111827;">{title}</div>'
            f'<div style="font-size:11px;color:#6b7280;margin-top:2px;">{desc}</div>'
            f'</td></tr></table></div>',
            unsafe_allow_html=True,
        )
        if stage < len(stages) - 1:
            st.markdown(
                '<p style="text-align:center;color:#9ca3af;font-size:14px;margin:0;">↓</p>',
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:8px;'
        'padding:10px 16px;margin-top:12px;font-size:11px;color:#6b7280;">'
        'Prototype: Trust Score weights and thresholds are fixed in config.py. '
        'Production: these are updated automatically after each retraining cycle. '
        'The retraining pipeline runs quarterly or when label pool grows by ≥ 500 records.'
        '</div>',
        unsafe_allow_html=True,
    )


# ── Model performance ─────────────────────────────────────────────────────────

def _render_performance() -> None:
    st.markdown("#### Model Performance Over Training Cycles")
    st.markdown(
        '<div style="background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;'
        'padding:10px 14px;margin-bottom:14px;font-size:11px;color:#78350f;">'
        'Simulated performance metrics. In production these are computed from '
        'hold-out evaluation after each retraining cycle.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Simulated improvement data across 5 cycles
    cycles    = ["Baseline", "Cycle 1", "Cycle 2", "Cycle 3", "Cycle 4"]
    precision = [0.72, 0.78, 0.83, 0.89, 0.93]
    recall    = [0.68, 0.74, 0.80, 0.85, 0.91]
    f1        = [0.70, 0.76, 0.815, 0.87, 0.92]
    fraud_det = [0.55, 0.64, 0.72, 0.81, 0.88]

    fig = go.Figure()
    for name, values, color in [
        ("Precision",         precision, "#2563eb"),
        ("Recall",            recall,    "#16a34a"),
        ("F1 Score",          f1,        "#7c3aed"),
        ("Fraud Detection Rate", fraud_det, "#dc2626"),
    ]:
        fig.add_trace(go.Scatter(
            x=cycles, y=values, name=name,
            mode="lines+markers",
            line=dict(color=color, width=2),
            marker=dict(size=8),
        ))

    fig.update_layout(
        height=300,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0.5, 1.0], showgrid=True, gridcolor="#f0f0f0"),
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        showlegend=True,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Confusion matrix (latest cycle)
    st.markdown("#### Confusion Matrix — Cycle 4 (Simulated)")
    cm_data = [[412, 18], [22, 148]]
    fig2 = go.Figure(go.Heatmap(
        z=cm_data,
        x=["Predicted Legitimate", "Predicted Fraud"],
        y=["Actual Legitimate", "Actual Fraud"],
        colorscale=[[0, "#f0fdf4"], [1, "#16a34a"]],
        text=[[str(v) for v in row] for row in cm_data],
        texttemplate="%{text}",
        showscale=False,
    ))
    fig2.update_layout(
        height=220, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("True Positives (Legit)", "412")
    with k2:
        st.metric("False Negatives (Missed Fraud)", "22", delta="Critical — missed fraud", delta_color="inverse")
    with k3:
        st.metric("True Negatives (Caught Fraud)", "148")
    with k4:
        st.metric("False Positives (False HITL)", "18", delta="Acceptable", delta_color="off")
