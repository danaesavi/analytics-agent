# agent/executor.py
from typing import Any, Dict

import pandas as pd

from agent.planner import AnalysisPlan
from agent.tools.aggregations import topk_group_metric
from agent.tools.compare import compare_groups
from agent.tools.metrics import add_occupancy_proxy, add_revenue_proxy




class Executor:
    def _load(self, path: str) -> pd.DataFrame:
        if path.endswith(".parquet"):
            return pd.read_parquet(path)
        if path.endswith(".csv"):
            return pd.read_csv(path)
        raise ValueError(f"Unsupported file type: {path}")

    def execute(self, plan: AnalysisPlan) -> Dict[str, Any]:
        df = self._load(plan.data_path)

        # Resolve metric (base vs derived)
        if plan.derived_metric == "occupancy_proxy":
            df = add_occupancy_proxy(df)
            metric_col = "occupancy_proxy"
        elif plan.derived_metric == "revenue_proxy":
            df = add_revenue_proxy(df)
            metric_col = "revenue_proxy"
        else:
            metric_col = plan.metric_col

        if plan.analysis_type == "topk":
            if not plan.group_col:
                raise ValueError("topk requires plan.group_col")
            if not metric_col:
                raise ValueError("topk requires a metric (metric_col or derived_metric)")

            min_group_size = 10 if plan.group_col == "neighbourhood" else 1

            res = topk_group_metric(
                df=df,
                group_col=plan.group_col,
                metric_col=metric_col,
                agg=plan.agg,
                k=plan.top_k,
                min_group_size=min_group_size,
            )
            return {
                "table": res.table,
                "plot": {
                    "kind": "bar",
                    "x": plan.group_col,
                    "y": "value",
                    "title": f"Top {plan.top_k} {plan.group_col} by {plan.agg}({metric_col})",
                },
                "df_shape": df.shape,
            }

        elif plan.analysis_type == "compare":
            if not plan.compare_col:
                raise ValueError("compare requires plan.compare_col")
            if not metric_col:
                raise ValueError("compare requires a metric (metric_col or derived_metric)")

            res = compare_groups(
                df=df,
                compare_col=plan.compare_col,
                metric_col=metric_col,
                agg=plan.agg,
            )

            return {
                "table": res,
                "plot": {
                    "kind": "bar",
                    "x": plan.compare_col,
                    "y": "value",
                    "title": f"{plan.agg}({metric_col}) by {plan.compare_col}",
                },
                "df_shape": df.shape,
            }

        raise ValueError(f"Unknown analysis_type: {plan.analysis_type}")