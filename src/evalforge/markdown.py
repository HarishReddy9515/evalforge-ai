from __future__ import annotations

from pathlib import Path

from .compare import ComparisonSummary
from .runner import EvaluationSummary


def write_markdown_report(summary: EvaluationSummary, output_path: Path, comparison: ComparisonSummary | None = None) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(summary, comparison), encoding="utf-8")


def render_markdown(summary: EvaluationSummary, comparison: ComparisonSummary | None = None) -> str:
    lines = [
        "# EvalForge AI Report",
        "",
        f"- Total cases: {summary.total}",
        f"- Passed: {summary.passed}",
        f"- Review: {summary.review}",
        f"- Failed: {summary.failed}",
        f"- Average risk: {summary.average_risk}",
        "",
    ]

    if comparison:
        lines.extend(
            [
                "## Baseline Comparison",
                "",
                f"- Baseline average risk: {comparison.baseline_average_risk}",
                f"- Candidate average risk: {comparison.candidate_average_risk}",
                f"- Risk delta: {comparison.risk_delta}",
                f"- Improved cases: {comparison.improved}",
                f"- Regressed cases: {comparison.regressed}",
                f"- Unchanged cases: {comparison.unchanged}",
                "",
            ]
        )

    lines.extend(["## Cases", ""])
    for item in summary.cases:
        lines.extend(
            [
                f"### {item.case.get('id', 'case')}",
                "",
                f"- Verdict: {item.metrics.verdict}",
                f"- Risk: {item.metrics.risk_score}",
                f"- Relevance: {item.metrics.relevance}",
                f"- Groundedness: {item.metrics.groundedness}",
                f"- Citation score: {item.metrics.citation_score}",
                "",
                "Findings:",
                *[f"- {finding}" for finding in item.metrics.findings],
                "",
            ]
        )

    return "\n".join(lines)
