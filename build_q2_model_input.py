from __future__ import annotations

from itertools import product
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
INPUT_PATH = ROOT / "data" / "m3_demographic_long.csv"
OUTPUT_PATH = ROOT / "data" / "q2_model_input.csv"


def normalize_text(value: str) -> str:
    return " ".join(str(value).replace('"', "").split()).strip().lower()


def clamp_percent(value: float) -> float:
    return max(0.0, min(100.0, value))


def find_question(df: pd.DataFrame, contains_text: str) -> str:
    token = normalize_text(contains_text)
    matches = sorted({q for q in df["question"].unique() if token in normalize_text(q)})
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one question for token '{contains_text}', found: {matches}")
    return matches[0]


def find_response(df: pd.DataFrame, question: str, contains_text: str) -> str:
    token = normalize_text(contains_text)
    subset = df[df["question"] == question]
    matches = sorted({r for r in subset["response"].unique() if token in normalize_text(r)})
    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one response for token '{contains_text}' under question '{question}', found: {matches}"
        )
    return matches[0]


def get_rate(
    df: pd.DataFrame,
    question: str,
    segment_group: str,
    segment: str,
    response: str | None = None,
) -> float:
    subset = df[
        (df["question"] == question)
        & (df["segment_group"] == segment_group)
        & (df["segment"] == segment)
    ]
    if response is not None:
        subset = subset[subset["response"] == response]

    if subset.empty:
        raise ValueError(
            f"No rate found for question='{question}', response='{response}', segment_group='{segment_group}', segment='{segment}'"
        )
    return float(subset.iloc[0]["percent"])


def combined_rate(
    df: pd.DataFrame,
    question: str,
    sex: str,
    age: str,
    education: str,
    response: str | None = None,
    base_year: str = "2025",
) -> float:
    base = get_rate(df, question, "Total by year", base_year, response=response)
    sex_rate = get_rate(df, question, "Gender", sex, response=response)
    age_rate = get_rate(df, question, "Age", age, response=response)
    edu_rate = get_rate(df, question, "Eduation", education, response=response)

    if base <= 0:
        return 0.0

    combined = base * (sex_rate / base) * (age_rate / base) * (edu_rate / base)
    return clamp_percent(combined)


def normalized_weighted_average(values: list[float], weights: list[float]) -> float:
    total = sum(values)
    if total <= 0:
        return 0.0
    probs = [value / total for value in values]
    return sum(prob * weight for prob, weight in zip(probs, weights))


