"""HTML email builder and Gmail SMTP dispatcher."""

import asyncio
import json
import logging
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.database import Paper

logger = logging.getLogger(__name__)

_HEADER_BG = "#1e293b"
_HEADER_TEXT = "#f8fafc"
_ACCENT = "#6366f1"


def _score_badge_color(score: float | None) -> str:
    if score is None:
        return "#6b7280"
    if score >= 8:
        return "#16a34a"
    if score >= 5:
        return "#d97706"
    return "#6b7280"


def _format_authors(authors_json: str, max_authors: int = 3) -> str:
    try:
        names: list[str] = json.loads(authors_json)
    except (json.JSONDecodeError, TypeError):
        return authors_json or ""
    if len(names) <= max_authors:
        return ", ".join(names)
    return ", ".join(names[:max_authors]) + " et al."


def _render_paper_card(paper: Paper) -> str:
    badge_color = _score_badge_color(paper.impact_score)
    score_label = int(paper.impact_score) if paper.impact_score is not None else "?"
    authors = _format_authors(paper.authors)
    source_label = "arXiv" if paper.source == "arxiv" else "Semantic Scholar"

    pdf_link = ""
    if paper.pdf_url:
        pdf_link = (
            f' &nbsp; <a href="{paper.pdf_url}" style="color:{_ACCENT};text-decoration:none;">'
            f"PDF ↓</a>"
        )

    return f"""
<div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin-bottom:12px;">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
    <span style="background:{badge_color};color:#fff;font-size:12px;font-weight:700;
                 padding:2px 8px;border-radius:12px;">{score_label}</span>
    <a href="{paper.url}" style="color:#0f172a;font-size:15px;font-weight:600;text-decoration:none;">
      {paper.title}
    </a>
  </div>
  <p style="margin:0 0 6px;font-size:12px;color:#64748b;">{authors} &bull; {source_label}</p>
  <p style="margin:0 0 8px;font-size:13px;font-style:italic;font-weight:600;color:#1d4ed8;">
    {paper.key_takeaway or ""}
  </p>
  <p style="margin:0 0 10px;font-size:13px;color:#334155;line-height:1.5;">
    {paper.summary or ""}
  </p>
  <a href="{paper.url}" style="color:{_ACCENT};font-size:13px;text-decoration:none;font-weight:500;">
    Read Paper →
  </a>{pdf_link}
</div>"""


def _render_subfield_section(subfield: str, papers: list[Paper]) -> str:
    cards = "".join(_render_paper_card(p) for p in papers)
    count = len(papers)
    label = f"{subfield} &mdash; {count} paper{'s' if count != 1 else ''}"
    return f"""
<div style="margin-bottom:24px;">
  <h2 style="font-size:16px;font-weight:700;color:#0f172a;
             border-left:4px solid {_ACCENT};padding-left:10px;margin:0 0 12px;">
    {label}
  </h2>
  {cards}
</div>"""


def build_digest_html(
    curation_result: dict,
    digest_date: datetime | None = None,
) -> str:
    """Render a full HTML digest email from a curator result dict."""
    date = digest_date or datetime.now(timezone.utc)
    date_str = date.strftime("%B %d, %Y")
    top_papers: list[Paper] = curation_result["top_papers"]
    by_subfield: dict[str, list[Paper]] = curation_result["by_subfield"]
    total = curation_result["total_annotated"]

    subfield_count = len(by_subfield)
    summary_bar = (
        f"{len(top_papers)} paper{'s' if len(top_papers) != 1 else ''} &bull; "
        f"{subfield_count} subfield{'s' if subfield_count != 1 else ''} &bull; "
        f"{total} annotated today"
    )

    sections = "".join(
        _render_subfield_section(sf, papers) for sf, papers in by_subfield.items()
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:24px 0;">
  <tr><td align="center">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width:680px;">

      <!-- Header -->
      <tr><td style="background:{_HEADER_BG};border-radius:8px 8px 0 0;padding:24px 28px;">
        <h1 style="margin:0;font-size:22px;font-weight:800;color:{_HEADER_TEXT};">
          PaperPulse
        </h1>
        <p style="margin:4px 0 0;font-size:14px;color:#94a3b8;">
          Your AI Research Digest &mdash; {date_str}
        </p>
      </td></tr>

      <!-- Summary bar -->
      <tr><td style="background:#334155;padding:10px 28px;">
        <p style="margin:0;font-size:13px;color:#cbd5e1;">{summary_bar}</p>
      </td></tr>

      <!-- Body -->
      <tr><td style="background:#f8fafc;padding:24px 28px;">
        {sections}
      </td></tr>

      <!-- Footer -->
      <tr><td style="background:{_HEADER_BG};border-radius:0 0 8px 8px;padding:16px 28px;text-align:center;">
        <p style="margin:0;font-size:12px;color:#64748b;">
          Powered by Gemini 2.5 Flash &bull; PaperPulse
        </p>
      </td></tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""


def _send_via_smtp(
    subject: str,
    html_body: str,
    recipients: list[str],
    sender_email: str,
    app_password: str,
) -> None:
    """Synchronous Gmail SMTP send with plain-text fallback."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)

    plain_text = (
        f"{subject}\n\n"
        "Open this email in an HTML-capable client to view the full digest.\n"
    )
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipients, msg.as_string())


async def send_digest_email(
    html_body: str,
    recipients: list[str],
    sender_email: str,
    app_password: str,
    subject: str | None = None,
) -> None:
    """Async wrapper around Gmail SMTP send. Raises on failure."""
    resolved_subject = subject or f"PaperPulse Digest \u2014 {datetime.now(timezone.utc).strftime('%B %d, %Y')}"
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        _send_via_smtp,
        resolved_subject,
        html_body,
        recipients,
        sender_email,
        app_password,
    )
    logger.info("Digest email sent to %d recipient(s)", len(recipients))
