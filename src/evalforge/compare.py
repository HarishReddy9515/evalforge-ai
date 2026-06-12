from __future__ import annotations

from dataclasses import dataclass

from .runner import EvaluationSummary


@dataclass(frozen=True)
class CaseDelta:
    case_id: str
    old_risk: float
    new_risk: float
    delta: float
    status: str


@dataclass(frozen=True)
class ComparisonSummary:
    baseline_average_risk: float
    candidate_average_risk: float
    risk_delta: float
    improved: int
    regressed: int
    unchanged: int
    case_deltas: list[CaseDelta]


def compare_summaries(baseline: EvaluationSummary, candidate: EvaluationSummary) -> ComparisonSummary:
    baseline_by_id = {item.case["id"]: item for item in baseline.cases}
    deltas: list[CaseDelta] = []

    for item in candidate.cases:
        case_id = item.case["id"]
        if case_id not in baseline_by_id:
            continue
        old_risk = baseline_by_id[case_id].metrics.risk_score
        new_risk = item.metrics.risk_score
        delta = round(new_risk - old_risk, 2)
        status = "improved" if delta < -0.03 else "regressed" if delta > 0.03 else "unchanged"
        deltas.append(CaseDelta(case_id, old_risk, new_risk, delta, status))

    improved = sum(1 for item in deltas if item.status == "improved")
    regressed = sum(1 for item in deltas if item.status == "regressed")
    unchanged = sum(1 for item in deltas if item.status == "unchanged")

    return ComparisonSummary(
        baseline_average_risk=baseline.average_risk,
        candidate_average_risk=candidate.average_risk,
        risk_delta=round(candidate.average_risk - baseline.average_risk, 2),
        improved=improved,
        regressed=regressed,
        unchanged=unchanged,
        case_deltas=deltas,
    )