def main() -> None:
    df = pd.read_csv(INPUT_PATH)

    question_has_account = find_question(df, "has account with online sportsbook")
    question_placed_bet = find_question(df, "percent that have placed a bet on a sporting event")
    question_chased = find_question(df, "percent that have chased")
    question_high_100 = find_question(df, "percent that have bet a total of $100 or more")
    question_high_500 = find_question(df, "percent that have bet a total of $500 or more")
    question_belief = find_question(df, "i think i can make money by placing bets")
    question_deposit = find_question(df, "how often do you depost money")
    question_withdraw = find_question(df, "how often do you withdraw winnings")
    question_investigate = find_question(df, "how often do you investigate possible bets")
    question_largest_win = find_question(df, "largest amount of money you have ever won")

    response_weekly_deposit = find_response(df, question_deposit, "weekly or more often")
    response_leave_winnings = find_response(df, question_withdraw, "leave my winnings in the account")
    response_never_withdraw = find_response(df, question_withdraw, "never withdrawn")

    investigate_responses = [
        find_response(df, question_investigate, "more than 2 times a day"),
        find_response(df, question_investigate, "once or twice each day"),
        find_response(df, question_investigate, "a couple of times a week"),
        find_response(df, question_investigate, "once in a while"),
        find_response(df, question_investigate, "never"),
    ]
    investigate_weights = [2.5, 1.5, 0.35, 0.1, 0.0]

    largest_win_responses = [
        find_response(df, question_largest_win, "$50 or less"),
        find_response(df, question_largest_win, "$50-$99.99"),
        find_response(df, question_largest_win, "$100-$199.99"),
        find_response(df, question_largest_win, "$200-$499.99"),
        find_response(df, question_largest_win, "$500-$999.99"),
        find_response(df, question_largest_win, "$1000 or more"),
    ]
    largest_win_weights = [25.0, 75.0, 150.0, 350.0, 750.0, 1250.0]

    sexes = ["Male", "Female"]
    ages = ["18-34", "35-49", "50-64", "65+"]
    educations = ["No college", "B.A. or higher"]

    rows: list[dict[str, float | str]] = []
    for sex, age, education in product(sexes, ages, educations):
        has_account_rate = combined_rate(df, question_has_account, sex, age, education)
        placed_bet_given_account_rate = combined_rate(df, question_placed_bet, sex, age, education)
        p_has_account = has_account_rate / 100.0
        p_placed_bet_given_account = placed_bet_given_account_rate / 100.0
        p_active_bettor = p_has_account * p_placed_bet_given_account

        chase_rate = combined_rate(df, question_chased, sex, age, education)
        high_bet_100_rate = combined_rate(df, question_high_100, sex, age, education)
        high_bet_500_rate = combined_rate(df, question_high_500, sex, age, education)
        weekly_deposit_rate = combined_rate(
            df,
            question_deposit,
            sex,
            age,
            education,
            response=response_weekly_deposit,
        )
        leave_winnings_rate = combined_rate(
            df,
            question_withdraw,
            sex,
            age,
            education,
            response=response_leave_winnings,
        )
        never_withdraw_rate = combined_rate(
            df,
            question_withdraw,
            sex,
            age,
            education,
            response=response_never_withdraw,
        )
        belief_can_make_money_rate = combined_rate(df, question_belief, sex, age, education)

        investigate_values = [
            combined_rate(df, question_investigate, sex, age, education, response=response)
            for response in investigate_responses
        ]
        expected_investigations_per_day = normalized_weighted_average(
            investigate_values,
            investigate_weights,
        )

        largest_win_values = [
            combined_rate(df, question_largest_win, sex, age, education, response=response)
            for response in largest_win_responses
        ]
        expected_max_win_day_proxy = normalized_weighted_average(
            largest_win_values,
            largest_win_weights,
        )

        risk_score_raw = (
            0.25 * (chase_rate / 100.0)
            + 0.20 * (high_bet_500_rate / 100.0)
            + 0.15 * (high_bet_100_rate / 100.0)
            + 0.15 * (weekly_deposit_rate / 100.0)
            + 0.15 * (leave_winnings_rate / 100.0)
            + 0.10 * (belief_can_make_money_rate / 100.0)
        )

        rows.append(
            {
                "sex": sex,
                "age_band": age,
                "education": education,
                "has_account_rate": has_account_rate,
                "placed_bet_given_account_rate": placed_bet_given_account_rate,
                "p_has_account": p_has_account,
                "p_placed_bet_given_account": p_placed_bet_given_account,
                "p_active_bettor": p_active_bettor,
                "chase_rate": chase_rate,
                "high_bet_100_rate": high_bet_100_rate,
                "high_bet_500_rate": high_bet_500_rate,
                "weekly_deposit_rate": weekly_deposit_rate,
                "leave_winnings_rate": leave_winnings_rate,
                "never_withdraw_rate": never_withdraw_rate,
                "belief_can_make_money_rate": belief_can_make_money_rate,
                "expected_investigations_per_day": expected_investigations_per_day,
                "expected_max_win_day_proxy": expected_max_win_day_proxy,
                "risk_score_raw": risk_score_raw,
            }
        )

    output = pd.DataFrame(rows)
    output["risk_score_z"] = (output["risk_score_raw"] - output["risk_score_raw"].mean()) / output[
        "risk_score_raw"
    ].std(ddof=0)
    output["risk_tier"] = pd.qcut(output["risk_score_raw"], q=3, labels=["low", "medium", "high"])
    output = output.sort_values(["sex", "age_band", "education"]).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_PATH, index=False)
    print(f"wrote {OUTPUT_PATH} ({len(output)} rows)")


if __name__ == "__main__":
    main()
