# LLM-Based Regression Test Evaluation

This module provides automated evaluation of connector regression test reports using LLM models via OpenAI-compatible APIs. The evaluation analyzes test results, metrics, and differences between control and target connector versions to make an intelligent pass/fail judgment.

## Overview

The LLM evaluation step runs automatically after regression tests complete in GitHub Actions. It:

1. **Extracts data** from the HTML regression test report
2. **Analyzes** test results, stream coverage, record counts, and message metrics
3. **Evaluates** using an LLM (GitHub Models or OpenAI) with a configurable prompt
4. **Generates** a comprehensive summary with pass/fail judgment
5. **Outputs** the summary to `GITHUB_STEP_SUMMARY` for display in the GitHub Actions UI

## Features

- **Intelligent Analysis**: Uses LLM to understand context and make nuanced judgments about test results
- **Comprehensive Evaluation**: Considers test pass/fail status, data differences, coverage metrics, and error messages
- **Configurable Prompts**: Supports custom evaluation prompts for specific use cases
- **GitHub Integration**: Automatically displays results in GitHub Actions job summaries
- **Fallback Logic**: Provides simple pass/fail evaluation if LLM call fails

## Usage

### In GitHub Actions (Automatic)

The LLM evaluation runs automatically in the `regression_tests.yml` workflow after regression tests complete. No manual intervention is required.

The workflow step:
- Finds the most recent `report.html` in `/tmp/regression_tests_artifacts/`
- Runs the evaluation script with the OpenAI API key from secrets
- Writes results to `GITHUB_STEP_SUMMARY`

### Manual Execution

You can also run the evaluation script manually:

```bash
# From airbyte-ci/connectors/live-tests directory
poetry install  # Install dependencies including beautifulsoup4 and openai

# Run evaluation
poetry run python src/live_tests/regression_tests/llm_evaluation/evaluate_report.py \
  --report-path /path/to/report.html \
  --output-json /path/to/output.json
```

### With Custom Prompt

Create a custom evaluation prompt file:

```bash
# Create custom prompt
cat > custom_prompt.txt << 'EOF'
You are evaluating a regression test for a critical production connector.
Be extremely strict in your evaluation. Any data loss or corruption should
result in a FAIL. Provide detailed analysis of all differences found.
EOF

# Run with custom prompt
poetry run python src/live_tests/regression_tests/llm_evaluation/evaluate_report.py \
  --report-path /path/to/report.html \
  --prompt-file custom_prompt.txt
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY` (required): API key for LLM access (OpenAI API key or GitHub token for GitHub Models)
- `OPENAI_BASE_URL` (optional): Base URL for OpenAI-compatible API (e.g., `https://models.github.ai/inference` for GitHub Models)
- `EVAL_MODEL` (optional): Model name to use (defaults to `gpt-4o`, use `openai/gpt-4o` for GitHub Models)
- `GITHUB_STEP_SUMMARY` (optional): Path to GitHub Actions step summary file

### Using GitHub Models (Default in CI)

The workflow is configured to use GitHub Models API by default, which provides free LLM access in GitHub Actions:

```yaml
env:
  OPENAI_API_KEY: ${{ github.token }}
  OPENAI_BASE_URL: https://models.github.ai/inference
  EVAL_MODEL: openai/gpt-4o
```

Required workflow permissions:
```yaml
permissions:
  contents: read
  models: read
```

### Using OpenAI API

To use OpenAI's API instead of GitHub Models:

1. Set `OPENAI_API_KEY` secret in GitHub repository settings with your OpenAI API key
2. Remove or comment out `OPENAI_BASE_URL` in the workflow
3. Set `EVAL_MODEL` to `gpt-4o` (without the `openai/` prefix)

For local testing with OpenAI:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export EVAL_MODEL="gpt-4o"
# Don't set OPENAI_BASE_URL
```

### Command-Line Arguments

- `--report-path` (required): Path to the regression test `report.html` file
- `--prompt-file` (optional): Path to a custom evaluation prompt file
- `--output-json` (optional): Path to write detailed evaluation results as JSON

## Evaluation Criteria

The default evaluation prompt considers:

1. **Test Results**: All tests should pass; failed tests result in FAIL
2. **Record Count Differences**: Significant differences between control and target versions are flagged
3. **Message Count Differences**: Changes in message types that could indicate issues
4. **Stream Coverage**: Reasonable coverage of available streams
5. **Error Severity**: Warnings and errors are evaluated for impact

### Severity Levels

- **Critical** (🔴): Data loss, corruption, or multiple test failures
- **Major** (🟠): Significant differences or single test failure
- **Minor** (🟡): Small differences or warnings that don't affect functionality
- **None** (🟢): All tests pass with no significant issues

## Output Format

The evaluation generates a markdown summary with:

- **Pass/Fail Status**: Clear indication with emoji (✅/❌)
- **Summary**: 2-3 sentence overview of the evaluation
- **Severity Level**: Visual indicator of issue severity
- **Test Statistics**: Counts of passed/failed/warning tests
- **Connector Information**: Version details and context
- **Stream Coverage**: Metrics about tested streams
- **Detailed Reasoning**: In-depth analysis of findings
- **Recommendations**: Actionable suggestions for addressing issues

### Example Output

```markdown
# ✅ Regression Test Evaluation: PASS

