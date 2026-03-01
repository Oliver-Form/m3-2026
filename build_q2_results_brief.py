from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

INPUT_SCENARIO_SUBGROUP = DATA_DIR / "q2_scenario_subgroup_summary.csv"
INPUT_SCENARIO_OVERALL = DATA_DIR / "q2_scenario_overall_summary.csv"
INPUT_STAGEA_COEFS = DATA_DIR / "q2_stageA_coefficients.csv"

TOP_RISK_OUT = DATA_DIR / "q2_top_risk_subgroups.csv"
SCENARIO_DELTA_OUT = DATA_DIR / "q2_scenario_deltas.csv"
BRIEF_OUT = DATA_DIR / "q2_results_brief.md"


def pct(x: float) -> str:
    return f"{100.0 * x:.1f}%"


def usd(x: float) -> str:
    return f"${x:,.0f}"


def main() -> None:
    subgroup = pd.read_csv(INPUT_SCENARIO_SUBGROUP)
    overall = pd.read_csv(INPUT_SCENARIO_OVERALL)
    coefs = pd.read_csv(INPUT_STAGEA_COEFS)

    base = subgroup[subgroup["scenario"] == "base_hold"].copy()
    base["subgroup"] = base["sex"] + " | " + base["age_band"] + " | " + base["education"]

    top_risk = (
        base.sort_values(["p_loss_over_2000", "mean_net_gain_loss_usd"], ascending=[False, True])
        .head(5)
        .loc[
            :,
            [
                "subgroup",
                "risk_tier",
                "active_rate",
                "mean_net_gain_loss_usd",
                "p_loss_over_500",
                "p_loss_over_2000",
                "p_loss_over_5000",
            ],
        ]
        .reset_index(drop=True)
    )
    top_risk.to_csv(TOP_RISK_OUT, index=False)

    overall = overall.set_index("scenario").copy()
    low = overall.loc["low_hold"]
    base_row = overall.loc["base_hold"]
    high = overall.loc["high_hold"]

    deltas = pd.DataFrame(
        [
            {
                "metric": "mean_net_gain_loss_usd",
                "low_hold": low["mean_net_gain_loss_usd"],
                "base_hold": base_row["mean_net_gain_loss_usd"],
                "high_hold": high["mean_net_gain_loss_usd"],
                "high_minus_low": high["mean_net_gain_loss_usd"] - low["mean_net_gain_loss_usd"],
            },
            {
                "metric": "p_loss_over_2000",
                "low_hold": low["p_loss_over_2000"],
                "base_hold": base_row["p_loss_over_2000"],
                "high_hold": high["p_loss_over_2000"],
                "high_minus_low": high["p_loss_over_2000"] - low["p_loss_over_2000"],
            },
            {
                "metric": "p_loss_over_5000",
                "low_hold": low["p_loss_over_5000"],
                "base_hold": base_row["p_loss_over_5000"],
                "high_hold": high["p_loss_over_5000"],
                "high_minus_low": high["p_loss_over_5000"] - low["p_loss_over_5000"],
            },
        ]
    )
    deltas.to_csv(SCENARIO_DELTA_OUT, index=False)

    coef_sex_male = float(coefs.loc[coefs["feature"] == "sex_Male", "coefficient"].iloc[0])
    coef_age_50_64 = float(coefs.loc[coefs["feature"] == "age_band_50-64", "coefficient"].iloc[0])
    coef_age_65 = float(coefs.loc[coefs["feature"] == "age_band_65+", "coefficient"].iloc[0])
    coef_edu_no_college = float(coefs.loc[coefs["feature"] == "education_No college", "coefficient"].iloc[0])
    coef_risk = float(coefs.loc[coefs["feature"] == "risk_score_z", "coefficient"].iloc[0])

    lines: list[str] = []
    lines.append("# Q2 Results Brief (Auto-generated)")
    lines.append("")
    lines.append("## 1) Overall calibrated scenario results")
    lines.append(
        f"- Base hold scenario: mean annual net = {usd(base_row['mean_net_gain_loss_usd'])}, active rate = {pct(base_row['active_rate'])}, P(loss > $2,000) = {pct(base_row['p_loss_over_2000'])}."
    )
    lines.append(
        f"- Low vs high hold sensitivity: mean annual net shifts by {usd(high['mean_net_gain_loss_usd'] - low['mean_net_gain_loss_usd'])} per person; P(loss > $2,000) shifts by {pct(high['p_loss_over_2000'] - low['p_loss_over_2000'])}."
    )
    lines.append(
        f"- Tail risk in base scenario: P(loss > $500) = {pct(base_row['p_loss_over_500'])}, P(loss > $5,000) = {pct(base_row['p_loss_over_5000'])}."
    )
    lines.append("")
    lines.append("## 2) Highest-risk subgroups (base hold)")
    for idx, row in top_risk.iterrows():
        lines.append(
            f"- {idx+1}. {row['subgroup']} ({row['risk_tier']} risk): mean annual net {usd(row['mean_net_gain_loss_usd'])}, P(loss > $2,000) = {pct(row['p_loss_over_2000'])}, active rate = {pct(row['active_rate'])}."
        )
    lines.append("")
    lines.append("## 3) Stage A participation model interpretation")
    lines.append(
        f"- Positive coefficient on `sex_Male` ({coef_sex_male:.3f}) and `risk_score_z` ({coef_risk:.3f}) indicates higher participation odds for male and higher-risk-profile groups."
    )
    lines.append(
        f"- Negative coefficients on older age groups (`age_band_50-64` = {coef_age_50_64:.3f}, `age_band_65+` = {coef_age_65:.3f}) indicate lower participation odds relative to ages 18-34."
    )
    lines.append(
        f"- `education_No college` coefficient ({coef_edu_no_college:.3f}) is negative in this baseline fit, suggesting lower participation odds versus B.A. or higher, conditional on other model inputs."
    )
    lines.append("")
    lines.append("## 4) Files produced")
    lines.append("- `data/q2_top_risk_subgroups.csv`")
    lines.append("- `data/q2_scenario_deltas.csv`")
    lines.append("- `data/q2_results_brief.md`")

    BRIEF_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {TOP_RISK_OUT}")
    print(f"wrote {SCENARIO_DELTA_OUT}")
    print(f"wrote {BRIEF_OUT}")


if __name__ == "__main__":
    main()
