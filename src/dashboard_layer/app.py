from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from plotly.subplots import make_subplots

if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[2]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from src.dashboard_layer.backend_adapter import (
        RAW_REQUIRED_COLUMNS,
        build_payload_from_row,
        get_default_payload,
        load_agent_audit_tail,
        load_configured_analysis_dataset,
        load_contract_snapshot,
        load_model_comparison,
        load_predictive_feature_list,
        run_decision_flow,
        run_fleet_snapshot,
        run_scenario_flow,
        run_selected_unit_history,
        validate_uploaded_dataframe,
    )
    from src.dashboard_layer.components import (
        decision_figure,
        inject_styles,
        json_box,
        metric_tile,
        render_hero,
        rul_interval_figure,
        scenario_delta_figure,
        service_message,
    )
else:
    from .backend_adapter import (
        RAW_REQUIRED_COLUMNS,
        build_payload_from_row,
        get_default_payload,
        load_agent_audit_tail,
        load_configured_analysis_dataset,
        load_contract_snapshot,
        load_model_comparison,
        load_predictive_feature_list,
        run_decision_flow,
        run_fleet_snapshot,
        run_scenario_flow,
        run_selected_unit_history,
        validate_uploaded_dataframe,
    )
    from .components import (
        decision_figure,
        inject_styles,
        json_box,
        metric_tile,
        render_hero,
        rul_interval_figure,
        scenario_delta_figure,
        service_message,
    )


def init_state() -> None:
    if "payload" not in st.session_state:
        st.session_state.payload = get_default_payload()
    if "decision_result" not in st.session_state:
        st.session_state.decision_result = None
    if "scenario_result" not in st.session_state:
        st.session_state.scenario_result = None
    if "input_mode" not in st.session_state:
        st.session_state.input_mode = "Manual"
    if "uploaded_df" not in st.session_state:
        st.session_state.uploaded_df = None
    if "upload_context" not in st.session_state:
        st.session_state.upload_context = None
    if "decision_payload_signature" not in st.session_state:
        st.session_state.decision_payload_signature = None
    if "scenario_payload_signature" not in st.session_state:
        st.session_state.scenario_payload_signature = None
    if "configured_analysis_df" not in st.session_state:
        st.session_state.configured_analysis_df = load_configured_analysis_dataset()
    if "uploaded_filename" not in st.session_state:
        st.session_state.uploaded_filename = None
    if "scenario_prompt" not in st.session_state:
        st.session_state.scenario_prompt = "cycle +25; op_setting_1 = 0.6; sensor_11 -0.1"


def payload_signature(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True)


def numeric_suffix(name: str) -> int:
    return int(name.split("_")[-1])


def load_upload_into_payload(uploaded_file) -> tuple[dict | None, pd.DataFrame | None, str | None]:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as exc:
        return None, None, f"Could not read the uploaded CSV: {exc}"
    ok, missing = validate_uploaded_dataframe(df)
    if not ok:
        return None, None, f"Missing required columns: {', '.join(missing)}"
    df = df[RAW_REQUIRED_COLUMNS].copy().reset_index(drop=False).rename(columns={"index": "row_id"})
    return build_payload_from_row(df.iloc[0]), df, None


@st.cache_data(show_spinner=False)
def cached_selected_unit_history(uploaded_df: pd.DataFrame, dataset_id: str, unit_id: int) -> pd.DataFrame:
    return run_selected_unit_history(uploaded_df, dataset_id, unit_id)


@st.cache_data(show_spinner=False)
def cached_fleet_snapshot(uploaded_df: pd.DataFrame, dataset_id: str) -> pd.DataFrame:
    return run_fleet_snapshot(uploaded_df, dataset_id)


def row_label(row: pd.Series) -> str:
    return f"row {int(row['row_id'])} | {row['dataset_id']} / unit {int(row['unit_id'])} / cycle {int(row['cycle'])}"


def urgency_label(priority_code: str) -> str:
    mapping = {
        "P1": "Immediate action",
        "P2": "Plan maintenance soon",
        "P3": "Routine monitoring",
    }
    return mapping.get(priority_code, priority_code)


def risk_score_descriptor(risk_score: float | None) -> str:
    if risk_score is None:
        return "unavailable"
    if risk_score < 40:
        return "low"
    if risk_score < 70:
        return "moderate"
    return "high"


def build_summary_explanation(result: dict) -> str:
    descriptor = risk_score_descriptor(result.get("risk_score"))
    return (
        f"Condition is {result['risk_level']} because the current signal resolves to a {descriptor} risk score "
        f"under the frozen policy and the recommendation remains in `{result['service_status']}` service state."
    )


