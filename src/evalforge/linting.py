from __future__ import annotations

from dataclasses import dataclass


REQUIRED_FIELDS = ["id", "question", "context", "answer", "expected_topics", "requires_refusal"]


@dataclass(frozen=True)
class LintIssue:
    case_id: str
    severity: str
    message: str


def lint_cases(cases: list[dict]) -> list[LintIssue]:
    issues: list[LintIssue] = []
    seen_ids: set[str] = set()

    for index, case in enumerate(cases, start=1):
        case_id = str(case.get("id") or f"row-{index}")
        for field in REQUIRED_FIELDS:
            if field not in case:
                issues.append(LintIssue(case_id, "error", f"Missing required field: {field}"))

        if case_id in seen_ids:
            issues.append(LintIssue(case_id, "error", "Duplicate case id."))
        seen_ids.add(case_id)

        if not str(case.get("question", "")).strip():
            issues.append(LintIssue(case_id, "error", "Question is empty."))
        if not str(case.get("answer", "")).strip():
            issues.append(LintIssue(case_id, "error", "Answer is empty."))
        if not isinstance(case.get("context", []), list):
            issues.append(LintIssue(case_id, "error", "Context must be a list of strings."))
        if not isinstance(case.get("expected_topics", []), list):
            issues.append(LintIssue(case_id, "error", "Expected topics must be a list."))
        if len(str(case.get("answer", "")).split()) < 4:
            issues.append(LintIssue(case_id, "warning", "Answer is very short; metrics may be noisy."))
        if case.get("context") == [] and not case.get("requires_refusal", False):
            issues.append(LintIssue(case_id, "warning", "Non-refusal case has no context."))

    return issues


def has_errors(issues: list[LintIssue]) -> bool:
    return any(issue.severity == "error" for issue in issues)
