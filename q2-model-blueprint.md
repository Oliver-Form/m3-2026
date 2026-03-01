# Q2 Blueprint: Predict Who Gambles and Annual Gain/Loss

## Objective
Build a model that answers:
1) Given `sex`, `age`, and `education` (`No college` vs `B.A. or higher`), how likely is someone to participate in online sports gambling?
2) Conditional on participating, how much do they gain/lose over one year?
3) How does inferred risk tolerance shift the loss distribution?

This blueprint uses the M3 provided demographic table as the strongest prior source and combines it with your larger bet/odds dataset for realistic annual outcome simulation.

---

## What the M3 Data Gives You (Directly Useful Signals)
From `m3-provided-demographic-data.csv`, you already have group-level rates by sex/age/education for:
- account ownership (entry to market)
- placing at least one online bet
- investigation frequency
- deposit frequency
- withdrawal behavior
- chasing losses
- high single-day bet thresholds (`$100+`, `$500+`)
- self-belief (`I think I can make money`)
- win/lose/break-even self-report

These are perfect to build a **behavioral risk index** and participation priors by demographic group.

---

## Best Model Architecture (Recommended)
Use a **two-stage hurdle model + Monte Carlo outcome engine**.

### Stage A: Participation model (binary)
Predict probability of annual participation:
\[
P(\text{gamble}=1\mid \text{sex, age, education})
\]

Recommended form:
- logistic regression (simple, interpretable), or
- Bayesian logistic (better uncertainty with sparse subgroup counts).

Target for calibration from M3:
- `Has account with online sportsbook`
- adjusted by `% have placed a bet` among account holders.

Practical derived target:
\[
P(\text{active bettor}) \approx P(\text{has account}) \times P(\text{placed bet} \mid \text{account})
\]

### Stage B: Annual net amount model (continuous, heavy-tailed)
For those with `gamble=1`, model annual net gain/loss:
\[
Y = \text{annual winnings} - \text{annual losses}
\]

Recommended form:
- **mixture distribution** (e.g., lognormal body + Pareto tail for stakes/volume), or
- quantile regression / gradient boosting for robust conditional distribution estimation.

Because gambling outcomes are skewed and fat-tailed, do **not** use plain Gaussian regression.

### Stage C: Monte Carlo bet-path simulation
Convert risk profile + bet style assumptions into yearly outcomes:
1. sample number of bets/year from frequency profile
2. sample stake sizes from subgroup-specific stake distribution
3. sample bet odds/type from the large odds dataset (linked by risk tier)
4. apply bookmaker margin / implied edge
5. aggregate to annual net per person

This gives full distributions, not just means.

---

## Risk Tolerance Construction (Key Part You Asked For)
Construct latent `risk_score` from M3 subgroup metrics.

### Suggested normalized components
For each demographic subgroup \(g\):
- `chase_rate_g`
- `high_bet_100_g`
- `high_bet_500_g`
- `weekly_deposit_g`
- `leave_winnings_in_account_g`
- `belief_can_make_money_g`
- inverse withdrawal discipline (e.g., fewer cash-outs => higher risk)

Compute:
\[
risk\_score_g = \sum_k w_k z_{gk}
\]
where \(z_{gk}\) are standardized subgroup metrics and \(w_k\) are either:
- equal weights (fast baseline), or
- weights learned by PCA / supervised fit against known loss proxies.

Then bin to tiers:
- low risk (bottom 33%)
- medium risk (middle 33%)
- high risk (top 33%)

Use tier to control:
- bet frequency,
- average stake,
- preference for longer odds/parlays,
- variance of returns.

---

## How to Link to Your Big Bet/Odds Dataset
Use the big dataset to estimate realistic bet-level mechanics:
- empirical odds distribution by bet type
- implied probabilities and overround (house edge)
- typical stake-size relationships if available

Map risk tiers to odds choices:
- low risk: shorter odds, lower variance
- medium risk: balanced distribution
- high risk: longer odds/parlays, higher variance and larger downside tails

Then simulate annual paths for synthetic individuals sampled from demographic groups.

---

## End-to-End Pipeline (Implementation Steps)
1. **Reshape M3 table** into long tidy format with columns:
   - `metric`, `sex`, `age_band`, `education`, `value_pct`
2. **Build subgroup priors** for participation and risk components.
3. **Create synthetic population** with features:
   - `sex`, `age_band`, `education`, `risk_tier`
4. **Fit Stage A** participation model on calibrated subgroup targets.
5. **Calibrate Stage B/Simulation** parameters to known aggregates (e.g., handle/GGR).
6. **Run Monte Carlo** (e.g., 5k–50k people, 500+ simulation seeds).
7. **Output**:
   - probability of gambling by subgroup
   - expected annual net
   - median and 5/95 percentiles
   - probability of losing more than thresholds (e.g., $500, $2,000, $5,000)

---

## Minimum Viable Version (Fast + Defensible)
If you need speed:
- Stage A: logistic with only `sex + age_band + education`
- Risk score: equal-weight index from `chase`, `high_bet_500`, `weekly_deposit`, `leave_winnings`
- Simulation: 3 risk-tier-specific parameter sets (frequency, stake, odds preference)
- Calibrate one global house edge and one variance multiplier per risk tier

This is strong enough for competition quality if assumptions are transparent.

---

## Suggested Outputs for Your Report
Include these tables/plots:
1. Participation probability heatmap (`sex x age`, split by education)
2. Annual net loss distribution by subgroup (box/violin plots)
3. Tail-risk chart: \(P(\text{loss} > T)\) by subgroup for multiple \(T\)
4. Sensitivity analysis (house edge ±, frequency ±, risk-score weights ±)

---

## Validation Strategy
Use three checks:
1. **Calibration check**: simulated aggregate losses align with known market totals within tolerance.
2. **Face-validity check**: subgroup ranking resembles M3 behavior indicators (e.g., higher chasing => higher losses).
3. **Stress check**: results stable under reasonable parameter perturbations.

---

## Core Assumptions to State Explicitly
- M3 subgroup percentages are treated as representative priors.
- Self-reported win/loss is directional, not exact monetary truth.
- Bet-level outcome process is approximated from available odds/market data.
- Unobserved factors (income, psychology, promotions) are partially absorbed into risk tiers.

---

## Practical Recommendation
For your specific question (sex, age, education → likelihood and amount), the **best balance of rigor + implementability** is:

- **Hurdle model** for participation + annual amount,
- **latent risk index** from M3 behavioral indicators,
- **Monte Carlo engine** tied to real odds distributions from your large dataset.

This gives interpretable subgroup probabilities and realistic annual gain/loss distributions with uncertainty bands.

---

## Optional Next File to Add
If you want, add a second file `q2-model-spec.csv` listing exact parameters to estimate:
- participation coefficients
- risk-index weights
- per-tier frequency/stake/odds parameters
- calibration constants (house edge multipliers)

That makes coding and tuning much faster and reproducible.