def build_analysis_explanation(result: dict) -> str:
    risk_score = result.get("risk_score")
    descriptor = risk_score_descriptor(risk_score)
    band = result.get("confidence_band") or {}
    lower = band.get("lower")
    upper = band.get("upper")
    uncertainty_text = "uncertainty is unavailable"
    if lower is not None and upper is not None:
        spread = float(upper) - float(lower)
        if spread < 20:
            uncertainty_text = "uncertainty is narrow"
        elif spread < 45:
            uncertainty_text = "uncertainty is moderate"
        else:
            uncertainty_text = "uncertainty is wide"
    score_text = "risk score is unavailable" if risk_score is None else f"risk score is {float(risk_score):.1f}"
    return (
        f"Predicted RUL is {result['rul_pred']:.2f} cycles, {uncertainty_text}, and the resulting "
        f"{score_text} resolves to a {result['risk_level']} condition under the deterministic policy."
    )


def build_summary_history(payload: dict, history_limit: int = 8) -> pd.DataFrame:
    uploaded_df = st.session_state.uploaded_df
    configured_df = st.session_state.configured_analysis_df

    # In File Upload mode, the trend should reflect the uploaded unit history,
    # not just the prefix up to the selected row's cycle.
    if st.session_state.input_mode == "File Upload" and uploaded_df is not None:
        selected_history = cached_selected_unit_history(uploaded_df, payload["dataset_id"], int(payload["unit_id"]))
        if not selected_history.empty:
            recent = selected_history.sort_values("cycle").tail(history_limit).copy()
            if not recent.empty:
                recent["trend_source"] = "uploaded_history"
                return recent

    analysis_df = configured_df
    if analysis_df is not None:
        selected_history = cached_selected_unit_history(analysis_df, payload["dataset_id"], int(payload["unit_id"]))
        if not selected_history.empty:
            recent = selected_history[selected_history["cycle"] <= int(payload["cycle"])].sort_values("cycle").tail(history_limit).copy()
            if not recent.empty:
                recent["trend_source"] = "configured_history"
                return recent
    return pd.DataFrame()


def trend_interpretation(history: pd.DataFrame) -> str:
    if len(history) < 2:
        return "insufficient history"
    cycle_delta = float(history["cycle"].iloc[-1] - history["cycle"].iloc[0])
    if cycle_delta <= 0:
        return "stable"
    rul_delta = float(history["rul_pred"].iloc[-1] - history["rul_pred"].iloc[0])
    slope = rul_delta / cycle_delta
    if slope <= -1.2:
        return "rapidly declining"
    if slope <= -0.4:
        return "declining"
    return "stable"


def temporal_interpretation(history: pd.DataFrame) -> str:
    status = trend_interpretation(history)
    mapping = {
        "rapidly declining": "Rapid degradation: predicted RUL is dropping quickly across recent cycles.",
        "declining": "Gradual degradation: predicted RUL is trending downward over time.",
        "stable": "Stable behavior: predicted RUL is changing slowly across the recent history.",
        "insufficient history": "Insufficient history: more same-unit cycles are needed to interpret temporal behavior.",
    }
    return mapping.get(status, status)


