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
from typing import Any, Dict, Optional

from bs4 import BeautifulSoup
from openai import OpenAI


def extract_report_data(html_path: Path) -> Dict[str, Any]:
    """
    Extract key data from the HTML report for LLM evaluation.

    Args:
        html_path: Path to the report.html file

    Returns:
        Dictionary containing extracted report data
    """
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")

    context = {}
    context_section = soup.find("h2", string="Context")
    if context_section:
        context_list = context_section.find_next("ul")
        if context_list:
            for li in context_list.find_all("li"):
                text = li.get_text(strip=True)
                if ":" in text:
                    key, value = text.split(":", 1)
                    context[key.strip()] = value.strip()

    coverage = {}
    coverage_section = soup.find("h3", string="Stream coverage")
    if coverage_section:
        coverage_table = coverage_section.find_next("table")
        if coverage_table:
            cells = coverage_table.find_all("td")
            for i in range(0, len(cells), 2):
                if i + 1 < len(cells):
                    key = cells[i].get_text(strip=True)
                    value = cells[i + 1].get_text(strip=True)
                    coverage[key] = value

    test_results = []
    test_results_section = soup.find("h2", string="Test results")
    if not test_results_section:
        test_results_section = soup.find("h2", string=lambda text: text and "Test results" in text)

    if test_results_section:
        section_content = test_results_section.find_next("div", class_="section_content")
        if section_content:
            for test_div in section_content.find_all("div", class_="test-result"):
                test_name_h3 = test_div.find("h3", class_="test-name")
                if test_name_h3:
                    test_name = test_name_h3.get_text(strip=True)
                    style = test_name_h3.get("style", "")
                    if "green" in style or "#7ee787" in style:
                        result = "passed"
                    elif "crimson" in style or "red" in style:
                        result = "failed"
                    elif "yellow" in style or "#fddf68" in style:
                        result = "warning"
                    else:
                        result = "unknown"

                    output = ""
                    pre_tag = test_div.find("pre")
                    if pre_tag:
                        output = pre_tag.get_text(strip=True)

                    test_results.append(
                        {
                            "name": test_name,
                            "result": result,
                            "output": output[:500] if output else "",  # Limit output length
                        }
                    )

    message_metrics = {}
    message_section = soup.find("h3", string="Message types")
    if message_section:
        message_table = message_section.find_next("table")
        if message_table:
            rows = message_table.find_all("tr")
            for row in rows[2:]:  # Skip header rows
                cells = row.find_all("td")
                if cells:
                    message_type = cells[0].get_text(strip=True)
                    differences = []
                    for cell in cells[1:]:
                        if "highlighted" in cell.get("class", []):
                            differences.append(cell.get_text(strip=True))
                    if differences:
                        message_metrics[message_type] = differences

    record_metrics = {}
    record_section = soup.find("h3", string="Record count per stream")
    if record_section:
        command_headers = record_section.find_all_next("h4")
        for command_header in command_headers:
            command = command_header.get_text(strip=True)
            record_table = command_header.find_next("table")
            if record_table:
                stream_diffs = []
                rows = record_table.find_all("tr")
                for row in rows[1:]:  # Skip header
                    cells = row.find_all("td")
                    if len(cells) >= 4:
                        stream_name = cells[0].get_text(strip=True)
                        control_count = cells[1].get_text(strip=True)
                        target_count = cells[2].get_text(strip=True)
                        diff = cells[3].get_text(strip=True)
                        if "highlighted" in cells[3].get("class", []) or diff != "0":
                            stream_diffs.append(
                                {"stream": stream_name, "control": control_count, "target": target_count, "difference": diff}
                            )
                if stream_diffs:
                    record_metrics[command] = stream_diffs
            if record_table and command_header.find_next("h3"):
                break

    return {
        "context": context,
        "coverage": coverage,
        "test_results": test_results,
        "message_metrics": message_metrics,
        "record_metrics": record_metrics,
    }


