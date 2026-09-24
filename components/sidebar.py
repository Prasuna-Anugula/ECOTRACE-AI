"""
EcoTrace AI — Sidebar Navigation Component
"""

import streamlit as st
from config import APP_NAME, APP_VERSION


def render_sidebar() -> str:
    """
    Render the sidebar navigation.
    Returns the selected page name as a string.
    """
    with st.sidebar:
        # ── Logo / brand ──────────────────────────────────────────────────
        st.markdown(
            """
            <div style="padding: 8px 0 20px 0;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
                    <div style="width:32px;height:32px;background:#166534;border-radius:8px;
                                display:flex;align-items:center;justify-content:center;">
                        <span style="color:#fff;font-size:16px;font-weight:700;">E</span>
                    </div>
                    <span style="font-size:18px;font-weight:700;color:#111827;
                                 letter-spacing:-0.3px;">EcoTrace AI</span>
                </div>
                <p style="font-size:11px;color:#6b7280;margin:0;padding-left:42px;
                           line-height:1.4;">Evidence-based e-waste traceability</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<hr style="border:none;border-top:1px solid #e5e7eb;margin:0 0 16px 0;">',
            unsafe_allow_html=True,
        )

        # ── Navigation items ──────────────────────────────────────────────
        pages = {
            "Dashboard":            ("dashboard",     "◫"),
            "New Verification":     ("verification",  "＋"),
            "Verification History": ("history",       "≡"),
            "Audit Dashboard":      ("audit",         "▦"),
            "System Architecture":  ("architecture",  "⬡"),
        }

        # Determine current page from session state
        current = st.session_state.get("current_page", "Dashboard")

        selected = None
        for label, (key, icon) in pages.items():
            is_active = (label == current)
            bg    = "#f0fdf4" if is_active else "transparent"
            color = "#166534" if is_active else "#374151"
            fw    = "600"     if is_active else "400"
            border= "1px solid #bbf7d0" if is_active else "1px solid transparent"

            clicked = st.button(
                f"{icon}  {label}",
                key=f"nav_{key}",
                use_container_width=True,
            )
            # Apply styling via markdown after each button
            st.markdown(
                f"""
                <style>
                div[data-testid="stButton"] button[kind="secondary"]
                    [data-testid="baseButton-secondary"] {{}}
                </style>
                """,
                unsafe_allow_html=True,
            )
            if clicked:
                selected = label

        # ── Prototype mode footer ─────────────────────────────────────────
        st.markdown("---")
        st.markdown(
            f"""
            <div style="font-size:11px;color:#9ca3af;line-height:1.8;">
                <div style="font-weight:600;color:#6b7280;margin-bottom:4px;">
                    PROTOTYPE MODE
                </div>
                <div>CV/OCR: <span style="color:#d97706;font-weight:600;">MOCK</span></div>
                <div>Data: <span style="color:#d97706;font-weight:600;">SYNTHETIC</span></div>
                <div>Version: <span style="color:#6b7280;">{APP_VERSION}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected if selected else current