def sidebar_payload_editor() -> dict:
    payload = json.loads(json.dumps(st.session_state.payload))
    with st.sidebar:
        st.markdown("### Request Console")
        st.session_state.input_mode = st.radio(
            "Input Mode",
            options=["Manual", "File Upload"],
            index=0 if st.session_state.input_mode == "Manual" else 1,
            horizontal=True,
        )

        if st.session_state.input_mode == "File Upload":
            uploaded_file = st.file_uploader("Upload engine monitoring CSV", type=["csv"], key="uploaded_csv_file")
            if uploaded_file is not None:
                loaded_payload, uploaded_df, error = load_upload_into_payload(uploaded_file)
                if error:
                    st.error(error)
                else:
                    st.session_state.uploaded_df = uploaded_df
                    st.session_state.uploaded_filename = uploaded_file.name
                    previous_context = st.session_state.upload_context or {}
                    default_row_id = int(previous_context.get("row_id", int(uploaded_df.iloc[0]["row_id"])))
                    if default_row_id not in uploaded_df["row_id"].astype(int).tolist():
                        default_row_id = int(uploaded_df.iloc[0]["row_id"])
                    row_options = uploaded_df["row_id"].astype(int).tolist()
                    selected_row_id = st.selectbox(
                        "Selected Uploaded Row",
                        options=row_options,
                        index=row_options.index(default_row_id),
                        format_func=lambda rid: row_label(uploaded_df.loc[uploaded_df["row_id"].astype(int) == int(rid)].iloc[0]),
                    )
                    selected_row = uploaded_df.loc[uploaded_df["row_id"].astype(int) == int(selected_row_id)].iloc[0]
                    payload = build_payload_from_row(selected_row)
                    payload["source"] = "dashboard.upload"
                    st.session_state.upload_context = {
                        "dataset_id": str(selected_row["dataset_id"]),
                        "unit_id": int(selected_row["unit_id"]),
                        "cycle": int(selected_row["cycle"]),
                        "row_id": int(selected_row_id),
                    }
                    st.caption(f"Loaded {len(uploaded_df)} rows from `{uploaded_file.name}`. The selected row is the source of truth for the uploaded record.")
                    derived_df = pd.DataFrame(
                        [
                            {"field": "dataset_id", "value": str(selected_row["dataset_id"])},
                            {"field": "unit_id", "value": int(selected_row["unit_id"])},
                            {"field": "cycle", "value": int(selected_row["cycle"])},
                        ]
                    )
                    st.dataframe(derived_df, use_container_width=True, hide_index=True)
                    if st.button("Load Selected Row Into Manual Mode", use_container_width=True):
                        manual_payload = build_payload_from_row(selected_row, source="dashboard.manual.from_upload")
                        st.session_state.payload = manual_payload
                        st.session_state.input_mode = "Manual"
                        st.session_state.scenario_result = None
                        st.rerun()
                    with st.expander("Uploaded Record Preview", expanded=False):
                        st.dataframe(pd.DataFrame([selected_row]).drop(columns=["row_id"]), use_container_width=True, hide_index=True)
            elif st.session_state.uploaded_df is not None:
                uploaded_df = st.session_state.uploaded_df
                previous_context = st.session_state.upload_context or {}
                default_row_id = int(previous_context.get("row_id", int(uploaded_df.iloc[0]["row_id"])))
                if default_row_id not in uploaded_df["row_id"].astype(int).tolist():
                    default_row_id = int(uploaded_df.iloc[0]["row_id"])
                row_options = uploaded_df["row_id"].astype(int).tolist()
                selected_row_id = st.selectbox(
                    "Selected Uploaded Row",
                    options=row_options,
                    index=row_options.index(default_row_id),
                    format_func=lambda rid: row_label(uploaded_df.loc[uploaded_df["row_id"].astype(int) == int(rid)].iloc[0]),
                )
                selected_row = uploaded_df.loc[uploaded_df["row_id"].astype(int) == int(selected_row_id)].iloc[0]
                payload = build_payload_from_row(selected_row)
                payload["source"] = "dashboard.upload"
                st.session_state.upload_context = {
                    "dataset_id": str(selected_row["dataset_id"]),
                    "unit_id": int(selected_row["unit_id"]),
                    "cycle": int(selected_row["cycle"]),
                    "row_id": int(selected_row_id),
                }
                filename = st.session_state.uploaded_filename or "uploaded CSV"
                st.caption(f"Using cached rows from `{filename}`. The selected row is the source of truth for the uploaded record.")
                derived_df = pd.DataFrame(
                    [
                        {"field": "dataset_id", "value": str(selected_row["dataset_id"])},
                        {"field": "unit_id", "value": int(selected_row["unit_id"])},
                        {"field": "cycle", "value": int(selected_row["cycle"])},
                    ]
                )
                st.dataframe(derived_df, use_container_width=True, hide_index=True)
                if st.button("Load Selected Row Into Manual Mode", use_container_width=True):
                    manual_payload = build_payload_from_row(selected_row, source="dashboard.manual.from_upload")
                    st.session_state.payload = manual_payload
                    st.session_state.input_mode = "Manual"
                    st.session_state.scenario_result = None
                    st.rerun()
                with st.expander("Uploaded Record Preview", expanded=False):
                    st.dataframe(pd.DataFrame([selected_row]).drop(columns=["row_id"]), use_container_width=True, hide_index=True)
            else:
                st.info("Upload a CSV with dataset, unit, cycle, 3 operating settings, and 21 sensor columns.")
        else:
            payload["dataset_id"] = st.selectbox("Dataset", options=["FD001", "FD002", "FD003", "FD004"], index=["FD001", "FD002", "FD003", "FD004"].index(payload["dataset_id"]))
            payload["unit_id"] = int(st.number_input("Unit ID", min_value=1, value=int(payload["unit_id"]), step=1))
            payload["cycle"] = int(st.number_input("Cycle", min_value=1, value=int(payload["cycle"]), step=1))
            payload["source"] = st.text_input("Source", value=payload.get("source", "dashboard.manual"))
            if st.session_state.uploaded_df is not None and st.session_state.upload_context is not None:
                st.caption(
                    "Manual editing is using values prefilled from the selected uploaded row. "
                    "The uploaded CSV remains available if you switch back to File Upload mode."
                )

            with st.expander("Operating Settings", expanded=True):
                for key in sorted(payload["op_settings"].keys(), key=numeric_suffix):
                    payload["op_settings"][key] = float(st.number_input(key, value=float(payload["op_settings"][key]), format="%.4f", key=f"manual_{key}"))

            with st.expander("Health-Sensitive Sensors", expanded=True):
                sensor_keys = sorted(payload["sensors"].keys(), key=numeric_suffix)
                first_col, second_col = st.columns(2)
                for idx, key in enumerate(sensor_keys):
                    column = first_col if idx % 2 == 0 else second_col
                    with column:
                        payload["sensors"][key] = float(st.number_input(key, value=float(payload["sensors"][key]), format="%.4f", key=f"sensor_{key}"))

        st.caption("Manual mode exposes all 3 operating settings and all 21 sensor inputs in numeric order.")

        if st.button("Decision", use_container_width=True, type="primary"):
            st.session_state.payload = payload
            st.session_state.decision_result = run_decision_flow(payload)
            st.session_state.decision_payload_signature = payload_signature(payload)
            st.rerun()

        if st.button("Reset Sample", use_container_width=True):
            st.session_state.payload = get_default_payload()
            st.session_state.decision_result = None
            st.session_state.scenario_result = None
            st.session_state.decision_payload_signature = None
            st.session_state.scenario_payload_signature = None
            st.session_state.upload_context = None
            st.session_state.uploaded_df = None
            st.session_state.uploaded_filename = None
            st.rerun()

    st.session_state.payload = payload
    return payload


