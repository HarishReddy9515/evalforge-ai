from __future__ import annotations

from dataclasses import dataclass
import re


PII_PATTERNS = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "phone": re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
}


@dataclass(frozen=True)
class PrivacyFinding:
    case_id: str
    pii_type: str
    field: str


def scan_cases(cases: list[dict]) -> list[PrivacyFinding]:
    findings: list[PrivacyFinding] = []
    for index, case in enumerate(cases, start=1):
        case_id = str(case.get("id") or f"row-{index}")
        for field in ["question", "answer"]:
            findings.extend(scan_text(case_id, field, str(case.get(field, ""))))
        for context_index, context in enumerate(case.get("context", []) or []):
            findings.extend(scan_text(case_id, f"context[{context_index}]", str(context)))
    return findings


def scan_text(case_id: str, field: str, text: str) -> list[PrivacyFinding]:
    findings: list[PrivacyFinding] = []
    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(text):
            findings.append(PrivacyFinding(case_id=case_id, pii_type=pii_type, field=field))
    return findings


def redact_case(case: dict) -> dict:
    redacted = dict(case)
    for field in ["question", "answer"]:
        redacted[field] = redact_text(str(redacted.get(field, "")))
    redacted["context"] = [redact_text(str(item)) for item in redacted.get("context", []) or []]
    return redacted


def redact_cases(cases: list[dict]) -> list[dict]:
    return [redact_case(case) for case in cases]


def redact_text(text: str) -> str:
    redacted = text
    for pii_type, pattern in PII_PATTERNS.items():
        redacted = pattern.sub(f"[REDACTED_{pii_type.upper()}]", redacted)
    return redacted
