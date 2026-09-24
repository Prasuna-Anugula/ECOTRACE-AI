"""
EcoTrace AI — Recycler Card Component
──────────────────────────────────────
Reusable card for displaying a recycler company's trust score,
facilities, capacity, footprint, and item handling capability.

SAFE HTML RULES:
- No display:flex / display:grid (Streamlit sanitizer strips them)
- No split open/close tags across multiple st.markdown() calls
- Use <table> for side-by-side layouts
- Every st.markdown() call is self-contained
"""

from __future__ import annotations
import streamlit as st


def render_recycler_card(r: dict, show_detail_button: bool = True) -> bool:
    """
    Render a single recycler company card.
    Returns True if the 'View Full Profile' button was clicked.
    """
    tier   = r.get("tier", {})
    flags  = r.get("anomaly_flags", [])
    facs   = r.get("facilities", [])

    tier_color  = tier.get("color",  "#374151")
    tier_bg     = tier.get("bg",     "#f9fafb")
    tier_border = tier.get("border", "#e5e7eb")
    tier_icon   = tier.get("icon",   "")
    tier_label  = tier.get("tier",   "")

    ts_pct  = int(r.get("trust_score",    0) * 100)
    gpr_pct = int(r.get("gate_pass_rate", 0) * 100)

    bar_color = (
        "#16a34a" if r.get("trust_score", 0) >= 0.85 else
        "#2563eb" if r.get("trust_score", 0) >= 0.70 else
        "#d97706" if r.get("trust_score", 0) >= 0.60 else
        "#dc2626"
    )

    # ── Certifications ────────────────────────────────────────────────────────
    cert_html = "".join(
        f'<span style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:4px;'
        f'padding:2px 7px;font-size:10px;color:#166534;font-weight:600;">{c}</span>&nbsp;'
        for c in r.get("certifications", [])
    )

    # ── Expiry warning ────────────────────────────────────────────────────────
    expiry_html = ""
    if r.get("expiry_warning"):
        expiry_html = (
            f'<div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:6px;'
            f'padding:5px 10px;margin-top:6px;font-size:11px;color:#9a3412;">'
            f'&#9200; Registration expires in {r.get("expiry_days", 0)} days</div>'
        )

    # ── Anomaly flags ─────────────────────────────────────────────────────────
    flags_html = ""
    if flags:
        rows = "".join(
            f'<div style="font-size:11px;color:#991b1b;padding:2px 0;">&#9888; {f}</div>'
            for f in flags
        )
        flags_html = (
            f'<div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:6px;'
            f'padding:8px 10px;margin-top:8px;">'
            f'<div style="font-size:11px;font-weight:700;color:#991b1b;margin-bottom:4px;">'
            f'Anomaly Flags</div>{rows}</div>'
        )

    # ── Facilities summary (table layout) ─────────────────────────────────────
    fac_rows_html = ""
    for fac in facs:
        cap   = fac.get("capacity", {})
        foot  = fac.get("footprint", {})
        ih    = fac.get("item_handling", {})
        stats = fac.get("monthly_stats", {})
        prim  = "&#9733; Primary" if fac.get("is_primary") else "Secondary"
        prim_c = "#166534" if fac.get("is_primary") else "#6b7280"
        d_tag = "Yes" if ih.get("accepts_dismantled") else "No"
        p_tag = "Yes" if ih.get("accepts_intact_packaged") else "No"

        fac_rows_html += (
            f'<div style="border:1px solid #e5e7eb;border-radius:8px;'
            f'padding:10px 14px;margin-top:8px;background:#fafafa;">'
            f'<table style="width:100%;border-collapse:collapse;">'
            f'<tr><td colspan="4">'
            f'<span style="font-size:12px;font-weight:700;color:#111827;">'
            f'{fac.get("facility_name","")}</span>'
            f'&nbsp;<span style="font-size:10px;color:{prim_c};font-weight:600;">{prim}</span>'
            f'&nbsp;&nbsp;<span style="font-size:10px;color:#6b7280;">'
            f'{fac.get("city","")}, {fac.get("state","")}</span>'
            f'</td></tr>'
            f'<tr><td colspan="4" style="font-size:11px;color:#6b7280;padding:2px 0 6px 0;">'
            f'{fac.get("address","")}</td></tr>'
            f'<tr style="font-size:11px;">'
            f'<td style="color:#6b7280;padding:3px 8px 3px 0;width:25%;">Capacity</td>'
            f'<td style="font-weight:700;color:#111827;width:25%;">'
            f'{cap.get("processing_capacity_tons_per_month",0)} t/mo</td>'
            f'<td style="color:#6b7280;padding:3px 8px;width:25%;">Daily items</td>'
            f'<td style="font-weight:700;color:#111827;">'
            f'{cap.get("daily_throughput_items",0)}/day</td>'
            f'</tr>'
            f'<tr style="font-size:11px;">'
            f'<td style="color:#6b7280;padding:3px 8px 3px 0;">Area</td>'
            f'<td style="font-weight:700;color:#111827;">{foot.get("total_area_sqm",0):,} m&#178;</td>'
            f'<td style="color:#6b7280;padding:3px 8px;">Workforce</td>'
            f'<td style="font-weight:700;color:#111827;">{foot.get("workforce_total",0)} staff</td>'
            f'</tr>'
            f'<tr style="font-size:11px;">'
            f'<td style="color:#6b7280;padding:3px 8px 3px 0;">Dismantled</td>'
            f'<td style="font-weight:700;color:#111827;">{d_tag}</td>'
            f'<td style="color:#6b7280;padding:3px 8px;">Packaged/Intact</td>'
            f'<td style="font-weight:700;color:#111827;">{p_tag}</td>'
            f'</tr>'
            f'<tr style="font-size:11px;">'
            f'<td style="color:#6b7280;padding:3px 8px 3px 0;">This month</td>'
            f'<td style="font-weight:700;color:#111827;">{stats.get("items_received",0):,} rcvd</td>'
            f'<td style="color:#6b7280;padding:3px 8px;">Dismantled</td>'
            f'<td style="font-weight:700;color:#111827;">{stats.get("items_dismantled",0):,} items</td>'
            f'</tr>'
            f'</table></div>'
        )

    # ── Full card HTML ────────────────────────────────────────────────────────
    st.markdown(
        f'<div style="background:#ffffff;border:1.5px solid {tier_border};'
        f'border-radius:14px;padding:18px 20px;margin-bottom:16px;">'

        # Header: name + tier badge using table
        f'<table style="width:100%;border-collapse:collapse;">'
        f'<tr>'
        f'<td style="vertical-align:top;">'
        f'<div style="font-size:16px;font-weight:800;color:#111827;">'
        f'{r.get("company_name","")}</div>'
        f'<div style="font-size:11px;color:#6b7280;margin-top:2px;">'
        f'Reg: {r.get("registration_number","")} &nbsp;|&nbsp; '
        f'Est. {r.get("established_year","")} &nbsp;|&nbsp; '
        f'{r.get("facility_count",1)} facilit{"y" if r.get("facility_count",1)==1 else "ies"}'
        f'</div></td>'
        f'<td style="vertical-align:top;text-align:right;width:120px;">'
        f'<div style="background:{tier_bg};border:1px solid {tier_border};'
        f'border-radius:8px;padding:5px 12px;display:inline-block;text-align:center;">'
        f'<div style="font-size:16px;">{tier_icon}</div>'
        f'<div style="font-size:10px;font-weight:800;color:{tier_color};">{tier_label}</div>'
        f'</div></td>'
        f'</tr></table>'

        # Trust score bar
        f'<div style="margin-top:14px;margin-bottom:6px;">'
        f'<table style="width:100%;border-collapse:collapse;">'
        f'<tr><td style="font-size:11px;font-weight:600;color:#374151;">EcoTrace Trust Score</td>'
        f'<td style="text-align:right;font-size:11px;font-weight:800;color:{bar_color};">'
        f'{ts_pct}%</td></tr></table>'
        f'<div style="background:#e5e7eb;border-radius:4px;height:6px;">'
        f'<div style="background:{bar_color};width:{ts_pct}%;height:6px;border-radius:4px;"></div>'
        f'</div></div>'

        # Gate pass rate bar
        f'<div style="margin-bottom:10px;">'
        f'<table style="width:100%;border-collapse:collapse;">'
        f'<tr><td style="font-size:11px;font-weight:600;color:#374151;">Processing Gate Pass Rate</td>'
        f'<td style="text-align:right;font-size:11px;font-weight:800;color:{bar_color};">'
        f'{gpr_pct}%</td></tr></table>'
        f'<div style="background:#e5e7eb;border-radius:4px;height:6px;">'
        f'<div style="background:{bar_color};width:{gpr_pct}%;height:6px;border-radius:4px;"></div>'
        f'</div></div>'

        # Key metrics table
        f'<table style="width:100%;border-collapse:collapse;font-size:11px;margin-top:4px;">'
        f'<tr>'
        f'<td style="color:#6b7280;padding:3px 8px 3px 0;width:25%;">Items Verified</td>'
        f'<td style="font-weight:700;color:#111827;width:25%;">{r.get("total_items_verified",0):,}</td>'
        f'<td style="color:#6b7280;padding:3px 8px;width:25%;">Avg Process Time</td>'
        f'<td style="font-weight:700;color:#111827;">{r.get("avg_processing_time_hours",0)} hrs</td>'
        f'</tr>'
        f'<tr>'
        f'<td style="color:#6b7280;padding:3px 8px 3px 0;">Available Credits</td>'
        f'<td style="font-weight:700;color:#111827;">{r.get("available_credits_kg",0):,.0f} kg</td>'
        f'<td style="color:#6b7280;padding:3px 8px;">Price per kg</td>'
        f'<td style="font-weight:700;color:#111827;">&#8377;{r.get("price_per_kg_inr",0)}</td>'
        f'</tr>'
        f'<tr>'
        f'<td style="color:#6b7280;padding:3px 8px 3px 0;">Total Capacity</td>'
        f'<td style="font-weight:700;color:#111827;">{r.get("total_capacity_tpm",0)} t/mo</td>'
        f'<td style="color:#6b7280;padding:3px 8px;">Total Area</td>'
        f'<td style="font-weight:700;color:#111827;">{r.get("total_area_sqm",0):,} m&#178;</td>'
        f'</tr>'
        f'</table>'

        # Specialization
        f'<div style="margin-top:10px;font-size:11px;color:#6b7280;">'
        f'<span style="font-weight:600;color:#374151;">Specialization: </span>'
        f'{r.get("specialization","")}</div>'

        # Certifications
        f'<div style="margin-top:8px;">{cert_html}</div>'

        # Expiry + flags
        f'{expiry_html}'
        f'{flags_html}'

        # Facilities
        f'<div style="margin-top:12px;">'
        f'<div style="font-size:11px;font-weight:700;color:#374151;margin-bottom:2px;">'
        f'Registered Facilities</div>'
        f'{fac_rows_html}'
        f'</div>'

        f'</div>',
        unsafe_allow_html=True,
    )

    if show_detail_button:
        if st.button(
            f"View Full Profile — {r.get('company_name', '')}",
            key=f"view_profile_{r.get('recycler_id', '')}",
            use_container_width=True,
        ):
            return True
    return False
