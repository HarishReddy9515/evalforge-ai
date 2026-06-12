# EvalForge AI

EvalForge AI is an offline evaluation toolkit for LLM and RAG applications. It scores answer quality, citation behavior, groundedness, refusal quality, and regression risk, then generates a clean HTML report.

This project showcases production AI engineering skills:

- evaluation dataset design
- RAG groundedness checks
- hallucination risk detection
- citation and source coverage scoring
- refusal/safety behavior checks
- regression comparison between model versions
- report generation for stakeholders

It has no required dependencies and no API key requirement, so anyone can run it immediately.

## Quick start

Run the sample evaluation:

```bash
python -m src.evalforge.cli data/eval_cases.jsonl reports/report.html
```

Open:

```text
reports/report.html
```

Run the smoke test:

```bash
python scripts/smoke_test.py
```

## Input format

Each JSONL row represents one evaluated AI response:

```json
{
  "id": "benefits-password",
  "question": "How do I reset my benefits portal password?",
  "context": ["Use the Forgot password link. Reset emails expire after 30 minutes."],
  "answer": "Use the Forgot password link. The reset email expires after 30 minutes. [source: benefits_portal.md]",
  "expected_topics": ["Forgot password", "30 minutes"],
  "requires_refusal": false
}
```

## Metrics

- **Relevance**: answer overlaps with the question and expected topics.
- **Groundedness**: answer content is supported by supplied context.
- **Citation score**: answer includes source/citation signals when context is used.
- **Refusal score**: sensitive cases are escalated or refused correctly.
- **Risk score**: flags unsupported claims, weak source coverage, and missed refusals.

## Why this matters

AI teams need more than demos. They need to prove that a model did not regress, that RAG answers are grounded, and that risky questions are handled safely. EvalForge demonstrates that mindset.

## Future roadmap

- Add OpenAI Evals or Responses API integration
- Add embeddings-based semantic scoring
- Add prompt/version comparison dashboards
- Add CI mode with pass/fail thresholds
- Add dataset generator from production feedback
