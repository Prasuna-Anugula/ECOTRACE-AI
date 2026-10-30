"""
EcoTrace AI — Producer Compliance Dashboard (upgraded)
────────────────────────────────────────────────────────
Shows full EPR compliance status:
  - Obligation vs fulfilled with deadline countdown
  - Shortfall alert with urgency colour coding
  - Purchase history (credits bought)
  - Recommended basket from marketplace
  - Partner recycler summary

NO display:flex/grid. All layout via st.columns() and <table>.
"""

from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
from services.credit_ledger import (
    get_all_producers,
    get_producer_obligation,
    recommend_basket,
    get_credits_for_producer,
)
from services.recycler_trust import get_all_recyclers


# ── helpers ───────────────────────────────────────────────────────────────────

def _gauge(pct: float, label: str, colour: str) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(pct, 1),
        number={"suffix": "%", "font": {"size": 30, "color": colour}},
        title={"text": label, "font": {"size": 11, "color": "#6b7280"}},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%"},
            "bar":  {"color": colour, "thickness": 0.28},
            "bgcolor": "#f8fafc",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  30], "color": "#fef2f2"},
                {"range": [30, 60], "color": "#fffbeb"},
                {"range": [60, 80], "color": "#eff6ff"},
                {"range": [80, 100],"color": "#f0fdf4"},
            ],
            "threshold": {
                "line": {"color": "#374151", "width": 2},
                "thickness": 0.75, "value": 80,
            },
        },
    ))
    fig.update_layout(
        height=230, margin=dict(t=20, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


STATUS_META = {
    "COMPLIANT": {"color": "#166534", "bg": "#f0fdf4", "border": "#bbf7d0", "icon": "✓"},
    "ON_TRACK":  {"color": "#1d4ed8", "bg": "#eff6ff", "border": "#93c5fd", "icon": "→"},
    "AT_RISK":   {"color": "#d97706", "bg": "#fffbeb", "border": "#fcd34d", "icon": "⚠"},
    "CRITICAL":  {"color": "#dc2626", "bg": "#fef2f2", "border": "#fca5a5", "icon": "!"},
}


# ── main ──────────────────────────────────────────────────────────────────────

def render_producer_dashboard() -> None:
    st.markdown("## Producer Compliance Dashboard")
    st.caption("Track your EPR obligation, purchased credits, shortfall, and deadline risk.")

    producers = get_all_producers()
    if not producers:
        st.info("No producer data available.")
        return

    names      = [p["company_name"] for p in producers]
    sel_name   = st.selectbox("Select Producer Account", names, key="prod_sel")
    prod_rec   = next(p for p in producers if p["company_name"] == sel_name)
    prod_id    = prod_rec["producer_id"]
    obl        = get_producer_obligation(prod_id)

    if not obl:
        st.warning("No obligation data found.")
        return

    status     = obl["status"]
    sm         = STATUS_META.get(status, STATUS_META["AT_RISK"])
    pct        = obl["pct_done"]
    days_left  = obl["days_left"]
    shortfall  = obl["shortfall_kg"]

    # ── Status banner ──────────────────────────────────────────────────────
    days_color = "#dc2626" if days_left < 30 else "#d97706" if days_left < 90 else "#166534"
    st.markdown(
        f'<div style="background:{sm["bg"]};border:1.5px solid {sm["border"]};'
        f'border-radius:12px;padding:14px 20px;margin-bottom:16px;">'
        f'<table style="width:100%;border-collapse:collapse;"><tr>'
        f'<td style="vertical-align:top;">'
        f'<div style="font-size:18px;font-weight:900;color:#111827;">{sel_name}</div>'
        f'<div style="font-size:12px;color:#6b7280;margin-top:2px;">'
        f'Reg: {prod_rec["registration_number"]} &nbsp;|&nbsp; '
        f'Deadline: {prod_rec["deadline"]} &nbsp;|&nbsp; '
        f'Year: {prod_rec["compliance_year"]}'
        f'</div></td>'
        f'<td style="text-align:right;vertical-align:top;width:220px;">'
        f'<div style="font-size:13px;font-weight:800;color:{sm["color"]};">'
        f'{sm["icon"]} {status.replace("_"," ")}</div>'
        f'<div style="font-size:26px;font-weight:900;color:{days_color};">'
        f'{days_left} days left</div>'
        f'<div style="font-size:10px;color:#6b7280;">until compliance deadline</div>'
        f'</td></tr></table>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── KPIs ───────────────────────────────────────────────────────────────
    g_col, k_col = st.columns([1, 2])
    with g_col:
        st.plotly_chart(
            _gauge(pct, "Obligation Fulfilled", sm["color"]),
            use_container_width=True, config={"displayModeBar": False},
        )
    with k_col:
        r1c1, r1c2 = st.columns(2)
        r2c1, r2c2 = st.columns(2)
        with r1c1:
            st.metric("Annual Obligation",  f"{obl['obligation_kg']/1000:,.1f} t  ({obl['obligation_kg']:,.0f} kg)")
        with r1c2:
            st.metric("Fulfilled",          f"{obl['fulfilled_kg']/1000:,.1f} t", delta=f"{pct:.1f}% of target")
        with r2c1:
            st.metric("Shortfall",          f"{shortfall/1000:,.1f} t  ({shortfall:,.0f} kg)",
                      delta="Action required" if shortfall > 0 else "Fully covered",
                      delta_color="inverse" if shortfall > 0 else "normal")
        with r2c2:
            st.metric("Days to Deadline",   str(days_left),
                      delta="Critical" if days_left < 30 else "At risk" if days_left < 90 else "OK",
                      delta_color="inverse" if days_left < 90 else "normal")

    # Progress bar
    bar_color = sm["color"]
    st.markdown(
        f'<div style="margin:8px 0 16px 0;">'
        f'<table style="width:100%;border-collapse:collapse;"><tr>'
        f'<td style="font-size:12px;font-weight:600;color:#374151;">Obligation Progress</td>'
        f'<td style="text-align:right;font-size:12px;font-weight:800;color:{bar_color};">'
        f'{obl["fulfilled_kg"]:,.0f} / {obl["obligation_kg"]:,.0f} kg ({pct:.1f}%)</td>'
        f'</tr></table>'
        f'<div style="background:#e5e7eb;border-radius:6px;height:10px;margin-top:4px;">'
        f'<div style="background:{bar_color};width:{min(pct,100):.1f}%;height:10px;border-radius:6px;"></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # ── Shortfall alert + basket recommendation ────────────────────────────
    if shortfall > 0:
        basket = recommend_basket(remaining_kg=shortfall, min_trust=0.85, producer_id=prod_id)
        f_color  = "#166534" if basket["can_fulfil"] else "#dc2626"
        f_bg     = "#f0fdf4" if basket["can_fulfil"] else "#fef2f2"
        f_border = "#bbf7d0" if basket["can_fulfil"] else "#fca5a5"
        f_label  = "RECOMMENDED BASKET — OBLIGATION CAN BE FULFILLED" if basket["can_fulfil"] \
                   else "INSUFFICIENT SUPPLY — CREDITS BELOW REQUIRED"

        st.markdown("#### Recommended Purchase Basket")
        st.markdown(
            f'<div style="background:{f_bg};border:1.5px solid {f_border};'
            f'border-radius:10px;padding:14px 18px;margin-bottom:12px;">'
            f'<div style="font-size:13px;font-weight:800;color:{f_color};">{f_label}</div>'
            f'<div style="font-size:11px;color:#6b7280;margin-top:4px;">'
            f'Shortfall: <strong>{shortfall/1000:,.2f} t ({shortfall:,.0f} kg)</strong> &nbsp;&bull;&nbsp; '
            f'Covered by basket: <strong>{basket["total_covered"]/1000:,.2f} t</strong> &nbsp;&bull;&nbsp; '
            f'Est. total cost: <strong>&#8377;{basket["total_cost"]:,.0f}</strong>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        if basket["basket"]:
            hdr = st.columns([2.5, 1.2, 1.2, 1.2, 1.5, 1.5])
            for col, h in zip(hdr, ["Recycler", "Trust", "Gate Pass", "Buy (kg)", "Price/kg", "Cost (₹)"]):
                with col:
                    st.markdown(
                        f'<div style="font-size:11px;font-weight:700;color:#374151;'
                        f'padding:6px 0;border-bottom:2px solid #e5e7eb;">{h}</div>',
                        unsafe_allow_html=True,
                    )
            for item in basket["basket"]:
                ts_c = "#16a34a" if item["trust_score"] >= 0.85 else "#2563eb"
                bc   = st.columns([2.5, 1.2, 1.2, 1.2, 1.5, 1.5])
                vals = [
                    item["company_name"],
                    f"{int(item['trust_score']*100)}%",
                    f"{int(item['gate_pass_rate']*100)}%",
                    f"{item['to_buy_kg']:,.1f}",
                    f"₹{item['price_per_kg']}",
                    f"₹{item['cost_inr']:,.0f}",
                ]
                colors = ["#111827", ts_c, "#374151", "#111827", "#374151", "#111827"]
                for col, v, c in zip(bc, vals, colors):
                    with col:
                        st.markdown(
                            f'<div style="font-size:12px;font-weight:600;color:{c};padding:5px 0;">{v}</div>',
                            unsafe_allow_html=True,
                        )

        act1, act2 = st.columns(2)
        with act1:
            if st.button("Go to Marketplace →", type="primary", use_container_width=True):
                st.session_state["current_page"] = "EPR Marketplace"
                st.rerun()
        with act2:
            st.button("Download Compliance Report", use_container_width=True,
                      disabled=True, help="Available in production version")

    # ── Purchase history ───────────────────────────────────────────────────
    st.markdown("#### Purchase History")
    credits = get_credits_for_producer(prod_id)
    if credits:
        h = st.columns([1.8, 1.4, 1.0, 1.0, 1.0, 1.4])
        for col, label in zip(h, ["Credit ID", "Recycler", "Item", "kg", "Paid ₹", "Status"]):
            with col:
                st.markdown(
                    f'<div style="font-size:11px;font-weight:700;color:#374151;'
                    f'padding:6px 0;border-bottom:2px solid #e5e7eb;">{label}</div>',
                    unsafe_allow_html=True,
                )
        for c in credits:
            row = st.columns([1.8, 1.4, 1.0, 1.0, 1.0, 1.4])
            vals = [
                c["credit_id"],
                c["recycler_name"].split()[0],
                c["item_type"],
                str(c["credit_kg"]),
                f"₹{c['sale_price_inr']:,.0f}" if c.get("sale_price_inr") else "—",
                c["status"],
            ]
            for col, v in zip(row, vals):
                with col:
                    st.markdown(
                        f'<div style="font-size:11px;padding:5px 0;'
                        f'border-bottom:1px solid #f3f4f6;">{v}</div>',
                        unsafe_allow_html=True,
                    )
    else:
        st.info("No purchased credits on record for this producer.")

    st.markdown(
        '<div style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:8px;'
        'padding:10px 16px;margin-top:16px;font-size:11px;color:#9ca3af;">'
        '<strong>Prototype Notice:</strong> All obligation figures, credit data, and '
        'purchase history are synthetic examples only.</div>',
        unsafe_allow_html=True,
    )
