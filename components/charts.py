"""
EcoTrace AI — Dashboard Charts Component
All charts use Plotly with the EcoTrace design palette.
Data is loaded from mock_facilities.json and mock_transactions.json.

NOTE: LAYOUT_DEFAULTS must NOT include showlegend — each chart sets it
explicitly to avoid the "multiple values for keyword argument" error in
Plotly 7.x when update_layout(**LAYOUT_DEFAULTS, showlegend=False) is called.
"""

from __future__ import annotations
import json
import os
import plotly.graph_objects as go
import streamlit as st


# ── Colour palette ────────────────────────────────────────────────────────────
GREEN  = "#16a34a"
AMBER  = "#d97706"
RED    = "#dc2626"
BLUE   = "#2563eb"

# showlegend is intentionally absent — set per chart
_BASE = dict(
    font_family="Inter, system-ui, sans-serif",
    font_color="#374151",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=36, b=0),
)


def _load_json(filename: str) -> list:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "data", filename)
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return []


# ── Chart 1: Badge issuance by facility ──────────────────────────────────────

def chart_badge_by_facility() -> go.Figure:
    facilities = _load_json("mock_facilities.json")
    names    = [f["name"].replace(" ", "<br>") for f in facilities]
    badges   = [f["badges_issued"]  for f in facilities]
    received = [f["items_received"] for f in facilities]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Items Received", x=names, y=received,
                         marker_color=BLUE, opacity=0.7))
    fig.add_trace(go.Bar(name="Badges Issued",  x=names, y=badges,
                         marker_color=GREEN))
    fig.update_layout(
        **_BASE,
        title="Badge Issuance by Facility",
        title_font_size=13,
        barmode="group",
        showlegend=True,
        legend=dict(orientation="h", y=-0.18),
        height=300,
        xaxis=dict(showgrid=False, tickfont_size=10),
        yaxis=dict(gridcolor="#f3f4f6", tickfont_size=10),
    )
    return fig


# ── Chart 2: Intake vs processing volume ─────────────────────────────────────

def chart_intake_vs_processing() -> go.Figure:
    facilities = _load_json("mock_facilities.json")
    names     = [f["name"] for f in facilities]
    received  = [f["items_received"]  for f in facilities]
    processed = [f["items_processed"] for f in facilities]

    fig = go.Figure()
    fig.add_trace(go.Scatter(name="Received",  x=names, y=received,
                             mode="lines+markers",
                             line=dict(color=BLUE, width=2),
                             marker=dict(size=7)))
    fig.add_trace(go.Scatter(name="Processed", x=names, y=processed,
                             mode="lines+markers",
                             line=dict(color=GREEN, width=2),
                             marker=dict(size=7)))
    fig.update_layout(
        **_BASE,
        title="Intake vs Processing Volume",
        title_font_size=13,
        showlegend=True,
        legend=dict(orientation="h", y=-0.22),
        height=280,
        xaxis=dict(showgrid=False, tickfont_size=10),
        yaxis=dict(gridcolor="#f3f4f6", tickfont_size=10),
    )
    return fig


# ── Chart 3: Trust Score distribution ────────────────────────────────────────

def chart_trust_score_distribution() -> go.Figure:
    txns   = _load_json("mock_transactions.json")
    scores = [t["trust_score"] for t in txns if t.get("trust_score") is not None]

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=scores,
        nbinsx=12,
        marker_color=BLUE,
        marker_line_color="white",
        marker_line_width=1,
        opacity=0.80,
        name="Trust Scores",
    ))

    # Plotly-7-safe threshold lines — pass annotation as a dict, not flat kwargs
    for x_val, label, colour in [
        (0.80, "Auto-verified ≥0.80", GREEN),
        (0.55, "HITL min ≥0.55",     AMBER),
    ]:
        fig.add_vline(
            x=x_val,
            line_dash="dash",
            line_color=colour,
            annotation=dict(text=label, font_size=10, font_color=colour),
        )

    fig.update_layout(
        **_BASE,
        title="Trust Score Distribution",
        title_font_size=13,
        showlegend=False,
        height=280,
        xaxis=dict(title="Score", showgrid=False, tickfont_size=10, range=[0, 1]),
        yaxis=dict(title="Count", gridcolor="#f3f4f6", tickfont_size=10),
    )
    return fig


# ── Chart 4: Processing completion failures ───────────────────────────────────

def chart_completion_failures() -> go.Figure:
    facilities = _load_json("mock_facilities.json")
    names    = [f["name"] for f in facilities]
    failures = [f["completion_failures"] for f in facilities]
    colours  = [RED if v > 30 else AMBER if v > 10 else GREEN for v in failures]

    fig = go.Figure(go.Bar(
        x=failures, y=names, orientation="h",
        marker_color=colours,
        text=failures, textposition="outside",
        textfont=dict(size=11),
    ))
    fig.update_layout(
        **_BASE,
        title="Processing Completion Failures by Facility",
        title_font_size=13,
        showlegend=False,
        height=260,
        xaxis=dict(showgrid=False, tickfont_size=10),
        yaxis=dict(showgrid=False, tickfont_size=10),
    )
    return fig


# ── Chart 5: Facility anomaly indicator ──────────────────────────────────────

def chart_anomaly_indicator() -> go.Figure:
    facilities = _load_json("mock_facilities.json")
    names    = [f["name"] for f in facilities]
    statuses = [f.get("anomaly_status", "NORMAL") for f in facilities]
    colours  = [GREEN if s == "NORMAL" else RED for s in statuses]

    fig = go.Figure(go.Bar(
        x=names, y=[1] * len(names),
        marker_color=colours,
        text=statuses,
        textposition="inside",
        textfont=dict(color="white", size=11),
    ))
    fig.update_layout(
        **_BASE,
        title="Facility Anomaly Status",
        title_font_size=13,
        showlegend=False,
        height=220,
        xaxis=dict(showgrid=False, tickfont_size=10),
        yaxis=dict(visible=False),
    )
    return fig
