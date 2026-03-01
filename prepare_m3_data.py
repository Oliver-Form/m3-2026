from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT_CSV = ROOT / "online-sports-betting-personal.csv"
OUTPUT_DIR = ROOT / "data"
LEFT_OUT = OUTPUT_DIR / "us_demographic_long.csv"
RIGHT_OUT = OUTPUT_DIR / "aux_tables_long.csv"


def normalize_text(value: str) -> str:
    return " ".join(value.replace("\n", " ").split()).strip()


def parse_percent(value: str) -> float | None:
    cleaned = normalize_text(value)
    if not cleaned:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    if not match:
        return None
    return float(match.group(0))


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [[cell.strip() for cell in row] for row in csv.reader(file)]


def extract_left_table(rows: list[list[str]]) -> list[dict[str, str | float | int]]:
    group_row = rows[1]
    segment_row = rows[2]

    segments: list[tuple[int, str, str]] = []
    active_group = ""
    for col in range(1, 11):
        group_value = normalize_text(group_row[col])
        if group_value:
            active_group = group_value
        segment_value = normalize_text(segment_row[col])
        if segment_value:
            segments.append((col, active_group, segment_value))

    records: list[dict[str, str | float | int]] = []
    for row_index in range(3, len(rows)):
        row = rows[row_index]
        question = normalize_text(row[0]) if len(row) > 0 else ""
        if not question or question.lower().startswith("source:"):
            continue

        for col, group_name, segment_name in segments:
            if col >= len(row):
                continue
            value = parse_percent(row[col])
            if value is None:
                continue
            records.append(
                {
                    "question": question,
                    "segment_group": group_name,
                    "segment": segment_name,
                    "percent": value,
                }
            )
    return records


def extract_right_tables(rows: list[list[str]]) -> list[dict[str, str | float]]:
    records: list[dict[str, str | float]] = []
    current_section = ""
    headers: list[str] = []

    for row in rows:
        if len(row) < 16:
            row = row + [""] * (16 - len(row))

        label = normalize_text(row[12])
        values = [normalize_text(row[13]), normalize_text(row[14]), normalize_text(row[15])]
        numeric_values = [parse_percent(value) for value in values]

        if not label and not any(values):
            continue

        lower_label = label.lower()
        if lower_label.startswith("source:"):
            current_section = ""
            headers = []
            continue

        if label and not any(values):
            current_section = label
            headers = []
            continue

        if not any(number is not None for number in numeric_values):
            if any(values):
                headers = [value for value in values]
                if label and not current_section:
                    current_section = label
            continue

        if not headers:
            headers = ["column_1", "column_2", "column_3"]

        for idx, number in enumerate(numeric_values):
            if number is None:
                continue
            records.append(
                {
                    "section": current_section or "Auxiliary table",
                    "metric": label,
                    "series": headers[idx] if idx < len(headers) and headers[idx] else f"column_{idx + 1}",
                    "percent": number,
                }
            )

    return records


def write_csv(path: Path, records: list[dict[str, str | float | int]]) -> None:
    if not records:
        return
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = list(records[0].keys())
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    rows = read_rows(INPUT_CSV)
    left_records = extract_left_table(rows)
    right_records = extract_right_tables(rows)
    write_csv(LEFT_OUT, left_records)
    write_csv(RIGHT_OUT, right_records)
    print(f"wrote {LEFT_OUT} ({len(left_records)} rows)")
    print(f"wrote {RIGHT_OUT} ({len(right_records)} rows)")


if __name__ == "__main__":
    main()