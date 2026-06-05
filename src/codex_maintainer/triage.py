"""Issue triage command: classify, prioritize, and label GitHub issues."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any, Optional, cast

import openai
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

console = Console()

_SYSTEM_PROMPT = """You are an expert OSS project triager.

Analyze the GitHub issue and return a JSON object with exactly these fields:
- "type": one of "bug", "feature", "question", "documentation", "performance", "security",
  "duplicate", "invalid"
- "priority": one of "critical", "high", "medium", "low"
- "labels": list of 1-4 concise label strings (e.g. ["bug", "good first issue"])
- "summary": one sentence summarizing the issue
- "suggested_action": one sentence telling the maintainer what to do next
- "complexity": one of "trivial", "small", "medium", "large", "unknown"

Return only valid JSON, no extra text."""

_PRIORITY_COLORS = {
    "critical": "bold red",
    "high": "red",
    "medium": "yellow",
    "low": "green",
}


class TriageResult(BaseModel):
    type: str
    priority: str
    labels: list[str]
    summary: str
    suggested_action: str
    complexity: str


def _get_issue_data(issue: int, repo: Optional[str]) -> dict[str, Any]:
    cmd = ["gh", "issue", "view", str(issue), "--json", "title,body,author,createdAt"]
    if repo:
        cmd += ["--repo", repo]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return cast(dict[str, Any], json.loads(result.stdout))


def _apply_labels(issue: int, repo: Optional[str], labels: list[str]) -> None:
    cmd = ["gh", "issue", "edit", str(issue), "--add-label", ",".join(labels)]
    if repo:
        cmd += ["--repo", repo]
    subprocess.run(cmd, check=True)


def run_triage(issue: int, repo: Optional[str], model: str, apply: bool) -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        console.print("[red]Error:[/red] OPENAI_API_KEY is not set.")
        raise SystemExit(1)

    with console.status(f"Fetching issue #{issue}..."):
        try:
            data = _get_issue_data(issue, repo)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]GitHub CLI error:[/red] {e.stderr.strip()}")
            raise SystemExit(1)

    user_content = (
        f"## Issue #{issue}: {data['title']}\n\n"
        f"**Author:** {data['author']['login']}\n"
        f"**Created:** {data['createdAt']}\n\n"
        f"**Body:**\n{data.get('body') or '(no body)'}"
    )

    client = openai.OpenAI(api_key=api_key)

    with console.status(f"Triaging with {model}..."):
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            response_format={"type": "json_object"},
            max_tokens=512,
        )

    result = TriageResult.model_validate_json(response.choices[0].message.content or "{}")

    priority_color = _PRIORITY_COLORS.get(result.priority, "white")

    table = Table(title=f"Triage: Issue #{issue}", show_header=True, header_style="bold cyan")
    table.add_column("Field", style="cyan", width=20)
    table.add_column("Value")
    table.add_row("Type", result.type)
    table.add_row("Priority", f"[{priority_color}]{result.priority}[/{priority_color}]")
    table.add_row("Complexity", result.complexity)
    table.add_row("Labels", ", ".join(result.labels))
    table.add_row("Summary", result.summary)
    table.add_row("Suggested Action", result.suggested_action)
    console.print(table)

    if apply:
        with console.status("Applying labels..."):
            try:
                _apply_labels(issue, repo, result.labels)
                console.print(f"[green]Labels applied:[/green] {', '.join(result.labels)}")
            except subprocess.CalledProcessError as e:
                msg = f"[yellow]Could not apply labels:[/yellow] {e.stderr.strip()}"
                console.print(msg)
