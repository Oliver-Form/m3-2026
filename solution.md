# M3 Challenge Report
## Q2: Know the Spread — Who Really Pays the Price of Sports Betting?

---

## The Big Picture

We know the sports betting industry is booming. We know the house always wins in aggregate. But here's the question nobody has a clean answer to: **who, exactly, is losing — and how much?**

Industry profit figures tell us the total pot of money flowing from bettors to bookmakers. What they don't tell us is how that pain is distributed. Is it spread thinly across millions of casual fans placing the odd weekend parlay? Or is it concentrated — hammering specific groups of people who bet harder, more often, and with less restraint?

Our model answers this. We built a simulation engine that takes a person's age, sex, education level, and behavioral risk profile, and produces a realistic projection of what their year of online sports betting looks like — how much they stake, how much comes back, and how likely they are to end the year significantly in the hole.

The answer, as it turns out, is uncomfortable: **gambling losses are not evenly distributed. They are concentrated in identifiable demographic pockets, and the people losing the most are often the ones who can least afford to treat it as entertainment.**

---

## Where Our Data Comes From

í
To make the simulation realistic at the individual-bet level — what kinds of odds people take, how stake sizes relate to payouts — we drew on a large external dataset of ~100,000 real bet records ([bets.csv](bets.csv)). Importantly, we use this dataset **only as a library of plausible bet mechanics**, not as a source of demographic truth. The "who" comes from M3; the "how each bet plays out" comes from observed betting patterns.

This distinction matters. We didn't want to overclaim by treating an external dataset as ground truth for population behavior. So we enforced a strict separation: demographics and participation from M3, bet-level mechanics from the external source, and then transparent calibration to tie them together.

Processed data tables:
- Reshaped M3 survey: [data/m3_demographic_long.csv](data/m3_demographic_long.csv)
- Model-ready subgroup input: [data/q2_model_input.csv](data/q2_model_input.csv)

---

## How the Model Works

We built this in two connected stages — first figuring out *who actually bets*, and then simulating *what happens to them over a year*.

### Stage 1: Who gambles? (The Participation Model)

Not everyone with a sportsbook account is an active bettor, and not everyone in a demographic group has an account. So we estimated the probability that a person in each subgroup (defined by sex, age bracket, and education level) is an active online sports bettor in a given year:

$$
P(\text{active bettor}) = P(\text{has account}) \times P(\text{placed a bet} \mid \text{has account})
$$

We then fit a logistic regression across subgroups to identify which demographic factors push participation up or down. The model is deliberately simple and interpretable — the goal is to see clear patterns, not to overfit noise.

**What the participation model tells us** ([data/q2_stageA_coefficients.csv](data/q2_stageA_coefficients.csv)):
- **Being male** substantially increases the odds of active betting (coefficient: +0.64 on the log-odds scale).
- **Age matters a lot.** Compared to 18–34-year-olds, people aged 50–64 and 65+ are dramatically less likely to bet actively (coefficients of -1.41 and -1.54, respectively). This is one of the strongest effects in the model.
- **Higher behavioral risk scores** predict higher participation — meaning the people most inclined to risky betting behavior are also the ones most likely to be betting at all.

Overall, about **31% of the simulated population** ends up classified as active bettors in a given year — a figure consistent with recent survey estimates.

Full participation predictions: [data/q2_stageA_predictions.csv](data/q2_stageA_predictions.csv)

### Stage 2: What happens to them? (The Annual Outcome Simulation)

This is where it gets interesting. For every active bettor, we simulate an entire year of betting using a Monte Carlo engine — essentially running thousands of individual "betting careers" and watching what happens.

Here's how it works for each simulated person:

1. **Assign a risk profile.** Using the M3 behavioral indicators — how often they chase losses, whether they've placed $100+ or $500+ single-day wagers, how frequently they deposit, whether they withdraw winnings or leave money in their account, and whether they believe they can make money from betting — we construct a composite risk score for each demographic subgroup. Groups are then bucketed into **low**, **medium**, and **high** risk tiers.

2. **Simulate betting volume.** Higher-risk bettors place more bets per year and wager larger amounts per bet. The model scales both frequency and stake size by risk tier.

3. **Simulate individual bets.** For each bet, we sample realistic odds and payout structures from the external bet-level dataset. This gives us authentic-feeling bet dynamics — the mix of small wins, near-misses, and occasional big payouts that keep people engaged.

4. **Add up the year.** Total amount staked, total payouts received, and the net result. Most people lose. Some lose a lot.

5. **Measure the damage.** For each subgroup, we compute the average annual loss and — critically — the probability of catastrophic outcomes: losing more than $500, more than $2,000, or more than $5,000 in a year.

This Monte Carlo approach (30,000 simulated individuals) gives us **full distributions of outcomes**, not just averages. That matters because gambling losses are extremely skewed — the average can look manageable while hiding a long tail of devastating individual outcomes.

Simulation outputs:
- Individual-level results: [data/q2_simulated_individual_outcomes.csv](data/q2_simulated_individual_outcomes.csv)
- Subgroup summaries: [data/q2_subgroup_summary.csv](data/q2_subgroup_summary.csv)
- Overall summary: [data/q2_overall_summary.csv](data/q2_overall_summary.csv)

---

## Stress-Testing the Results: What If We're Wrong About the House Edge?

One thing we didn't want to do is present a single set of numbers and pretend we're certain. The "house edge" — the percentage the bookmaker keeps on average — is a key driver of how much bettors lose, and it can vary.

