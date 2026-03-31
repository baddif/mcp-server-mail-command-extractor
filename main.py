#!/usr/bin/env python3
"""
CLI and MCP entrypoint for mail_command_extractor skill.

This file exposes a Typer CLI and an MCP tool named `mail_command_extractor`.
Parameters MUST match the skill schema: `emails` (JSON array or path to file) and
`detection_rules` (JSON object or path to file). Optional `merge_duplicates`.

CLI usage examples are provided in Skill.md.
"""
import sys
import json
import asyncio
import logging
from typing import Any

import typer
from pathlib import Path

# Use the project's skill implementation
from mail_command_extractor_skill import MailCommandExtractorSkill
try:
    from skill_compat import ExecutionContext
except Exception:
    # Minimal ExecutionContext fallback
    class ExecutionContext:
        def __init__(self):
            self._store = {}
        def set(self, k, v):
            self._store[k] = v
        def get(self, k, default=None):
            return self._store.get(k, default)

app = typer.Typer()
impl = MailCommandExtractorSkill()
_is_cli = len(sys.argv) > 1

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)


def _load_json_or_file(value: str):
    """If `value` is a path to file, read it; else try to parse JSON from string."""
    p = Path(value)
    if p.exists():
        return json.loads(p.read_text(encoding='utf-8'))
    try:
        return json.loads(value)
    except Exception as e:
        raise typer.BadParameter(f"Value is not a valid file path or JSON string: {e}")


def format_mcp(result: dict) -> dict:
    # FastMCP expects a content block with a JSON string
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(result, ensure_ascii=False)
            }
        ]
    }


@app.command()
def mail_command_extractor(
    emails: str = typer.Argument(..., help="Path to JSON file or JSON string containing the emails array (matched_emails)."),
    detection_rules: str = typer.Argument(..., help="Path to JSON file or JSON string containing detection_rules object."),
    merge_duplicates: bool = typer.Option(True, help="Whether to merge duplicate commands")
):
    """CLI/MCP tool: run mail command extractor.

    Parameters names must match the skill schema exactly: `emails`, `detection_rules`.
    For CLI usage, provide file paths. For MCP usage, the MCP framework will pass parsed objects.
    """
    try:
        # Load inputs (CLI will pass file paths typically)
        if isinstance(emails, str):
            emails_parsed = _load_json_or_file(emails)
        else:
            emails_parsed = emails

        if isinstance(detection_rules, str):
            rules_parsed = _load_json_or_file(detection_rules)
        else:
            rules_parsed = detection_rules

        ctx = ExecutionContext()

        # The skill expects to be called with ctx and kwargs
        # Use the parameter names defined in the schema
        result = impl.execute(ctx, emails=emails_parsed, detection_rules=rules_parsed, merge_duplicates=merge_duplicates)

        # CLI prints raw JSON
        typer.echo(json.dumps(result, ensure_ascii=False))
        return
    except Exception as e:
        error = {"success": False, "data": None, "error": str(e)}
        typer.echo(json.dumps(error), err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        app()
    else:
        # When integrated into an MCP server, the FastMCP framework would call this.
        # For direct runs without args, show help.
        app()
