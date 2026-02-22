# agent/reporter.py
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import matplotlib.pyplot as plt

from agent.planner import AnalysisPlan


class Reporter:
    def generate(self, plan: AnalysisPlan, results: Dict[str, Any]) -> str:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path("outputs") / run_id
        out_dir.mkdir(parents=True, exist_ok=True)

        (out_dir / "plan.json").write_text(json.dumps(plan.to_dict(), indent=2))
        (out_dir / "metadata.json").write_text(json.dumps({"df_shape": results.get("df_shape")}, indent=2))

        table = results["table"]
        chart_path = out_dir / "chart.png"

        plot = results.get("plot", {})
        plt.figure()

        if plot.get("kind") == "bar":
            xcol = plot["x"]
            ycol = plot["y"]
            x = table[xcol].astype(str)
            y = table[ycol]
            plt.bar(x, y)
            plt.xticks(rotation=30, ha="right")
            plt.title(plot.get("title", "Top-K"))
        else:
            plt.title("Result")

        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

        report_md = out_dir / "report.md"
        report_md.write_text(
            "\n".join(
                [
                    "# Analytics Agent Report",
                    "",
                    f"**Question:** {plan.question}",
                    "",
                    "## Plan",
                    "```json",
                    json.dumps(plan.to_dict(), indent=2),
                    "```",
                    "",
                    "## Results (table)",
                    "",
                    table.to_markdown(index=False),
                    "",
                    "## Chart",
                    "",
                    f"![chart](./{chart_path.name})",
                    "",
                ]
            )
        )

        return str(out_dir)