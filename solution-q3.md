# M3 Challenge Report
## Q3: Don't Break the Bank — The Savings Shadow

---

## The Question Behind the Question

Q1 told us how much money people have left after paying for the basics. Q2 told us how much of that money disappears into sports betting apps. Now Q3 asks us to step back and make sense of what that means for real people's lives.

There are many ways to frame gambling's impact — comparisons to other entertainment, debt risk, household budget stress. But we chose to answer what we think is the most unsettling version of the question: **what does a gambling habit silently cost you over a lifetime?**

Not the cost you see — the bets placed, the balance going down. The cost you *never* see: the wealth you would have had if that money had been saved and left to grow. We call this **the savings shadow** — the gap between the financial life you're living and the one you could have had.

The math is straightforward. The results are not.

---

## From Annual Losses to Lifetime Consequences

### The core calculation

Our approach connects Q1 and Q2 directly. For every demographic subgroup, we already know two things:

1. **From Q1:** Their estimated annual disposable income — what's left after taxes, rent, food, and healthcare.
2. **From Q2:** Their estimated annual gambling loss — the average net money lost to online sports betting per year.

The first thing we compute is the **gambling burden ratio**: what share of a person's disposable income — their "free money" — is consumed by betting losses.

$$
\text{gambling burden} = \frac{\text{annual gambling loss}}{\text{annual disposable income}}
$$

Then we ask: what if that money had been invested instead? If someone saves a fixed amount every year and earns a reasonable return, the total grows through compound interest. This is the most basic principle in personal finance — money invested early grows exponentially over time. We compute the **future value** of annual gambling losses as if they had been invested from the person's current age until retirement at 65:

$$
\text{savings shadow} = \text{annual loss} \times \frac{(1 + r)^{T} - 1}{r}
$$

where $r$ is the assumed annual real (inflation-adjusted) return and $T$ is years until retirement.

We use a baseline of **4% real annual return** — the long-run average for a diversified portfolio after inflation. This isn't speculative; it's the number financial planners use for conservative retirement projections.

### A note on disposable income granularity

The M3-provided disposable income data is broken down by age band but not by sex or education. So within each age group, we apply the same disposable income figure across all sex × education subgroups. This means our burden ratios are driven primarily by differences in gambling losses (which *are* fully subgroup-specific from Q2) rather than differences in income. We note this transparently: if anything, income differences by education would widen the burden gap further (lower-income subgroups losing a higher share), making our estimates conservative for the most vulnerable groups.

---

## What the Numbers Say

### The gambling burden: who's losing the biggest share?

| Group | Annual Loss | Disposable Income | Burden (% of free money) |
|-------|:-:|:-:|:-:|
| **Men 18–34, college-educated** | $1,860 | $20,475 | **9.1%** |
| **Men 35–49, college-educated** | $1,349 | $16,001 | **8.4%** |
| **Men 35–49, no college** | $915 | $16,001 | **5.7%** |
| **Men 18–34, no college** | $1,146 | $20,475 | **5.6%** |
| Women 18–34, college-educated | $228 | $20,475 | 1.1% |
| Women 35–49, college-educated | $174 | $16,001 | 1.1% |
| Men 50–64, college-educated | $517 | $18,374 | 2.8% |
| All other groups | <$170 | — | <1% |

One in eleven dollars of disposable income for young, college-educated men vanishes into betting apps. For all women and most older adults, the figure is negligible. The asymmetry is stark.

*(Visual: [data/plots/q3_gambling_burden_pct.png](data/plots/q3_gambling_burden_pct.png))*

### The savings shadow: what that money could have become

Here's where compound growth turns a concerning annual figure into a devastating lifetime one. A 26-year-old (the midpoint of our 18–34 bracket) has 39 years until retirement. Every dollar not invested today is a dollar that doesn't compound for four decades.

| Group | Annual Loss | Years to 65 | **Savings Shadow (4% real)** |
|-------|:-:|:-:|:-:|
| **Men 18–34, college-educated** | $1,860 | 39 | **$168,163** |
| **Men 18–34, no college** | $1,146 | 39 | **$103,650** |
| **Men 35–49, college-educated** | $1,349 | 23 | **$49,384** |
| **Men 35–49, no college** | $915 | 23 | **$33,513** |
| Women 18–34, college-educated | $228 | 39 | $20,650 |
| Men 50–64, college-educated | $517 | 8 | $4,760 |

A young college-educated man who bets at the average rate for his demographic is on track to arrive at retirement **$168,000 poorer** than if he'd put that same money into a basic index fund. That's not a worst-case scenario — that's the average outcome for his group.

*(Visual: [data/plots/q3_savings_shadow_by_subgroup.png](data/plots/q3_savings_shadow_by_subgroup.png))*

---

## Making It Real: What $168,000 Buys

Abstract dollar figures, even large ones, can feel distant. So we translated the savings shadow into tangible life milestones using standard US benchmarks:

For the highest-loss group (**men, 18–34, college-educated**), the lifetime savings shadow of $168,163 is equivalent to:

