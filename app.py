"""
EcoTrace AI — Main Application Entry Point
==========================================
Responsibilities:
  - Configure Streamlit page
  - Inject global CSS
  - Initialize session state
  - Render sidebar navigation
  - Route to the correct page module

Do NOT put business logic here.
"""

import sys
import os

# ── Ensure project root is on sys.path so all imports resolve correctly ───────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st

from config import APP_NAME, APP_TAGLINE, APP_VERSION, ROLE_RECYCLER, ROLE_PRODUCER


# ── Page configuration (must be first Streamlit call) ─────────────────────────
st.set_page_config(
    page_title=f"{APP_NAME}",
    page_icon="♻",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            f"**{APP_NAME}** {APP_VERSION}\n\n"
            f"{APP_TAGLINE}\n\n"
            "Prototype mode — CV/OCR outputs are mocked for architecture validation."
        )
    },
)


# ── Global CSS ─────────────────────────────────────────────────────────────────
def _inject_global_css() -> None:
    st.markdown(
        """
        <style>
        /* ── Google Fonts fallback stack ── */
        html, body, [class*="css"] {
            font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
        }

        /* ── Global background / text ── */
        .stApp {
            background-color: #f8fafc;
            color: #111827;
        }

        /* ── Remove default Streamlit header padding ── */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 1280px;
        }

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e5e7eb;
            min-width: 220px !important;
        }
        section[data-testid="stSidebar"] .stButton button {
            background: transparent;
            border: 1px solid transparent;
            border-radius: 8px;
            color: #374151;
            font-size: 13px;
            font-weight: 500;
            padding: 8px 12px;
            text-align: left;
            width: 100%;
            transition: background 0.15s, color 0.15s;
        }
        section[data-testid="stSidebar"] .stButton button:hover {
            background: #f0fdf4;
            color: #166534;
            border-color: #bbf7d0;
        }

        /* ── Metrics ── */
        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 12px 14px;
        }
        [data-testid="stMetricValue"] {
            font-size: 24px !important;
            font-weight: 800 !important;
        }

        /* ── Inputs / Sliders ── */
        .stSlider [data-testid="stThumbValue"] {
            font-size: 11px;
        }
        div[data-baseweb="select"] {
            border-radius: 8px !important;
        }
        .stTextInput input, .stSelectbox select {
            border-radius: 8px;
            border-color: #d1d5db;
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            border-bottom: 2px solid #e5e7eb;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 6px 6px 0 0;
            font-size: 13px;
            font-weight: 600;
            padding: 8px 16px;
            color: #6b7280;
        }
        .stTabs [aria-selected="true"] {
            color: #166534 !important;
            border-bottom: 2px solid #16a34a !important;
            background: #f0fdf4 !important;
        }

        /* ── Buttons ── */
        .stButton button[kind="primary"] {
            background: #166534;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 13px;
            padding: 10px 20px;
            transition: background 0.15s;
        }
        .stButton button[kind="primary"]:hover {
            background: #14532d;
        }
        .stButton button[kind="secondary"] {
            border-radius: 8px;
            border-color: #d1d5db;
            font-size: 13px;
        }

        /* ── Toggle ── */
        .stToggle label {
            font-size: 12px;
        }

        /* ── File uploader ── */
        [data-testid="stFileUploader"] {
            border-radius: 8px;
        }

        /* ── Expander ── */
        .stExpander {
            border: 1px solid #e5e7eb !important;
            border-radius: 10px !important;
            background: #fff;
        }
        .stExpander summary {
            font-size: 13px;
            font-weight: 600;
            color: #374151;
        }

        /* ── Hide Streamlit branding ── */
        #MainMenu { visibility: hidden; }
        footer     { visibility: hidden; }
        header     { visibility: hidden; }

        /* ── Scrollbar ── */
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track  { background: #f1f5f9; }
        ::-webkit-scrollbar-thumb  { background: #cbd5e1; border-radius: 4px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Session state initialisation ──────────────────────────────────────────────
def _init_session_state() -> None:
    """Initialise top-level session state keys used across pages."""
    defaults: dict = {
        "current_page":    "Landing",
        "user_role":              None,
        "selected_recycler_id":   None,
        # Verification state
        "item_state":             "dismantled",
        "component":              "PCB",
        "component_confidence":   0.94,
        "material_plausibility":  0.90,
        "ocr_confidence":         0.92,
        "serial_uniqueness":      1.00,
        "facility_validity":      1.00,
        "gps_validity":           0.96,
        "image_quality":          0.88,
        "weight_consistency":     0.93,
        "completion_evidence":    True,
        "within_time_window":     True,
        "narration_hard_gate":    True,
        "batch_id":               "BATCH-2026-00124",
        "facility_name":          "GreenCycle Hyderabad",
        "serial":                 "SN-ECOTRACE-92831",
        "trust_score":            None,
        "trust_status":           None,
        "gate_passed":            None,
        "badge_decision":         None,
        "narration_result":       None,
        "score_result":           None,
        "gate_result":            None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ── Sidebar navigation ─────────────────────────────────────────────────────────
def _render_sidebar() -> None:
    role    = st.session_state.get("user_role")
    current = st.session_state.get("current_page", "Landing")

    with st.sidebar:
        # Brand
        portal_label = "Recycler Portal" if role == ROLE_RECYCLER else \
                       "Producer Portal" if role == ROLE_PRODUCER else \
                       "Select Portal"
        portal_color = "#166534" if role == ROLE_RECYCLER else \
                       "#1d4ed8" if role == ROLE_PRODUCER else "#374151"
        portal_icon  = "🔧" if role == ROLE_RECYCLER else \
                       "🏢" if role == ROLE_PRODUCER else "♻"

        st.markdown(
            f"""
            <div style="padding:8px 0 14px 0;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                    <div style="width:34px;height:34px;background:{portal_color};
                                border-radius:9px;display:flex;
                                align-items:center;justify-content:center;
                                flex-shrink:0;">
                        <span style="font-size:18px;line-height:1;">{portal_icon}</span>
                    </div>
                    <div>
                        <div style="font-size:15px;font-weight:800;color:#111827;
                                    letter-spacing:-0.3px;line-height:1.2;">
                            EcoTrace AI
                        </div>
                        <div style="font-size:10px;color:{portal_color};font-weight:700;
                                    line-height:1.3;">
                            {portal_label}
                        </div>
                    </div>
                </div>
            </div>
            <hr style="border:none;border-top:1px solid #e5e7eb;margin:0 0 10px 0;">
            """,
            unsafe_allow_html=True,
        )

        # Switch portal button (always visible if role is set)
        if role is not None:
            if st.button("⇄  Switch Portal", key="nav_switch", use_container_width=True, type="secondary"):
                st.session_state["user_role"]     = None
                st.session_state["current_page"]  = "Landing"
                st.rerun()
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # Nav items based on role
        if role == ROLE_RECYCLER:
            nav_items = [
                ("Dashboard",            "◫  Dashboard"),
                ("New Verification",     "＋  New Verification"),
                ("Verification History", "≡  Verification History"),
                ("Audit Dashboard",      "▦  Audit Dashboard"),
                ("System Architecture",  "⬡  System Architecture"),
            ]
        elif role == ROLE_PRODUCER:
            nav_items = [
                ("EPR Marketplace",       "🏪  EPR Marketplace"),
                ("Producer Dashboard",    "📊  My Compliance"),
                ("Recycler Profile",      "🔍  Recycler Profile"),
                ("System Architecture",   "⬡  System Architecture"),
            ]
        else:
            nav_items = []

        for page_key, page_label in nav_items:
            if st.button(
                page_label,
                key=f"nav_{page_key}",
                use_container_width=True,
                type="secondary",
            ):
                st.session_state["current_page"] = page_key
                st.rerun()

        # Prototype badge at bottom
        st.markdown(
            f"""
            <div style="position:fixed;bottom:16px;left:0;width:220px;
                        padding:0 16px;box-sizing:border-box;">
                <div style="background:#f8fafc;border:1px solid #e5e7eb;
                            border-radius:8px;padding:10px 12px;">
                    <div style="font-size:10px;font-weight:700;color:#6b7280;
                                letter-spacing:0.08em;text-transform:uppercase;
                                margin-bottom:5px;">Prototype Mode</div>
                    <div style="font-size:11px;color:#6b7280;line-height:1.8;">
                        <div>CV/OCR:
                            <span style="color:#d97706;font-weight:700;">MOCK</span>
                        </div>
                        <div>Data:
                            <span style="color:#d97706;font-weight:700;">SYNTHETIC</span>
                        </div>
                        <div>Version:
                            <span style="color:#9ca3af;">{APP_VERSION}</span>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Page router ────────────────────────────────────────────────────────────────
def _route_page(page: str) -> None:
    # ── Landing / Role selector ──────────────────────────────────────────────
    if page == "Landing" or st.session_state.get("user_role") is None:
        from pages.role_selector import render_role_selector
        render_role_selector()
        return

    role = st.session_state.get("user_role")

    # ── Recycler portal pages ────────────────────────────────────────────────
    if role == ROLE_RECYCLER:
        if page == "Dashboard":
            from pages.dashboard     import render_dashboard
            render_dashboard()
        elif page == "New Verification":
            from pages.verification  import render_verification
            render_verification()
        elif page == "Verification History":
            from pages.history       import render_history
            render_history()
        elif page == "Audit Dashboard":
            from pages.audit         import render_audit
            render_audit()
        elif page == "System Architecture":
            from pages.architecture  import render_architecture
            render_architecture()
        else:
            # Default fallback for recycler
            from pages.dashboard import render_dashboard
            render_dashboard()

    # ── Producer portal pages ────────────────────────────────────────────────
    elif role == ROLE_PRODUCER:
        if page == "EPR Marketplace":
            from pages.producer_marketplace import render_producer_marketplace
            render_producer_marketplace()
        elif page == "Producer Dashboard":
            from pages.producer_dashboard   import render_producer_dashboard
            render_producer_dashboard()
        elif page == "Recycler Profile":
            from pages.recycler_profile     import render_recycler_profile
            render_recycler_profile()
        elif page == "System Architecture":
            from pages.architecture         import render_architecture
            render_architecture()
        else:
            # Default fallback for producer
            from pages.producer_marketplace import render_producer_marketplace
            render_producer_marketplace()

    else:
        st.error(f"Unknown role or page: role='{role}', page='{page}'")


# ── Main ───────────────────────────────────────────────────────────────────────
def main() -> None:
    _inject_global_css()
    _init_session_state()
    _render_sidebar()

    current_page = st.session_state.get("current_page", "Landing")
    role         = st.session_state.get("user_role")

    # Prototype mode banner — only show inside portals, not on landing
    if role is not None:
        st.markdown(
            """
            <div style="background:#fef9c3;border:1px solid #fde68a;
                        border-radius:8px;padding:7px 14px;margin-bottom:16px;">
                <span style="font-size:12px;color:#92400e;">
                    <strong>Prototype Mode</strong> —
                    CV/OCR predictions are mocked for architecture validation.
                    All data is synthetic and does not represent real-world records.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    _route_page(current_page)


if __name__ == "__main__":
    main()
