# agent/planner.py
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Literal, Optional

from rag.retriever import RagRetriever
from agent.llm import plan_from_llm

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

        # Focused retrieval for derived metrics
        extra_snippets = []
        if "occupancy" in q:
            extra_snippets = self.retriever.retrieve("occupancy_proxy", top_k=2)
        elif "revenue" in q and "proxy" in q:
            extra_snippets = self.retriever.retrieve("revenue_proxy", top_k=2)

        # merge, deduplicate by (title, source)
        seen = set()
        all_snippets = []
        for s in snippets + extra_snippets:
            key = (s.get("title"), s.get("source"))
            if key not in seen:
                seen.add(key)
                all_snippets.append(s)

        snippets = all_snippets

        print("RAG snippets:")
        for s in snippets:
            print("-", s.get("title"), "|", s.get("source"))
        llm_plan = plan_from_llm(question, snippets)

        # defaults
        analysis_type = "topk"
        group_col = "neighbourhood"
        metric_col = "price"
        agg = "mean"
        top_k = 5
        compare_col = None

        # Decide derived metric based on retrieved titles (source of truth)
        derived_metric: Optional[DerivedMetric] = None
        used: List[str] = []

        for s in snippets:
            title = (s.get("title") or "").strip().lower().replace(" ", "_")
            if title in RAG_METRIC_TO_DERIVED:
                derived_metric = RAG_METRIC_TO_DERIVED[title]
                used.append(title)
                break

        # grounding enforcement (only for derived metrics)
        if "occupancy" in q and derived_metric is None:
            raise ValueError("Definition for occupancy_proxy not found in docs.")
        if "revenue" in q and "proxy" in q and derived_metric is None:
            raise ValueError("Definition for revenue_proxy not found in docs.")

        # if RAG found a derived metric, use its default agg unless LLM overrides later
        if derived_metric is not None:
            agg = RAG_METRIC_DEFAULT_AGG.get(derived_metric, agg)

        # LLM overrides safe planning fields
        analysis_type = llm_plan.get("analysis_type", analysis_type)
        group_col = llm_plan.get("group_col", group_col)
        agg = llm_plan.get("agg", agg)
        top_k = llm_plan.get("top_k", top_k)
        compare_col = llm_plan.get("compare_col", compare_col)

        # deterministic fallbacks / cleanup
        for k in [3, 5, 10, 20]:
            if f"top {k}" in q:
                top_k = k
                break

        if "room type" in q or "room_type" in q:
            group_col = "room_type"

        is_compare = ("compare" in q) or (" vs " in q) or ("versus" in q)
        if is_compare and ("superhost" in q or "superhosts" in q):
            compare_col = "is_superhost"
            analysis_type = "compare"

        # validate analysis_type
        if analysis_type == "compare":
            return AnalysisPlan(
                question=question,
                data_path=data_path,
                analysis_type="compare",
                compare_col=compare_col or "is_superhost",
                metric_col=metric_col,
                derived_metric=derived_metric,
                agg=agg,
                rag_snippets=snippets,
                rag_used_titles=used,
            )

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