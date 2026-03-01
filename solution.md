# M3 Modelling Challenge: Best Python-Focused Path

## Best Question to Tackle with a Coding-Heavy Python Solution

**Recommended primary question: Q2 – "Know the Spread"**

Q2 is the best fit for a strong Python solution because it naturally supports:
- predictive modeling,
- probability distributions,
- simulation (Monte Carlo),
- uncertainty quantification,
- clear visualizations by demographic groups.

It also gives you the most flexibility to show technical depth without needing highly sensitive real-world personal financial data.

---

## Suggested Strategy (High-scoring and practical)

Use **Q2 as the core model**, then connect results to Q1/Q3-style interpretation in your write-up:
- Build an annual gain/loss model for individuals by demographic profile and betting behavior.
- Convert model outputs into understandable societal impact metrics (mini-Q3 framing).
- Optionally include a lightweight disposable-income proxy to show affordability stress.

This gives you a complete narrative: **behavior -> outcomes -> consequences**.

---

## Model Concept for Q2

### 1) Inputs (features)
At minimum:
- age group
- gender (if used, handle carefully and discuss ethics)
- income band (or disposable income proxy)
- betting frequency (bets/week)
- average stake size
- risk tolerance category (low/medium/high)
- bet type mix (single bets vs parlays)

Optional enrichment:
- employment status
- education level
- region (U.S./U.K. differences)
- seasonality (sports season effects)

### 2) Behavioral assumptions
Define transparent assumptions such as:
- win probability adjusted by bet type,
- bookmaker edge (house margin),
- higher risk tolerance -> higher variance,
- higher frequency -> larger cumulative expected loss.

### 3) Output
Predict for each synthetic individual:
- expected annual net gain/loss,
- confidence interval (e.g., 5th–95th percentile from simulation),
- probability of losing more than threshold values (e.g., $500, $2,000).

---

## Recommended Python Approach

### Core stack
- `pandas` for data tables
- `numpy` for simulation
- `scipy` for distributions (optional)
- `matplotlib`/`seaborn` for plots
- `scikit-learn` (optional) for calibration or regression layer

### Implementation pattern
1. Generate a **synthetic population** with demographic distributions.
2. Simulate yearly betting outcomes per person using repeated random trials.
3. Aggregate by demographic groups.
4. Run sensitivity analysis on key assumptions:
   - house edge,
   - average stake,
   - frequency,
   - risk profile mix.
5. Visualize:
   - loss distribution histogram,
   - boxplots by age/income group,
   - heatmap of risk drivers.

---

## Using the Supplied M3 CSV (Now Cleaned)

The provided file (`online-sports-betting-personal.csv`) is a report-style table, not person-level microdata.

To make it usable for coding/modeling, this repo now includes:
- `prepare_m3_data.py`
- `data/us_demographic_long.csv` (330 rows)
- `data/aux_tables_long.csv` (47 rows)

Run:

```bash
python prepare_m3_data.py
```

Recommended usage in your model:
- Use `us_demographic_long.csv` to calibrate demographic parameters (e.g., account ownership rate, chasing behavior, high-loss risk indicators).
- Use `aux_tables_long.csv` for market-level behavior assumptions (frequency mix, monthly wager bands, participation rates).
- Since data is aggregated percentages, generate a synthetic population and sample behavior probabilities from these calibrated rates.

This keeps your submission empirically grounded while still enabling individual-level simulation outputs for Q2.

---

## Simple Mathematical Framing

For person $i$ and bet $j$:

$$
X_{ij} =
\begin{cases}
+s_{ij}(o_{ij}-1), & \text{win} \\
-s_{ij}, & \text{loss}
\end{cases}
$$

where:
- $s_{ij}$ is stake,
- $o_{ij}$ is decimal odds,
- win probability is $p_{ij}$ (adjusted for bookmaker margin).

Annual net outcome:

$$
Y_i = \sum_{j=1}^{N_i} X_{ij}
$$

Then estimate:
- $E[Y_i]$,
- quantiles of $Y_i$,
- $P(Y_i < -T)$ for thresholds $T$.

---

## Ideas That Impress Judges

- **Uncertainty-first reporting**: do not give only point predictions.
- **Fairness/ethics note**: if using demographic features, explain purpose and avoid harmful conclusions.
- **Scenario analysis**:
  - baseline,
  - recession (lower disposable income),
  - increased advertising exposure (higher frequency).
- **Interpretability**: identify top drivers of loss risk.
- **Policy relevance**: estimate how many individuals exceed “financial stress” thresholds.

---

## Recommendations for Your Final Submission

1. **Pick Q2 as your official main question.**
2. Keep assumptions explicit in a dedicated table.
3. Include at least 3 demographic comparisons and 3 scenario tests.
4. Report model limitations clearly (synthetic data, assumption sensitivity).
5. Add a short “what this means for households/society” section (Q3 linkage).

---

## Optional Extension (if you have extra time)

Add a lightweight Q1 component:
- Estimate disposable income from salary and household factors,
- define affordability ratio:

$$
\text{Gambling Burden}_i = \frac{\max(0, -Y_i)}{\text{DisposableIncome}_i}
$$

Then classify risk bands (low/moderate/high burden) to strengthen real-world impact.

---

## Bottom Line

If your goal is a **coding-forward, data-science-style submission in Python**, choose **Q2** and frame results so they also answer the spirit of Q3.