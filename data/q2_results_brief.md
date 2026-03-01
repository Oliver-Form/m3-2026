# Q2 Results Brief (Auto-generated)

## 1) Overall calibrated scenario results
- Base hold scenario: mean annual net = $-1,326, active rate = 31.2%, P(loss > $2,000) = 18.3%.
- Low vs high hold sensitivity: mean annual net shifts by $-527 per person; P(loss > $2,000) shifts by 1.8%.
- Tail risk in base scenario: P(loss > $500) = 20.7%, P(loss > $5,000) = 14.0%.

## 2) Highest-risk subgroups (base hold)
- 1. Male | 18-34 | B.A. or higher (high risk): mean annual net $-2,870, P(loss > $2,000) = 32.4%, active rate = 51.0%.
- 2. Male | 35-49 | B.A. or higher (high risk): mean annual net $-2,273, P(loss > $2,000) = 30.1%, active rate = 47.6%.
- 3. Male | 18-34 | No college (high risk): mean annual net $-1,865, P(loss > $2,000) = 24.4%, active rate = 39.7%.
- 4. Male | 35-49 | No college (high risk): mean annual net $-1,575, P(loss > $2,000) = 23.0%, active rate = 37.4%.
- 5. Female | 18-34 | B.A. or higher (medium risk): mean annual net $-343, P(loss > $2,000) = 10.3%, active rate = 21.2%.

## 3) Stage A participation model interpretation
- Positive coefficient on `sex_Male` (0.639) and `risk_score_z` (0.455) indicates higher participation odds for male and higher-risk-profile groups.
- Negative coefficients on older age groups (`age_band_50-64` = -1.414, `age_band_65+` = -1.540) indicate lower participation odds relative to ages 18-34.
- `education_No college` coefficient (-0.277) is negative in this baseline fit, suggesting lower participation odds versus B.A. or higher, conditional on other model inputs.

## 4) Files produced
- `data/q2_top_risk_subgroups.csv`
- `data/q2_scenario_deltas.csv`
- `data/q2_results_brief.md`
