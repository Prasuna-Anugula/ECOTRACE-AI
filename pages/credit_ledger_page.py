"""
EcoTrace AI — Credit Ledger Page
──────────────────────────────────
Shows the full lifecycle of all Evidence Attestation (EA) credits:
  PENDING → ISSUED → LISTED → SOLD → RETIRED

Hash chain integrity panel shows whether any record has been tampered with.
NO display:flex/grid. All layout via st.columns() and <table>.
"""

from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
from services.credit_ledger import (
    get_all_credits,
    get_lifecycle_summary,
    get_chain_integrity_status,
    STATUS_COLOURS,
    LIFECYCLE_ORDER,
)


def _status_badge(status: str) -> str:
    sc = STATUS_COLOURS.get(status, STATUS_COLOURS["PENDING"])
    label = status if status != "BLOCKED" else "BLOCKED (Gate Failed)"
    return (
        f'<span style="background:{sc["bg"]};border:1px solid {sc["border"]};'
        f'border-radius:4px;padding:2px 8px;font-size:10px;'
        f'font-weight:700;color:{sc["color"]};">{label}</span>'
    )


def _lifecycle_funnel(summary: dict) -> go.Figure:
    labels = LIFECYCLE_ORDER + ["BLOCKED"]
    values = [summary.get(s, {}).get("credit_kg", 0.0) for s in labels]
    colors = [STATUS_COLOURS[s]["color"] for s in labels]

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        text=[f"{v:,.1f} kg" for v in values],
        textposition="outside",
        textfont=dict(size=11),
    ))
    fig.update_layout(
        height=260,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="Credit kg", showgrid=True, gridcolor="#f0f0f0"),
        xaxis=dict(showgrid=False),
        showlegend=False,
    )
    return fig