## Summary
All regression tests passed successfully with minimal differences between control and target versions. Record counts show expected variations due to data updates. No critical issues detected.

## Severity: 🟢 NONE

## Test Statistics
- **Total Tests**: 12
- **Passed**: 12
- **Failed**: 0
- **Warnings**: 0

## Connector Information
- **Connector**: airbyte/source-faker
- **Control Version**: 1.2.3
- **Target Version**: dev

## Stream Coverage
- **Available in catalog**: 5
- **In use (in configured catalog)**: 5
- **Coverage**: 100.00%

## Detailed Reasoning
All test cases executed successfully. Record count differences are within acceptable ranges and reflect natural data growth. HTTP traffic patterns are consistent between versions. No schema changes detected.

## Recommendations
No action required. The connector is ready for release.

---
*This evaluation was generated using OpenAI GPT-4o*
```

## Architecture

### Components

1. **`evaluate_report.py`**: Main script with three key functions:
   - `load_report_text()`: Converts HTML report to clean text using BeautifulSoup
   - `evaluate_with_llm()`: Calls OpenAI-compatible API for evaluation
   - `write_github_summary()`: Formats and writes markdown output

2. **Data Extraction**: Uses BeautifulSoup to:
   - Parse HTML report and extract text content
   - Remove script and style elements
   - Truncate to 200K characters if needed

3. **LLM Integration**: Uses OpenAI Python SDK to:
   - Support both OpenAI API and GitHub Models API
   - Send full report text to the LLM for analysis
   - Request JSON-formatted evaluation response
   - Handle API errors with fallback logic
   - Retry without response_format if not supported

4. **Output Generation**: Creates markdown summary with:
   - Visual indicators (emojis)
   - Pass/fail status and severity
   - Detailed reasoning and recommendations
   - Model information footer

### Error Handling

- **Missing Report**: Gracefully handles missing report files with warning message
- **API Failures**: Falls back to simple pass/fail logic based on test results
- **Parsing Errors**: Continues with partial data if HTML parsing fails

## Dependencies

- `beautifulsoup4`: HTML parsing
- `openai`: OpenAI API client
- `pathlib`: File path handling
- Standard library: `argparse`, `json`, `os`, `sys`

## Future Enhancements

Potential improvements for future versions:

1. **Historical Comparison**: Compare current results with previous runs
2. **Trend Analysis**: Track metrics over time to identify patterns
3. **Custom Evaluators**: Support for connector-specific evaluation logic
4. **Multi-Model Support**: Allow using different LLM providers
5. **Confidence Scores**: Provide confidence levels for pass/fail decisions
6. **Interactive Mode**: Allow human review and override of LLM decisions

## Troubleshooting

### LLM Evaluation Skipped

If you see "LLM Evaluation Skipped" in the GitHub Actions summary:
- Check that regression tests completed successfully
- Verify that `report.html` was generated in `/tmp/regression_tests_artifacts/`
- Review test logs for errors during report generation

### API Key Errors

If you see "OPENAI_API_KEY environment variable not set":
- For GitHub Models (default): Ensure the workflow has `models: read` permission
- For OpenAI API: Ensure the `OPENAI_API_KEY` secret is configured in GitHub repository settings
- Verify the secret/token is passed to the workflow step in `regression_tests.yml`

### Evaluation Failures

If the LLM evaluation fails but tests passed:
- Check OpenAI API status and rate limits
- Review the fallback evaluation in the output
- Consider running the evaluation manually with `--output-json` for debugging

## Contributing

When modifying the evaluation logic:

1. Update the default prompt in `evaluate_with_llm()` if changing criteria
2. Add new data extraction logic in `extract_report_data()` for new metrics
3. Update the output format in `write_github_summary()` for new sections
4. Test with real regression test reports before submitting PR
5. Update this README with any new features or changes

## License

Copyright (c) 2024 Airbyte, Inc., all rights reserved.
