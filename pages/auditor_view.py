"""
EcoTrace AI — Auditor View
────────────────────────────
Regulator / CPCB auditor panel:
  - System-wide KPIs
  - Anomaly table across all facilities
  - Credit ledger with drill-down
  - Exportable CSV report (prototype: shows data as text)
  - Audit outcome recording (labels for model retraining)

NO display:flex/grid. All layout via st.columns() and <table>.
"""

from __future__ import annotations
import json
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from services.credit_ledger import (
    get_all_credits,
    get_lifecycle_summary,
    get_chain_integrity_status,
    get_audit_outcomes,
    STATUS_COLOURS,
)
from services.recycler_trust import get_all_recyclers
from services.anomaly_detection import detect_anomalies_all
import json
import os

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _load_facilities() -> list[dict]:
    path = os.path.join(_DATA_DIR, "mock_facilities.json")
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return raw if isinstance(raw, list) else raw.get("facilities", [])


def render_auditor_view() -> None:
    st.markdown("## Auditor Dashboard")
    st.caption("CPCB / Regulatory Auditor view — system-wide anomalies, credit integrity, and audit outcomes.")

    tab_overview, tab_anomalies, tab_credits, tab_outcomes, tab_export = st.tabs([
        "System Overview",
        "Anomaly Flags",
        "Credit Integrity",
        "Audit Outcomes",
        "Export Report",
    ])

    with tab_overview:
        _render_overview()

    with tab_anomalies:
        _render_anomalies()

    with tab_credits:
        _render_credit_integrity()

    with tab_outcomes:
        _render_audit_outcomes()

    with tab_export:
        _render_export()


# ── System overview ───────────────────────────────────────────────────────────

def _render_overview() -> None:
    credits    = get_all_credits()
    lifecycle  = get_lifecycle_summary()
    recyclers  = get_all_recyclers()
    chain      = get_chain_integrity_status(credits)

    total_credits_kg = sum(c["credit_kg"] for c in credits)
    sold_kg          = sum(c["credit_kg"] for c in credits if c["status"] == "SOLD")
    blocked          = sum(1 for c in credits if not c["gate_passed"])
    avg_trust        = (
        sum(c["trust_score"] for c in credits) / len(credits) if credits else 0
    )
    flagged_recyclers = sum(1 for r in recyclers if r.get("anomaly_flags"))

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    for col, label, val, delta, delta_inv in [
        (k1, "Total Credits",      f"{total_credits_kg:,.1f} kg",  None, False),
        (k2, "Sold Credits",       f"{sold_kg:,.1f} kg",           f"{sold_kg/total_credits_kg*100:.0f}% of issued" if total_credits_kg else "0%", False),
        (k3, "Gate Blocked",       str(blocked),                   "Credits not issued", True),
        (k4, "Avg Trust Score",    f"{avg_trust:.3f}",             None, False),
        (k5, "Recyclers Flagged",  str(flagged_recyclers),         "anomaly flags", True),
        (k6, "Chain Integrity",    f"{chain['ok']}/{chain['total']}", "records verified", False),
    ]:
        with col:
            st.metric(label, val, delta=delta, delta_color="inverse" if (delta and delta_inv) else "normal")

    st.markdown("---")

    # Lifecycle chart
    st.markdown("#### Credit Lifecycle Distribution")
    statuses = list(STATUS_COLOURS.keys())
    vals     = [lifecycle.get(s, {}).get("credit_kg", 0.0) for s in statuses]
    colors   = [STATUS_COLOURS[s]["color"] for s in statuses]
    fig = go.Figure(go.Bar(
        x=statuses, y=vals, marker_color=colors,
        text=[f"{v:,.1f}" for v in vals], textposition="outside",
    ))
    fig.update_layout(
        height=250, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="Credit kg", showgrid=True, gridcolor="#f0f0f0"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Trust score distribution
    st.markdown("#### Trust Score Distribution Across All Credits")
    scores = [c["trust_score"] for c in credits]
    if scores:
        fig2 = go.Figure(go.Histogram(
            x=scores, nbinsx=20,
            marker_color="#16a34a", opacity=0.8,
        ))
        fig2.update_layout(
            height=220, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Trust Score"),
            yaxis=dict(title="Count", showgrid=True, gridcolor="#f0f0f0"),
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})