def render_credit_ledger() -> None:
    st.markdown("## Evidence Attestation Credit Ledger")
    st.caption(
        "Full lifecycle view of every EA credit. "
        "Hash chain integrity ensures no record has been tampered with."
    )

    credits  = get_all_credits()
    summary  = get_lifecycle_summary()
    chain    = get_chain_integrity_status(credits)

    # ── Hash chain integrity banner ────────────────────────────────────────
    if chain["intact"]:
        st.markdown(
            f'<div style="background:#f0fdf4;border:1px solid #bbf7d0;'
            f'border-left:4px solid #16a34a;border-radius:8px;'
            f'padding:10px 16px;margin-bottom:16px;">'
            f'<table style="width:100%;border-collapse:collapse;"><tr>'
            f'<td><div style="font-size:13px;font-weight:700;color:#166534;">'
            f'&#10003; Hash Chain Intact — All {chain["total"]} records verified</div>'
            f'<div style="font-size:11px;color:#6b7280;margin-top:2px;">'
            f'No tampering detected. Every record\'s hash matches its computed value.</div>'
            f'</td>'
            f'<td style="text-align:right;width:120px;">'
            f'<div style="font-size:28px;font-weight:900;color:#16a34a;">'
            f'{chain["ok"]}/{chain["total"]}</div>'
            f'<div style="font-size:10px;color:#6b7280;">records verified</div>'
            f'</td></tr></table></div>',
            unsafe_allow_html=True,
        )
    else:
        broken_list = ", ".join(chain["broken_ids"])
        st.markdown(
            f'<div style="background:#fef2f2;border:1px solid #fca5a5;'
            f'border-left:4px solid #dc2626;border-radius:8px;'
            f'padding:10px 16px;margin-bottom:16px;">'
            f'<div style="font-size:13px;font-weight:700;color:#991b1b;">'
            f'&#9888; Hash Chain Broken — {chain["broken"]} record(s) failed integrity check</div>'
            f'<div style="font-size:11px;color:#6b7280;margin-top:2px;">'
            f'Affected credits: {broken_list}. These records may have been tampered with.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Lifecycle summary KPIs ─────────────────────────────────────────────
    st.markdown("#### Lifecycle Summary")
    cols = st.columns(len(LIFECYCLE_ORDER) + 1)
    for col, status in zip(cols, LIFECYCLE_ORDER + ["BLOCKED"]):
        sc   = STATUS_COLOURS[status]
        data = summary.get(status, {"count": 0, "credit_kg": 0.0})
        with col:
            st.markdown(
                f'<div style="background:{sc["bg"]};border:1px solid {sc["border"]};'
                f'border-radius:10px;padding:10px 12px;text-align:center;">'
                f'<div style="font-size:10px;font-weight:700;color:{sc["color"]};'
                f'text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">'
                f'{status}</div>'
                f'<div style="font-size:22px;font-weight:900;color:{sc["color"]};">'
                f'{data["count"]}</div>'
                f'<div style="font-size:11px;color:#6b7280;">'
                f'{data["credit_kg"]:,.1f} kg</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Lifecycle funnel chart ─────────────────────────────────────────────
    st.plotly_chart(
        _lifecycle_funnel(summary),
        use_container_width=True,
        config={"displayModeBar": False},
    )

    # ── Filter controls ────────────────────────────────────────────────────
    st.markdown("#### All Credits")
    fc1, fc2 = st.columns([1, 3])
    with fc1:
        status_filter = st.selectbox(
            "Filter by status",
            ["All"] + LIFECYCLE_ORDER + ["BLOCKED"],
            key="ledger_status_filter",
        )

    filtered = get_all_credits(
        status_filter=None if status_filter == "All" else status_filter
    )
    if status_filter == "BLOCKED":
        filtered = [c for c in get_all_credits() if not c["gate_passed"]]

    st.markdown(
        f'<div style="font-size:12px;color:#6b7280;margin-bottom:8px;">'
        f'Showing {len(filtered)} credit{"s" if len(filtered) != 1 else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Column headers ─────────────────────────────────────────────────────
    hdr = st.columns([1.8, 1.5, 1.2, 1.0, 1.0, 1.5, 1.0])
    for col, h in zip(hdr, ["Credit ID", "Batch", "Recycler", "Item Type", "Credit kg", "Status", "Hash OK"]):
        with col:
            st.markdown(
                f'<div style="font-size:11px;font-weight:700;color:#374151;'
                f'padding:6px 0;border-bottom:2px solid #e5e7eb;">{h}</div>',
                unsafe_allow_html=True,
            )

    # ── Credit rows ────────────────────────────────────────────────────────
    for c in filtered:
        sc       = STATUS_COLOURS.get(c["status"], STATUS_COLOURS["PENDING"])
        chain_ok = c.get("chain_ok", True)
        row      = st.columns([1.8, 1.5, 1.2, 1.0, 1.0, 1.5, 1.0])

        with row[0]:
            st.markdown(
                f'<div style="font-size:11px;font-weight:700;color:#111827;'
                f'padding:6px 0;font-family:monospace;">{c["credit_id"]}</div>',
                unsafe_allow_html=True,
            )
        with row[1]:
            st.markdown(
                f'<div style="font-size:11px;color:#6b7280;padding:6px 0;">{c["batch_id"]}</div>',
                unsafe_allow_html=True,
            )
        with row[2]:
            st.markdown(
                f'<div style="font-size:11px;color:#374151;padding:6px 0;">'
                f'{c["recycler_name"].split()[0]}</div>',
                unsafe_allow_html=True,
            )
        with row[3]:
            st.markdown(
                f'<div style="font-size:11px;color:#374151;padding:6px 0;">{c["item_type"]}</div>',
                unsafe_allow_html=True,
            )
        with row[4]:
            st.markdown(
                f'<div style="font-size:11px;font-weight:700;color:#111827;padding:6px 0;">'
                f'{c["credit_kg"]:.2f}</div>',
                unsafe_allow_html=True,
            )
        with row[5]:
            st.markdown(
                f'<div style="padding:4px 0;">{_status_badge(c["status"])}</div>',
                unsafe_allow_html=True,
            )
        with row[6]:
            icon  = "&#10003;" if chain_ok else "&#9888;"
            color = "#16a34a" if chain_ok else "#dc2626"
            st.markdown(
                f'<div style="font-size:13px;font-weight:700;color:{color};padding:5px 0;">'
                f'{icon}</div>',
                unsafe_allow_html=True,
            )

    # ── Credit detail expander ─────────────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("#### Credit Detail — Hash Chain Audit Trail")
    selected_id = st.selectbox(
        "Select a credit to inspect",
        [c["credit_id"] for c in filtered],
        key="ledger_detail_select",
    )

    selected = next((c for c in filtered if c["credit_id"] == selected_id), None)
    if selected:
        sc       = STATUS_COLOURS.get(selected["status"], STATUS_COLOURS["PENDING"])
        chain_ok = selected.get("chain_ok", True)
        chain_color = "#16a34a" if chain_ok else "#dc2626"

        st.markdown(
            f'<div style="border:1.5px solid {sc["border"]};border-radius:12px;'
            f'padding:16px 20px;">'
            f'<table style="width:100%;border-collapse:collapse;font-size:12px;">'
            + _detail_row("Credit ID",        selected["credit_id"])
            + _detail_row("Batch ID",         selected["batch_id"])
            + _detail_row("Recycler",         selected["recycler_name"])
            + _detail_row("Facility",         selected["facility_id"])
            + _detail_row("Item Type",        selected["item_type"])
            + _detail_row("Item State",       selected["item_state"].title())
            + _detail_row("Input Weight",     f"{selected['weight_kg']} kg")
            + _detail_row("Credit Value",     f"{selected['credit_kg']} kg EA")
            + _detail_row("Trust Score",      str(selected["trust_score"]))
            + _detail_row("Gate Passed",      "Yes" if selected["gate_passed"] else "No")
            + _detail_row("Status",           selected["status"])
            + _detail_row("Created",          selected.get("created_at", "—"))
            + _detail_row("Issued",           selected.get("issued_at") or "—")
            + _detail_row("Listed",           selected.get("listed_at") or "—")
            + _detail_row("Sold",             selected.get("sold_at") or "—")
            + _detail_row("Retired",          selected.get("retired_at") or "—")
            + _detail_row("Buyer",            selected.get("buyer_producer_id") or "—")
            + _detail_row("Sale Price",       f"₹{selected['sale_price_inr']}" if selected.get("sale_price_inr") else "—")
            + _detail_row("Hash",             f'<span style="font-family:monospace;font-size:10px;">{selected.get("hash","—")}</span>')
            + _detail_row("Prev Hash",        f'<span style="font-family:monospace;font-size:10px;">{selected.get("prev_hash","—")}</span>')
            + _detail_row("Chain Integrity",  f'<span style="font-weight:700;color:{chain_color};">{"INTACT" if chain_ok else "BROKEN"}</span>')
            + f'</table></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:8px;'
        'padding:10px 16px;margin-top:16px;font-size:11px;color:#9ca3af;">'
        '<strong>Prototype Notice:</strong> Hash chain uses SHA-256 on key fields. '
        'In production: cryptographic signatures + IPFS storage for full tamper-evidence. '
        'All credit data is synthetic.</div>',
        unsafe_allow_html=True,
    )


def _detail_row(label: str, value: str) -> str:
    return (
        f'<tr style="border-bottom:1px solid #f3f4f6;">'
        f'<td style="color:#6b7280;padding:4px 12px 4px 0;width:40%;'
        f'vertical-align:top;">{label}</td>'
        f'<td style="font-weight:600;color:#111827;padding:4px 0;">{value}</td>'
        f'</tr>'
    )
