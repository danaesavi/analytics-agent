# agent/run.py
import argparse
from agent.planner import Planner
from agent.executor import Executor
from agent.reporter import Reporter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to CSV or Parquet file")
    parser.add_argument("--question", required=True, help="Natural language question")
    args = parser.parse_args()

    planner = Planner()
    executor = Executor()
    reporter = Reporter()

    plan = planner.create_plan(question=args.question, data_path=args.data)
    results = executor.execute(plan)
    out_dir = reporter.generate(plan, results)

    print(f"Report saved to: {out_dir}")


if __name__ == "__main__":
    main()
