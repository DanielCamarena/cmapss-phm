from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
OUT_EDA = ROOT / "out" / "eda"
OUT_PROCESSED = ROOT / "out" / "processed"
FIG_EDA = ROOT / "fig" / "eda"

DATASETS = ["FD001", "FD002", "FD003", "FD004"]
META_COLUMNS = ["unit_id", "cycle"]
SETTING_COLUMNS = [f"op_setting_{i}" for i in range(1, 4)]
SENSOR_COLUMNS = [f"sensor_{i}" for i in range(1, 22)]
ALL_COLUMNS = META_COLUMNS + SETTING_COLUMNS + SENSOR_COLUMNS
KEY_SENSORS = ["sensor_2", "sensor_3", "sensor_4", "sensor_7", "sensor_11", "sensor_12", "sensor_15", "sensor_21"]


@dataclass
class DatasetBundle:
    train: pd.DataFrame
    test: pd.DataFrame
    rul: pd.DataFrame


def ensure_dirs() -> None:
    for path in [OUT_EDA, OUT_PROCESSED, FIG_EDA]:
        path.mkdir(parents=True, exist_ok=True)


def load_split(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=r"\s+", header=None, engine="python")
    if df.shape[1] > len(ALL_COLUMNS):
        df = df.iloc[:, : len(ALL_COLUMNS)]
    df.columns = ALL_COLUMNS
    return df


def load_rul(path: Path) -> pd.DataFrame:
    rul = pd.read_csv(path, sep=r"\s+", header=None, engine="python")
    if rul.shape[1] > 1:
        rul = rul.iloc[:, :1]
    rul.columns = ["rul"]
    rul["test_unit_id"] = np.arange(1, len(rul) + 1)
    return rul


def load_all() -> dict[str, DatasetBundle]:
    bundles: dict[str, DatasetBundle] = {}
    for dataset_id in DATASETS:
        bundles[dataset_id] = DatasetBundle(
            train=load_split(DATA_DIR / f"train_{dataset_id}.txt"),
            test=load_split(DATA_DIR / f"test_{dataset_id}.txt"),
            rul=load_rul(DATA_DIR / f"RUL_{dataset_id}.txt"),
        )
        bundles[dataset_id].train["dataset_id"] = dataset_id
        bundles[dataset_id].test["dataset_id"] = dataset_id
        bundles[dataset_id].rul["dataset_id"] = dataset_id
    return bundles


def build_inventory_and_quality(bundles: dict[str, DatasetBundle]) -> tuple[pd.DataFrame, pd.DataFrame]:
    inventory_rows: list[dict[str, object]] = []
    quality_rows: list[dict[str, object]] = []

    for dataset_id, bundle in bundles.items():
        test_units = bundle.test["unit_id"].nunique()
        rul_count = len(bundle.rul)
        for split_name, df in [("train", bundle.train), ("test", bundle.test)]:
            inventory_rows.append(
                {
                    "dataset_id": dataset_id,
                    "split": split_name,
                    "rows": len(df),
                    "columns": df.shape[1] - 1,
                    "unit_count": int(df["unit_id"].nunique()),
                    "min_cycle": int(df["cycle"].min()),
                    "max_cycle": int(df["cycle"].max()),
                    "missing_values": int(df.isna().sum().sum()),
                    "duplicate_rows": int(df.duplicated().sum()),
                }
            )
            quality_rows.append(
                {
                    "dataset_id": dataset_id,
                    "split": split_name,
                    "check": "column_count_equals_26",
                    "status": "ok" if (df.shape[1] - 1) == 26 else "issue",
                    "details": f"observed={(df.shape[1] - 1)} expected=26",
                }
            )
            quality_rows.append(
                {
                    "dataset_id": dataset_id,
                    "split": split_name,
                    "check": "missing_values",
                    "status": "ok" if int(df.isna().sum().sum()) == 0 else "issue",
                    "details": f"missing_total={int(df.isna().sum().sum())}",
                }
            )
            quality_rows.append(
                {
                    "dataset_id": dataset_id,
                    "split": split_name,
                    "check": "duplicate_rows",
                    "status": "ok" if int(df.duplicated().sum()) == 0 else "issue",
                    "details": f"duplicate_rows={int(df.duplicated().sum())}",
                }
            )
        quality_rows.append(
            {
                "dataset_id": dataset_id,
                "split": "test",
                "check": "rul_count_matches_test_units",
                "status": "ok" if test_units == rul_count else "issue",
                "details": f"test_units={test_units} rul_rows={rul_count}",
            }
        )
    return pd.DataFrame(inventory_rows), pd.DataFrame(quality_rows)


