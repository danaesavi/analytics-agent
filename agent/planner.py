# agent/planner.py
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Literal, Optional

from rag.retriever import RagRetriever

DerivedMetric = Literal["occupancy_proxy", "revenue_proxy"]
AnalysisType = Literal["topk", "compare"]


@dataclass
class AnalysisPlan:
    question: str
    data_path: str
    analysis_type: AnalysisType

    # topk fields
    group_col: Optional[str] = None
    top_k: int = 5

    # metric selection
    metric_col: Optional[str] = "price"  # base column metric
    derived_metric: Optional[DerivedMetric] = None
    agg: str = "mean"

    # compare fields
    compare_col: Optional[str] = None

    # RAG traceability
    rag_snippets: List[Dict[str, Any]] = field(default_factory=list)
    rag_used_titles: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


RAG_METRIC_TO_DERIVED = {
    "occupancy_proxy": "occupancy_proxy",
    "revenue_proxy": "revenue_proxy",
}

RAG_METRIC_DEFAULT_AGG = {
    "occupancy_proxy": "mean",
    "revenue_proxy": "sum",
}


class Planner:
    def __init__(self):
        self.retriever = RagRetriever.load()

    def create_plan(self, question: str, data_path: str) -> AnalysisPlan:
        q = question.lower()
        snippets = self.retriever.retrieve(question, top_k=4)

        # Decide derived metric based on retrieved titles (source of truth)
        derived_metric: Optional[DerivedMetric] = None
        used: List[str] = []

        for s in snippets:
            title = (s.get("title") or "").strip()
            if title in RAG_METRIC_TO_DERIVED:
                derived_metric = RAG_METRIC_TO_DERIVED[title]  # type: ignore[assignment]
                used.append(title)
                break

        # defaults
        group_col = "neighbourhood"
        metric_col = "price"
        agg = "mean"
        top_k = 5

        # infer k
        for k in [3, 5, 10, 20]:
            if f"top {k}" in q:
                top_k = k
                break

        # infer group column
        if "room type" in q or "room_type" in q:
            group_col = "room_type"

        # compare intent
        is_compare = ("compare" in q) or (" vs " in q) or ("versus" in q)
        if is_compare and ("superhost" in q or "superhosts" in q):
            compare_col = "is_superhost"
            if derived_metric is not None:
                agg = RAG_METRIC_DEFAULT_AGG.get(derived_metric, agg)

            return AnalysisPlan(
                question=question,
                data_path=data_path,
                analysis_type="compare",
                compare_col=compare_col,
                metric_col=metric_col,
                derived_metric=derived_metric,
                agg=agg,
                rag_snippets=snippets,
                rag_used_titles=used,
            )

        # default: topk
        if derived_metric is not None:
            agg = RAG_METRIC_DEFAULT_AGG.get(derived_metric, agg)

        return AnalysisPlan(
            question=question,
            data_path=data_path,
            analysis_type="topk",
            group_col=group_col,
            metric_col=metric_col,
            derived_metric=derived_metric,
            agg=agg,
            top_k=top_k,
            rag_snippets=snippets,
            rag_used_titles=used,
        )