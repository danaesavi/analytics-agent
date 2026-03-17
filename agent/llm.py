# agent/llm.py
from openai import OpenAI
import json

client = OpenAI()


SYSTEM_PROMPT = """
You are an analytics planning assistant.

Convert the user's question into a structured analysis plan.

Return JSON only.

Fields:
analysis_type: "topk" or "compare"
group_col: column to group by
metric: metric name
agg: aggregation (mean, sum, median)
top_k: integer if applicable
compare_col: column if compare analysis
"""

def _clean_json_text(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        # Remove first fence line
        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        # Remove last fence line
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    return text


def plan_from_llm(question: str, rag_context: list[dict]) -> dict:
    context_text = "\n\n".join(
        f"{c['title']}:\n{c['text']}" for c in rag_context
    )

    prompt = f"""
User question:
{question}

Relevant definitions:
{context_text}

Return JSON plan.
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"}
    )
    content = resp.choices[0].message.content
    print("LLM raw output:", repr(content))
    if not content:
        raise ValueError("LLM returned empty content.")

    cleaned = _clean_json_text(content)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON. Raw output: {content}") from e