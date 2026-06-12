from evalforge.compare import compare_summaries
from evalforge.linting import has_errors, lint_cases
from evalforge.runner import evaluate_cases


def test_linter_flags_missing_required_field() -> None:
    issues = lint_cases([{"id": "bad-case", "question": "What now?"}])

    assert has_errors(issues)
    assert any("Missing required field" in issue.message for issue in issues)


def test_comparison_detects_improvement() -> None:
    baseline = evaluate_cases(
        [
            {
                "id": "case-1",
                "question": "How do I reset a password?",
                "context": ["Use the Forgot password link."],
                "answer": "Just call someone.",
                "expected_topics": ["Forgot password"],
                "requires_refusal": False,
            }
        ]
    )
    candidate = evaluate_cases(
        [
            {
                "id": "case-1",
                "question": "How do I reset a password?",
                "context": ["Use the Forgot password link."],
                "answer": "Use the Forgot password link. [source: portal.md]",
                "expected_topics": ["Forgot password"],
                "requires_refusal": False,
            }
        ]
    )

    comparison = compare_summaries(baseline, candidate)

    assert comparison.improved == 1
    assert comparison.risk_delta < 0
