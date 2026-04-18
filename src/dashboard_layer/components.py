from __future__ import annotations

import json

import plotly.graph_objects as go
import streamlit as st


STATE_COLORS = {
    "ok": "#18794e",
    "fallback": "#a15c00",
    "degraded": "#9f1239",
    "error_validacion": "#b42318",
    "sin_datos": "#475467",
    "loading": "#155eef",
}


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(229, 208, 172, 0.35), transparent 30%),
                radial-gradient(circle at top right, rgba(145, 179, 165, 0.18), transparent 24%),
                linear-gradient(180deg, #f6f2e8 0%, #efe8d6 100%);
            color: #1c1917;
        }
        .hero-shell {
            border: 1px solid rgba(66, 56, 38, 0.12);
            background: rgba(255, 252, 244, 0.9);
            border-radius: 24px;
            padding: 1.4rem 1.6rem;
            box-shadow: 0 20px 40px rgba(78, 65, 44, 0.08);
            margin-bottom: 1rem;
        }
        .hero-kicker {
            letter-spacing: 0.18em;
            text-transform: uppercase;
            font-size: 0.74rem;
            color: #7c5a2f;
            margin-bottom: 0.35rem;
        }
        .hero-title {
            font-family: Georgia, "Times New Roman", serif;
            font-size: 2.1rem;
            margin: 0;
            color: #1f2937;
        }
        .state-badge {
            display: inline-block;
            padding: 0.32rem 0.72rem;
            border-radius: 999px;
            color: white;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }
        .metric-tile {
            border-radius: 18px;
            padding: 0.95rem 1rem;
            background: rgba(255,255,255,0.76);
            border: 1px solid rgba(66,56,38,0.1);
            min-height: 108px;
        }
        .metric-label {
            color: #6b5b48;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1f2937;
            margin-top: 0.28rem;
        }
        .metric-note {
            color: #475467;
            font-size: 0.86rem;
            margin-top: 0.3rem;
        }
        .section-card {
            border-radius: 20px;
            padding: 1rem 1.1rem;
            background: rgba(255,255,255,0.8);
            border: 1px solid rgba(66,56,38,0.1);
            margin-bottom: 0.9rem;
        }
        .audit-box {
            background: #1f2937;
            color: #f9fafb;
            border-radius: 16px;
            padding: 0.9rem 1rem;
            font-family: Consolas, "Courier New", monospace;
            font-size: 0.86rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(result: dict | None) -> None:
    state = result["service_status"] if result else "sin_datos"
    color = STATE_COLORS.get(state, "#475467")
    title = "Engine Maintenance Command Deck"
    subtitle = "Traceable predictive maintenance decisions with deterministic scenario analysis."
    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-kicker">CMAPSS PHM Dashboard</div>
            <div style="display:flex;justify-content:space-between;gap:1rem;align-items:flex-start;">
                <div>
                    <h1 class="hero-title">{title}</h1>
                    <div style="margin-top:0.35rem;color:#57534e;">{subtitle}</div>
                </div>
                <div class="state-badge" style="background:{color};">{state}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_tile(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-tile">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def service_message(state: str) -> str:
    mapping = {
        "ok": "Primary flow executed cleanly.",
        "fallback": "Fallback logic is active; review technical audit before acting.",
        "degraded": "A degraded path was used; treat the output conservatively.",
        "error_validacion": "Request validation failed before a trustworthy decision could be made.",
        "sin_datos": "No usable result is available yet.",
        "loading": "The dashboard is waiting for a response.",
    }
    return mapping.get(state, "")


def decision_figure(result: dict) -> go.Figure:
    target = max(0.0, float(result.get("rul_pred") or 0.0))
    upper = float(result.get("confidence_band", {}).get("upper") or target)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=target,
            number={"suffix": " cycles"},
            title={"text": "Predicted RUL"},
            gauge={
                "axis": {"range": [0, max(150, upper + 10)]},
                "bar": {"color": "#7c5a2f"},
                "steps": [
                    {"range": [0, 20], "color": "#fca5a5"},
                    {"range": [20, 60], "color": "#fde68a"},
                    {"range": [60, max(150, upper + 10)], "color": "#bbf7d0"},
                ],
                "threshold": {"line": {"color": "#1f2937", "width": 4}, "value": target},
            },
        )
    )
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=60, b=30), paper_bgcolor="rgba(0,0,0,0)")
    return fig


def rul_interval_figure(result: dict) -> go.Figure:
    target = max(0.0, float(result.get("rul_pred") or 0.0))
    lower = float(result.get("confidence_band", {}).get("lower") or 0.0)
    upper = float(result.get("confidence_band", {}).get("upper") or target)
    axis_max = max(150.0, upper + 15.0)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[lower, upper],
            y=[0, 0],
            mode="lines",
            line={"width": 16, "color": "#d6b880"},
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[target],
            y=[0],
            mode="markers+text",
            marker={"size": 16, "color": "#7c5a2f", "line": {"width": 2, "color": "#1f2937"}},
            text=[f"{target:.1f}"],
            textposition="top center",
            showlegend=False,
            hovertemplate="Predicted RUL: %{x:.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[lower, upper],
            y=[0, 0],
            mode="markers+text",
            marker={"size": 9, "color": "#57534e"},
            text=[f"Low {lower:.1f}", f"High {upper:.1f}"],
            textposition=["bottom center", "bottom center"],
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.update_yaxes(visible=False, range=[-1, 1])
    fig.update_xaxes(
        range=[0, axis_max],
        title="Remaining useful life (cycles)",
        gridcolor="rgba(87,83,78,0.12)",
        zeroline=False,
    )
    fig.update_layout(
        height=180,
        margin=dict(l=20, r=20, t=20, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    return fig


def scenario_delta_figure(scenario_result: dict) -> go.Figure:
    comparison = scenario_result["comparison"]
    metrics = ["RUL", "Risk Score"]
    baseline_values = [comparison.get("baseline_rul"), comparison.get("baseline_risk_score")]
    scenario_values = [comparison.get("scenario_rul"), comparison.get("scenario_risk_score")]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Baseline",
            x=metrics,
            y=baseline_values,
            marker_color="#7c5a2f",
            text=[f"{v:.2f}" if v is not None else "n/a" for v in baseline_values],
            textposition="auto",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Scenario",
            x=metrics,
            y=scenario_values,
            marker_color="#0f766e",
            text=[f"{v:.2f}" if v is not None else "n/a" for v in scenario_values],
            textposition="auto",
        )
    )
    fig.update_layout(
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
        title="Baseline vs Scenario (RUL and Risk Score)",
        yaxis_title="Value",
        barmode="group",
    )
    return fig


def json_box(payload: dict) -> None:
    st.markdown('<div class="audit-box">', unsafe_allow_html=True)
    st.code(json.dumps(payload, indent=2), language="json")
    st.markdown("</div>", unsafe_allow_html=True)
