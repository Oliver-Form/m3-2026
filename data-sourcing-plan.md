# Q2 Data Sourcing Plan (What You Can Realistically Get + How to Combine It)

## Goal
Build a defensible input dataset for Q2 (annual gain/loss prediction) using mostly public data plus synthetic person-level records.

---

## 1) What Data Is Realistically Available

### A) Gambling market totals and hold (U.S.)
Likely sources:
- American Gaming Association (AGA) research and state-by-state summaries
- State regulator dashboards/reports (e.g., New York, New Jersey, Pennsylvania gaming commissions)

What you can get:
- sportsbook handle (amount wagered)
- gross gaming revenue (GGR)
- implied hold rate = GGR / handle
- monthly/annual trends by state

Use in model:
- calibrate expected house edge and baseline loss intensity
- check your simulated aggregate losses against known totals

---

### B) Gambling market totals and participation (U.K.)
Likely sources:
- UK Gambling Commission official statistics
- Office for National Statistics (ONS) relevant participation releases

What you can get:
- participation rates
- total market sizes / segments
- high-level demographic trends (where published)

Use in model:
- set U.K.-specific participation and frequency assumptions
- compare with U.S. to create country scenarios

---

### C) Demographics and income capacity
U.S. likely sources:
- U.S. Census (ACS)
- Bureau of Labor Statistics (Consumer Expenditure Survey)

U.K. likely sources:
- ONS household income/family spending releases

What you can get:
- age distributions
- sex/gender distributions
- income bands, household composition
- expenditure baselines

Use in model:
- generate realistic synthetic population
- estimate disposable-income proxy for affordability/burden metrics

---

### D) Behavioral gambling survey data (already have part of this)
Current repo source:
- `online-sports-betting-personal.csv` (already cleaned with `prepare_m3_data.py`)

Additional likely sources:
- YouGov reports
- Pew reports (if available for betting behavior segments)
- academic/public policy papers with tabulated survey outcomes

What you can get:
- account ownership rates
- betting frequency bands
- self-reported win/loss tendencies
- risky behaviors (chasing losses, large one-day bets)

Use in model:
- probability distributions for behavior by demographic segment
- risk-tier definitions (low/medium/high behavior profiles)

---

### E) Operator/investor reports (public companies)
Likely sources:
- annual reports / investor decks (DraftKings, Flutter, Entain, etc.)

What you can get:
- high-level KPI trends (active users, ARPU, margin context)
- business-mix clues for assumptions

Use in model:
- sanity-check assumptions for average spend and margin ranges
- triangulate scenario bounds

---

## 2) What You Probably Cannot Get Publicly
- person-level sportsbook bet logs (bet-by-bet outcomes tied to demographics)
- deposit/withdrawal event streams per user
- exact per-user profitability from operators

Conclusion:
- build synthetic microdata calibrated to public aggregates
- clearly label synthetic assumptions in final paper

---

## 3) Recommended "Assemble-It" Data Stack for Your Submission

### Core files to maintain
1. `data/us_demographic_long.csv`  
   (from your cleaned M3 source; demographic behavior percentages)
2. `data/aux_tables_long.csv`  
   (frequency and monthly wagering distribution context)
3. `data/external_market_totals.csv`  
   (manual collection: country/state/year/month/handle/ggr/hold)
4. `data/demographic_baseline.csv`  
   (age/income/gender population shares from Census/ONS)
5. `data/q2_synthetic_population.csv`  
   (generated person-level records for simulation)

---

## 4) Merge Logic (How to Put It Together)

1. Build demographic priors from `demographic_baseline.csv`.
2. Map each synthetic person to behavior probabilities using `us_demographic_long.csv`.
3. Use `aux_tables_long.csv` to shape frequency and stake-band distributions.
4. Calibrate expected margin/hold so aggregate simulated losses align with `external_market_totals.csv`.
5. Simulate yearly outcomes per person and compute:
   - annual net gain/loss
   - probability of severe loss thresholds
   - burden ratio vs disposable income proxy

---

## 5) Minimum Viable Collection Plan (Fast)

If you have limited time, collect only:
- M3 provided survey tables (already done)
- one reliable U.S. handle/GGR source (national or a few states)
- one U.K. participation/market source
- one demographic baseline source (age + income bands)

This is enough for a defensible calibrated Monte Carlo model.

---

## 6) Data Quality Checklist
Before modeling, verify:
- time periods align (same year where possible)
- percentages are consistently scaled (0-100 vs 0-1)
- country labels are consistent (`US`, `UK`)
- segment names are standardized (e.g., `18-34`, `35-49`)
- assumptions are documented in one table

---

## 7) Suggested Citation Strategy
In your report, separate sources by role:
- calibration sources (market totals, hold)
- behavioral priors (surveys)
- demographic priors (Census/ONS)
- validation targets (published aggregates)

That structure makes your methodology easy to audit and score well.

---

## 8) Practical Next Step in This Repo
Create `data/external_market_totals.csv` with columns:
- `region`
- `year`
- `month` (optional)
- `handle`
- `ggr`
- `hold_rate`
- `source`

Then your simulation script can calibrate directly against observed totals.
