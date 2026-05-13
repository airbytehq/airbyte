You can use Airbyte Agents programmatically three ways:

- [**SDK**](/ai-agents/interfaces/sdk): a typed Python library. Best for Python apps, notebooks, scripts, and AI agents.
- [**API**](/ai-agents/interfaces/api): an HTTP API. Best for non-Python backends and languages the SDK doesn't cover.
- [**CLI**](/ai-agents/interfaces/cli): a Go binary (`airbyte-agent`) that wraps the API. Best for shell scripts, CI jobs, and AI-agent harnesses that prefer shelling out to making HTTP calls.

Most Airbyte Agents operations are available through all three interfaces. Where the SDK can't do something directly, use the API (or the CLI, which wraps it) as noted explicitly in docs.