def write_schema_report() -> None:
    lines = [
        "NASA C-MAPSS schema",
        "",
        "Parsing rule: whitespace-separated text with trailing empty fields dropped.",
        f"Total modeled columns: {len(ALL_COLUMNS)}",
        "",
        "Columns:",
    ]
    for idx, name in enumerate(ALL_COLUMNS, start=1):
        lines.append(f"{idx:02d}. {name}")
    lines.append("")
    lines.append("Notes:")
    lines.append("- unit_id and cycle are identifiers used for grouping and ordering.")
    lines.append("- op_setting_1..3 represent operating condition variables.")
    lines.append("- sensor_1..21 represent the measured sensor channels retained in the benchmark.")
    (OUT_EDA / "01_schema_report.txt").write_text("\n".join(lines), encoding="utf-8")


def build_stats(bundles: dict[str, DatasetBundle]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    stats_frames: list[pd.DataFrame] = []
    global_source: list[pd.DataFrame] = []
    low_variance_rows: list[dict[str, object]] = []

    for dataset_id, bundle in bundles.items():
        combined = pd.concat(
            [
                bundle.train.assign(split="train"),
                bundle.test.assign(split="test"),
            ],
            ignore_index=True,
        )
        features = combined[SETTING_COLUMNS + SENSOR_COLUMNS]
        desc = features.describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]).T.reset_index()
        desc = desc.rename(columns={"index": "feature"})
        desc.insert(0, "dataset_id", dataset_id)
        stats_frames.append(desc)

        for feature in SETTING_COLUMNS + SENSOR_COLUMNS:
            series = combined[feature]
            global_source.append(
                pd.DataFrame(
                    {
                        "dataset_id": dataset_id,
                        "feature": feature,
                        "split": combined["split"],
                        "value": series,
                    }
                )
            )
            variance = float(series.var())
            nunique = int(series.nunique())
            low_variance_rows.append(
                {
                    "dataset_id": dataset_id,
                    "feature": feature,
                    "variance": variance,
                    "nunique": nunique,
                    "is_low_variance": variance < 1e-8 or nunique <= 2,
                }
            )

        corr = combined[SENSOR_COLUMNS].corr()
        fig, ax = plt.subplots(figsize=(12, 10))
        im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
        ax.set_title(f"{dataset_id} sensor correlation heatmap")
        ax.set_xticks(range(len(SENSOR_COLUMNS)))
        ax.set_yticks(range(len(SENSOR_COLUMNS)))
        ax.set_xticklabels(SENSOR_COLUMNS, rotation=90, fontsize=6)
        ax.set_yticklabels(SENSOR_COLUMNS, fontsize=6)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        fig.tight_layout()
        fig.savefig(FIG_EDA / f"02_correlation_heatmap_{dataset_id.lower()}.png", dpi=200)
        plt.close(fig)

    stats_by_dataset = pd.concat(stats_frames, ignore_index=True)
    global_stats = (
        pd.concat(global_source, ignore_index=True)
        .groupby(["feature"])["value"]
        .agg(["count", "mean", "std", "min", "median", "max"])
        .reset_index()
    )
    global_stats.insert(0, "scope", "all_datasets_combined")
    low_variance = pd.DataFrame(low_variance_rows)
    return global_stats, stats_by_dataset, low_variance


def add_train_rul(df: pd.DataFrame) -> pd.DataFrame:
    max_cycle = df.groupby("unit_id")["cycle"].transform("max")
    result = df.copy()
    result["rul"] = max_cycle - result["cycle"]
    return result


