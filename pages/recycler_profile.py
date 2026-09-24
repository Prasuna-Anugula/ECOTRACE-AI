"""
EcoTrace AI — Recycler Profile Page
─────────────────────────────────────
Full detail view for a single recycler company.
NO display:flex / display:grid — Streamlit sanitizer strips them.
All side-by-side layouts use <table>.
"""

from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
from services.recycler_trust import get_recycler_by_id, get_credit_listings


def _trust_gauge(score: float, title: str) -> go.Figure:
    color = (
        "#16a34a" if score >= 0.85 else
        "#2563eb" if score >= 0.70 else
        "#d97706" if score >= 0.60 else
        "#dc2626"
    )
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(score * 100, 1),
        number={"suffix": "%", "font": {"size": 28, "color": color}},
        title={"text": title, "font": {"size": 11, "color": "#6b7280"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#d1d5db"},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "#f8fafc",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  60],  "color": "#fef2f2"},
                {"range": [60, 70],  "color": "#fffbeb"},
                {"range": [70, 85],  "color": "#eff6ff"},
                {"range": [85, 100], "color": "#f0fdf4"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.75,
                "value": round(score * 100, 1),
            },
        },
    ))
    fig.update_layout(
        height=200,
        margin=dict(t=20, b=10, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _monthly_bar(fac: dict) -> go.Figure:
    stats  = fac.get("monthly_stats", {})
    labels = ["Received", "Processed", "Dismantled", "Intact/Packaged"]
    values = [
        stats.get("items_received", 0),
        stats.get("items_processed", 0),
        stats.get("items_dismantled", 0),
        stats.get("items_intact_packaged", 0),
    ]
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=["#6b7280", "#16a34a", "#2563eb", "#d97706"],
        text=values, textposition="outside",
        textfont=dict(size=11),
    ))
    fig.update_layout(
        height=220,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0", title="Items"),
        xaxis=dict(showgrid=False),
        showlegend=False,
    )
    return fig


def _row(label: str, value: str) -> str:
    """Single key-value row for detail tables."""
    return (
        f'<tr style="border-bottom:1px solid #f0f0f0;">'
        f'<td style="font-size:11px;color:#6b7280;padding:4px 12px 4px 0;'
        f'width:50%;vertical-align:top;">{label}</td>'
        f'<td style="font-size:11px;font-weight:700;color:#111827;'
        f'padding:4px 0;vertical-align:top;">{value}</td>'
        f'</tr>'
    )


