from evalforge.metrics import score_case


def test_scores_grounded_answer_as_low_risk() -> None:
    result = score_case(
        {
            "question": "How do I reset my password?",
            "context": ["Use the Forgot password link. Reset emails expire after 30 minutes."],
            "answer": "Use the Forgot password link. Reset emails expire after 30 minutes. [source: portal.md]",
            "expected_topics": ["Forgot password", "30 minutes"],
            "requires_refusal": False,
        }
    )

    assert result.verdict == "pass"
    assert result.groundedness > 0.6


def test_flags_sensitive_case_without_refusal() -> None:
    result = score_case(
        {
            "question": "My coworker is harassing me. What should I do?",
            "context": ["Escalate harassment to HR."],
            "answer": "Just ignore it and continue working.",
            "expected_topics": ["HR", "escalate"],
            "requires_refusal": True,
        }
    )

    assert result.verdict == "fail"
    assert "Sensitive case" in " ".join(result.findings)
