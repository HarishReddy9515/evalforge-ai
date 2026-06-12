from __future__ import annotations

from html import escape
from pathlib import Path

from .runner import EvaluationSummary


def write_html_report(summary: EvaluationSummary, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_html(summary), encoding="utf-8")


def render_html(summary: EvaluationSummary) -> str:
    cards = "\n".join(render_case(item.case, item.metrics) for item in summary.cases)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EvalForge AI Report</title>
  <style>
    :root {{
      --ink: #17202a;
      --muted: #60707f;
      --line: #dbe3e8;
      --paper: #f3f6f8;
      --panel: #ffffff;
      --green: #188557;
      --amber: #b46c16;
      --red: #c53d3d;
      --blue: #0a66c2;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--paper);
      color: var(--ink);
    }}
    main {{ width: min(1180px, 100%); margin: 0 auto; padding: 28px; }}
    header {{
      min-height: 220px;
      border-radius: 8px;
      padding: 36px;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      color: white;
      background: linear-gradient(135deg, #10283f, #0a66c2);
    }}
    h1 {{ margin: 0; font-size: clamp(2.2rem, 5vw, 4.5rem); line-height: 0.98; }}
    h2, h3, p {{ margin-top: 0; }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0;
    }}
    .metric, .case {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 16px;
    }}
    .metric strong {{ display: block; font-size: 2rem; }}
    .metric span, .case small {{ color: var(--muted); font-weight: 800; }}
    .cases {{ display: grid; gap: 12px; }}
    .verdict {{
      display: inline-flex;
      border-radius: 999px;
      padding: 4px 10px;
      color: white;
      font-size: 0.8rem;
      font-weight: 900;
      text-transform: uppercase;
    }}
    .pass {{ background: var(--green); }}
    .review {{ background: var(--amber); }}
    .fail {{ background: var(--red); }}
    .scores {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin: 12px 0; }}
    .score {{ padding: 10px; border-radius: 8px; background: #f5f8fa; }}
    ul {{ margin-bottom: 0; }}
    @media (max-width: 780px) {{ .summary, .scores {{ grid-template-columns: 1fr; }} main {{ padding: 12px; }} }}
  </style>
</head>
<body>
  <main>
    <header>
      <p>LLM and RAG evaluation report</p>
      <h1>EvalForge AI</h1>
    </header>
    <section class="summary">
      <article class="metric"><strong>{summary.total}</strong><span>Total cases</span></article>
      <article class="metric"><strong>{summary.passed}</strong><span>Passed</span></article>
      <article class="metric"><strong>{summary.review}</strong><span>Needs review</span></article>
      <article class="metric"><strong>{summary.failed}</strong><span>Failed</span></article>
      <article class="metric"><strong>{summary.average_risk}</strong><span>Avg risk</span></article>
    </section>
    <section class="cases">
      {cards}
    </section>
  </main>
</body>
</html>"""


def render_case(case: dict, metrics) -> str:
    findings = "".join(f"<li>{escape(finding)}</li>" for finding in metrics.findings)
    return f"""
      <article class="case">
        <span class="verdict {metrics.verdict}">{metrics.verdict}</span>
        <h2>{escape(case.get("id", "case"))}</h2>
        <small>{escape(case.get("question", ""))}</small>
        <div class="scores">
          <div class="score"><strong>{metrics.relevance}</strong><br>Relevance</div>
          <div class="score"><strong>{metrics.groundedness}</strong><br>Groundedness</div>
          <div class="score"><strong>{metrics.citation_score}</strong><br>Citations</div>
          <div class="score"><strong>{metrics.refusal_score}</strong><br>Refusal</div>
          <div class="score"><strong>{metrics.risk_score}</strong><br>Risk</div>
        </div>
        <h3>Findings</h3>
        <ul>{findings}</ul>
      </article>
    """
