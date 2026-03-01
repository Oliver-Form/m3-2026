"""
Q3: The Savings Shadow — Quantifying the Lifetime Wealth Cost of Gambling Losses

Takes Q2 subgroup gambling loss estimates + Q1 disposable income by age,
and computes:
  1. Gambling burden ratio (annual loss / disposable income)
  2. Compound "savings shadow" — lifetime wealth lost if losses had been invested
  3. Milestone equivalents (house, college, retirement years)
  4. Scenario grid (3 hold rates × 3 return rates)

Outputs tables to data/ and charts to data/plots/.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

OUT = "data"
PLOTS = os.path.join(OUT, "plots")
os.makedirs(PLOTS, exist_ok=True)

# ── 1. Load data ─────────────────────────────────────────────────────────────

disp = pd.read_csv("disposable-income-by-age.csv")
q2_base = pd.read_csv(os.path.join(OUT, "q2_subgroup_summary.csv"))
q2_scen = pd.read_csv(os.path.join(OUT, "q2_scenario_subgroup_summary.csv"))

# ── 2. Map age bands ────────────────────────────────────────────────────────
# Q2: 18-34, 35-49, 50-64, 65+
# Disposable: <30, 30-49, 50-64, 65-74, >74

# Reasonable mappings:
#   18-34 → <30  (closest; most 18-34 bettors skew young)
#   35-49 → 30-49
#   50-64 → 50-64  (exact match)
#   65+   → average of 65-74 and >74

disp_65_plus = (
    disp.loc[disp["age_band"].isin(["65-74", ">74"]), "mean_disposable_income_usd"]
    .mean()
)

age_map = {
    "18-34": disp.loc[disp["age_band"] == "<30", "mean_disposable_income_usd"].values[0],
    "35-49": disp.loc[disp["age_band"] == "30-49", "mean_disposable_income_usd"].values[0],
    "50-64": disp.loc[disp["age_band"] == "50-64", "mean_disposable_income_usd"].values[0],
    "65+":   disp_65_plus,
}

# Midpoint ages for retirement horizon calculation
age_midpoints = {"18-34": 26, "35-49": 42, "50-64": 57, "65+": 70}
RETIREMENT_AGE = 65

# ── 3. Compute burden ratios (base hold) ────────────────────────────────────

q2_base["disposable_income"] = q2_base["age_band"].map(age_map)
q2_base["annual_loss"] = q2_base["mean_net_gain_loss_usd"].abs()
q2_base["gambling_burden_pct"] = (
    q2_base["annual_loss"] / q2_base["disposable_income"] * 100
)

# ── 4. Compound savings shadow ──────────────────────────────────────────────

REAL_RETURN_RATES = [0.03, 0.04, 0.05]  # conservative, base, optimistic
RETURN_LABELS = ["3% real", "4% real", "5% real"]


def future_value_annuity(annual_amount, rate, years):
    """Future value of annual contributions compounded at `rate` for `years`."""
    if years <= 0 or rate == 0:
        return annual_amount * max(years, 0)
    return annual_amount * ((1 + rate) ** years - 1) / rate


def compute_shadow(row, rate):
    mid_age = age_midpoints[row["age_band"]]
    years = max(RETIREMENT_AGE - mid_age, 0)
    return future_value_annuity(row["annual_loss"], rate, years)


# Base-hold, base-return (4%) shadow for the main table
q2_base["years_to_retirement"] = q2_base["age_band"].map(
    lambda a: max(RETIREMENT_AGE - age_midpoints[a], 0)
)
q2_base["savings_shadow_4pct"] = q2_base.apply(
    lambda r: compute_shadow(r, 0.04), axis=1
)

# ── 5. Scenario grid: 3 hold rates × 3 return rates ────────────────────────

scenario_rows = []
for _, row in q2_scen.iterrows():
    for rate, label in zip(REAL_RETURN_RATES, RETURN_LABELS):
        mid_age = age_midpoints[row["age_band"]]
        years = max(RETIREMENT_AGE - mid_age, 0)
        loss = abs(row["mean_net_gain_loss_usd"])
        shadow = future_value_annuity(loss, rate, years)
        scenario_rows.append({
            "sex": row["sex"],
            "age_band": row["age_band"],
            "education": row["education"],
            "risk_tier": row["risk_tier"],
            "hold_scenario": row["scenario"],
            "return_scenario": label,
            "annual_loss_usd": loss,
            "years_to_retirement": years,
            "savings_shadow_usd": shadow,
        })

scenario_df = pd.DataFrame(scenario_rows)

# ── 6. Milestone equivalents ────────────────────────────────────────────────
# Using US benchmarks (approximate 2025 values)

MILESTONES = {
    "home_down_payment_20pct": 63600,      # 20% of ~$318K median US home
    "four_year_public_college": 112_000,    # in-state tuition + living, 4 years
    "annual_retirement_spending": 52_000,   # median retiree spending/year
    "six_month_emergency_fund": 26_000,     # ~$4,300/mo median expenses × 6
}


def milestone_equivalents(shadow_usd):
    return {
        "home_down_payments": round(shadow_usd / MILESTONES["home_down_payment_20pct"], 2),
        "college_degrees_funded": round(shadow_usd / MILESTONES["four_year_public_college"], 2),
        "retirement_years_funded": round(shadow_usd / MILESTONES["annual_retirement_spending"], 2),
        "emergency_funds": round(shadow_usd / MILESTONES["six_month_emergency_fund"], 2),
    }


# Add milestones to base table
for key in ["home_down_payments", "college_degrees_funded",
            "retirement_years_funded", "emergency_funds"]:
    q2_base[key] = q2_base["savings_shadow_4pct"].apply(
        lambda s: milestone_equivalents(s)[key]
    )

# ── 7. Build summary tables and save ────────────────────────────────────────

# Main burden + shadow table
cols_main = [
    "sex", "age_band", "education", "risk_tier",
    "active_rate", "annual_loss", "disposable_income",
    "gambling_burden_pct", "years_to_retirement", "savings_shadow_4pct",
    "home_down_payments", "college_degrees_funded",
    "retirement_years_funded", "emergency_funds",
]
main_table = q2_base[cols_main].copy()
main_table = main_table.sort_values("savings_shadow_4pct", ascending=False)
main_table.to_csv(os.path.join(OUT, "q3_savings_shadow.csv"), index=False)
print(f"[Q3] Saved {os.path.join(OUT, 'q3_savings_shadow.csv')}")

# Scenario grid
scenario_df.to_csv(os.path.join(OUT, "q3_scenario_grid.csv"), index=False)
print(f"[Q3] Saved {os.path.join(OUT, 'q3_scenario_grid.csv')}")

# Top-line summary: aggregate across population by hold × return scenario
topline_rows = []
for hold in scenario_df["hold_scenario"].unique():
    for ret in scenario_df["return_scenario"].unique():
        mask = (scenario_df["hold_scenario"] == hold) & (scenario_df["return_scenario"] == ret)
        subset = scenario_df[mask]
        # Weight by n_people from q2_scen (same ordering)
        matched = q2_scen[q2_scen["scenario"] == hold].reset_index(drop=True)
        weights = matched["n_people"].values
        losses = subset["annual_loss_usd"].values
        shadows = subset["savings_shadow_usd"].values
        topline_rows.append({
            "hold_scenario": hold,
            "return_scenario": ret,
            "weighted_mean_annual_loss": np.average(losses, weights=weights),
            "weighted_mean_savings_shadow": np.average(shadows, weights=weights),
        })

topline = pd.DataFrame(topline_rows)
topline.to_csv(os.path.join(OUT, "q3_topline_scenarios.csv"), index=False)
print(f"[Q3] Saved {os.path.join(OUT, 'q3_topline_scenarios.csv')}")

# ── 8. Charts ────────────────────────────────────────────────────────────────

plt.rcParams.update({"figure.dpi": 150, "font.size": 10})

# --- Chart 1: Savings shadow by subgroup (horizontal bar, base hold / 4% return) ---
fig, ax = plt.subplots(figsize=(10, 7))
plot_data = main_table.head(16).copy()  # all subgroups
plot_data["label"] = (
    plot_data["sex"] + ", " + plot_data["age_band"] + ", " + plot_data["education"]
)
plot_data = plot_data.sort_values("savings_shadow_4pct")

colors = plot_data["risk_tier"].map(
    {"high": "#d62728", "medium": "#ff7f0e", "low": "#2ca02c"}
)
bars = ax.barh(plot_data["label"], plot_data["savings_shadow_4pct"], color=colors)
ax.set_xlabel("Lifetime Savings Lost by Retirement (USD, 4% real return)")
ax.set_title("The Savings Shadow: Lifetime Wealth Cost of Gambling by Demographic")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

# Legend for risk tiers
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor="#d62728", label="High risk"),
    Patch(facecolor="#ff7f0e", label="Medium risk"),
    Patch(facecolor="#2ca02c", label="Low risk"),
]
ax.legend(handles=legend_elements, loc="lower right")
plt.tight_layout()
fig.savefig(os.path.join(PLOTS, "q3_savings_shadow_by_subgroup.png"))
plt.close()
print(f"[Q3] Saved {os.path.join(PLOTS, 'q3_savings_shadow_by_subgroup.png')}")

# --- Chart 2: Gambling burden (% of disposable income) by subgroup ---
fig, ax = plt.subplots(figsize=(10, 7))
burden_data = main_table.sort_values("gambling_burden_pct")
burden_data["label"] = (
    burden_data["sex"] + ", " + burden_data["age_band"] + ", " + burden_data["education"]
)
colors = burden_data["risk_tier"].map(
    {"high": "#d62728", "medium": "#ff7f0e", "low": "#2ca02c"}
)
ax.barh(burden_data["label"], burden_data["gambling_burden_pct"], color=colors)
ax.set_xlabel("Annual Gambling Loss as % of Disposable Income")
ax.set_title("Gambling Burden: Who Loses the Biggest Share of Their Disposable Income?")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
ax.legend(handles=legend_elements, loc="lower right")
plt.tight_layout()
fig.savefig(os.path.join(PLOTS, "q3_gambling_burden_pct.png"))
plt.close()
print(f"[Q3] Saved {os.path.join(PLOTS, 'q3_gambling_burden_pct.png')}")

# --- Chart 3: Milestone equivalents for top 5 subgroups ---
fig, axes = plt.subplots(1, 4, figsize=(16, 5), sharey=True)
top5 = main_table.head(5).copy()
top5["label"] = top5["sex"].str[0] + " " + top5["age_band"] + "\n" + top5["education"]

milestone_cols = [
    ("home_down_payments", "Home Down\nPayments", "#1f77b4"),
    ("college_degrees_funded", "College\nDegrees", "#ff7f0e"),
    ("retirement_years_funded", "Retirement\nYears", "#2ca02c"),
    ("emergency_funds", "Emergency\nFunds", "#d62728"),
]

for ax, (col, title, color) in zip(axes, milestone_cols):
    ax.barh(top5["label"], top5[col], color=color)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel("Equivalent count")

fig.suptitle(
    "What Gambling Losses Could Have Paid For (Top 5 Highest-Loss Groups, by Retirement)",
    fontsize=13, fontweight="bold", y=1.02,
)
plt.tight_layout()
fig.savefig(os.path.join(PLOTS, "q3_milestone_equivalents.png"), bbox_inches="tight")
plt.close()
print(f"[Q3] Saved {os.path.join(PLOTS, 'q3_milestone_equivalents.png')}")

# --- Chart 4: Scenario heatmap — savings shadow under different assumptions ---
# Focus on the single most-at-risk group: Male, 18-34, B.A. or higher
focus = scenario_df[
    (scenario_df["sex"] == "Male")
    & (scenario_df["age_band"] == "18-34")
    & (scenario_df["education"] == "B.A. or higher")
].copy()

pivot = focus.pivot_table(
    index="hold_scenario", columns="return_scenario", values="savings_shadow_usd"
)
# Reorder
hold_order = ["low_hold", "base_hold", "high_hold"]
ret_order = ["3% real", "4% real", "5% real"]
pivot = pivot.reindex(index=hold_order, columns=ret_order)

fig, ax = plt.subplots(figsize=(8, 4))
im = ax.imshow(pivot.values, cmap="YlOrRd", aspect="auto")

ax.set_xticks(range(len(ret_order)))
ax.set_xticklabels(ret_order)
ax.set_yticks(range(len(hold_order)))
ax.set_yticklabels(["Low hold (8%)", "Base hold (10%)", "High hold (12%)"])
ax.set_xlabel("Investment Return Assumption")
ax.set_ylabel("House Edge Scenario")
ax.set_title("Lifetime Savings Lost: Male, 18–34, College-Educated\n(Scenario Sensitivity)")

for i in range(len(hold_order)):
    for j in range(len(ret_order)):
        val = pivot.values[i, j]
        ax.text(j, i, f"${val:,.0f}", ha="center", va="center",
                fontsize=11, fontweight="bold",
                color="white" if val > pivot.values.mean() else "black")

plt.colorbar(im, ax=ax, format=mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
plt.tight_layout()
fig.savefig(os.path.join(PLOTS, "q3_scenario_heatmap.png"))
plt.close()
print(f"[Q3] Saved {os.path.join(PLOTS, 'q3_scenario_heatmap.png')}")

# ── 9. Print headline results ───────────────────────────────────────────────

print("\n" + "=" * 70)
print("Q3 HEADLINE RESULTS")
print("=" * 70)

top = main_table.head(5)
for _, row in top.iterrows():
    print(
        f"  {row['sex']}, {row['age_band']}, {row['education']}:  "
        f"loses ${row['annual_loss']:,.0f}/yr  "
        f"({row['gambling_burden_pct']:.1f}% of disposable income)  →  "
        f"${row['savings_shadow_4pct']:,.0f} lost by retirement"
    )

print()
print("Milestone equivalents for highest-risk group (Male, 18-34, B.A.+):")
toprow = main_table.iloc[0]
print(f"  Home down payments:     {toprow['home_down_payments']:.1f}")
print(f"  College degrees funded: {toprow['college_degrees_funded']:.1f}")
print(f"  Retirement years:       {toprow['retirement_years_funded']:.1f}")
print(f"  Emergency funds:        {toprow['emergency_funds']:.1f}")

print("\nDone.")