# ── Anomaly flags ─────────────────────────────────────────────────────────────

def _render_anomalies() -> None:
    recyclers = get_all_recyclers()

    normal   = [r for r in recyclers if not r.get("anomaly_flags")]
    flagged  = [r for r in recyclers if r.get("anomaly_flags")]

    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Total Recyclers",   len(recyclers))
    with k2:
        st.metric("Flagged (REVIEW)",  len(flagged),
                  delta="Require investigation" if flagged else None,
                  delta_color="inverse" if flagged else "normal")
    with k3:
        st.metric("Normal",            len(normal))

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if flagged:
        st.markdown("#### Flagged Recyclers")
        for r in flagged:
            flags = r.get("anomaly_flags", [])
            flag_rows = "".join(
                f'<tr><td style="font-size:11px;color:#991b1b;padding:2px 0;">&#9888; {f}</td></tr>'
                for f in flags
            )
            st.markdown(
                f'<div style="background:#fef2f2;border:1px solid #fca5a5;'
                f'border-left:4px solid #dc2626;border-radius:10px;'
                f'padding:12px 16px;margin-bottom:10px;">'
                f'<table style="width:100%;border-collapse:collapse;">'
                f'<tr><td style="vertical-align:top;">'
                f'<div style="font-size:13px;font-weight:800;color:#111827;">'
                f'{r["company_name"]}</div>'
                f'<div style="font-size:11px;color:#6b7280;">Reg: {r["registration_number"]}'
                f' &nbsp;|&nbsp; Trust: {int(r.get("trust_score",0)*100)}%'
                f' &nbsp;|&nbsp; Gate Pass: {int(r.get("gate_pass_rate",0)*100)}%</div>'
                f'</td>'
                f'<td style="text-align:right;vertical-align:top;width:100px;">'
                f'<div style="font-size:11px;font-weight:700;color:#dc2626;">'
                f'{len(flags)} flag{"s" if len(flags)>1 else ""}</div>'
                f'</td></tr>'
                f'<tr><td colspan="2" style="padding-top:8px;">'
                f'<table style="width:100%;border-collapse:collapse;">{flag_rows}</table>'
                f'</td></tr>'
                f'</table></div>',
                unsafe_allow_html=True,
            )
    else:
        st.success("No anomaly flags detected across any registered recycler.")

    st.markdown("#### All Recycler Anomaly Status")
    hdr = st.columns([2.5, 1.2, 1.2, 1.5, 2])
    for col, h in zip(hdr, ["Recycler", "Trust", "Gate Pass", "Status", "Flags"]):
        with col:
            st.markdown(
                f'<div style="font-size:11px;font-weight:700;color:#374151;'
                f'padding:6px 0;border-bottom:2px solid #e5e7eb;">{h}</div>',
                unsafe_allow_html=True,
            )
    for r in sorted(recyclers, key=lambda x: len(x.get("anomaly_flags", [])), reverse=True):
        flags  = r.get("anomaly_flags", [])
        status = "REVIEW" if flags else "NORMAL"
        sc     = "#dc2626" if flags else "#16a34a"
        row    = st.columns([2.5, 1.2, 1.2, 1.5, 2])
        for col, val in zip(row, [
            r["company_name"],
            f"{int(r.get('trust_score',0)*100)}%",
            f"{int(r.get('gate_pass_rate',0)*100)}%",
            f'<span style="font-size:10px;font-weight:700;color:{sc};">{status}</span>',
            f"{len(flags)} flag{'s' if len(flags)!=1 else ''}" if flags else "—",
        ]):
            with col:
                st.markdown(
                    f'<div style="font-size:12px;padding:5px 0;">{val}</div>',
                    unsafe_allow_html=True,
                )


# ── Credit integrity ──────────────────────────────────────────────────────────