| Milestone | Equivalents |
|-----------|:-:|
| **Home down payments** (20% on median US home) | **2.6** |
| **Four-year public college degrees** (in-state, tuition + living) | **1.5** |
| **Years of retirement spending** (at median retiree consumption) | **3.2** |
| **Fully-funded emergency reserves** (6 months of expenses) | **6.5** |

Put differently: the money this group loses to betting over a career could fund **a child's entire college education and still leave enough for a three-year head start on retirement**. Or it could cover the down payment on two and a half homes.

These aren't hypothetical future dollars — they're the real purchasing power (in today's money, since we use inflation-adjusted returns) that quietly evaporates, one $20 parlay at a time.

*(Visual: [data/plots/q3_milestone_equivalents.png](data/plots/q3_milestone_equivalents.png))*

---

## What If We're Wrong? Scenario Sensitivity

We don't want to hang the story on one set of assumptions. Two key parameters drive the savings shadow: how much the house takes (the hold rate, from Q2's calibration) and how much investments would have earned (the return rate). We ran the calculation across a 3×3 grid of scenarios.

**For the highest-risk group (men, 18–34, college-educated):**

| | 3% real return | 4% real return | 5% real return |
|---|:-:|:-:|:-:|
| **Low hold (8%)** | $169,159 | $211,721 | $267,189 |
| **Base hold (10%)** | $207,282 | **$259,436** | $327,405 |
| **High hold (12%)** | $245,405 | $307,152 | $387,621 |

The range spans from ~$169,000 (optimistic on both fronts) to nearly **$388,000** (pessimistic hold, optimistic returns). Even in the most conservative corner of this grid, the savings shadow exceeds $169,000. In the most aggressive-but-plausible scenario, it approaches **$400,000** — almost half a million dollars in lost lifetime wealth from a single behavioral pattern.

*(Visual: [data/plots/q3_scenario_heatmap.png](data/plots/q3_scenario_heatmap.png))*

**Population-wide averages** tell a similar story. Across all demographic groups (weighted by population share), the average savings shadow ranges from $57,000 (low hold, low return) to $126,000 (high hold, high return), with a base case of **$86,000** per person.

Full scenario data: [data/q3_topline_scenarios.csv](data/q3_topline_scenarios.csv)

---

## The Uncomfortable Insight

The savings shadow reveals something that annual loss statistics alone cannot: **gambling doesn't just cost you money today — it costs you a fundamentally different financial future.**

A $1,860 annual loss is noticeable but manageable. Many people would shrug at it — it's less than $160 a month, the cost of a couple of nice dinners. But the same amount, compounded over a career, is the difference between having a retirement cushion and not having one. Between giving your kids a college fund and telling them to take out loans. Between owning your home outright at 65 and still carrying a mortgage.

And critically, this burden falls unevenly. The groups who bet the most and lose the most — young men — are exactly the groups with the longest time horizons ahead of them. They have the most to lose from compound growth they'll never see. The savings shadow is deepest precisely where it's least visible: at the beginning of a career, when $1,800 a year feels like nothing, but is quietly shaping the trajectory of an entire financial life.

Older adults, by contrast, barely register. Their participation rates are low, their losses are modest, and their shorter time horizons mean even those losses don't compound into life-altering sums. The savings shadow is, in a real sense, a young person's problem.

---

## Limitations

1. **We assume consistency.** The model applies the same annual loss over the full horizon to retirement. In reality, some people stop betting, others escalate. We don't model individual trajectories — this is a "what if current behavior persists" projection, not a prediction.

2. **Not everyone would invest.** The savings shadow assumes the money would have earned a market return. Some of it would have been spent on other things. We frame this explicitly as an *opportunity cost* — the upper bound on what's being given up — not a guaranteed outcome.

3. **Disposable income is age-level only.** As noted, we can't split income by sex or education within age bands. This makes the burden ratios approximate, though the direction of any bias (higher-educated groups likely have more income, making their burden ratios slightly lower) is known.

4. **The 4% real return is a benchmark, not a promise.** Markets vary. We show the 3%–5% range to bracket uncertainty.

---

## Reproducibility

This analysis is generated by a single script on top of Q2 outputs:

```bash
python run_q3_savings_shadow.py
```

Inputs: [disposable-income-by-age.csv](disposable-income-by-age.csv), [data/q2_subgroup_summary.csv](data/q2_subgroup_summary.csv), [data/q2_scenario_subgroup_summary.csv](data/q2_scenario_subgroup_summary.csv)

Outputs:
- [data/q3_savings_shadow.csv](data/q3_savings_shadow.csv) — full burden and shadow table
- [data/q3_scenario_grid.csv](data/q3_scenario_grid.csv) — all subgroups × all scenarios
- [data/q3_topline_scenarios.csv](data/q3_topline_scenarios.csv) — population-weighted summaries
- Charts: [data/plots/q3_savings_shadow_by_subgroup.png](data/plots/q3_savings_shadow_by_subgroup.png), [data/plots/q3_gambling_burden_pct.png](data/plots/q3_gambling_burden_pct.png), [data/plots/q3_milestone_equivalents.png](data/plots/q3_milestone_equivalents.png), [data/plots/q3_scenario_heatmap.png](data/plots/q3_scenario_heatmap.png)
