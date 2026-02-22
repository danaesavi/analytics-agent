# eval/run_eval.py
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path
from typing import Any, Dict, List

import yaml

from agent.planner import Planner
from agent.executor import Executor
from agent.reporter import Reporter


def load_questions(path: Path) -> List[Dict[str, Any]]:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, list):
        raise ValueError("questions.yaml must be a list of {id, question} items")
    for item in data:
        if "id" not in item or "question" not in item:
            raise ValueError("Each question must have 'id' and 'question'")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Run eval suite for analytics-agent")
    parser.add_argument("--data", required=True, help="Path to dataset (csv/parquet)")
    parser.add_argument("--questions", default="eval/questions.yaml", help="Path to questions.yaml")
    parser.add_argument("--out", default="eval/results.csv", help="Where to write results CSV")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of questions (0 = all)")
    args = parser.parse_args()

    data_path = args.data
    questions_path = Path(args.questions)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    planner = Planner()
    executor = Executor()
    reporter = Reporter()

    questions = load_questions(questions_path)
    if args.limit and args.limit > 0:
        questions = questions[: args.limit]

    rows: List[Dict[str, Any]] = []
    n_ok = 0

    for item in questions:
        qid = str(item["id"])
        question = str(item["question"])

        t0 = time.time()
        status = "ok"
        error = ""
        out_dir = ""

        try:
            plan = planner.create_plan(question=question, data_path=data_path)
            results = executor.execute(plan)
            out_dir = reporter.generate(plan, results)
            n_ok += 1
        except Exception as e:
            status = "error"
            error = f"{type(e).__name__}: {e}"

        dt_ms = int((time.time() - t0) * 1000)

        rows.append(
            {
                "id": qid,
                "question": question,
                "status": status,
                "latency_ms": dt_ms,
                "output_dir": out_dir,
                "error": error,
            }
        )

        print(f"[{status.upper():5}] {qid}: {question} ({dt_ms} ms){' -> ' + out_dir if out_dir else ''}")
        if error:
            print(f"        {error}")

    # Write CSV
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "question", "status", "latency_ms", "output_dir", "error"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print()
    print(f"Wrote results to {out_path}")
    print(f"Passed {n_ok}/{len(rows)}")


if __name__ == "__main__":
    main()