def _render_credit_integrity() -> None:
    credits = get_all_credits()
    chain   = get_chain_integrity_status(credits)

    if chain["intact"]:
        st.success(f"Hash chain intact — all {chain['total']} credit records verified.")
    else:
        st.error(
            f"Hash chain BROKEN — {chain['broken']} record(s) failed: "
            f"{', '.join(chain['broken_ids'])}"
        )

    st.markdown("#### Credit Records with Chain Status")
    hdr = st.columns([1.8, 1.4, 1.2, 1.0, 1.0, 1.5, 1.0])
    for col, h in zip(hdr, ["Credit ID", "Batch", "Recycler", "Type", "kg", "Status", "Chain"]):
        with col:
            st.markdown(
                f'<div style="font-size:11px;font-weight:700;color:#374151;'
                f'padding:6px 0;border-bottom:2px solid #e5e7eb;">{h}</div>',
                unsafe_allow_html=True,
            )
    for c in credits:
        ok    = c.get("chain_ok", True)
        color = "#16a34a" if ok else "#dc2626"
        row   = st.columns([1.8, 1.4, 1.2, 1.0, 1.0, 1.5, 1.0])
        sc    = STATUS_COLOURS.get(c["status"], STATUS_COLOURS["PENDING"])
        for col, val in zip(row, [
            c["credit_id"],
            c["batch_id"],
            c["recycler_name"].split()[0],
            c["item_type"],
            str(c["credit_kg"]),
            f'<span style="font-size:10px;font-weight:700;color:{sc["color"]};">{c["status"]}</span>',
            f'<span style="color:{color};font-weight:700;">{"OK" if ok else "FAIL"}</span>',
        ]):
            with col:
                st.markdown(
                    f'<div style="font-size:11px;padding:5px 0;">{val}</div>',
                    unsafe_allow_html=True,
                )


# ── Audit outcomes ────────────────────────────────────────────────────────────

def _render_audit_outcomes() -> None:
    outcomes = get_audit_outcomes()

    st.markdown(
        '<div style="background:#eff6ff;border:1px solid #bfdbfe;'
        'border-left:4px solid #2563eb;border-radius:8px;padding:10px 14px;'
        'margin-bottom:14px;font-size:12px;color:#374151;">'
        'Audit outcomes become labelled training data for model improvement. '
        'CONFIRMED_LEGITIMATE (label=1) and CONFIRMED_FRAUD (label=0) records feed '
        'back into the Trust Score and anomaly detection retraining pipeline. '
        'See the Feedback Loop page for the full retraining workflow.'
        '</div>',
        unsafe_allow_html=True,
    )

    total     = len(outcomes)
    legit     = sum(1 for o in outcomes if o["outcome"] == "CONFIRMED_LEGITIMATE")
    fraud     = sum(1 for o in outcomes if o["outcome"] == "CONFIRMED_FRAUD")

    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Total Audit Outcomes", total)
    with k2:
        st.metric("Confirmed Legitimate", legit)
    with k3:
        st.metric("Confirmed Fraud",      fraud,
                  delta="Feed into retraining" if fraud else None,
                  delta_color="off")

    st.markdown("#### Recorded Outcomes")
    for o in outcomes:
        colour = "#16a34a" if o["outcome"] == "CONFIRMED_LEGITIMATE" else "#dc2626"
        label  = o["outcome"].replace("_", " ")
        st.markdown(
            f'<div style="border:1px solid #e5e7eb;border-left:3px solid {colour};'
            f'border-radius:8px;padding:10px 14px;margin-bottom:8px;">'
            f'<table style="width:100%;border-collapse:collapse;"><tr>'
            f'<td style="vertical-align:top;">'
            f'<div style="font-size:12px;font-weight:700;color:#111827;">{o["credit_id"]}'
            f' &nbsp;&#8212;&nbsp; {o["batch_id"]}</div>'
            f'<div style="font-size:11px;color:#6b7280;margin-top:2px;">'
            f'Auditor: {o["auditor_id"]} &nbsp;|&nbsp; Date: {o["audit_date"]}'
            f'</div>'
            f'<div style="font-size:11px;color:#374151;margin-top:4px;">{o["notes"]}</div>'
            f'</td>'
            f'<td style="text-align:right;vertical-align:top;width:180px;">'
            f'<span style="font-size:11px;font-weight:700;color:{colour};">{label}</span>'
            f'<div style="font-size:10px;color:#6b7280;margin-top:4px;">'
            f'Training label: {o["label_for_training"]}</div>'
            f'</td></tr></table></div>',
            unsafe_allow_html=True,
        )

    # Add new outcome form
    st.markdown("#### Record New Audit Outcome")
    credits = get_all_credits()
    credit_ids = [c["credit_id"] for c in credits]

    with st.form("audit_outcome_form"):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            sel_credit = st.selectbox("Credit / Batch", credit_ids)
        with fc2:
            outcome_choice = st.selectbox("Outcome", ["CONFIRMED_LEGITIMATE", "CONFIRMED_FRAUD", "INCONCLUSIVE"])
        with fc3:
            auditor_id = st.text_input("Auditor ID", placeholder="AUD-CPCB-XXX")
        notes = st.text_area("Notes", placeholder="Describe findings from physical inspection...")
        sub   = st.form_submit_button("Record Outcome", type="primary", use_container_width=True)

    if sub:
        label = 1 if outcome_choice == "CONFIRMED_LEGITIMATE" else (0 if outcome_choice == "CONFIRMED_FRAUD" else -1)
        st.success(
            f"Outcome recorded: **{sel_credit}** → **{outcome_choice}** "
            f"(training label: {label}). "
            f"*Prototype — not persisted to disk.*"
        )