def evaluate_with_llm(report_data: Dict[str, Any], prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Use OpenAI LLM to evaluate the regression test report.

    Args:
        report_data: Extracted report data
        prompt: Optional custom evaluation prompt

    Returns:
        Dictionary containing evaluation results with 'pass', 'summary', and 'reasoning' keys
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    if prompt is None:
        prompt = """You are an expert at evaluating connector regression test results. 
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

    report_summary = f"""

{json.dumps(report_data['context'], indent=2)}

{json.dumps(report_data['coverage'], indent=2)}

"""

    passed_tests = [t for t in report_data["test_results"] if t["result"] == "passed"]
    failed_tests = [t for t in report_data["test_results"] if t["result"] == "failed"]
    warning_tests = [t for t in report_data["test_results"] if t["result"] == "warning"]

    report_summary += f"""
- Passed: {len(passed_tests)}
- Failed: {len(failed_tests)}
- Warnings: {len(warning_tests)}

{json.dumps([{'name': t['name'], 'output': t['output']} for t in failed_tests], indent=2)}

{json.dumps([{'name': t['name'], 'output': t['output']} for t in warning_tests], indent=2)}

{json.dumps(report_data['message_metrics'], indent=2)}

{json.dumps(report_data['record_metrics'], indent=2)}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": report_summary}],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        evaluation = json.loads(response.choices[0].message.content)
        return evaluation
    except Exception as e:
        return {
            "pass": len(failed_tests) == 0,
            "summary": f"LLM evaluation failed: {str(e)}. Falling back to simple pass/fail based on test results.",
            "reasoning": f"Failed tests: {len(failed_tests)}, Passed tests: {len(passed_tests)}",
            "severity": "critical" if failed_tests else "none",
            "recommendations": "Review the test failures manually.",
        }


def write_github_summary(evaluation: Dict[str, Any], report_data: Dict[str, Any]) -> None:
    """
    Write the evaluation summary to GITHUB_STEP_SUMMARY.

    Args:
        evaluation: LLM evaluation results
        report_data: Extracted report data
    """
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_file:
        print("Warning: GITHUB_STEP_SUMMARY environment variable not set. Writing to stdout instead.")
        summary_file = "/dev/stdout"

    status_emoji = "✅" if evaluation["pass"] else "❌"
    severity_emoji = {"critical": "🔴", "major": "🟠", "minor": "🟡", "none": "🟢"}.get(evaluation.get("severity", "none"), "⚪")

    markdown = f"""# {status_emoji} Regression Test Evaluation: {"PASS" if evaluation['pass'] else "FAIL"}

{evaluation['summary']}


- **Total Tests**: {len(report_data['test_results'])}
- **Passed**: {len([t for t in report_data['test_results'] if t['result'] == 'passed'])}
- **Failed**: {len([t for t in report_data['test_results'] if t['result'] == 'failed'])}
- **Warnings**: {len([t for t in report_data['test_results'] if t['result'] == 'warning'])}

- **Connector**: {report_data['context'].get('Connector image', 'N/A')}
- **Control Version**: {report_data['context'].get('Control version', 'N/A')}
- **Target Version**: {report_data['context'].get('Target version', 'N/A')}

{chr(10).join([f"- **{k}**: {v}" for k, v in report_data['coverage'].items()])}

{evaluation['reasoning']}

{evaluation.get('recommendations', 'No specific recommendations.')}

---
*This evaluation was generated using OpenAI GPT-4o*
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

    print(f"Extracting data from report: {args.report_path}")
    report_data = extract_report_data(args.report_path)

    custom_prompt = None
    if args.prompt_file and args.prompt_file.exists():
        with open(args.prompt_file, "r", encoding="utf-8") as f:
            custom_prompt = f.read()
        print(f"Using custom prompt from: {args.prompt_file}")

    print("Evaluating report with OpenAI LLM...")
    evaluation = evaluate_with_llm(report_data, custom_prompt)

    print(f"\nEvaluation Result: {'PASS' if evaluation['pass'] else 'FAIL'}")
    print(f"Summary: {evaluation['summary']}")

    write_github_summary(evaluation, report_data)

    if args.output_json:
        output_data = {"evaluation": evaluation, "report_data": report_data}
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)
        print(f"Evaluation results written to: {args.output_json}")

    sys.exit(0 if evaluation["pass"] else 1)


if __name__ == "__main__":
    main()
