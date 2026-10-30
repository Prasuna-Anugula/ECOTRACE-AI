"""
EcoTrace AI — Onboarding Page
──────────────────────────────
Two tabs:
  1. Producer Registration — enter products + annual tonnes placed on market.
     Obligation calculator shows tonnes to fulfil.
  2. Recycler Registration — enter facilities + capacity declaration.

NO display:flex/grid. All layout via st.columns() and <table>.
"""

from __future__ import annotations
import streamlit as st
from services.credit_ledger import (
    compute_obligation,
    get_all_producers,
    get_all_registered_recyclers,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _section(title: str, subtitle: str = "") -> None:
    st.markdown(
        f'<div style="margin-bottom:16px;">'
        f'<div style="font-size:18px;font-weight:900;color:#111827;">{title}</div>'
        f'{"<div style=font-size:13px;color:#6b7280;margin-top:3px;>" + subtitle + "</div>" if subtitle else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )


def _info_box(text: str, colour: str = "#1d4ed8", bg: str = "#eff6ff", border: str = "#bfdbfe") -> None:
    st.markdown(
        f'<div style="background:{bg};border:1px solid {border};border-left:4px solid {colour};'
        f'border-radius:8px;padding:10px 14px;margin-bottom:14px;font-size:12px;color:#374151;">'
        f'{text}</div>',
        unsafe_allow_html=True,
    )


def _kpi(col, label: str, value: str, colour: str = "#111827") -> None:
    col.markdown(
        f'<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:12px 14px;">'
        f'<div style="font-size:10px;font-weight:700;color:#6b7280;text-transform:uppercase;'
        f'letter-spacing:0.06em;margin-bottom:4px;">{label}</div>'
        f'<div style="font-size:22px;font-weight:900;color:{colour};">{value}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── main render ───────────────────────────────────────────────────────────────

def render_onboarding() -> None:
    st.markdown("## Onboarding")
    st.caption("Register as a Producer or Recycler to participate in the EcoTrace EPR marketplace.")

    tab_producer, tab_recycler, tab_existing = st.tabs([
        "Producer Registration",
        "Recycler Registration",
        "Registered Entities",
    ])

    with tab_producer:
        _render_producer_onboarding()

    with tab_recycler:
        _render_recycler_onboarding()

    with tab_existing:
        _render_existing_registrations()


# ── Producer onboarding ───────────────────────────────────────────────────────

def _render_producer_onboarding() -> None:
    _section(
        "Producer Registration",
        "Register your company, declare products placed on market, and calculate your EPR obligation.",
    )

    _info_box(
        "Under E-Waste Management Rules 2022, every producer must register with CPCB and "
        "fulfil an annual recycling obligation equal to a percentage of the weight of products "
        "placed on the Indian market. EcoTrace calculates this obligation automatically "
        "from your product declarations."
    )

    with st.form("producer_registration_form"):
        st.markdown("#### Company Details")
        c1, c2 = st.columns(2)
        with c1:
            company_name = st.text_input("Company Name", placeholder="e.g. Acme Electronics India Pvt Ltd")
            contact_email = st.text_input("EPR Contact Email", placeholder="epr@company.in")
        with c2:
            cpcb_reg = st.text_input("CPCB Registration Number", placeholder="CPCB-PRD-YYYY-XXXXX")
            contact_person = st.text_input("EPR Responsible Person", placeholder="Full name")

        st.markdown("#### Product Declaration")
        _info_box(
            "Declare each product category you sell in India. "
            "The obligation calculator uses units × average weight × EPR rate to compute your annual target.",
            colour="#166534", bg="#f0fdf4", border="#bbf7d0",
        )

        epr_rate = st.slider(
            "EPR Rate (%)",
            min_value=10, max_value=100, value=30, step=5,
            help="The percentage of placed-on-market weight you must recycle. Default: 30% (E-Waste Rules 2022).",
        )

        st.markdown("**Add Product Categories**")
        n_products = st.number_input("Number of product categories", min_value=1, max_value=10, value=2, step=1)

        products = []
        for i in range(int(n_products)):
            st.markdown(f"*Product {i+1}*")
            pc1, pc2, pc3 = st.columns(3)
            with pc1:
                cat = st.selectbox(
                    "Category",
                    ["Mobile", "Laptop", "Tablet", "Desktop", "Television",
                     "Refrigerator", "Washing Machine", "Printer", "Monitor", "Server"],
                    key=f"cat_{i}",
                )
            with pc2:
                units = st.number_input(
                    "Units sold/year", min_value=0, value=100000, step=10000, key=f"units_{i}",
                )
            with pc3:
                avg_wt = st.number_input(
                    "Avg weight (kg)", min_value=0.01, value=0.20, step=0.01, key=f"wt_{i}",
                    format="%.2f",
                )
            products.append({"category": cat, "units_sold_per_year": int(units), "avg_weight_kg": float(avg_wt)})

        submitted = st.form_submit_button("Calculate Obligation & Register", type="primary", use_container_width=True)

    if submitted and company_name:
        result = compute_obligation(products, epr_rate_percent=epr_rate)
        st.markdown("---")
        st.markdown("#### Obligation Calculation Result")

        k1, k2, k3, k4 = st.columns(4)
        _kpi(k1, "Total placed on market", f"{result['total_placed_kg']/1000:,.1f} t")
        _kpi(k2, "EPR Rate", f"{epr_rate}%")
        _kpi(k3, "Annual Obligation", f"{result['obligation_t']:,.1f} t", colour="#dc2626")
        _kpi(k4, "Obligation in kg", f"{result['obligation_kg']:,.0f} kg", colour="#dc2626")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown("**Breakdown by product category:**")

        hdr = st.columns([2, 1.5, 1.5, 1.5, 2])
        for col, h in zip(hdr, ["Category", "Units/year", "Avg weight", "Total kg", "Obligation kg"]):
            with col:
                st.markdown(
                    f'<div style="font-size:11px;font-weight:700;color:#374151;'
                    f'padding:6px 0;border-bottom:2px solid #e5e7eb;">{h}</div>',
                    unsafe_allow_html=True,
                )
        for row in result["by_product"]:
            rc = st.columns([2, 1.5, 1.5, 1.5, 2])
            for col, val in zip(rc, [
                row["category"],
                f"{row['units']:,}",
                f"{row['avg_kg']} kg",
                f"{row['total_kg']:,.0f} kg",
                f"{row['obligation_kg']:,.0f} kg",
            ]):
                with col:
                    st.markdown(
                        f'<div style="font-size:12px;padding:5px 0;border-bottom:1px solid #f3f4f6;">'
                        f'{val}</div>',
                        unsafe_allow_html=True,
                    )

        st.success(
            f"Registration prepared for **{company_name}**. "
            f"Annual EPR obligation: **{result['obligation_t']:,.1f} tonnes** "
            f"({result['obligation_kg']:,.0f} kg). "
            f"Deadline: 31 December 2026. "
            f"*Prototype — no data is actually saved.*"
        )
    elif submitted:
        st.warning("Please enter your company name before submitting.")


# ── Recycler onboarding ───────────────────────────────────────────────────────

def _render_recycler_onboarding() -> None:
    _section(
        "Recycler Registration",
        "Register your recycling company, declare facilities and processing capacity.",
    )

    _info_box(
        "Registered recyclers can submit verification records through the EcoTrace pipeline "
        "(Stages 0–11), earn Evidence Attestation credits, and list credits on the marketplace. "
        "Each facility must have valid CPCB registration and declared capacity."
    )

    with st.form("recycler_registration_form"):
        st.markdown("#### Company Details")
        r1, r2 = st.columns(2)
        with r1:
            company_name = st.text_input("Company Name", placeholder="e.g. GreenRecycle Pvt Ltd", key="rec_name")
            contact_email = st.text_input("Compliance Email", placeholder="compliance@company.in", key="rec_email")
            cpcb_reg = st.text_input("CPCB Registration Number", placeholder="CPCB-EPR-YYYY-XXXXX", key="rec_cpcb")
        with r2:
            hq_city  = st.text_input("Headquarters City", placeholder="e.g. Hyderabad", key="rec_city")
            contact_person = st.text_input("EPR Contact Person", placeholder="Full name", key="rec_person")
            specialization = st.text_input("Specialization", placeholder="e.g. Mobile devices and battery recycling", key="rec_spec")

        st.markdown("#### Facility Declaration")
        n_facilities = st.number_input("Number of facilities", min_value=1, max_value=5, value=1, step=1)
        facilities = []
        for i in range(int(n_facilities)):
            st.markdown(f"*Facility {i+1}*")
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                fac_name = st.text_input("Facility Name", key=f"fac_name_{i}", placeholder="City — Unit name")
                fac_city = st.text_input("City", key=f"fac_city_{i}")
            with fc2:
                capacity_tpm = st.number_input(
                    "Processing capacity (tonnes/month)", min_value=1, value=30, step=5, key=f"cap_{i}",
                )
                workforce = st.number_input("Workforce count", min_value=1, value=20, step=5, key=f"wf_{i}")
            with fc3:
                area_sqm = st.number_input("Facility area (m²)", min_value=100, value=3000, step=100, key=f"area_{i}")
                hazmat   = st.toggle("Hazmat certified", key=f"hazmat_{i}", value=True)

            item_types = st.multiselect(
                "Item types accepted",
                ["PCB", "Battery", "Mobile", "Laptop", "Television", "Desktop",
                 "Keyboard", "Mouse", "Printer", "Server"],
                default=["PCB", "Battery"],
                key=f"items_{i}",
            )
            facilities.append({
                "name": fac_name, "city": fac_city,
                "capacity_tpm": capacity_tpm, "workforce": workforce,
                "area_sqm": area_sqm, "hazmat": hazmat, "item_types": item_types,
            })

        submitted_r = st.form_submit_button("Register Recycler", type="primary", use_container_width=True)

    if submitted_r and company_name:
        total_cap = sum(f["capacity_tpm"] for f in facilities)
        annual_cap = total_cap * 12 * 1000

        k1, k2, k3 = st.columns(3)
        _kpi(k1, "Total Capacity", f"{total_cap} t/month")
        _kpi(k2, "Annual Capacity", f"{annual_cap/1000:,.0f} t/year")
        _kpi(k3, "Facilities Declared", str(len(facilities)))

        st.success(
            f"Recycler registration prepared for **{company_name}**. "
            f"{len(facilities)} facilit{'y' if len(facilities)==1 else 'ies'} declared. "
            f"Total capacity: **{total_cap} tonnes/month**. "
            f"*Prototype — no data is actually saved.*"
        )


# ── Existing registrations ────────────────────────────────────────────────────

def _render_existing_registrations() -> None:
    _section("Registered Entities", "Currently registered producers and recyclers in the system.")

    tab_p, tab_r = st.tabs(["Producers", "Recyclers"])

    with tab_p:
        producers = get_all_producers()
        for p in producers:
            obligation_t = p.get("annual_obligation_kg", 0) / 1000
            st.markdown(
                f'<div style="border:1px solid #e5e7eb;border-radius:10px;'
                f'padding:14px 18px;margin-bottom:10px;">'
                f'<table style="width:100%;border-collapse:collapse;">'
                f'<tr>'
                f'<td style="vertical-align:top;">'
                f'<div style="font-size:14px;font-weight:800;color:#111827;">{p["company_name"]}</div>'
                f'<div style="font-size:11px;color:#6b7280;margin-top:2px;">'
                f'Reg: {p["registration_number"]} &nbsp;|&nbsp; Contact: {p["contact_person"]} &nbsp;|&nbsp; {p["contact_email"]}'
                f'</div></td>'
                f'<td style="text-align:right;vertical-align:top;width:180px;">'
                f'<div style="font-size:11px;color:#6b7280;">Annual Obligation</div>'
                f'<div style="font-size:20px;font-weight:900;color:#dc2626;">{obligation_t:,.0f} t</div>'
                f'<div style="font-size:10px;color:#6b7280;">Deadline: {p["deadline"]}</div>'
                f'</td></tr>'
                f'<tr><td colspan="2" style="padding-top:8px;">'
                f'<div style="font-size:11px;color:#6b7280;">Products: '
                f'{", ".join(pr["category"] for pr in p.get("products", []))}'
                f'</div></td></tr>'
                f'</table></div>',
                unsafe_allow_html=True,
            )

    with tab_r:
        recyclers = get_all_registered_recyclers()
        for r in recyclers:
            cap_t = r.get("total_capacity_tpm", 0)
            st.markdown(
                f'<div style="border:1px solid #e5e7eb;border-radius:10px;'
                f'padding:14px 18px;margin-bottom:10px;">'
                f'<table style="width:100%;border-collapse:collapse;">'
                f'<tr>'
                f'<td style="vertical-align:top;">'
                f'<div style="font-size:14px;font-weight:800;color:#111827;">{r["company_name"]}</div>'
                f'<div style="font-size:11px;color:#6b7280;margin-top:2px;">'
                f'Reg: {r["registration_number"]} &nbsp;|&nbsp; Contact: {r["contact_person"]}'
                f'</div>'
                f'<div style="font-size:11px;color:#6b7280;margin-top:3px;">'
                f'Handles: {", ".join(r.get("item_types_handled",[]))}'
                f'</div></td>'
                f'<td style="text-align:right;vertical-align:top;width:160px;">'
                f'<div style="font-size:11px;color:#6b7280;">Capacity</div>'
                f'<div style="font-size:20px;font-weight:900;color:#166534;">{cap_t} t/mo</div>'
                f'<div style="font-size:10px;color:#6b7280;">{r["facility_count"]} facilit{"y" if r["facility_count"]==1 else "ies"}</div>'
                f'</td></tr>'
                f'</table></div>',
                unsafe_allow_html=True,
            )