# ── Export report ─────────────────────────────────────────────────────────────

def _render_export() -> None:
    st.markdown("#### Export Audit Report")
    st.markdown(
        '<div style="background:#f8fafc;border:1px solid #e5e7eb;'
        'border-radius:8px;padding:12px 16px;margin-bottom:16px;'
        'font-size:12px;color:#374151;">'
        'In production, this exports a signed PDF report for CPCB submission. '
        'The prototype generates a JSON summary that can be reviewed or submitted manually.'
        '</div>',
        unsafe_allow_html=True,
    )

    report_type = st.selectbox(
        "Report Type",
        [
            "Full System Summary",
            "Anomaly Flags Only",
            "Credit Lifecycle Summary",
            "Audit Outcomes (Training Labels)",
        ],
        key="export_type",
    )

    if st.button("Generate Report", type="primary", use_container_width=False):
        credits  = get_all_credits()
        recyclers = get_all_recyclers()
        outcomes = get_audit_outcomes()
        chain    = get_chain_integrity_status(credits)

        if report_type == "Full System Summary":
            report = {
                "report_type":     "Full System Summary",
                "generated_at":    "2026-09-25T12:00:00Z",
                "total_credits":   len(credits),
                "chain_intact":    chain["intact"],
                "flagged_recyclers": sum(1 for r in recyclers if r.get("anomaly_flags")),
                "audit_outcomes":  len(outcomes),
                "credits_by_status": {
                    s: sum(1 for c in credits if c["status"] == s)
                    for s in ["PENDING", "ISSUED", "LISTED", "SOLD", "RETIRED"]
                },
            }
        elif report_type == "Anomaly Flags Only":
            report = {
                "report_type": "Anomaly Flags",
                "flagged": [
                    {
                        "company": r["company_name"],
                        "trust_score": r["trust_score"],
                        "flags": r["anomaly_flags"],
                    }
                    for r in recyclers if r.get("anomaly_flags")
                ],
            }
        elif report_type == "Credit Lifecycle Summary":
            report = {
                "report_type": "Credit Lifecycle",
                "credits": [
                    {
                        "credit_id":   c["credit_id"],
                        "status":      c["status"],
                        "credit_kg":   c["credit_kg"],
                        "recycler":    c["recycler_name"],
                        "chain_ok":    c.get("chain_ok", True),
                    }
                    for c in credits
                ],
            }
        else:
            report = {
                "report_type":   "Audit Outcomes (Training Labels)",
                "outcomes":      outcomes,
                "label_summary": {
                    "legitimate": sum(1 for o in outcomes if o["label_for_training"] == 1),
                    "fraud":      sum(1 for o in outcomes if o["label_for_training"] == 0),
                },
            }

        st.download_button(
            label="Download JSON Report",
            data=json.dumps(report, indent=2),
            file_name=f"ecotrace_report_{report_type.lower().replace(' ','_')}.json",
            mime="application/json",
            use_container_width=True,
        )

        with st.expander("Preview Report"):
            st.json(report)
