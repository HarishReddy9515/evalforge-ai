from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from .metrics import MetricResult, score_case


@dataclass(frozen=True)
class EvaluatedCase:
    case: dict
    metrics: MetricResult


@dataclass(frozen=True)
class EvaluationSummary:
    total: int
    passed: int
    review: int
    failed: int
    average_risk: float
    cases: list[EvaluatedCase]


def load_cases(path: Path) -> list[dict]:
    cases: list[dict] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                cases.append(json.loads(line))
    return cases


def evaluate_cases(cases: list[dict]) -> EvaluationSummary:
    evaluated = [EvaluatedCase(case=case, metrics=score_case(case)) for case in cases]
    total = len(evaluated)
    passed = sum(1 for item in evaluated if item.metrics.verdict == "pass")
    review = sum(1 for item in evaluated if item.metrics.verdict == "review")
    failed = sum(1 for item in evaluated if item.metrics.verdict == "fail")
    average_risk = round(sum(item.metrics.risk_score for item in evaluated) / total, 2) if total else 0.0

    return EvaluationSummary(
        total=total,
        passed=passed,
        review=review,
        failed=failed,
        average_risk=average_risk,
        cases=evaluated,
    )


def summary_to_json(summary: EvaluationSummary) -> dict:
    return {
        "total": summary.total,
        "passed": summary.passed,
        "review": summary.review,
        "failed": summary.failed,
        "average_risk": summary.average_risk,
        "cases": [
            {
                "case": item.case,
                "metrics": asdict(item.metrics),
            }
            for item in summary.cases
        ],
    }
