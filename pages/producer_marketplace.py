"""
EcoTrace AI — Producer Marketplace Page
────────────────────────────────────────
Shows all verified recycler companies with trust scores,
facility details, capacity, footprint, and item handling capabilities.
Producers enter their EPR obligation to see fulfilment analysis.

NO display:flex / display:grid — Streamlit sanitizer strips them.
"""

from __future__ import annotations
import streamlit as st
from services.recycler_trust import (
    get_all_recyclers,
    get_all_states,
    get_all_item_types,
)
from components.recycler_card import render_recycler_card


def render_producer_marketplace() -> None:

    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown(
        '<div style="margin-bottom:20px;">'
        '<div style="font-size:22px;font-weight:900;color:#111827;letter-spacing:-0.3px;">'
        'EPR Certificate Marketplace</div>'
        '<div style="font-size:13px;color:#6b7280;margin-top:3px;">'
        'Search and compare verified recycler companies. '
        'Every Trust Score is calculated from actual EcoTrace verification history '
        '&mdash; not self-reported data.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Trust tier legend ──────────────────────────────────────────────────────
    st.markdown(
        '<div style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:10px;'
        'padding:10px 16px;margin-bottom:18px;font-size:11px;">'
        '<strong style="color:#374151;">Trust Tiers: </strong>'
        '<span style="color:#166534;font-weight:700;">RECOMMENDED (&ge;85%)</span>'
        '&nbsp;&nbsp;'
        '<span style="color:#1d4ed8;font-weight:700;">VERIFIED (70&ndash;84%)</span>'
        '&nbsp;&nbsp;'
        '<span style="color:#d97706;font-weight:700;">CAUTION (60&ndash;69%)</span>'
        '&nbsp;&nbsp;'
        '<span style="color:#dc2626;font-weight:700;">HIGH RISK (anomaly flags)</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ═════════════════════════════════════════════════════════════════════════
    # SEARCH & FILTER PANEL
    # ═════════════════════════════════════════════════════════════════════════
    with st.expander("Search & Filter Recyclers", expanded=True):

        # ── 1. EPR Obligation section ─────────────────────────────────────────
        st.markdown(
            '<div style="background:#eff6ff;border:1px solid #bfdbfe;'
            'border-radius:8px;padding:12px 16px;margin-bottom:14px;">'
            '<div style="font-size:12px;font-weight:700;color:#1d4ed8;margin-bottom:3px;">'
            'My EPR Obligation</div>'
            '<div style="font-size:11px;color:#6b7280;">'
            'Enter how many tonnes of credits you need to procure. '
            'EcoTrace will tell you whether the filtered market can cover it '
            'and the minimum number of recyclers required.'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        ob1, ob2 = st.columns(2)

        with ob1:
            obligation_tonnes = st.number_input(
                "Credits Required (tonnes)",
                min_value=0.0,
                max_value=500_000.0,
                value=0.0,
                step=100.0,
                format="%.0f",
                key="mp_obligation",
                help="Total tonnes of EPR credits you need to purchase from this marketplace.",
            )

        with ob2:
            obligation_kg = obligation_tonnes * 1000.0
            remaining_kg  = obligation_kg
            remaining_t   = obligation_tonnes

            if obligation_tonnes > 0:
                st.markdown(
                    '<div style="font-size:11px;font-weight:700;color:#374151;'
                    'margin-bottom:4px;margin-top:4px;">Credits to Source</div>'
                    f'<div style="font-size:28px;font-weight:900;color:#1d4ed8;">'
                    f'{obligation_tonnes:,.0f} t</div>'
                    f'<div style="font-size:10px;color:#6b7280;">'
                    f'{obligation_kg:,.0f} kg required from marketplace</div>',
                    unsafe_allow_html=True,
                )
            else:
                obligation_kg = 0.0
                remaining_kg  = 0.0
                remaining_t   = 0.0
                st.markdown(
                    '<div style="font-size:11px;color:#9ca3af;margin-top:28px;">'
                    'Enter your requirement above to see fulfilment analysis.</div>',
                    unsafe_allow_html=True,
                )

        # Divider between obligation and filter controls
        st.markdown(
            '<hr style="border:none;border-top:1px solid #e5e7eb;margin:14px 0;">',
            unsafe_allow_html=True,
        )

        # ── 2. Filter controls ────────────────────────────────────────────────
        r1c1, r1c2, r1c3 = st.columns(3)

        with r1c1:
            min_trust = st.slider(
                "Min Trust Score (%)",
                min_value=0, max_value=100, value=60, step=5,
                key="mp_min_trust",
            ) / 100.0

        with r1c2:
            min_gate = st.slider(
                "Min Gate Pass Rate (%)",
                min_value=0, max_value=100, value=60, step=5,
                key="mp_min_gate",
            ) / 100.0

        with r1c3:
            all_states   = ["All"] + get_all_states()
            state_filter = st.selectbox(
                "State / Location",
                options=all_states,
                key="mp_state",
            )

        r2c1, r2c2, r2c3 = st.columns(3)

        with r2c1:
            all_types   = ["All"] + get_all_item_types()
            item_filter = st.selectbox(
                "Item Type Accepted",
                options=all_types,
                key="mp_item_type",
            )

        with r2c2:
            sort_options = {
                "trust_score":    "Trust Score (high to low)",
                "gate_pass_rate": "Gate Pass Rate (high to low)",
                "credits":        "Available Credits (high to low)",
                "capacity":       "Processing Capacity (high to low)",
                "price_asc":      "Price (low to high)",
                "price_desc":     "Price (high to low)",
            }
            sort_by = st.selectbox(
                "Sort By",
                options=list(sort_options.keys()),
                format_func=lambda x: sort_options[x],
                key="mp_sort",
            )

        with r2c3:
            show_flagged = st.toggle(
                "Show High-Risk Recyclers",
                value=True,
                key="mp_show_flagged",
            )

    # ═════════════════════════════════════════════════════════════════════════
    # LOAD DATA
    # ═════════════════════════════════════════════════════════════════════════
    recyclers = get_all_recyclers(
        min_trust=min_trust,
        min_gate_pass=min_gate,
        item_type_filter=item_filter,
        state_filter=state_filter,
        sort_by=sort_by,
    )

    if not show_flagged:
        recyclers = [r for r in recyclers if not r.get("anomaly_flags")]

    # ═════════════════════════════════════════════════════════════════════════
    # OBLIGATION FULFILMENT ANALYSIS
    # Shows only when an obligation has been entered
    # ═════════════════════════════════════════════════════════════════════════
    if obligation_tonnes > 0 and remaining_kg > 0:
        total_avail_kg = sum(r.get("available_credits_kg", 0.0) for r in recyclers)
        can_fulfil     = total_avail_kg >= remaining_kg
        fulfilment_pct = (
            min((total_avail_kg / remaining_kg) * 100.0, 100.0)
            if remaining_kg > 0 else 100.0
        )

        # Minimum recyclers needed to cover remaining obligation (greedy)
        running          = 0.0
        recyclers_needed = 0
        for rec in sorted(
            recyclers,
            key=lambda x: x.get("available_credits_kg", 0),
            reverse=True,
        ):
            if running >= remaining_kg:
                break
            running += rec.get("available_credits_kg", 0.0)
            recyclers_needed += 1

        f_color  = "#166534" if can_fulfil else "#dc2626"
        f_bg     = "#f0fdf4" if can_fulfil else "#fef2f2"
        f_border = "#bbf7d0" if can_fulfil else "#fca5a5"
        f_label  = (
            "OBLIGATION CAN BE FULFILLED"
            if can_fulfil else
            "INSUFFICIENT CREDITS IN FILTERED MARKET"
        )
        f_icon   = "&#10003;" if can_fulfil else "&#9888;"

        st.markdown(
            f'<div style="background:{f_bg};border:1.5px solid {f_border};'
            f'border-radius:10px;padding:14px 18px;margin-bottom:16px;">'
            f'<table style="width:100%;border-collapse:collapse;">'
            f'<tr>'
            f'<td style="vertical-align:middle;">'
            f'<div style="font-size:14px;font-weight:800;color:{f_color};">'
            f'{f_icon} {f_label}</div>'
            f'<div style="font-size:11px;color:#6b7280;margin-top:5px;line-height:1.8;">'
            f'Remaining need: &nbsp;<strong>{remaining_t:,.0f} t '
            f'({remaining_kg:,.0f} kg)</strong>'
            f'&nbsp;&nbsp;&bull;&nbsp;&nbsp;'
            f'Available in filtered market: &nbsp;<strong>'
            f'{total_avail_kg / 1000:,.1f} t ({total_avail_kg:,.0f} kg)</strong>'
            f'&nbsp;&nbsp;&bull;&nbsp;&nbsp;'
            f'Coverage: &nbsp;<strong style="color:{f_color};">'
            f'{fulfilment_pct:.1f}%</strong>'
            f'</div>'
            f'</td>'
            f'<td style="text-align:right;vertical-align:middle;'
            f'padding-left:24px;width:160px;">'
            f'<div style="font-size:10px;color:#6b7280;text-transform:uppercase;'
            f'letter-spacing:0.05em;margin-bottom:2px;">Min recyclers<br>needed</div>'
            f'<div style="font-size:36px;font-weight:900;color:{f_color};'
            f'line-height:1;">{recyclers_needed}</div>'
            f'</td>'
            f'</tr>'
            f'</table>'
            f'</div>',
            unsafe_allow_html=True,
        )

    elif obligation_tonnes > 0 and remaining_kg == 0:
        # Already fully covered — this state no longer applies; skip silently
        pass

    # ═════════════════════════════════════════════════════════════════════════
    # SUMMARY KPIs
    # ═════════════════════════════════════════════════════════════════════════
    recommended   = sum(1 for r in recyclers if r.get("trust_score", 0) >= 0.85)
    total_credits = sum(r.get("available_credits_kg", 0.0) for r in recyclers)
    avg_trust     = (
        sum(r.get("trust_score", 0.0) for r in recyclers) / len(recyclers)
        if recyclers else 0.0
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Recyclers Found", len(recyclers))
    with k2:
        st.metric("EcoTrace Recommended", recommended)
    with k3:
        st.metric(
            "Total Available Credits",
            f"{total_credits / 1000:,.1f} t",
            delta=f"{total_credits:,.0f} kg",
        )
    with k4:
        st.metric("Avg Trust Score", f"{avg_trust * 100:.1f}%")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if not recyclers:
        st.info(
            "No recyclers match your current filters. "
            "Try adjusting the Trust Score or Gate Pass Rate sliders."
        )
        return

    # ── Recycler count label ───────────────────────────────────────────────────
    st.markdown(
        f'<div style="font-size:12px;color:#6b7280;margin-bottom:12px;">'
        f'Showing {len(recyclers)} recycler{"s" if len(recyclers) != 1 else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ═════════════════════════════════════════════════════════════════════════
    # RECYCLER CARDS
    # ═════════════════════════════════════════════════════════════════════════
    for r in recyclers:
        clicked = render_recycler_card(r, show_detail_button=True)
        if clicked:
            st.session_state["selected_recycler_id"] = r["recycler_id"]
            st.session_state["current_page"]         = "Recycler Profile"
            st.rerun()

    # ── Disclaimer ────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:8px;'
        'padding:12px 16px;margin-top:8px;font-size:11px;color:#6b7280;line-height:1.8;">'
        '<strong>Marketplace Disclaimer:</strong> '
        'Trust Scores and Gate Pass Rates are calculated from EcoTrace verified '
        'transaction history. Available credit quantities are indicative and subject '
        'to confirmation. Prices are listed by recyclers and not guaranteed by EcoTrace. '
        'Always verify CPCB registration validity before purchasing EPR certificates. '
        '<strong>Prototype Notice:</strong> All data is synthetic for demonstration only.'
        '</div>',
        unsafe_allow_html=True,
    )
