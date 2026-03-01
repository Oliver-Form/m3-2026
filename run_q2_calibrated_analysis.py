from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from run_q2_baseline_model import load_bets, simulate_population, split_pools_by_risk, summarize_outputs


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
PLOTS_DIR = DATA_DIR / "plots"

INPUT_SUBGROUPS = DATA_DIR / "q2_model_input.csv"
INPUT_BETS = ROOT / "bets.csv"

CALIBRATION_OUT = DATA_DIR / "q2_calibration_summary.csv"
SCENARIO_SUBGROUP_OUT = DATA_DIR / "q2_scenario_subgroup_summary.csv"
SCENARIO_OVERALL_OUT = DATA_DIR / "q2_scenario_overall_summary.csv"
SCENARIO_SIM_OUT = DATA_DIR / "q2_scenario_simulated_outcomes.csv"


def compute_observed_hold(bets: pd.DataFrame) -> float:
    total_stake = float(bets["stake"].sum())
    total_net = float((bets["gain"] - bets["stake"]).sum())
    return -total_net / total_stake if total_stake > 0 else 0.0


def calibrate_payout_multiplier(sim_df: pd.DataFrame, target_hold: float) -> float:
    total_stake = float(sim_df["yearly_total_staked_usd"].sum())
    total_payout = float(sim_df["yearly_total_payout_usd"].sum())
    if total_payout <= 0 or total_stake <= 0:
        return 1.0
    multiplier = (1.0 - target_hold) * total_stake / total_payout
    return max(0.1, multiplier)


def apply_calibration(sim_df: pd.DataFrame, payout_multiplier: float) -> pd.DataFrame:
    calibrated = sim_df.copy()
    calibrated["yearly_total_payout_usd"] = calibrated["yearly_total_payout_usd"] * payout_multiplier
    calibrated["yearly_net_gain_loss_usd"] = (
        calibrated["yearly_total_payout_usd"] - calibrated["yearly_total_staked_usd"]
    )
    return calibrated


def subgroup_label(df: pd.DataFrame) -> pd.Series:
    return df["sex"] + " | " + df["age_band"] + " | " + df["education"]


