#!/usr/bin/env python3
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Run Codex in structured-output mode and validate the extracted payload."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


class StructuredOutputError(RuntimeError):
    """Raised when Codex does not return usable structured output."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Invoke Codex with a JSON schema and extract the final structured output.")
    parser.add_argument(
        "--schema-path",
        type=Path,
        required=True,
        help="Path to the JSON schema file passed to Codex via --output-schema.",
    )
    parser.add_argument(
        "--prompt-file",
        type=Path,
        required=True,
        help="Path to the prompt text file sent to Codex on stdin.",
    )
    parser.add_argument(
        "--result-path",
        type=Path,
        required=True,
        help="Path where the extracted structured output JSON should be written.",
    )
    parser.add_argument(
        "--raw-output-path",
        type=Path,
        help="Optional path for the raw Codex stdout transcript.",
    )
    parser.add_argument(
        "--cwd",
        type=Path,
        default=Path.cwd(),
        help="Working directory for the Codex invocation. Defaults to the current directory.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=720,
        help="Maximum seconds to wait for Codex before failing.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Optional Codex model to pass as `-m`. Falls back to the Codex CLI's configured default when omitted.",
    )
    parser.add_argument(
        "--reasoning-effort",
        type=str,
        default=None,
        choices=["low", "medium", "high", "xhigh"],
        help="Optional reasoning effort to pass as `-c model_reasoning_effort=...`. Falls back to the Codex CLI's configured default when omitted.",
    )
    parser.add_argument(
        "--sandbox",
        type=str,
        default="read-only",
        choices=["read-only", "workspace-write", "danger-full-access"],
        help="Codex sandbox mode. Default `read-only` matches audit-style callers (plan consensus, general consensus, arch preflight). Use `workspace-write` when the prompt instructs Codex to edit files directly (research review, doc gap-fills).",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def extract_structured_output(path: Path) -> Any:
    if not path.exists():
        raise StructuredOutputError("Codex did not write the requested output file.")

    text = read_text(path)
    if not text.strip():
        raise StructuredOutputError("Codex wrote an empty output file.")

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise StructuredOutputError(f"Codex wrote invalid JSON: {exc}") from exc


def summarize_failure(stdout: str, stderr: str) -> str:
    details = [part.strip() for part in (stdout, stderr) if part.strip()]
    if not details:
        return "no stdout or stderr was captured"
    return " | ".join(dict.fromkeys(details))


def run_codex(
    prompt: str,
    schema_path: Path,
    result_path: Path,
    cwd: Path,
    timeout_seconds: int,
    model: str | None = None,
    reasoning_effort: str | None = None,
    sandbox: str = "read-only",
) -> subprocess.CompletedProcess[str]:
    command = ["codex", "exec", "-C", str(cwd)]
    if model:
        command.extend(["-m", model])
    if reasoning_effort:
        command.extend(["-c", f'model_reasoning_effort="{reasoning_effort}"'])
    command.extend(
        [
            "--skip-git-repo-check",
            "--sandbox",
            sandbox,
            "--output-schema",
            str(schema_path),
            "-o",
            str(result_path),
            "-",
        ]
    )
    return subprocess.run(
        command,
        input=prompt,
        text=True,
        capture_output=True,
        check=False,
        cwd=str(cwd),
        timeout=timeout_seconds,
    )


def main() -> int:
    args = parse_args()
    prompt = read_text(args.prompt_file)

    try:
        completed = run_codex(
            prompt=prompt,
            schema_path=args.schema_path,
            result_path=args.result_path,
            cwd=args.cwd,
            timeout_seconds=args.timeout_seconds,
            model=args.model,
            reasoning_effort=args.reasoning_effort,
            sandbox=args.sandbox,
        )
    except subprocess.TimeoutExpired as exc:
        raise StructuredOutputError(f"Codex timed out after {args.timeout_seconds}s") from exc

    if args.raw_output_path is not None:
        write_text(args.raw_output_path, completed.stdout)

    if completed.returncode != 0:
        raise StructuredOutputError(
            f"Codex exited with status {completed.returncode}: {summarize_failure(completed.stdout, completed.stderr)}"
        )

    structured_output = extract_structured_output(args.result_path)
    rendered_output = json.dumps(structured_output, indent=2, sort_keys=True) + "\n"
    write_text(args.result_path, rendered_output)
    sys.stdout.write(rendered_output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except StructuredOutputError as exc:
        print(f"Structured output error: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
