# LLM-Based Regression Test Evaluation

Automated evaluation of connector regression test reports using LLM models.

## How It Works

After regression tests complete, this evaluates the HTML report and writes a pass/fail judgment to `GITHUB_STEP_SUMMARY`.

## Configuration

**Environment Variables:**
- `OPENAI_API_KEY` - API key (use `ollama` for Ollama)
- `OPENAI_BASE_URL` - Base URL for OpenAI-compatible API (e.g., `http://127.0.0.1:11434/v1` for Ollama)
- `EVAL_MODEL` - Model name (defaults to `gpt-4o`)

**Evaluation Prompt:**
Stored in `.github/prompts/regression-evaluation.prompt.yaml` following GitHub's prompt format. Uses `{{report_text}}` placeholder for dynamic content injection.

## Local Testing

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.2:3b

# Set environment
export OPENAI_API_KEY=ollama
export OPENAI_BASE_URL=http://127.0.0.1:11434/v1
export EVAL_MODEL=llama3.2:3b

# Run evaluation
cd airbyte-ci/connectors/live-tests
poetry install
poetry run python src/live_tests/regression_tests/llm_evaluation/evaluate_report.py \
  --report-path /path/to/report.html
```