def summary_tab(result: dict | None, payload: dict) -> None:
    if not result:
        st.info("Run a decision or scenario from the left panel to populate the dashboard.")
        return
    summary_history = build_summary_history(payload)
    trend_status = trend_interpretation(summary_history)
    urgency = urgency_label(result["recommendation_priority"])
    explanation = build_summary_explanation(result)

    hero_left, hero_right = st.columns([1.15, 0.85])
    with hero_left:
        st.markdown("#### RUL Estimate")
        primary_cols = st.columns([1.1, 0.9])
        with primary_cols[0]:
            metric_tile(
                "Predicted RUL",
                f"{result['rul_pred']:.2f}" if result["rul_pred"] is not None else "n/a",
                "Estimated remaining useful life in cycles",
            )
        with primary_cols[1]:
            metric_tile(
                "Risk Level",
                result["risk_level"].upper(),
                "Primary condition status for immediate interpretation",
            )
        st.plotly_chart(decision_figure(result), use_container_width=True)
        st.caption("See Analysis for confidence bounds and detailed uncertainty diagnostics.")

    with hero_right:
        st.markdown("#### Decision Meaning")
        metric_cols = st.columns(2)
        with metric_cols[0]:
            metric_tile("Urgency", urgency, "Plain-language action urgency derived from the recommendation policy")
        with metric_cols[1]:
            metric_tile("State", result["service_status"], service_message(result["service_status"]))

        st.caption("Risk Level describes condition severity. Urgency expresses how quickly the operator should act.")
        st.markdown("##### Condition Summary")
        st.write(explanation)
        st.markdown("##### Immediate Action")
        st.write(result["recommendation_text"])
        st.markdown("##### Rationale")
        st.write(f"{result['rationale']} Current urgency is **{urgency.lower()}**.")
        if result.get("safety_notes"):
            st.warning(" ".join(result["safety_notes"]))

    st.markdown("---")
    trend_col, context_col = st.columns([1.1, 0.9])
    with trend_col:
        st.markdown("#### Recent RUL Evolution")
        if len(summary_history) < 2:
            st.info("Insufficient history for this unit to show a recent RUL trend.")
        else:
            trend_fig = px.line(
                summary_history,
                x="cycle",
                y="rul_pred",
                markers=True,
                title="Recent RUL Trend",
            )
            trend_fig.update_traces(line_color="#7c5a2f", marker_color="#1f2937")
            trend_fig.update_layout(height=320, margin=dict(l=20, r=20, t=60, b=20), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(trend_fig, use_container_width=True)
            st.caption("Trend uses recent predictions from the same unit, ordered by cycle.")

    with context_col:
        st.markdown("#### Decision Context")
        context_df = pd.DataFrame(
            [
                {"signal": "Active request", "value": f"{payload['dataset_id']} / unit {payload['unit_id']} / cycle {payload['cycle']}"},
                {"signal": "Condition", "value": result["risk_level"]},
                {"signal": "Urgency", "value": urgency},
                {"signal": "Recent trend", "value": trend_status},
                {"signal": "Recommendation", "value": result["recommendation_text"]},
            ]
        )
        st.dataframe(context_df, use_container_width=True, hide_index=True)


def analysis_tab(result: dict | None) -> None:
    if not result:
        st.info("No decision result is available yet.")
        return
    payload = st.session_state.payload
    uploaded_df = st.session_state.uploaded_df
    configured_df = st.session_state.configured_analysis_df
    model_comparison = load_model_comparison()
    selected_features = load_predictive_feature_list()
    analysis_df = uploaded_df if uploaded_df is not None else configured_df
    analysis_source = "uploaded CSV" if uploaded_df is not None else ("configured dataset" if configured_df is not None else None)
    band = result["confidence_band"] or {"lower": None, "upper": None, "method": "unavailable"}

    selected_history = pd.DataFrame()
    if analysis_df is not None:
        selected_history = cached_selected_unit_history(analysis_df, payload["dataset_id"], int(payload["unit_id"]))

    st.markdown("#### Model Explanation")
    explanation_left, explanation_right = st.columns([1.15, 0.85])
    with explanation_left:
        explanation_metrics = st.columns(2)
        with explanation_metrics[0]:
            metric_tile(
                "Predicted RUL",
                f"{result['rul_pred']:.2f}" if result["rul_pred"] is not None else "n/a",
                "Reference estimate used by the deterministic policy",
            )
        with explanation_metrics[1]:
            band_text = "n/a" if band["lower"] is None else f"{band['lower']:.1f}-{band['upper']:.1f} cycles"
            metric_tile("RUL Interval", band_text, "Calibrated confidence band for the current prediction")
        st.plotly_chart(rul_interval_figure(result), use_container_width=True)
        st.caption("The interval summarizes uncertainty around the point estimate. Wider bands can increase the final risk score.")
    with explanation_right:
        explanation_tiles = st.columns(2)
        with explanation_tiles[0]:
            metric_tile(
                "Risk Score",
                "n/a" if result["risk_score"] is None else f"{result['risk_score']:.2f}",
                "Composite score derived from predicted life, uncertainty, and service-state adjustments",
            )
        with explanation_tiles[1]:
            metric_tile(
                "Risk Level",
                result["risk_level"].upper(),
                "Severity label resolved from the risk policy",
            )
        st.markdown("##### Why this risk level")
        st.write(
            "Risk Score combines predicted RUL, interval width, and any service-state penalty. "
            "Lower predicted life pushes risk upward, and wider uncertainty bands increase caution."
        )
        st.markdown("##### Interpretation")
        st.write(build_analysis_explanation(result))
        st.markdown("##### Recommendation context")
        st.write(result["recommendation_text"])
        if result.get("recommendation_alternatives"):
            st.caption("Secondary response options:")
            for item in result["recommendation_alternatives"]:
                st.write(f"- {item}")

    st.markdown("---")
    st.markdown("#### Temporal Behavior")
    if selected_history.empty:
        st.info("No engine-history dataset is available for the active request, so temporal interpretation cannot be built yet.")
    elif len(selected_history) < 2:
        st.info("Insufficient history for this unit to show temporal behavior.")
    else:
        st.caption(f"Historical scoring view for the selected engine from the {analysis_source}.")
        temporal_left, temporal_right = st.columns([1.2, 0.8])
        history_plot_df = selected_history.sort_values("cycle").copy()
        with temporal_left:
            history_fig = px.line(
                history_plot_df,
                x="cycle",
                y="rul_pred",
                markers=True,
                title="Predicted RUL vs Cycle",
            )
            history_fig.update_traces(line_color="#7c5a2f", marker_color="#1f2937")
            if {"confidence_lower", "confidence_upper"}.issubset(history_plot_df.columns):
                history_fig.add_scatter(
                    x=history_plot_df["cycle"],
                    y=history_plot_df["confidence_upper"],
                    mode="lines",
                    line={"width": 0},
                    showlegend=False,
                    hoverinfo="skip",
                )
                history_fig.add_scatter(
                    x=history_plot_df["cycle"],
                    y=history_plot_df["confidence_lower"],
                    mode="lines",
                    line={"width": 0},
                    fill="tonexty",
                    fillcolor="rgba(214, 184, 128, 0.18)",
                    name="Confidence band",
                )
            history_fig.update_layout(height=380, margin=dict(l=20, r=20, t=60, b=20), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(history_fig, use_container_width=True)
        with temporal_right:
            history_metrics = pd.DataFrame(
                [
                    {"signal": "Cycles scored", "value": int(history_plot_df["cycle"].nunique())},
                    {"signal": "Latest predicted RUL", "value": round(float(history_plot_df.iloc[-1]["rul_pred"]), 3)},
                    {"signal": "Min predicted RUL", "value": round(float(history_plot_df["rul_pred"].min()), 3)},
                    {"signal": "Max predicted RUL", "value": round(float(history_plot_df["rul_pred"].max()), 3)},
                    {"signal": "Trend interpretation", "value": trend_interpretation(history_plot_df)},
                ]
            )
            st.dataframe(history_metrics, use_container_width=True, hide_index=True)
            st.markdown("##### How to read it")
            st.write(temporal_interpretation(history_plot_df))
            st.caption("The line is recomputed from the same unit history. The shaded area shows the confidence interval over time when available.")

    if analysis_df is None:
        st.markdown("---")
        st.markdown("#### Fleet Context")
        st.info("Fleet analysis is hidden because no uploaded CSV or configured dashboard dataset is available.")
    else:
        fleet_snapshot = cached_fleet_snapshot(analysis_df, payload["dataset_id"])
        dataset_df = analysis_df[analysis_df["dataset_id"].astype(str) == str(payload["dataset_id"])].copy()
        st.markdown("---")
        st.markdown("#### Fleet Context")
        st.caption(f"Contextual view across the active dataset from the {analysis_source}.")

        if fleet_snapshot.empty:
            st.info("No fleet snapshot could be derived for the active dataset.")
        else:
            top_n = min(10, max(3, len(fleet_snapshot)))
            current_unit_mask = fleet_snapshot["unit_id"].astype(int) == int(payload["unit_id"])
            current_unit_row = fleet_snapshot.loc[current_unit_mask].head(1)
            current_rank = None
            if not current_unit_row.empty:
                ranked_full = fleet_snapshot.sort_values(["risk_score", "rul_pred"], ascending=[False, True]).reset_index(drop=True)
                rank_matches = ranked_full.index[ranked_full["unit_id"].astype(int) == int(payload["unit_id"])].tolist()
                if rank_matches:
                    current_rank = int(rank_matches[0]) + 1

            overview_cols = st.columns(4)
            with overview_cols[0]:
                metric_tile("Units Scored", str(len(fleet_snapshot)), "One latest-cycle record per unit")
            with overview_cols[1]:
                metric_tile("Lowest RUL", f"{fleet_snapshot['rul_pred'].min():.2f}", "Lowest predicted remaining useful life in the fleet")
            with overview_cols[2]:
                metric_tile("Highest Risk", f"{fleet_snapshot['risk_score'].max():.2f}", "Highest composite risk score across units")
            with overview_cols[3]:
                rank_value = "n/a" if current_rank is None else f"{current_rank} / {len(fleet_snapshot)}"
                metric_tile("Current Unit Rank", rank_value, "Relative position after sorting by highest risk then lowest RUL")

            fleet_left, fleet_right = st.columns(2)
            ranked_units = fleet_snapshot.sort_values(["risk_score", "rul_pred"], ascending=[False, True]).head(top_n)
            with fleet_left:
                top_fig = px.bar(
                    ranked_units,
                    x="unit_id",
                    y="risk_score",
                    color="risk_level",
                    title="Highest-Risk Units in Fleet",
                    text="rul_pred",
                    color_discrete_map={"critical": "#b42318", "warning": "#f79009", "healthy": "#18794e", "unknown": "#667085"},
                )
                top_fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
                top_fig.update_layout(height=360, margin=dict(l=20, r=20, t=60, b=20), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(top_fig, use_container_width=True)
            with fleet_right:
                risk_counts = fleet_snapshot["risk_level"].value_counts().rename_axis("risk_level").reset_index(name="count")
                risk_fig = px.bar(
                    risk_counts,
                    x="risk_level",
                    y="count",
                    color="risk_level",
                    title="Risk Distribution Across Fleet",
                    color_discrete_map={"critical": "#b42318", "warning": "#f79009", "healthy": "#18794e", "unknown": "#667085"},
                )
                risk_fig.update_layout(height=360, margin=dict(l=20, r=20, t=60, b=20), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(risk_fig, use_container_width=True)

            if not current_unit_row.empty:
                current_unit_summary = current_unit_row.iloc[0]
                st.caption(
                    f"Current unit position: rank {current_rank} of {len(fleet_snapshot)} by risk ordering, "
                    f"latest predicted RUL {float(current_unit_summary['rul_pred']):.2f} cycles, "
                    f"risk level {current_unit_summary['risk_level']}."
                )

            fleet_table = ranked_units[["unit_id", "last_cycle", "rul_pred", "risk_level", "risk_score", "service_status"]].copy()
            fleet_table.rename(
                columns={
                    "unit_id": "unit",
                    "last_cycle": "last cycle",
                    "rul_pred": "predicted RUL",
                    "risk_level": "risk level",
                    "risk_score": "risk score",
                    "service_status": "state",
                },
                inplace=True,
            )
            st.dataframe(fleet_table, use_container_width=True, hide_index=True)

            extra_left, extra_right = st.columns(2)
            with extra_left:
                rul_hist = px.histogram(
                    fleet_snapshot,
                    x="rul_pred",
                    nbins=min(20, max(5, len(fleet_snapshot))),
                    title="RUL Distribution Across Fleet",
                )
                rul_hist.update_layout(height=320, margin=dict(l=20, r=20, t=60, b=20), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(rul_hist, use_container_width=True)
            with extra_right:
                scatter_fig = px.scatter(
                    fleet_snapshot,
                    x="last_cycle",
                    y="rul_pred",
                    color="risk_level",
                    size="risk_score",
                    hover_data=["unit_id", "service_status"],
                    title="Last Cycle vs Predicted RUL",
                    color_discrete_map={"critical": "#b42318", "warning": "#f79009", "healthy": "#18794e", "unknown": "#667085"},
                )
                scatter_fig.update_layout(height=320, margin=dict(l=20, r=20, t=60, b=20), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(scatter_fig, use_container_width=True)

            if not dataset_df.empty:
                trend_left, trend_right = st.columns(2)
                with trend_left:
                    cycle_dist = px.histogram(
                        dataset_df,
                        x="cycle",
                        nbins=min(24, max(6, dataset_df["cycle"].nunique())),
                        title="Cycle Distribution (Dataset)",
                    )
                    cycle_dist.update_layout(height=320, margin=dict(l=20, r=20, t=60, b=20), paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(cycle_dist, use_container_width=True)
                with trend_right:
                    setting_columns = ["op_setting_1", "op_setting_2", "op_setting_3"]
                    op_box = make_subplots(
                        rows=len(setting_columns),
                        cols=1,
                        shared_xaxes=False,
                        vertical_spacing=0.08,
                        subplot_titles=setting_columns,
                    )
                    setting_colors = {
                        "op_setting_1": "#2563eb",
                        "op_setting_2": "#0ea5e9",
                        "op_setting_3": "#ef4444",
                    }
                    for row_index, setting in enumerate(setting_columns, start=1):
                        op_box.add_box(
                            y=dataset_df[setting],
                            name=setting,
                            marker_color=setting_colors[setting],
                            boxmean=True,
                            row=row_index,
                            col=1,
                        )
                        op_box.update_yaxes(title_text="value", row=row_index, col=1)
                    op_box.update_xaxes(showticklabels=False)
                    op_box.update_layout(
                        title="Operational Settings Distribution",
                        height=520,
                        margin=dict(l=20, r=20, t=90, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(255,255,255,0.55)",
                        showlegend=False,
                    )
                    st.plotly_chart(op_box, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Technical Diagnostics")
    detail_df = pd.DataFrame(
        [
            {"metric": "dataset_id", "value": payload["dataset_id"]},
            {"metric": "unit_id", "value": payload["unit_id"]},
            {"metric": "cycle", "value": payload["cycle"]},
            {"metric": "rul_pred", "value": result["rul_pred"]},
            {"metric": "risk_level", "value": result["risk_level"]},
            {"metric": "urgency", "value": urgency_label(result["recommendation_priority"])},
            {"metric": "service_status", "value": result["service_status"]},
            {"metric": "feature_count_used", "value": len(selected_features)},
        ]
    )
    with st.expander("Decision Breakdown", expanded=False):
        st.dataframe(detail_df, use_container_width=True, hide_index=True)
    with st.expander("Feature Boundary", expanded=False):
        st.caption("The dashboard captures the full raw schema and trims to the predictive feature subset at inference time.")
        st.code(", ".join(selected_features), language="text")
    with st.expander("Model Context", expanded=False):
        st.dataframe(
            model_comparison[["model_name", "rmse", "mae", "stability_score", "ms_per_sample", "model_type", "highlight"]],
            use_container_width=True,
            hide_index=True,
        )
    with st.expander("Traceability", expanded=False):
        st.json(result["trace"])
    with st.expander("Detailed Per-Cycle Table", expanded=False):
        if selected_history.empty:
            st.info("No per-cycle history is available for the active request.")
        else:
            st.dataframe(
                selected_history.sort_values("cycle", ascending=False),
                use_container_width=True,
                hide_index=True,
            )


def scenarios_tab(scenario_result: dict | None) -> None:
    payload = st.session_state.payload
    current_signature = payload_signature(payload)
    st.markdown("#### Describe Scenario (What-If)")
    scenario_prompt = st.text_area(
        "Scenario input",
        value=st.session_state.scenario_prompt,
        height=110,
        help="Describe intended edits using instructions such as `increase cycle by 25`, `set op_setting_1 to 0.6`, `sensor_11 -0.1`, or `apply high load profile`.",
        label_visibility="collapsed",
    )
    st.session_state.scenario_prompt = scenario_prompt

    if st.button("Run Scenario Analysis", type="primary"):
        st.session_state.scenario_result = run_scenario_flow(payload, scenario_prompt)
        st.session_state.decision_result = st.session_state.scenario_result["baseline"]
        st.session_state.scenario_payload_signature = current_signature
        st.session_state.decision_payload_signature = current_signature
        st.rerun()

    if scenario_result and st.session_state.scenario_payload_signature != current_signature:
        st.warning("The request changed after the last scenario run. Run Scenario Analysis again to refresh this tab.")
    if not scenario_result:
        st.info("Describe a what-if scenario and run it from this tab to compare baseline and modified conditions for the active request.")
        return
    if scenario_result.get("validation_errors"):
        st.error("Scenario request could not be executed.")
        for item in scenario_result["validation_errors"]:
            st.write(f"- {item}")

    st.markdown("#### Parsing Transparency")
    transparency_cols = st.columns(3)
    with transparency_cols[0]:
        metric_tile("Parsing Mode", scenario_result.get("parsing_mode", "unknown"), "Deterministic first, LLM only on parse fallback")
    with transparency_cols[1]:
        metric_tile("LLM Used", "true" if scenario_result.get("llm_used") else "false", "Whether an LLM contributed to parsing or explanation")
    with transparency_cols[2]:
        metric_tile("Assistant Mode", scenario_result.get("assistant_mode", "unknown"), "Audit contract value for the scenario assistant")
    st.caption(f"Original input: `{scenario_result.get('input_text', '')}`")
    parsed_changes_df = pd.DataFrame(scenario_result.get("parsed_changes", {}).get("changes", []))
    if not parsed_changes_df.empty:
        st.dataframe(parsed_changes_df[["field", "op", "value"]], use_container_width=True, hide_index=True)
    else:
        st.caption("No parsed changes are available.")

    st.markdown("#### Change Summary")
    if scenario_result["change_summary"]:
        for item in scenario_result["change_summary"]:
            st.write(f"- {item}")
    else:
        st.caption("No validated changes were applied.")

    info_left, info_right = st.columns(2)
    with info_left:
        st.markdown("#### Assumptions")
        for item in scenario_result["assumptions"]:
            st.write(f"- {item}")
    with info_right:
        st.markdown("#### Safety Notes")
        for item in scenario_result["safety_notes"]:
            st.write(f"- {item}")

    st.markdown("#### Baseline vs Scenario Comparison")
    st.plotly_chart(scenario_delta_figure(scenario_result), use_container_width=True)

    comparison = scenario_result["comparison"]
    delta_cols = st.columns(2)
    with delta_cols[0]:
        metric_tile(
            "Delta RUL",
            "n/a" if comparison.get("delta_rul") is None else f"{comparison['delta_rul']:+.2f}",
            "Scenario RUL minus baseline RUL",
        )
    with delta_cols[1]:
        metric_tile(
            "Delta Risk Score",
            "n/a" if comparison.get("delta_risk_score") is None else f"{comparison['delta_risk_score']:+.2f}",
            "Scenario risk score minus baseline risk score",
        )

    baseline_vs_scenario = pd.DataFrame(
        [
            {"metric": "Predicted RUL", "baseline": comparison.get("baseline_rul"), "scenario": comparison.get("scenario_rul")},
            {"metric": "Risk Score", "baseline": comparison.get("baseline_risk_score"), "scenario": comparison.get("scenario_risk_score")},
            {"metric": "Risk Level", "baseline": comparison.get("baseline_risk_level"), "scenario": comparison.get("scenario_risk_level")},
        ]
    )
    st.dataframe(baseline_vs_scenario, use_container_width=True, hide_index=True)

    st.markdown("#### Interpretation")
    st.write(scenario_result["comparison_interpretation"])
    st.write(scenario_result["operator_guidance"])
    st.caption(
        f"Mode: {scenario_result['assistant_mode']}"
        + (f" | Model: {scenario_result['llm_model_used']}" if scenario_result.get("llm_model_used") else "")
    )

    with st.expander("View comparison JSON", expanded=False):
        st.json(
            {
                "input_text": scenario_result.get("input_text"),
                "proposed_payload": scenario_result["proposed_payload"],
                "comparison": scenario_result["comparison"],
                "baseline": scenario_result.get("baseline"),
                "scenario": scenario_result.get("scenario"),
                "validation_errors": scenario_result.get("validation_errors", []),
            }
        )


def audit_tab(result: dict | None, scenario_result: dict | None) -> None:
    st.markdown("#### Technical Audit Trail")
    if result:
        st.write(f"Audit Record ID: `{result['audit_record_id']}`")
        st.write(f"Service Status: `{result['service_status']}`")
        st.write(f"Timestamp: `{result['timestamp']}`")
        st.write(f"Model Version: `{result['model_version']}`")
        st.json(result["trace"])
    else:
        st.info("No technical decision payload is available yet.")

    st.markdown("#### Contract Snapshot")
    st.json(load_contract_snapshot())

    st.markdown("#### Recent Agent Audit Entries")
    for entry in load_agent_audit_tail():
        with st.expander(f"{entry['type']} entry"):
            st.json(entry)

    if scenario_result:
        st.markdown("#### Scenario JSON")
        json_box(scenario_result)


def main() -> None:
    st.set_page_config(page_title="CMAPSS PHM Dashboard", page_icon=":material/monitoring:", layout="wide")
    inject_styles()
    init_state()
    payload = sidebar_payload_editor()
    current_signature = payload_signature(payload)
    decision_is_stale = (
        st.session_state.decision_result is not None
        and st.session_state.decision_payload_signature is not None
        and st.session_state.decision_payload_signature != current_signature
    )
    render_hero(None if decision_is_stale else st.session_state.decision_result)

    st.markdown(
        f"**Active Request**  `{payload['dataset_id']}` / unit `{payload['unit_id']}` / cycle `{payload['cycle']}`"
    )
    if decision_is_stale:
        st.warning("The selected request changed. Click `Decision` in the sidebar to refresh Summary and Analysis for this engine record.")

    summary, analysis, scenarios, audit = st.tabs(["Summary", "Analysis", "Scenarios", "Technical Audit"])
    with summary:
        summary_tab(None if decision_is_stale else st.session_state.decision_result, payload)
    with analysis:
        analysis_tab(None if decision_is_stale else st.session_state.decision_result)
    with scenarios:
        scenarios_tab(st.session_state.scenario_result)
    with audit:
        audit_tab(None if decision_is_stale else st.session_state.decision_result, st.session_state.scenario_result)


if __name__ == "__main__":
    main()