From our external bet data, we observed an average house take (or "hold") of about **10%**. But rather than lock in that single number, we ran the entire simulation under three scenarios:

| Scenario | House Hold Rate | Mean Annual Loss per Person |
|----------|:-:|:-:|
| **Optimistic** (lower edge) | 8.1% | -$1,062 |
| **Base case** | 10.1% | -$1,326 |
| **Pessimistic** (higher edge) | 12.1% | -$1,590 |

The swing from optimistic to pessimistic is about **$527 per person per year** — meaningful, but the core story doesn't change. Even in the best-case scenario, the same groups are losing the most. The *ranking* of who's most vulnerable barely shifts across scenarios; it's the *magnitude* that moves.

Calibration details: [data/q2_calibration_summary.csv](data/q2_calibration_summary.csv) | Scenario comparisons: [data/q2_scenario_overall_summary.csv](data/q2_scenario_overall_summary.csv)

---

## The Results: A Story of Concentration

### The headline numbers

Under our base-case scenario, here's what the simulated population looks like:

- **31.2%** of people are active online sports bettors.
- The average active bettor loses **$1,326 per year**.
- About **1 in 5** people (20.7%) lose more than $500 in a year.
- Nearly **1 in 5** (18.3%) lose more than $2,000.
- **14%** lose more than $5,000 — serious money by anyone's standard.

But these averages mask what's really going on.

### Who's getting hurt the most?

When we break the results down by demographic group, a stark pattern emerges ([data/q2_top_risk_subgroups.csv](data/q2_top_risk_subgroups.csv)):

| Group | Active Rate | Mean Annual Loss | Chance of Losing $2,000+ |
|-------|:-:|:-:|:-:|
| **Men, 18–34, college-educated** | 51.0% | **$2,870** | **32.4%** |
| **Men, 35–49, college-educated** | 47.6% | **$2,273** | **30.1%** |
| **Men, 18–34, no college** | 39.7% | **$1,865** | **24.4%** |
| **Men, 35–49, no college** | 37.4% | **$1,575** | **23.0%** |
| **Women, 18–34, college-educated** | 21.2% | **$343** | **10.3%** |

The most striking finding: **young, college-educated men** are both the most likely to bet and the most likely to lose big. More than half of men aged 18–34 with a bachelor's degree are active bettors, and nearly a third of them lose over $2,000 per year. That's not a rounding error — that's a third of an entire demographic subgroup experiencing significant annual financial harm from a single activity.

The gender gap is enormous. The highest-risk female subgroup (young, college-educated women) has a mean annual loss of $343 and a 10% chance of losing $2,000+. Their male counterparts lose **eight times more on average** and face **triple the tail risk**.

Meanwhile, older adults (50+) barely register. Their participation rates drop below 13%, their risk behaviors are muted, and their average losses are modest. The betting industry's financial extraction is overwhelmingly concentrated in people under 50.

### Visualizing the patterns

These charts make the concentration of harm visually apparent:

- **Average annual loss by demographic group:** [data/plots/q2_mean_net_by_subgroup.png](data/plots/q2_mean_net_by_subgroup.png)
- **Probability of losing more than $2,000:** [data/plots/q2_tail_risk_over_2000.png](data/plots/q2_tail_risk_over_2000.png)
- **Who's actually betting — participation heatmap:** [data/plots/q2_active_rate_heatmap.png](data/plots/q2_active_rate_heatmap.png)

---

## What This Tells Us

The central insight is that gambling harm is **structural, not random**. It isn't evenly sprinkled across the population. It flows through specific channels — high participation rates in certain groups, combined with risk-seeking behavior patterns (bigger bets, more frequent deposits, chasing losses) — and pools in predictable places.

Even when we dial the house edge down to optimistic levels, the same groups dominate the loss rankings. This means the concentration pattern isn't just an artifact of how much the bookmaker takes — it's baked into *who bets* and *how they bet*. Changing the house edge shifts how much everyone loses, but it doesn't change the fundamental inequality of who bears the burden.

This has real implications. If policymakers or public health advocates want to mitigate gambling harm, broad-based interventions (like slightly reducing betting limits for everyone) may be less effective than targeted approaches aimed at the specific demographic-behavioral intersections where the damage concentrates.

---

## Honest Limitations

We want to be transparent about what this model can and can't do:

1. **We're working with group-level survey data, not individual tracking.** The M3 survey tells us how groups behave on average — it doesn't follow individuals over time. Our simulation creates realistic individual-level outcomes, but they're synthetic draws from group-level patterns.

2. **The external bet data is used carefully but has limits.** We sourced it for realistic bet dynamics, not demographic inference. We've been explicit about this separation, but it means our stake/payout mechanics are only as good as that dataset.

3. **Modeling choices affect the numbers.** How we scale bet frequency and stake size by risk tier involves judgment calls. That's why we emphasize scenario ranges and relative rankings over precise dollar figures. The *ordering* of who's most at risk is robust; the exact dollar amounts should be read as indicative.

4. **Self-reported survey data has known biases.** People tend to underreport gambling losses and overreport wins. If anything, this means our estimates may be conservative.

---

## Reproducibility

Every number, table, and chart in this report is generated by running five scripts in sequence. No manual data manipulation, no hand-tuned figures — just code and data in:

```bash
python prepare_m3_data.py
python build_q2_model_input.py
python run_q2_baseline_model.py
python run_q2_calibrated_analysis.py
python build_q2_results_brief.py
```

All intermediate outputs are saved to the [data/](data/) directory for inspection.