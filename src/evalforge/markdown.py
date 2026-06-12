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
        "## Recommended Next Actions",
        "",
        *[f"- {action}" for action in recommended_actions(summary)],
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


def recommended_actions(summary: EvaluationSummary) -> list[str]:
    actions: list[str] = []
    if summary.failed:
        actions.append("Fix failed cases first; they represent likely hallucination, missed refusal, or unsupported answer risk.")
    if summary.review:
        actions.append("Review borderline cases and add better context, expected topics, or citation requirements.")
    if summary.average_risk > 0.4:
        actions.append("Tighten prompts or retrieval before shipping; average risk is above a comfortable release range.")
    if not actions:
        actions.append("No urgent risks detected. Expand the dataset with harder cases before the next release.")
    actions.append("Add at least one negative test for every critical user workflow.")
    return actions