def make_plots(base_subgroup: pd.DataFrame) -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    # Plot 1: mean annual net by subgroup
    ordered = base_subgroup.copy().sort_values("mean_net_gain_loss_usd")
    labels = subgroup_label(ordered)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(labels, ordered["mean_net_gain_loss_usd"], color="#4C78A8")
    ax.axhline(0, color="black", linewidth=1)
    ax.set_title("Mean Annual Net Gain/Loss by Subgroup (Base Hold)")
    ax.set_ylabel("USD")
    ax.set_xlabel("Subgroup")
    ax.tick_params(axis="x", rotation=75)
    fig.tight_layout()
    print(f"Plot 1 data:\n{ordered[['sex', 'age_band', 'education', 'mean_net_gain_loss_usd']].to_string()}")
    fig.savefig(PLOTS_DIR / "q2_mean_net_by_subgroup.png", dpi=180)
    plt.close(fig)

    # Plot 2: tail risk probability over $2,000í
    ordered_tail = base_subgroup.copy().sort_values("p_loss_over_2000", ascending=False)
    labels_tail = subgroup_label(ordered_tail)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(labels_tail, ordered_tail["p_loss_over_2000"], color="#F58518")
    ax.set_title("Probability of Annual Loss > $2,000 by Subgroup (Base Hold)")
    ax.set_ylabel("Probability")
    ax.set_xlabel("Subgroup")
    ax.tick_params(axis="x", rotation=75)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "q2_tail_risk_over_2000.png", dpi=180)
    plt.close(fig)

    # Plot 3: participation heatmap-like table by sex/age, split by education
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    educations = ["No college", "B.A. or higher"]
    age_order = ["18-34", "35-49", "50-64", "65+"]
    sex_order = ["Female", "Male"]

    for ax, edu in zip(axes, educations):
        subset = base_subgroup[base_subgroup["education"] == edu].copy()
        pivot = subset.pivot(index="age_band", columns="sex", values="active_rate")
        pivot = pivot.reindex(index=age_order, columns=sex_order)

        im = ax.imshow(pivot.values, cmap="Blues", aspect="auto", vmin=0, vmax=max(0.01, pivot.max().max()))
        ax.set_xticks(range(len(sex_order)))
        ax.set_xticklabels(sex_order)
        ax.set_yticks(range(len(age_order)))
        ax.set_yticklabels(age_order)
        ax.set_title(f"Active Rate Heatmap ({edu})")

        for i in range(len(age_order)):
            for j in range(len(sex_order)):
                val = pivot.values[i, j]
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", color="black", fontsize=9)

    cbar = fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.8)
    cbar.set_label("Active Rate")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "q2_active_rate_heatmap.png", dpi=180)
    plt.close(fig)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    subgroup_df = pd.read_csv(INPUT_SUBGROUPS)
    bets = load_bets(INPUT_BETS)
    pools = split_pools_by_risk(bets)
    observed_hold = compute_observed_hold(bets)

    target_holds = {
        "low_hold": max(0.01, observed_hold - 0.02),
        "base_hold": observed_hold,
        "high_hold": min(0.25, observed_hold + 0.02),
    }

    calibration_rows: list[dict[str, float | str]] = []
    subgroup_rows: list[pd.DataFrame] = []
    overall_rows: list[pd.DataFrame] = []
    sim_rows: list[pd.DataFrame] = []

    for scenario_name, target_hold in target_holds.items():
        sim_raw = simulate_population(subgroup_df, pools, n_people=30000, seed=42)
        multiplier = calibrate_payout_multiplier(sim_raw, target_hold)
        sim_cal = apply_calibration(sim_raw, multiplier)

        achieved_hold = (
            sim_cal["yearly_total_staked_usd"].sum() - sim_cal["yearly_total_payout_usd"].sum()
        ) / sim_cal["yearly_total_staked_usd"].sum()

        subgroup_summary, overall_summary = summarize_outputs(sim_cal)
        subgroup_summary["scenario"] = scenario_name
        overall_summary["scenario"] = scenario_name
        sim_cal["scenario"] = scenario_name

        subgroup_rows.append(subgroup_summary)
        overall_rows.append(overall_summary)
        sim_rows.append(sim_cal)

        calibration_rows.append(
            {
                "scenario": scenario_name,
                "target_hold": target_hold,
                "observed_hold_from_bets": observed_hold,
                "payout_multiplier": multiplier,
                "achieved_hold": float(achieved_hold),
                "total_staked_usd": float(sim_cal["yearly_total_staked_usd"].sum()),
                "total_payout_usd": float(sim_cal["yearly_total_payout_usd"].sum()),
                "total_net_gain_loss_usd": float(sim_cal["yearly_net_gain_loss_usd"].sum()),
            }
        )

    calibration_df = pd.DataFrame(calibration_rows)
    subgroup_df_out = pd.concat(subgroup_rows, ignore_index=True)
    overall_df_out = pd.concat(overall_rows, ignore_index=True)
    sim_df_out = pd.concat(sim_rows, ignore_index=True)

    calibration_df.to_csv(CALIBRATION_OUT, index=False)
    subgroup_df_out.to_csv(SCENARIO_SUBGROUP_OUT, index=False)
    overall_df_out.to_csv(SCENARIO_OVERALL_OUT, index=False)
    sim_df_out.to_csv(SCENARIO_SIM_OUT, index=False)

    base_subgroup = subgroup_df_out[subgroup_df_out["scenario"] == "base_hold"].copy()
    make_plots(base_subgroup)

    print(f"wrote {CALIBRATION_OUT}")
    print(f"wrote {SCENARIO_SUBGROUP_OUT} ({len(subgroup_df_out)} rows)")
    print(f"wrote {SCENARIO_OVERALL_OUT} ({len(overall_df_out)} rows)")
    print(f"wrote {SCENARIO_SIM_OUT} ({len(sim_df_out)} rows)")
    print(f"wrote plots in {PLOTS_DIR}")


if __name__ == "__main__":
    main()
