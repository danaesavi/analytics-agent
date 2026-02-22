# Analytics Agent
This project implements a modular Retrieval-Augmented Analytics Agent that translates natural language business questions into structured analysis plans, executes deterministic data workflows, and generates reproducible visual and narrative reports.

The system follows a planner → executor → reporter architecture, where planning is grounded in documentation via lightweight RAG, execution is performed through explicit analytics tools, and reporting ensures traceability and transparency.

An evaluation suite is included to measure reliability and regression behavior across predefined analytical queries.

## Project Structure
The system is structured as a modular retrieval-augmented analytics agent with clear separation between planning, execution, and reporting.

```text
analytics-agent/
│
├── agent/                  # Core agent logic
│   ├── planner.py          # Creates structured AnalysisPlan (RAG-grounded)
│   ├── executor.py         # Executes deterministic analytics (pandas-based)
│   ├── reporter.py         # Generates Markdown reports + plots
│   ├── run.py              # CLI entrypoint
│   └── tools/              # Atomic analytics tools
│       ├── aggregations.py # Top-k + grouped metrics
│       ├── anomalies.py    # Basic anomaly detection utilities
│       ├── plots.py        # Plot helpers
│       └── data.py         # Data loading utilities
│
├── data/                   # Local datasets (Parquet)
│   └── sample.parquet
│
├── docs/                   # Metric definitions (RAG source of truth)
│
├── rag/                    # Retrieval index + retriever
│
├── eval/                   # Evaluation harness
│   └── questions.yaml
│
├── tests/                  # Minimal smoke tests
│
├── outputs/                # Generated reports (gitignored)
│
├── pyproject.toml          # Modern Python packaging (uv-managed)
├── Makefile                # Reproducible commands (run, eval, rag_index)
└── README.md
```
