from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
INPUT_SUBGROUPS = ROOT / "data" / "q2_model_input.csv"
INPUT_BETS = ROOT / "bets.csv"
OUTPUT_DIR = ROOT / "data"

COEFFICIENTS_OUT = OUTPUT_DIR / "q2_stageA_coefficients.csv"
PREDICTIONS_OUT = OUTPUT_DIR / "q2_stageA_predictions.csv"
SIM_OUT = OUTPUT_DIR / "q2_simulated_individual_outcomes.csv"
SUBGROUP_SUMMARY_OUT = OUTPUT_DIR / "q2_subgroup_summary.csv"
OVERALL_SUMMARY_OUT = OUTPUT_DIR / "q2_overall_summary.csv"


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def logit(p: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    clipped = np.clip(p, eps, 1 - eps)
    return np.log(clipped / (1 - clipped))


def fit_logit_linear_model(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    features = pd.get_dummies(df[["sex", "age_band", "education"]], drop_first=True)
    features["risk_score_z"] = df["risk_score_z"]
    features = features.astype(float)

    X = np.column_stack([np.ones(len(features)), features.to_numpy()])
    y = logit(df["p_active_bettor"].to_numpy())

    ridge = 1e-6
    ident = np.eye(X.shape[1])
    ident[0, 0] = 0.0
    beta = np.linalg.solve(X.T @ X + ridge * ident, X.T @ y)

    y_hat = X @ beta
    p_hat = sigmoid(y_hat)

    coef_names = ["intercept", *features.columns.tolist()]
    coef_df = pd.DataFrame({"feature": coef_names, "coefficient": beta})

    pred_df = df[["sex", "age_band", "education", "p_active_bettor"]].copy()
    pred_df["p_active_bettor_pred"] = p_hat
    pred_df["prediction_error"] = pred_df["p_active_bettor_pred"] - pred_df["p_active_bettor"]

    return coef_df, pred_df


def load_bets(path: Path) -> pd.DataFrame:
    bets = pd.read_csv(path, sep=";")
    bets["is_win"] = bets["is_win"].astype(str).str.lower().map({"true": True, "false": False})
    bets["odds"] = pd.to_numeric(bets["odds"], errors="coerce")
    bets["stake"] = pd.to_numeric(bets["stake"], errors="coerce")
    bets["gain"] = pd.to_numeric(bets["gain"], errors="coerce")
    bets = bets.dropna(subset=["odds", "stake", "gain"]).copy()
    bets = bets[bets["stake"] > 0].copy()
    bets["net"] = bets["gain"] - bets["stake"]
    bets["net_per_stake"] = bets["net"] / bets["stake"]
    return bets


def split_pools_by_risk(bets: pd.DataFrame) -> dict[str, pd.DataFrame]:
    q40 = bets["odds"].quantile(0.40)
    q60 = bets["odds"].quantile(0.60)

    low_pool = bets[bets["odds"] <= q40].copy()
    med_pool = bets[(bets["odds"] > q40) & (bets["odds"] < q60)].copy()
    high_pool = bets[bets["odds"] >= q60].copy()

    if med_pool.empty:
        med_pool = bets.copy()

    return {"low": low_pool, "medium": med_pool, "high": high_pool}


def subgroup_bet_lambda(row: pd.Series) -> float:
    tier_base = {"low": 40.0, "medium": 90.0, "high": 180.0}[row["risk_tier"]]
    investigate_factor = 0.8 + min(float(row["expected_investigations_per_day"]), 2.0) / 2.5
    deposit_factor = 0.8 + float(row["weekly_deposit_rate"]) / 100.0
    return max(5.0, tier_base * investigate_factor * deposit_factor)


def subgroup_stake_multiplier(row: pd.Series) -> float:
    tier_mult = {"low": 0.75, "medium": 1.0, "high": 1.35}[row["risk_tier"]]
    high_500_factor = 0.8 + 1.2 * float(row["high_bet_500_rate"]) / 100.0
    return max(0.3, tier_mult * high_500_factor)


def simulate_population(
    subgroup_df: pd.DataFrame,
    pools: dict[str, pd.DataFrame],
    n_people: int = 30000,
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    subgroup_df = subgroup_df.copy().reset_index(drop=True)
    subgroup_df["subgroup_id"] = subgroup_df.index
    subgroup_df["subgroup_label"] = (
        subgroup_df["sex"] + "|" + subgroup_df["age_band"] + "|" + subgroup_df["education"]
    )

    subgroup_weights = subgroup_df["p_has_account"].to_numpy()
    subgroup_weights = subgroup_weights / subgroup_weights.sum()

    assigned = rng.choice(subgroup_df["subgroup_id"].to_numpy(), size=n_people, p=subgroup_weights)

    records: list[dict[str, float | int | str | bool]] = []
    for person_idx, subgroup_id in enumerate(assigned, start=1):
        row = subgroup_df.iloc[int(subgroup_id)]
        is_active = bool(rng.uniform() < float(row["p_active_bettor"]))

        annual_net = 0.0
        annual_staked = 0.0
        annual_payout = 0.0
        total_bets = 0

        if is_active:
            lam = subgroup_bet_lambda(row)
            n_bets = int(max(1, rng.poisson(lam)))
            total_bets = n_bets

            pool = pools[str(row["risk_tier"])]
            picks = pool.sample(n=n_bets, replace=True, random_state=int(rng.integers(0, 1_000_000_000)))
            stake_mult = subgroup_stake_multiplier(row)

            staked = picks["stake"].to_numpy() * stake_mult
            payout = picks["gain"].to_numpy() * stake_mult

            annual_staked = float(staked.sum())
            annual_payout = float(payout.sum())
            annual_net = annual_payout - annual_staked

        records.append(
            {
                "person_id": f"Q2_{person_idx:06d}",
                "sex": row["sex"],
                "age_band": row["age_band"],
                "education": row["education"],
                "risk_tier": row["risk_tier"],
                "p_active_bettor": float(row["p_active_bettor"]),
                "is_active_bettor": is_active,
                "bets_per_year": total_bets,
                "yearly_total_staked_usd": annual_staked,
                "yearly_total_payout_usd": annual_payout,
                "yearly_net_gain_loss_usd": annual_net,
            }
        )

    return pd.DataFrame(records)


def summarize_outputs(sim_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    subgroup_summary = (
        sim_df.groupby(["sex", "age_band", "education", "risk_tier"], as_index=False)
        .agg(
            n_people=("person_id", "count"),
            active_rate=("is_active_bettor", "mean"),
            mean_net_gain_loss_usd=("yearly_net_gain_loss_usd", "mean"),
            median_net_gain_loss_usd=("yearly_net_gain_loss_usd", "median"),
            p_loss_over_500=("yearly_net_gain_loss_usd", lambda s: float((s < -500).mean())),
            p_loss_over_2000=("yearly_net_gain_loss_usd", lambda s: float((s < -2000).mean())),
            p_loss_over_5000=("yearly_net_gain_loss_usd", lambda s: float((s < -5000).mean())),
        )
        .sort_values(["sex", "age_band", "education"])
    )

    overall = pd.DataFrame(
        {
            "n_people": [len(sim_df)],
            "active_rate": [float(sim_df["is_active_bettor"].mean())],
            "mean_net_gain_loss_usd": [float(sim_df["yearly_net_gain_loss_usd"].mean())],
            "median_net_gain_loss_usd": [float(sim_df["yearly_net_gain_loss_usd"].median())],
            "p_loss_over_500": [float((sim_df["yearly_net_gain_loss_usd"] < -500).mean())],
            "p_loss_over_2000": [float((sim_df["yearly_net_gain_loss_usd"] < -2000).mean())],
            "p_loss_over_5000": [float((sim_df["yearly_net_gain_loss_usd"] < -5000).mean())],
            "total_net_gain_loss_usd": [float(sim_df["yearly_net_gain_loss_usd"].sum())],
        }
    )

    return subgroup_summary, overall


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    subgroup_df = pd.read_csv(INPUT_SUBGROUPS)
    coef_df, pred_df = fit_logit_linear_model(subgroup_df)
    coef_df.to_csv(COEFFICIENTS_OUT, index=False)
    pred_df.to_csv(PREDICTIONS_OUT, index=False)

    bets = load_bets(INPUT_BETS)
    pools = split_pools_by_risk(bets)
    sim_df = simulate_population(subgroup_df, pools)
    sim_df.to_csv(SIM_OUT, index=False)

    subgroup_summary, overall_summary = summarize_outputs(sim_df)
    subgroup_summary.to_csv(SUBGROUP_SUMMARY_OUT, index=False)
    overall_summary.to_csv(OVERALL_SUMMARY_OUT, index=False)

    print(f"wrote {COEFFICIENTS_OUT}")
    print(f"wrote {PREDICTIONS_OUT}")
    print(f"wrote {SIM_OUT} ({len(sim_df)} rows)")
    print(f"wrote {SUBGROUP_SUMMARY_OUT} ({len(subgroup_summary)} rows)")
    print(f"wrote {OVERALL_SUMMARY_OUT}")


if __name__ == "__main__":
    main()
