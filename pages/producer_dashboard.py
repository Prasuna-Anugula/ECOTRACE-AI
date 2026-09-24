"""
EcoTrace AI — Producer Compliance Dashboard
─────────────────────────────────────────────
Shows a producer's EPR obligation progress, purchased credits,
and recycler partner summary.
"""

from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
from services.recycler_trust import get_producers, get_all_recyclers


def _obligation_gauge(purchased: float, target: float) -> go.Figure:
    pct = min((purchased / target) * 100, 100) if target else 0
    color = "#16a34a" if pct >= 80 else "#d97706" if pct >= 50 else "#dc2626"
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(pct, 1),
        number={"suffix": "%", "font": {"size": 32, "color": color}},
        delta={"reference": 80, "valueformat": ".1f", "suffix": "%"},
        title={"text": "EPR Obligation Progress", "font": {"size": 12}},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%"},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "#f8fafc",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 50],   "color": "#fef2f2"},
                {"range": [50, 80],  "color": "#fffbeb"},
                {"range": [80, 100], "color": "#f0fdf4"},
            ],
            "threshold": {
                "line": {"color": "#374151", "width": 3},
                "thickness": 0.75,
                "value": 80,
            },
        },
    ))
    fig.update_layout(
        height=250,
        margin=dict(t=20, b=10, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_producer_dashboard() -> None:
    st.markdown(
        """
        <div style="margin-bottom:20px;">
            <div style="font-size:22px;font-weight:900;color:#111827;">
                Producer Compliance Dashboard
            </div>
            <div style="font-size:13px;color:#6b7280;margin-top:3px;">
                Track your EPR obligation progress and purchased certificate status.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    producers = get_producers()
    if not producers:
        st.info("No producer data available.")
        return

    # Producer selector
    producer_names = [p["company_name"] for p in producers]
    selected_name  = st.selectbox("Select Producer Account", producer_names, key="prod_selector")
    prod = next(p for p in producers if p["company_name"] == selected_name)

    target    = prod.get("annual_target_kg", 0)
    purchased = prod.get("purchased_credits_kg", 0)
    verified  = prod.get("verified_credits_kg", 0)
    remaining = max(target - purchased, 0)
    pct_done  = (purchased / target * 100) if target else 0
    status    = prod.get("compliance_status", "UNKNOWN")
    deadline  = prod.get("deadline", "2026-12-31")

    status_color = "#166534" if status == "ON_TRACK" else "#dc2626" if status == "AT_RISK" else "#d97706"
    status_bg    = "#f0fdf4" if status == "ON_TRACK" else "#fef2f2" if status == "AT_RISK" else "#fffbeb"

    # Status banner
    st.markdown(
        f'<div style="background:{status_bg};border:1.5px solid {status_color}33;'
        f'border-radius:10px;padding:12px 18px;margin-bottom:16px;">'
        f'<table style="width:100%;border-collapse:collapse;">'
        f'<tr>'
        f'<td style="vertical-align:top;">'
        f'<div style="font-size:16px;font-weight:800;color:#111827;">'
        f'{prod.get("company_name","")}</div>'
        f'<div style="font-size:11px;color:#6b7280;margin-top:2px;">'
        f'Reg: {prod.get("registration_number","")} &nbsp;|&nbsp; '
        f'Deadline: {deadline} &nbsp;|&nbsp; '
        f'Categories: {", ".join(prod.get("product_categories",[]))}'
        f'</div></td>'
        f'<td style="text-align:right;vertical-align:top;width:160px;">'
        f'<div style="background:{status_bg};border:2px solid {status_color};'
        f'border-radius:8px;padding:6px 16px;display:inline-block;">'
        f'<div style="font-size:13px;font-weight:800;color:{status_color};">'
        f'{"OK" if status=="ON_TRACK" else "RISK"} {status.replace("_"," ")}'
        f'</div></div></td>'
        f'</tr></table>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Gauge + KPIs
    g_col, k_col = st.columns([1, 2])

    with g_col:
        st.plotly_chart(
            _obligation_gauge(purchased, target),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with k_col:
        k1, k2 = st.columns(2)
        k3, k4 = st.columns(2)
        with k1:
            st.metric("Annual Target", f"{target:,} kg")
        with k2:
            st.metric("Purchased Credits", f"{purchased:,} kg", delta=f"{pct_done:.1f}% of target")
        with k3:
            st.metric("Verified Credits", f"{verified:,} kg",
                      delta=f"{((verified/purchased)*100 if purchased else 0):.1f}% verified")
        with k4:
            st.metric(
                "Still Needed",
                f"{remaining:,} kg",
                delta=f"{'At risk' if remaining > 10000 else 'Manageable'}",
                delta_color="inverse",
            )

    # Progress bar
    bar_color = "#16a34a" if pct_done >= 80 else "#d97706" if pct_done >= 50 else "#dc2626"
    st.markdown(
        f"""
        <div style="margin:8px 0 16px 0;">
            <div style="display:flex;justify-content:space-between;
                        font-size:12px;color:#374151;margin-bottom:4px;">
                <span style="font-weight:600;">Overall EPR Progress</span>
                <span style="font-weight:800;color:{bar_color};">
                    {purchased:,} / {target:,} kg ({pct_done:.1f}%)
                </span>
            </div>
            <div style="background:#e5e7eb;border-radius:6px;height:10px;">
                <div style="background:{bar_color};width:{min(pct_done,100):.1f}%;
                            height:10px;border-radius:6px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Verified recycler partners
    st.markdown("#### Verified Recycler Partners")
    st.markdown(
        """
        <div style="font-size:11px;color:#6b7280;margin-bottom:10px;">
            Recyclers from whom this producer has purchased EPR certificates.
            Trust scores reflect EcoTrace verification data at time of purchase.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Show top recyclers from marketplace (first 3 recommended ones as mock partners)
    partners = get_all_recyclers(min_trust=0.85, sort_by="trust_score")[:3]

    hdr = st.columns([2.5, 1.2, 1.2, 1.2, 1.2, 1.5])
    for col, h in zip(hdr, ["Recycler", "Trust Score", "Gate Pass", "Credits Purchased", "Verified", "Status"]):
        with col:
            st.markdown(
                f'<div style="font-size:11px;font-weight:700;color:#374151;'
                f'padding:6px 0;border-bottom:2px solid #e5e7eb;">{h}</div>',
                unsafe_allow_html=True,
            )

    for p in partners:
        ts  = p.get("trust_score", 0)
        gpr = p.get("gate_pass_rate", 0)
        ts_c = "#16a34a" if ts >= 0.85 else "#2563eb" if ts >= 0.70 else "#dc2626"
        mock_purchased = round(purchased * 0.35, 0) if partners.index(p) == 0 else \
                         round(purchased * 0.25, 0) if partners.index(p) == 1 else \
                         round(purchased * 0.15, 0)
        mock_verified  = round(mock_purchased * 0.985, 0)

        pc1, pc2, pc3, pc4, pc5, pc6 = st.columns([2.5, 1.2, 1.2, 1.2, 1.2, 1.5])
        with pc1:
            st.markdown(f"<div style='font-size:12px;font-weight:600;padding:5px 0;'>{p.get('company_name','')}</div>", unsafe_allow_html=True)
        with pc2:
            st.markdown(f"<div style='font-size:12px;color:{ts_c};font-weight:700;padding:5px 0;'>{int(ts*100)}%</div>", unsafe_allow_html=True)
        with pc3:
            st.markdown(f"<div style='font-size:12px;font-weight:700;padding:5px 0;'>{int(gpr*100)}%</div>", unsafe_allow_html=True)
        with pc4:
            st.markdown(f"<div style='font-size:12px;padding:5px 0;'>{mock_purchased:,.0f} kg</div>", unsafe_allow_html=True)
        with pc5:
            st.markdown(f"<div style='font-size:12px;padding:5px 0;'>{mock_verified:,.0f} kg</div>", unsafe_allow_html=True)
        with pc6:
            st.markdown(f"<div style='font-size:12px;color:#16a34a;font-weight:700;padding:5px 0;'>✅ Verified</div>", unsafe_allow_html=True)

    # Action buttons
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🔍 Search Marketplace for More Credits", use_container_width=True, type="primary"):
            st.session_state["current_page"] = "EPR Marketplace"
            st.rerun()
    with b2:
        st.button("📥 Download Compliance Report (PDF)", use_container_width=True, disabled=True,
                  help="Available in production version")

    st.markdown(
        """
        <div style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:8px;
                    padding:10px 16px;margin-top:16px;">
            <div style="font-size:11px;color:#9ca3af;">
                <strong>Prototype Notice:</strong> Producer data, purchased credit figures,
                and partner lists are synthetic examples for demonstration only.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
