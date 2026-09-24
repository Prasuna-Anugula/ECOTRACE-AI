"""
EcoTrace AI — Role Selector / Landing Page
──────────────────────────────────────────
Portal entry point. User selects Recycler or Producer role.
NO display:flex / display:grid — all layout via st.columns() and <table>.
"""

from __future__ import annotations
import streamlit as st
from config import APP_NAME, APP_VERSION, ROLE_RECYCLER, ROLE_PRODUCER


def render_role_selector() -> None:
    # ── Hero header ───────────────────────────────────────────────────────────
    st.markdown(
        '<div style="text-align:center;padding:32px 0 8px 0;">'
        '<div style="font-size:32px;font-weight:900;color:#111827;letter-spacing:-0.5px;">'
        'EcoTrace AI</div>'
        '<div style="font-size:14px;color:#6b7280;margin-top:4px;">'
        'Evidence-based e-waste traceability &amp; EPR certificate marketplace'
        '</div>'
        '<div style="display:inline-block;background:#fef9c3;border:1px solid #fde68a;'
        'border-radius:6px;padding:4px 14px;margin-top:10px;'
        'font-size:11px;color:#92400e;">'
        'Prototype Mode &mdash; All CV/OCR outputs are mocked for architecture validation'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div style="text-align:center;font-size:15px;font-weight:700;'
        'color:#374151;margin-bottom:20px;">Select your portal to continue</div>',
        unsafe_allow_html=True,
    )

    # ── Two portal cards using st.columns ─────────────────────────────────────
    col1, spacer, col2 = st.columns([1, 0.06, 1])

    with col1:
        st.markdown(
            '<div style="background:#ffffff;border:2px solid #bbf7d0;'
            'border-radius:16px;padding:28px 24px;text-align:center;">'
            '<div style="font-size:40px;margin-bottom:12px;">&#128295;</div>'
            '<div style="font-size:18px;font-weight:800;color:#166534;margin-bottom:8px;">'
            'Recycler Portal</div>'
            '<div style="font-size:12px;color:#6b7280;line-height:1.7;margin-bottom:16px;">'
            'For registered e-waste recycling facilities.<br>'
            'Submit verifications, track processing evidence,<br>'
            'earn EPR credits, and manage your trust portfolio.'
            '</div>'
            '<div style="font-size:11px;color:#9ca3af;line-height:1.8;">'
            'New Verification &nbsp; &bull; &nbsp; Trust Score Engine<br>'
            'Processing Gate &nbsp; &bull; &nbsp; Audit Dashboard'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        if st.button(
            "Enter Recycler Portal",
            key="enter_recycler",
            use_container_width=True,
            type="primary",
        ):
            st.session_state["user_role"]    = ROLE_RECYCLER
            st.session_state["current_page"] = "Dashboard"
            st.rerun()

    with col2:
        st.markdown(
            '<div style="background:#ffffff;border:2px solid #bfdbfe;'
            'border-radius:16px;padding:28px 24px;text-align:center;">'
            '<div style="font-size:40px;margin-bottom:12px;">&#127970;</div>'
            '<div style="font-size:18px;font-weight:800;color:#1d4ed8;margin-bottom:8px;">'
            'Producer Portal</div>'
            '<div style="font-size:12px;color:#6b7280;line-height:1.7;margin-bottom:16px;">'
            'For electronics manufacturers with EPR obligations.<br>'
            'Search verified recyclers, compare trust scores,<br>'
            'buy EPR certificates with real audit trails.'
            '</div>'
            '<div style="font-size:11px;color:#9ca3af;line-height:1.8;">'
            'EPR Marketplace &nbsp; &bull; &nbsp; Recycler Profiles<br>'
            'Compliance Tracking &nbsp; &bull; &nbsp; Certificate Trail'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        if st.button(
            "Enter Producer Portal",
            key="enter_producer",
            use_container_width=True,
        ):
            st.session_state["user_role"]    = ROLE_PRODUCER
            st.session_state["current_page"] = "EPR Marketplace"
            st.rerun()

    # ── Why EcoTrace value props ───────────────────────────────────────────────
    st.markdown('<div style="height:32px"></div>', unsafe_allow_html=True)
    st.markdown(
        '<hr style="border:none;border-top:1px solid #e5e7eb;margin:0 0 24px 0;">'
        '<div style="text-align:center;font-size:12px;font-weight:700;'
        'color:#9ca3af;letter-spacing:0.08em;text-transform:uppercase;'
        'margin-bottom:16px;">Why EcoTrace</div>',
        unsafe_allow_html=True,
    )

    p1, p2, p3, p4 = st.columns(4)
    props = [
        ("&#128269;", "Item-Level Verification", "Every item verified through 12-stage pipeline"),
        ("&#9940;",   "Processing Gate",          "Separates intake proof from actual processing proof"),
        ("&#128202;", "Trust Marketplace",         "Objective recycler comparison with real metrics"),
        ("&#128279;", "Audit Trail",               "Blockchain-verifiable evidence for every certificate"),
    ]
    for col, (icon, title, desc) in zip([p1, p2, p3, p4], props):
        with col:
            st.markdown(
                f'<div style="text-align:center;padding:12px 8px;">'
                f'<div style="font-size:24px;margin-bottom:6px;">{icon}</div>'
                f'<div style="font-size:11px;font-weight:700;color:#374151;margin-bottom:4px;">'
                f'{title}</div>'
                f'<div style="font-size:10px;color:#9ca3af;line-height:1.5;">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        f'<div style="text-align:center;margin-top:24px;'
        f'font-size:10px;color:#d1d5db;">'
        f'{APP_NAME} {APP_VERSION} &nbsp;&middot;&nbsp; Prototype Mode'
        f'</div>',
        unsafe_allow_html=True,
    )
