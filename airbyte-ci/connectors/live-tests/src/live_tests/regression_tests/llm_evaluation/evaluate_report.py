#!/usr/bin/env python3
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
LLM-based evaluation of regression test reports.

This script reads a regression test report (HTML format) and uses OpenAI's LLM
to evaluate the results, make a pass/fail judgment, and generate a summary.
The summary is written to GITHUB_STEP_SUMMARY for display in GitHub Actions.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from openai import OpenAI

MAX_REPORT_CHARS = 200000

# Default evaluation prompt
EVAL_PROMPT = """You are an expert at evaluating connector regression test results. 
Your task is to analyze the test report and determine if the regression tests should PASS or FAIL.

Consider the following criteria:
1. All test cases should pass (no failed tests)
2. Record count differences between control and target versions should be minimal or explainable
3. Message count differences should not indicate data loss or corruption
4. Stream coverage should be reasonable
5. Any warnings or errors in test outputs should be evaluated for severity

Provide your evaluation in the following JSON format:
{
    "pass": true/false,
    "summary": "A concise 2-3 sentence summary of the evaluation",
    "reasoning": "Detailed reasoning for your pass/fail decision, including specific issues found",
    "severity": "critical/major/minor/none",
    "recommendations": "Any recommendations for addressing issues"
}

Be strict but fair in your evaluation. Minor differences are acceptable, but data loss, 
corruption, or test failures should result in a FAIL."""


def load_report_text(html_path: Path) -> str:
    """
    Load and convert HTML report to clean text.

    Args:
        html_path: Path to the report.html file

    Returns:
        Clean text representation of the report
    """
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")

    for element in soup(["script", "style"]):
        element.decompose()

    report_text = soup.get_text("\n", strip=True)

    report_text = "\n".join(line.strip() for line in report_text.splitlines() if line.strip())

    if len(report_text) > MAX_REPORT_CHARS:
        original_length = len(report_text)
        report_text = report_text[:MAX_REPORT_CHARS]
        truncation_note = f"\n\n[Report truncated from {original_length} to {MAX_REPORT_CHARS} characters for evaluation]"
        report_text += truncation_note
        print(f"Warning: Report truncated from {original_length} to {MAX_REPORT_CHARS} characters")

    return report_text


def evaluate_with_llm(report_text: str, prompt: str | None = None) -> dict[str, Any]:
    """
    Use OpenAI LLM to evaluate the regression test report.

    Supports both OpenAI API and GitHub Models API (OpenAI-compatible).
    Configure via environment variables:
    - OPENAI_API_KEY: API key (or GitHub token for GitHub Models)
    - OPENAI_BASE_URL: Optional base URL (e.g., https://models.github.ai/inference for GitHub Models)
    - EVAL_MODEL: Model name (defaults to gpt-4o)

    Args:
        report_text: Full text of the report
        prompt: Optional custom evaluation prompt (defaults to EVAL_PROMPT)

    Returns:
        Dictionary containing evaluation results with 'pass', 'summary', 'reasoning', 'severity', and 'recommendations' keys
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    model = os.environ.get("EVAL_MODEL", "gpt-4o")

    if base_url:
        client = OpenAI(api_key=api_key, base_url=base_url)
        print(f"Using custom base URL: {base_url}")
    else:
        client = OpenAI(api_key=api_key)

    print(f"Using model: {model}")

    if prompt is None:
        prompt = EVAL_PROMPT

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Report:\n\n{report_text}"},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        evaluation = json.loads(response.choices[0].message.content)
        return evaluation
    except Exception as e:
        error_msg = str(e).lower()
        if "response_format" in error_msg or "json_object" in error_msg:
            print(f"Warning: JSON response format not supported, retrying without it: {e}")
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": f"Report:\n\n{report_text}"},
                    ],
                    temperature=0.3,
                )
                content = response.choices[0].message.content
                evaluation = json.loads(content)
                return evaluation
            except Exception as retry_error:
                print(f"Retry also failed: {retry_error}")
                e = retry_error

        # Fallback to keyword-based evaluation
        has_failures = "failed" in report_text.lower() or "error" in report_text.lower()
        return {
            "pass": not has_failures,
            "summary": f"LLM evaluation failed: {str(e)}. Falling back to simple keyword-based evaluation.",
            "reasoning": "Unable to perform detailed analysis. Check for 'failed' or 'error' keywords in report.",
            "severity": "critical" if has_failures else "none",
            "recommendations": "Review the test report manually and retry LLM evaluation.",
        }


def write_github_summary(evaluation: dict[str, Any], model: str | None = None) -> None:
    """
    Write the evaluation summary to GITHUB_STEP_SUMMARY.

    Args:
        evaluation: LLM evaluation results
        model: Model name used for evaluation (optional)
    """
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_file:
        print("Warning: GITHUB_STEP_SUMMARY environment variable not set. Writing to stdout instead.")
        summary_file = "/dev/stdout"

    status_emoji = "✅" if evaluation["pass"] else "❌"
    severity_emoji = {"critical": "🔴", "major": "🟠", "minor": "🟡", "none": "🟢"}.get(evaluation.get("severity", "none"), "⚪")

    model_info = f"model: {model}" if model else "OpenAI-compatible API"

    markdown = f"""# {status_emoji} Regression Test Evaluation: {"PASS" if evaluation['pass'] else "FAIL"}

{evaluation['summary']}


{evaluation['reasoning']}

{evaluation.get('recommendations', 'No specific recommendations.')}

---
*This evaluation was generated using {model_info}*
"""

    with open(summary_file, "a", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Summary written to {summary_file}")


def main():
    """Main entry point for the LLM evaluation script."""
    parser = argparse.ArgumentParser(description="Evaluate regression test reports using OpenAI LLM")
    parser.add_argument("--report-path", type=Path, required=True, help="Path to the report.html file")
    parser.add_argument("--prompt-file", type=Path, help="Optional path to a custom evaluation prompt file")
    parser.add_argument("--output-json", type=Path, help="Optional path to write evaluation results as JSON")

    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    if not args.report_path.exists():
        print(f"Error: Report file not found: {args.report_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading report from: {args.report_path}")
    report_text = load_report_text(args.report_path)
    print(f"Report loaded: {len(report_text)} characters")

    custom_prompt = None
    if args.prompt_file and args.prompt_file.exists():
        with open(args.prompt_file, "r", encoding="utf-8") as f:
            custom_prompt = f.read()
        print(f"Using custom prompt from: {args.prompt_file}")

    print("Evaluating report with OpenAI LLM...")
    evaluation = evaluate_with_llm(report_text, custom_prompt)

    print(f"\nEvaluation Result: {'PASS' if evaluation['pass'] else 'FAIL'}")
    print(f"Summary: {evaluation['summary']}")

    model = os.environ.get("EVAL_MODEL", "gpt-4o")
    write_github_summary(evaluation, model)

    if args.output_json:
        output_data = {"evaluation": evaluation}
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)
        print(f"Evaluation results written to: {args.output_json}")

    sys.exit(0 if evaluation["pass"] else 1)


if __name__ == "__main__":
    main()
