from pathlib import Path

from evalforge.importers import csv_to_cases
from evalforge.privacy import redact_text, scan_cases
from evalforge.runner import load_cases


def test_redacts_common_pii() -> None:
    text = "Email jane@example.com or call 555-123-4567."

    redacted = redact_text(text)

    assert "[REDACTED_EMAIL]" in redacted
    assert "[REDACTED_PHONE]" in redacted


def test_scan_cases_finds_email() -> None:
    findings = scan_cases(
        [
            {
                "id": "case",
                "question": "Can a@b.com log in?",
                "answer": "Yes",
                "context": [],
            }
        ]
    )

    assert findings[0].pii_type == "email"


def test_csv_importer_writes_jsonl(tmp_path: Path) -> None:
    source = tmp_path / "cases.csv"
    target = tmp_path / "cases.jsonl"
    source.write_text(
        "id,question,context,answer,expected_topics,requires_refusal\n"
        "case-1,Question?,Context one|Context two,Answer,topic one|topic two,false\n",
        encoding="utf-8",
    )

    count = csv_to_cases(source, target)
    cases = load_cases(target)

    assert count == 1
    assert cases[0]["context"] == ["Context one", "Context two"]
    assert cases[0]["requires_refusal"] is False
