# agent/tools/metrics.py
import pandas as pd

def add_occupancy_proxy(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["occupancy_proxy"] = (30 - out["availability_30"]) / 30
    return out

def add_revenue_proxy(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["revenue_proxy"] = out["price"] * (30 - out["availability_30"])
    return out