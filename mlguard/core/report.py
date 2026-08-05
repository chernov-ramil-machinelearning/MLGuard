"""
Рендеринг findings, которые возвращает run_audit(), в разные форматы.

Ожидаемая схема каждого finding (см. mlguard/checks/*.py):
    {
        "check": str,          # имя чека, напр. "leakage_detector"
        "severity": str,       # "WARNING" | "CRITICAL" (регистр не важен)
        "column": str,
        "metric_value": float,
        "threshold": float,
        "message": str,
    }
"""
import json

import click

_SEVERITY_COLOR = {
    "CRITICAL": "bright_red",
    "WARNING": "yellow",
    "INFO": "white",
}


def format_table(findings: list[dict]) -> str:
    if not findings:
        return click.style("✓ Проблем не найдено", fg="green", bold=True)

    lines = []
    for f in findings:
        sev = str(f.get("severity", "")).upper()
        badge = click.style(f"{sev:8}", fg=_SEVERITY_COLOR.get(sev, "white"), bold=True)
        check = f.get("check", "?")
        column = f.get("column", "-")
        message = f.get("message", "")
        lines.append(f"[{badge}] {check:<20} {column:<25} {message}")

    summary = _summary_line(findings)
    return "\n".join(lines) + "\n\n" + summary


def format_json(findings: list[dict]) -> str:
    return json.dumps(findings, ensure_ascii=False, indent=2)


def format_markdown(findings: list[dict]) -> str:
    if not findings:
        return "✅ **Проблем не найдено**"

    lines = [
        "| Severity | Check | Column | Value | Threshold | Message |",
        "|---|---|---|---|---|---|",
    ]
    for f in findings:
        lines.append(
            f"| {f.get('severity', '')} | {f.get('check', '')} | {f.get('column', '')} "
            f"| {f.get('metric_value', '')} | {f.get('threshold', '')} | {f.get('message', '')} |"
        )
    lines.append("")
    lines.append(_summary_line(findings, markdown=True))
    return "\n".join(lines)


def _summary_line(findings: list[dict], markdown: bool = False) -> str:
    critical = sum(1 for f in findings if str(f.get("severity", "")).upper() == "CRITICAL")
    warning = sum(1 for f in findings if str(f.get("severity", "")).upper() == "WARNING")
    text = f"Итого: {len(findings)} findings — {critical} critical, {warning} warning."
    return f"**{text}**" if markdown else click.style(text, bold=True)


FORMATTERS = {
    "table": format_table,
    "json": format_json,
    "markdown": format_markdown,
}
