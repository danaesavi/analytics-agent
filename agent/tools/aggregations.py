# agent/tools/aggregations.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

import pandas as pd


AggFn = Literal["sum", "mean", "median", "count"]


@dataclass(frozen=True)
class TopKResult:
    table: pd.DataFrame
    group_col: str
    metric_col: str
    agg: AggFn
    k: int


def topk_group_metric(
    df: pd.DataFrame,
    group_col: str,
    metric_col: str,
    agg: AggFn = "mean",
    k: int = 5,
    min_group_size: int = 1,
) -> TopKResult:
    """
    Compute top-k groups by an aggregated metric.

    Example:
        topk_group_metric(df, "neighbourhood", "price", agg="mean", k=5)

    Guardrails:
        - validates columns exist
        - optionally filters groups with too few rows (min_group_size)
    """
    if group_col not in df.columns:
        raise ValueError(f"Group column '{group_col}' not in dataframe columns.")
    if metric_col not in df.columns and agg != "count":
        raise ValueError(f"Metric column '{metric_col}' not in dataframe columns.")

    tmp = df.copy()

    # Count per group for guardrails / filtering
    group_sizes = tmp.groupby(group_col, dropna=False).size().rename("_n")

    if agg == "count":
        agg_series = group_sizes
    elif agg == "sum":
        agg_series = tmp.groupby(group_col, dropna=False)[metric_col].sum()
    elif agg == "mean":
        agg_series = tmp.groupby(group_col, dropna=False)[metric_col].mean()
    elif agg == "median":
        agg_series = tmp.groupby(group_col, dropna=False)[metric_col].median()
    else:
        raise ValueError(f"Unsupported agg: {agg}")

    out = pd.concat([agg_series.rename("value"), group_sizes], axis=1).reset_index()

    # Filter small groups (optional but useful)
    out = out[out["_n"] >= min_group_size]

    out = out.sort_values("value", ascending=False).head(k).reset_index(drop=True)

    return TopKResult(
        table=out,
        group_col=group_col,
        metric_col=metric_col,
        agg=agg,
        k=k,
    )