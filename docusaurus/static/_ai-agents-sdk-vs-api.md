You can use Airbyte Agents programmatically in several ways:

- [**MCP server**](/ai-agents/interfaces/mcp): a remote, Airbyte-hosted server. Best for AI agents that speak the Model Context Protocol (Claude, ChatGPT, Cursor, VS Code). Zero install.
- [**SDK**](/ai-agents/interfaces/sdk): a typed Python library. Best for Python apps, notebooks, scripts, and AI agents built with frameworks like Pydantic AI or LangChain.
- [**CLI**](/ai-agents/interfaces/cli): a shell interface. Best for scripts, CI jobs, and AI-agent harnesses that call command-line tools.
- [**API**](/ai-agents/interfaces/api): an HTTP API. Best for non-Python backends, custom admin flows, and languages the SDK doesn't cover.
- [**Web app**](/ai-agents/interfaces/ui): a browser UI at [app.airbyte.ai](https://app.airbyte.ai). Best for no-code exploration and scheduled automations.

All interfaces share the same connectors, credentials, and [Context Store](/ai-agents/concepts/context-store). See [Choose how to use Airbyte Agents](/ai-agents/get-started/choose-how-to-use) for a detailed comparison.