def choose_units(df: pd.DataFrame, n: int) -> list[int]:
    counts = df.groupby("unit_id")["cycle"].max().sort_values(ascending=False)
    units = counts.index.tolist()
    if not units:
        return []
    sample = [units[0], units[len(units) // 2], units[-1]]
    return list(dict.fromkeys(sample[:n]))


def temporal_outputs(bundles: dict[str, DatasetBundle]) -> pd.DataFrame:
    sequence_rows: list[dict[str, object]] = []
    notes: list[str] = []

    for dataset_id, bundle in bundles.items():
        for split_name, df in [("train", bundle.train), ("test", bundle.test)]:
            seq = df.groupby("unit_id")["cycle"].max().reset_index(name="sequence_length")
            seq["dataset_id"] = dataset_id
            seq["split"] = split_name
            sequence_rows.append(seq)

        train_with_rul = add_train_rul(bundle.train)
        sampled_units = choose_units(train_with_rul, 3)

        fig, axes = plt.subplots(4, 2, figsize=(14, 12), sharex=False)
        axes = axes.flatten()
        for ax, sensor in zip(axes, KEY_SENSORS):
            for unit_id in sampled_units:
                unit_df = train_with_rul[train_with_rul["unit_id"] == unit_id]
                ax.plot(unit_df["cycle"], unit_df[sensor], label=f"unit {unit_id}", linewidth=1.2)
            ax.set_title(sensor)
            ax.set_xlabel("cycle")
            ax.set_ylabel("value")
        handles, labels = axes[0].get_legend_handles_labels()
        if handles:
            fig.legend(handles, labels, loc="upper center", ncol=len(sampled_units))
        fig.suptitle(f"{dataset_id} key sensor trends")
        fig.tight_layout(rect=[0, 0, 1, 0.97])
        fig.savefig(FIG_EDA / f"03_sensor_trends_{dataset_id.lower()}.png", dpi=200)
        plt.close(fig)

        fig, axes = plt.subplots(len(sampled_units), 1, figsize=(12, 10), sharex=False)
        if len(sampled_units) == 1:
            axes = [axes]
        for ax, unit_id in zip(axes, sampled_units):
            unit_df = train_with_rul[train_with_rul["unit_id"] == unit_id]
            ax.plot(unit_df["cycle"], unit_df["sensor_11"], label="sensor_11")
            ax.plot(unit_df["cycle"], unit_df["sensor_12"], label="sensor_12")
            ax.plot(unit_df["cycle"], unit_df["sensor_15"], label="sensor_15")
            ax.set_title(f"{dataset_id} unit {unit_id}")
            ax.set_xlabel("cycle")
            ax.set_ylabel("sensor value")
            ax.legend(loc="best")
        fig.tight_layout()
        fig.savefig(FIG_EDA / f"03_unit_examples_{dataset_id.lower()}.png", dpi=200)
        plt.close(fig)

        train_lengths = bundle.train.groupby("unit_id")["cycle"].max()
        notes.append(
            f"{dataset_id}: train units={bundle.train['unit_id'].nunique()}, "
            f"test units={bundle.test['unit_id'].nunique()}, "
            f"train length mean={train_lengths.mean():.1f}, "
            f"train length std={train_lengths.std():.1f}, "
            f"sampled units={sampled_units}"
        )

    (OUT_EDA / "03_temporal_notes.txt").write_text("\n".join(notes), encoding="utf-8")
    return pd.concat(sequence_rows, ignore_index=True)


def rul_outputs(bundles: dict[str, DatasetBundle]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    cap_fig, cap_axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    cap_axes = cap_axes.flatten()

    policy_lines = [
        "Target strategy recommendation",
        "",
        "Primary recommendation: use a capped RUL target with cap=125 for baseline experiments.",
        "Rationale: it reduces the dominance of very early-life samples while preserving late-life sensitivity.",
        "Secondary target: keep uncapped linear RUL for ablation and calibration analysis.",
        "",
        "Downstream guidance:",
        "- Report metrics for both uncapped and capped targets when comparing models.",
        "- Keep the cap configurable in preprocessing, defaulting to 125.",
        "- Preserve raw RUL in exported processed datasets for auditability.",
    ]

    for idx, (dataset_id, bundle) in enumerate(bundles.items()):
        train = add_train_rul(bundle.train)
        test_last = bundle.test.groupby("unit_id")["cycle"].max().reset_index(name="last_cycle")
        test_rul = bundle.rul.copy()
        test_rul["unit_id"] = test_rul["test_unit_id"]

        for split_name, values in [("train", train["rul"]), ("test", test_rul["rul"])]:
            rows.append(
                {
                    "dataset_id": dataset_id,
                    "split": split_name,
                    "count": int(values.shape[0]),
                    "mean": float(values.mean()),
                    "std": float(values.std()),
                    "min": float(values.min()),
                    "median": float(values.median()),
                    "max": float(values.max()),
                    "p95": float(values.quantile(0.95)),
                }
            )

        axes[idx].hist(train["rul"], bins=40, alpha=0.65, label="train_rul")
        axes[idx].hist(test_rul["rul"], bins=30, alpha=0.65, label="test_final_rul")
        axes[idx].set_title(dataset_id)
        axes[idx].set_xlabel("RUL")
        axes[idx].set_ylabel("count")
        axes[idx].legend(loc="best")

        capped_125 = train["rul"].clip(upper=125)
        capped_130 = train["rul"].clip(upper=130)
        cap_axes[idx].hist(train["rul"], bins=40, alpha=0.4, label="uncapped")
        cap_axes[idx].hist(capped_125, bins=40, alpha=0.5, label="cap125")
        cap_axes[idx].hist(capped_130, bins=40, alpha=0.5, label="cap130")
        cap_axes[idx].set_title(f"{dataset_id} cap comparison")
        cap_axes[idx].set_xlabel("RUL")
        cap_axes[idx].set_ylabel("count")
        cap_axes[idx].legend(loc="best")

    fig.tight_layout()
    fig.savefig(FIG_EDA / "04_rul_histograms.png", dpi=200)
    plt.close(fig)
    cap_fig.tight_layout()
    cap_fig.savefig(FIG_EDA / "04_rul_cap_comparison.png", dpi=200)
    plt.close(cap_fig)
    (OUT_EDA / "04_target_definition.txt").write_text("\n".join(policy_lines), encoding="utf-8")
    return pd.DataFrame(rows)


def split_train_valid(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_parts: list[pd.DataFrame] = []
    valid_parts: list[pd.DataFrame] = []
    for dataset_id, group in df.groupby("dataset_id"):
        unit_ids = sorted(group["unit_id"].unique())
        valid_count = max(1, int(round(0.2 * len(unit_ids))))
        valid_units = set(unit_ids[-valid_count:])
        train_parts.append(group[~group["unit_id"].isin(valid_units)].copy())
        valid_parts.append(group[group["unit_id"].isin(valid_units)].copy())
    return pd.concat(train_parts, ignore_index=True), pd.concat(valid_parts, ignore_index=True)


def build_processed_artifacts(bundles: dict[str, DatasetBundle], low_variance: pd.DataFrame) -> None:
    train_frames: list[pd.DataFrame] = []
    test_frames: list[pd.DataFrame] = []

    low_var_features = sorted(low_variance.loc[low_variance["is_low_variance"], "feature"].unique().tolist())
    selected_features = [col for col in SETTING_COLUMNS + SENSOR_COLUMNS if col not in low_var_features]

    for dataset_id, bundle in bundles.items():
        train_df = add_train_rul(bundle.train)
        test_df = bundle.test.copy()
        train_df["dataset_id"] = dataset_id
        test_df["dataset_id"] = dataset_id
        test_df["rul"] = np.nan
        train_frames.append(train_df)
        test_frames.append(test_df)

    train_all = pd.concat(train_frames, ignore_index=True)
    test_all = pd.concat(test_frames, ignore_index=True)
    train_split, valid_split = split_train_valid(train_all)

    scaler = StandardScaler()
    scaler.fit(train_split[selected_features])

    def transform(df: pd.DataFrame, split_name: str) -> pd.DataFrame:
        scaled = pd.DataFrame(scaler.transform(df[selected_features]), columns=selected_features, index=df.index)
        result = pd.concat(
            [
                df[["dataset_id", "unit_id", "cycle", "rul"]].reset_index(drop=True),
                scaled.reset_index(drop=True),
            ],
            axis=1,
        )
        result["split"] = split_name
        return result

    train_processed = transform(train_split, "train")
    valid_processed = transform(valid_split, "valid")
    test_processed = transform(test_all, "test")

    train_processed.to_parquet(OUT_PROCESSED / "train_processed.parquet", index=False)
    valid_processed.to_parquet(OUT_PROCESSED / "valid_processed.parquet", index=False)
    test_processed.to_parquet(OUT_PROCESSED / "test_processed.parquet", index=False)

    feature_lines = [
        "Selected baseline features",
        "",
        f"Removed low-variance features: {', '.join(low_var_features) if low_var_features else 'none'}",
        "",
        "Retained features:",
    ] + [f"- {feature}" for feature in selected_features]
    (OUT_EDA / "05_feature_list.txt").write_text("\n".join(feature_lines), encoding="utf-8")

    config = {
        "scaler": "StandardScaler",
        "fit_scope": "train split only",
        "selected_features": selected_features,
        "removed_low_variance_features": low_var_features,
        "target_column": "rul",
        "target_default_policy": {"name": "rul_capped", "default_cap": 125, "raw_rul_preserved": True},
        "window_policy": {"implemented_in_plan1": False, "recommended_window_lengths": [30, 50], "stride": 1},
    }
    (OUT_EDA / "05_preprocessing_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    split_policy = [
        "Leakage-safe split strategy",
        "",
        "Split unit: unit_id within each dataset_id.",
        "Validation allocation: last 20% of sorted unit IDs within each subset, minimum one unit.",
        "Ordering rule: cycle order preserved within each unit trajectory.",
        "Scaler fit: train split only.",
        "Sequence windows are not materialized in Plan 1 exports; only the documented policy is defined here.",
    ]
    (OUT_EDA / "05_split_strategy.txt").write_text("\n".join(split_policy), encoding="utf-8")


def write_closure_reports(
    inventory: pd.DataFrame,
    quality: pd.DataFrame,
    low_variance: pd.DataFrame,
    rul_distribution: pd.DataFrame,
) -> None:
    issues = quality[quality["status"] != "ok"]
    top_low_variance = low_variance[low_variance["is_low_variance"]].sort_values(["dataset_id", "feature"])
    summary = [
        "# EDA Findings Summary",
        "",
        f"- Inventory rows recorded: {len(inventory)}",
        f"- Data quality checks recorded: {len(quality)}",
        f"- Non-ok quality issues: {len(issues)}",
        f"- Low-variance feature flags: {int(top_low_variance['is_low_variance'].sum())}",
        "",
        "## Key observations",
        "- All four benchmark subsets were parsed using one consistent whitespace-delimited rule.",
        "- Train/test/RUL alignment was validated per subset.",
        "- Low-variance features were isolated before baseline preprocessing.",
        "- Train RUL was constructed from max_cycle - cycle and paired with test final-life labels for comparison.",
        "- Processed baseline artifacts were exported for downstream research and modeling work.",
    ]
    (OUT_EDA / "06_findings_summary.md").write_text("\n".join(summary), encoding="utf-8")

    risks = [
        "# Risks And Actions",
        "",
        "- Risk: multi-condition subsets may require condition-aware normalization.",
        "Action: compare per-dataset and per-regime performance in Plan 2 and Plan 3.",
        "- Risk: low-variance sensors may still be useful in interaction with other channels.",
        "Action: treat removal as a baseline choice, not a hard exclusion for all future models.",
        "- Risk: capped targets can improve optimization while hiding early-life resolution.",
        "Action: keep uncapped raw RUL available for ablation and calibration checks.",
        "- Risk: unit-based splitting by sorted IDs is deterministic but not stratified by lifetime.",
        "Action: revisit with grouped cross-validation during model comparison.",
    ]
    (OUT_EDA / "06_risks_and_actions.md").write_text("\n".join(risks), encoding="utf-8")

    baseline = [
        "# Baseline Plan",
        "",
        "1. Start with tabular baselines on processed row-level artifacts.",
        "2. Use the documented capped-RUL policy with cap=125 as the default supervised target.",
        "3. Compare against uncapped RUL before freezing the modeling choice.",
        "4. Add sequence windows in Plan 2 or Plan 3 using the documented 30/50-cycle candidates.",
        "5. Track performance separately for FD001/FD003 versus FD002/FD004 because operating conditions differ.",
        "",
        "## Recommended next handoff",
        "- Research phase should justify target capping and metric choices.",
        "- Predictive-layer implementation should preserve dataset_id, unit_id, and cycle through inference traces.",
        "- Any future feature pruning should be benchmarked against the full retained baseline set.",
    ]
    (OUT_EDA / "06_baseline_plan.md").write_text("\n".join(baseline), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    bundles = load_all()

    inventory, quality = build_inventory_and_quality(bundles)
    inventory.to_csv(OUT_EDA / "01_inventory_summary.csv", index=False)
    quality.to_csv(OUT_EDA / "01_data_quality_issues.csv", index=False)
    write_schema_report()

    global_stats, stats_by_dataset, low_variance = build_stats(bundles)
    global_stats.to_csv(OUT_EDA / "02_stats_global.csv", index=False)
    stats_by_dataset.to_csv(OUT_EDA / "02_stats_by_dataset.csv", index=False)
    low_variance.to_csv(OUT_EDA / "02_low_variance_sensors.csv", index=False)

    seq_lengths = temporal_outputs(bundles)
    seq_lengths.to_csv(OUT_EDA / "03_sequence_lengths.csv", index=False)

    rul_distribution = rul_outputs(bundles)
    rul_distribution.to_csv(OUT_EDA / "04_rul_distribution.csv", index=False)

    build_processed_artifacts(bundles, low_variance)
    write_closure_reports(inventory, quality, low_variance, rul_distribution)

    print("Plan 1 EDA execution complete.")
    print(f"Artifacts written to: {OUT_EDA}")
    print(f"Processed data written to: {OUT_PROCESSED}")
    print(f"Figures written to: {FIG_EDA}")


if __name__ == "__main__":
    main()
