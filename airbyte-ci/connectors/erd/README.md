# erd

A collection of utilities for generating ERDs.

# Setup

## Installation

`erd` tools use [Poetry](https://github.com/python-poetry/poetry) to manage dependencies,
and targets Python 3.11 and higher.

Assuming you're in Airbyte repo root:

```bash
cd airbyte-ci/connectors/erd
poetry install
```

## Usage

Pre-requisites:
* Env variable `GENAI_API_KEY`. Can be found at URL https://aistudio.google.com/app/apikey

`poetry run erd --source-path <source path> --source-technical-name <for example, 'source-facebook-marketing'>`

The script supports the option to ignore the LLM generation by passing parameter `--skip-llm-relationships`

## Contributing to `erd`

### Running tests

To run tests locally:

```bash
poetry run pytest
```

## Changelog
- 0.1.1: Update Python version requirement from 3.10 to 3.11.
- 0.1.0: Initial commit