def render_recycler_profile() -> None:
    recycler_id = st.session_state.get("selected_recycler_id")

    if not recycler_id:
        st.warning("No recycler selected. Go back to the Marketplace.")
        if st.button("Back to Marketplace"):
            st.session_state["current_page"] = "EPR Marketplace"
            st.rerun()
        return

    r = get_recycler_by_id(recycler_id)
    if not r:
        st.error("Recycler not found.")
        return

    tier   = r.get("tier", {})
    flags  = r.get("anomaly_flags", [])
    facs   = r.get("facilities", [])

    tier_color  = tier.get("color",  "#374151")
    tier_bg     = tier.get("bg",     "#f9fafb")
    tier_border = tier.get("border", "#e5e7eb")
    tier_icon   = tier.get("icon",   "")
    tier_label  = tier.get("tier",   "")

    # Back button
    if st.button("← Back to Marketplace", key="back_mkt"):
        st.session_state["current_page"] = "EPR Marketplace"
        st.rerun()

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── Header card ───────────────────────────────────────────────────────────
    cert_html = "".join(
        f'<span style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:4px;'
        f'padding:2px 7px;font-size:10px;color:#166534;font-weight:600;">{c}</span>&nbsp;'
        for c in r.get("certifications", [])
    )
    expiry_html = ""
    if r.get("expiry_warning"):
        expiry_html = (
            f'<div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:6px;'
            f'padding:5px 10px;margin-top:6px;font-size:11px;color:#9a3412;">'
            f'&#9200; Registration expires in {r.get("expiry_days", 0)} days</div>'
        )

    st.markdown(
        f'<div style="background:#ffffff;border:2px solid {tier_border};'
        f'border-radius:14px;padding:20px 24px;margin-bottom:18px;">'
        f'<table style="width:100%;border-collapse:collapse;">'
        f'<tr>'
        f'<td style="vertical-align:top;">'
        f'<div style="font-size:20px;font-weight:900;color:#111827;">'
        f'{r.get("company_name","")}</div>'
        f'<div style="font-size:12px;color:#6b7280;margin-top:3px;">'
        f'Registration: <strong>{r.get("registration_number","")}</strong>'
        f' &nbsp;|&nbsp; Valid until: <strong>{r.get("registration_valid_until","")}</strong>'
        f' &nbsp;|&nbsp; Est. <strong>{r.get("established_year","")}</strong>'
        f' &nbsp;|&nbsp; HQ: <strong>{r.get("headquarters","")}</strong>'
        f'</div>'
        f'<div style="margin-top:8px;">{cert_html}</div>'
        f'{expiry_html}'
        f'<div style="margin-top:8px;font-size:12px;color:#374151;">'
        f'<strong>Specialization:</strong> {r.get("specialization","")}'
        f' &nbsp;&middot;&nbsp; <strong>Contact:</strong> {r.get("contact_email","")}'
        f'</div>'
        f'</td>'
        f'<td style="vertical-align:top;text-align:right;width:130px;">'
        f'<div style="background:{tier_bg};border:1.5px solid {tier_border};'
        f'border-radius:10px;padding:10px 18px;text-align:center;">'
        f'<div style="font-size:22px;">{tier_icon}</div>'
        f'<div style="font-size:11px;font-weight:800;color:{tier_color};">{tier_label}</div>'
        f'</div></td>'
        f'</tr></table>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Trust gauges ──────────────────────────────────────────────────────────
    st.markdown("#### Trust Metrics")
    g1, g2, m1, m2 = st.columns(4)
    with g1:
        st.plotly_chart(_trust_gauge(r.get("trust_score", 0), "EcoTrace Trust Score"),
                        use_container_width=True, config={"displayModeBar": False})
    with g2:
        st.plotly_chart(_trust_gauge(r.get("gate_pass_rate", 0), "Gate Pass Rate"),
                        use_container_width=True, config={"displayModeBar": False})
    with m1:
        st.metric("Total Items Verified", f"{r.get('total_items_verified', 0):,}")
        st.metric("Avg Processing Time",  f"{r.get('avg_processing_time_hours', 0)} hrs")
    with m2:
        st.metric("Available EPR Credits", f"{r.get('available_credits_kg', 0):,.0f} kg")
        st.metric("Price per kg",          f"₹{r.get('price_per_kg_inr', 0)}")

    # ── Anomaly flags ──────────────────────────────────────────────────────────
    if flags:
        st.markdown("#### Anomaly Flags")
        for flag in flags:
            st.markdown(
                f'<div style="background:#fef2f2;border:1px solid #fca5a5;'
                f'border-radius:6px;padding:8px 14px;margin-bottom:6px;'
                f'font-size:12px;color:#991b1b;">&#9888; {flag}</div>',
                unsafe_allow_html=True,
            )

    # ── Aggregate footprint ────────────────────────────────────────────────────
    st.markdown("#### Aggregate Company Footprint")
    a1, a2, a3, a4, a5, a6 = st.columns(6)
    for col, label, val in [
        (a1, "Facilities",         str(r.get("facility_count", 0))),
        (a2, "Total Capacity",     f"{r.get('total_capacity_tpm', 0)} t/mo"),
        (a3, "Total Area",         f"{r.get('total_area_sqm', 0):,} m²"),
        (a4, "Total Workforce",    f"{r.get('total_workforce', 0)} staff"),
        (a5, "Dismantled/mo",      f"{r.get('total_dismantled_monthly', 0):,}"),
        (a6, "Intact/Packaged/mo", f"{r.get('total_intact_monthly', 0):,}"),
    ]:
        with col:
            st.metric(label, val)

    # ── Facilities ─────────────────────────────────────────────────────────────
    st.markdown("#### Registered Facilities")

    for idx, fac in enumerate(facs):
        cap  = fac.get("capacity", {})
        foot = fac.get("footprint", {})
        ih   = fac.get("item_handling", {})
        stats = fac.get("monthly_stats", {})
        eq   = fac.get("equipment", [])
        prim = "★ Primary Facility" if fac.get("is_primary") else "Secondary Facility"

        with st.expander(
            f"{fac.get('facility_name', '')} — {fac.get('city', '')}, {fac.get('state', '')}  |  {prim}",
            expanded=(idx == 0),
        ):
            st.markdown(
                f'<div style="font-size:12px;color:#6b7280;margin-bottom:12px;">'
                f'&#128205; {fac.get("address", "")} &nbsp;|&nbsp; '
                f'GPS: {fac.get("gps_lat", "")}, {fac.get("gps_lon", "")} &nbsp;|&nbsp; '
                f'Operational since: {fac.get("operational_since", "")}'
                f'</div>',
                unsafe_allow_html=True,
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown(
                    f'<div style="font-size:11px;font-weight:700;color:#374151;'
                    f'margin-bottom:8px;text-transform:uppercase;">Capacity</div>'
                    f'<table style="width:100%;border-collapse:collapse;">'
                    + _row("Processing cap.", f"{cap.get('processing_capacity_tons_per_month',0)} t/mo")
                    + _row("Storage cap.",    f"{cap.get('storage_capacity_tons',0)} tons")
                    + _row("Daily throughput",f"{cap.get('daily_throughput_items',0)} items/day")
                    + _row("Annual capacity", f"{cap.get('annual_capacity_tons',0)} t/year")
                    + f'</table>',
                    unsafe_allow_html=True,
                )

            with c2:
                st.markdown(
                    f'<div style="font-size:11px;font-weight:700;color:#374151;'
                    f'margin-bottom:8px;text-transform:uppercase;">Footprint</div>'
                    f'<table style="width:100%;border-collapse:collapse;">'
                    + _row("Total area",      f"{foot.get('total_area_sqm',0):,} m²")
                    + _row("Covered area",    f"{foot.get('covered_area_sqm',0):,} m²")
                    + _row("Open yard",       f"{foot.get('open_yard_sqm',0):,} m²")
                    + _row("Workforce",       f"{foot.get('workforce_total',0)} staff")
                    + _row("Technical staff", str(foot.get('workforce_technical',0)))
                    + _row("Shifts",          str(foot.get('shift_count',0)))
                    + _row("Energy",          foot.get('energy_source',''))
                    + _row("Water recycling", "Yes" if foot.get('water_recycling') else "No")
                    + _row("Emission cert",   foot.get('emission_certificate',''))
                    + f'</table>',
                    unsafe_allow_html=True,
                )

            with c3:
                st.markdown(
                    f'<div style="font-size:11px;font-weight:700;color:#374151;'
                    f'margin-bottom:8px;text-transform:uppercase;">Item Handling</div>'
                    f'<table style="width:100%;border-collapse:collapse;">'
                    + _row("Accepts dismantled",     "Yes" if ih.get('accepts_dismantled') else "No")
                    + _row("Accepts intact/packaged","Yes" if ih.get('accepts_intact_packaged') else "No")
                    + _row("In-house dismantling",   "Yes" if ih.get('dismantling_in_house') else "No")
                    + _row("Hazmat certified",       "Yes" if ih.get('hazmat_certified') else "No")
                    + _row("Battery cert",           "Yes" if ih.get('battery_handling_certified') else "No")
                    + _row("Dismantling rate",       f"{ih.get('dismantling_rate_items_per_day',0)} items/day")
                    + _row("Packaging rate",         f"{ih.get('packaging_rate_items_per_day',0)} items/day")
                    + f'</table>',
                    unsafe_allow_html=True,
                )

            # Accepted component/device types
            comp_tags = "".join(
                f'<span style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:4px;'
                f'padding:2px 8px;font-size:10px;color:#1d4ed8;font-weight:600;'
                f'margin:2px 2px 0 0;display:inline-block;">{c}</span>'
                for c in ih.get("component_types_accepted", [])
            )
            dev_tags = "".join(
                f'<span style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:4px;'
                f'padding:2px 8px;font-size:10px;color:#166534;font-weight:600;'
                f'margin:2px 2px 0 0;display:inline-block;">{d}</span>'
                for d in ih.get("device_types_accepted", [])
            )
            pack_tags = "".join(
                f'<span style="background:#faf5ff;border:1px solid #ddd6fe;border-radius:4px;'
                f'padding:2px 8px;font-size:10px;color:#7c3aed;font-weight:600;'
                f'margin:2px 2px 0 0;display:inline-block;">{p}</span>'
                for p in ih.get("packaging_accepted", [])
            )

            st.markdown(
                f'<div style="margin-top:10px;">'
                f'<div style="font-size:11px;font-weight:700;color:#374151;margin-bottom:4px;">'
                f'Components Accepted</div><div>{comp_tags or "—"}</div>'
                f'<div style="font-size:11px;font-weight:700;color:#374151;'
                f'margin:8px 0 4px 0;">Device Types Accepted</div><div>{dev_tags or "—"}</div>'
                f'<div style="font-size:11px;font-weight:700;color:#374151;'
                f'margin:8px 0 4px 0;">Packaging Accepted</div><div>{pack_tags or "—"}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Monthly stats bar
            st.markdown(
                '<div style="font-size:11px;font-weight:700;color:#374151;'
                'margin:12px 0 4px 0;">Monthly Processing Statistics</div>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(
                _monthly_bar(fac),
                use_container_width=True,
                config={"displayModeBar": False},
            )

            proc_ratio = stats.get("processing_ratio", 0)
            ratio_color = "#166534" if proc_ratio >= 0.9 else "#d97706" if proc_ratio >= 0.7 else "#dc2626"
            st.markdown(
                f'<div style="font-size:12px;color:#6b7280;margin-top:4px;">'
                f'Processing Ratio: <strong style="color:{ratio_color};">'
                f'{proc_ratio*100:.1f}%</strong>'
                f' &nbsp;|&nbsp; Credits generated this month: '
                f'<strong>{stats.get("credits_generated_kg",0):,} kg</strong>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Equipment
            if eq:
                eq_items = "".join(
                    f'<li style="font-size:11px;color:#374151;padding:2px 0;">{e}</li>'
                    for e in eq
                )
                st.markdown(
                    f'<div style="font-size:11px;font-weight:700;color:#374151;'
                    f'margin:10px 0 4px 0;">Equipment &amp; Infrastructure</div>'
                    f'<ul style="margin:0;padding-left:18px;">{eq_items}</ul>',
                    unsafe_allow_html=True,
                )

    # ── Available credit listings ──────────────────────────────────────────────
    listings = get_credit_listings(recycler_id=recycler_id)
    if listings:
        st.markdown("#### Available EPR Credit Listings")
        st.markdown(
            '<div style="font-size:11px;color:#6b7280;margin-bottom:10px;">'
            'Credits backed by EcoTrace verified item records.</div>',
            unsafe_allow_html=True,
        )
        hdr = st.columns([2, 1.5, 1.5, 1.5, 1.5])
        for col, h in zip(hdr, ["Item Type", "Available (kg)", "Price/kg (₹)", "Trust Score", "Min Order (kg)"]):
            with col:
                st.markdown(
                    f'<div style="font-size:11px;font-weight:700;color:#374151;'
                    f'padding:6px 0;border-bottom:2px solid #e5e7eb;">{h}</div>',
                    unsafe_allow_html=True,
                )
        for lst in listings:
            ts_c = "#166534" if lst.get("trust_score", 0) >= 0.85 else "#2563eb"
            lc = st.columns([2, 1.5, 1.5, 1.5, 1.5])
            vals = [
                lst.get("item_type", ""),
                f"{lst.get('available_kg',0):,}",
                f"₹{lst.get('price_per_kg_inr',0)}",
                f"{int(lst.get('trust_score',0)*100)}%",
                f"{lst.get('min_order_kg',0):,} kg",
            ]
            colors = ["#111827", "#111827", "#111827", ts_c, "#111827"]
            for col, v, c in zip(lc, vals, colors):
                with col:
                    st.markdown(
                        f'<div style="font-size:12px;font-weight:700;color:{c};'
                        f'padding:5px 0;">{v}</div>',
                        unsafe_allow_html=True,
                    )

    # Disclaimer
    st.markdown(
        '<div style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:8px;'
        'padding:10px 16px;margin-top:16px;font-size:11px;color:#9ca3af;">'
        '<strong>Prototype Notice:</strong> All facility data, trust scores, and credit '
        'listings are synthetic examples for architecture demonstration only.</div>',
        unsafe_allow_html=True,
    )
