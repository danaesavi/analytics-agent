# analytics-agent
This project implements a modular Analytics Agent that translates natural language business questions into structured analysis plans, executes reproducible data workflows, and generates visual + narrative reports.

The system follows a planner → executor → reporter architecture, includes explicit tool abstractions for data operations, and provides an evaluation suite to measure reliability and correctness.

Designed as a portfolio project to demonstrate applied agent engineering, structured reasoning, and analytics automation.

´´´
analytics-agent/
│
├── agent/
│   ├── __init__.py
│   ├── run.py
│   ├── planner.py
│   ├── executor.py
│   ├── reporter.py
│   │
│   └── tools/
│       ├── __init__.py
│       ├── data.py
│       ├── aggregations.py
│       ├── plots.py
│       └── anomalies.py
│
├── data/
│   └── sample.parquet
│
├── eval/
│   └── questions.yaml
│
├── outputs/        # gitignored
│
├── tests/
│   └── test_smoke.py
│
├── README.md
├── pyproject.toml
├── .gitignore
└── LICENSE
´´´