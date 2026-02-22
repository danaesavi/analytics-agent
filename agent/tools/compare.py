# agent/tools/compare.py
import pandas as pd

def compare_groups(df: pd.DataFrame, compare_col: str, metric_col: str, agg: str = "mean") -> pd.DataFrame:
    if compare_col not in df.columns:
        raise ValueError(f"compare_col '{compare_col}' not found")
    if metric_col not in df.columns:
        raise ValueError(f"metric_col '{metric_col}' not found")

    g = df.groupby(compare_col, dropna=False)[metric_col]
    if agg == "mean":
        out = g.mean()
    elif agg == "median":
        out = g.median()
    elif agg == "sum":
        out = g.sum()
    elif agg == "count":
        out = g.count()
    else:
        raise ValueError(f"Unsupported agg: {agg}")

    out = out.reset_index().rename(columns={metric_col: "value"})
    return out