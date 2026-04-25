---
sidebar_label: "FastMCP"
sidebar_position: 3
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Agent connector tutorial: FastMCP

In this tutorial, you'll create a new Python project with uv, build a FastMCP server that exposes one of Airbyte's agent connectors as an MCP tool, and use it to query GitHub data from any MCP-compatible agent. This tutorial uses GitHub, but if you don't have a GitHub account you can swap in any other agent connector and perform different operations.

Your MCP server executes through Airbyte. Airbyte Agents owns the OAuth apps, stores your third-party tokens, and refreshes them for you. Your Python code only ever sees your Airbyte client ID and client secret.

## Overview

This tutorial is for AI engineers and other technical users who work with data and AI tools. You can complete it in about 15 minutes.

The tutorial assumes you have basic knowledge of the following tools, but most software engineers shouldn't struggle with anything that follows.

- Python and package management with uv
- MCP (Model Context Protocol) and MCP servers
- GitHub, or a different third-party service you want to connect to

## Before you start

Before you begin this tutorial, ensure you have the following.

- [Python](https://www.python.org/downloads/) version 3.13 or later
- [uv](https://github.com/astral-sh/uv)
- An [Airbyte Agents account](https://app.airbyte.ai). You can sign up for free.
- Your Airbyte API credentials. Copy `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` from the [Profile page](https://app.airbyte.ai/profile) in the Airbyte Agents web app. See [Manage your user profile](../../admin/profile) for details.
- A GitHub connector added to your Airbyte Agents workspace. Add one of these two ways:
    - **Web app (recommended)**: Go to [Credentials](https://app.airbyte.ai/credentials) in the Airbyte Agents web app, add a GitHub connector, and authenticate it with a [GitHub personal access token](https://github.com/settings/tokens) (a classic token with `repo` scope is sufficient for this tutorial) or OAuth. See [Add a connector](../../interfaces/ui/add-connector) for details.
    - **API**: Create a connector with `POST /api/v1/integrations/connectors` and store your GitHub credentials. See [Add a connector](../../interfaces/api/add-connector) for details.
- An agent that supports MCP servers, such as [Claude Desktop](https://claude.ai/download), [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview), or [Cursor](https://www.cursor.com/).

## Part 1: Create a new Python project

Create a new project using uv:

```bash
uv init my-mcp-agent --app
cd my-mcp-agent
```

This creates a project with the following structure:

```text
my-mcp-agent/
├── .gitignore
├── .python-version
├── main.py
├── pyproject.toml
└── README.md
```

## Part 2: Install dependencies

Install the Airbyte agent SDK and FastMCP:

```bash
uv add airbyte-agent-sdk fastmcp python-dotenv
```

This command installs:

- `airbyte-agent-sdk`: The Airbyte Agents Python SDK, which ships every connector as a typed submodule.
- `fastmcp`: A Python framework for building MCP servers with minimal boilerplate.
- `python-dotenv`: A library you can use to load environment variables from a `.env` file.

## Part 3: Import FastMCP and the GitHub agent connector

1. Create a `server.py` file for your MCP server definition:

   ```bash
   touch server.py
   ```

2. Add the following imports to `server.py`:

    ```python title="server.py"
    import json

    from dotenv import load_dotenv
    from fastmcp import FastMCP
    from airbyte_agent_sdk import connect
    from airbyte_agent_sdk.connectors.github import GithubConnector
    ```

    These imports provide:

    - `json`: Serialize connector results for the MCP tool return value.
    - `load_dotenv`: Load environment variables from your `.env` file.
    - `FastMCP`: The FastMCP server class that handles MCP protocol communication.
    - `connect`: The Airbyte agent SDK entry point. One call returns a typed connector bound to your workspace.
    - `GithubConnector`: The connector class. You reference it when decorating the tool so the SDK can describe the connector's entities and actions to the agent.

## Part 4: Add a .env file with your secrets

1. Create a `.env` file in your project root and add your Airbyte API credentials to it. Replace the placeholder values with your actual credentials.

    ```text title=".env"
    AIRBYTE_CLIENT_ID=your-airbyte-client-id
    AIRBYTE_CLIENT_SECRET=your-airbyte-client-secret
    ```

    Copy these values from the [Profile page](https://app.airbyte.ai/profile) in the Airbyte Agents web app.

    :::warning
    Never commit your `.env` file to version control. If you do this by mistake, rotate your secrets immediately.
    :::

2. Add the following line to `server.py` after your imports to load the environment variables:

    ```python title="server.py"
    load_dotenv()
    ```

## Part 5: Configure your connector and MCP server

Now that your environment is set up, add the following code to `server.py` to create the GitHub connector and FastMCP server.

### Create the server and connector

```python title="server.py"
mcp = FastMCP("GitHub Agent")

github = connect("github")
```

`FastMCP("GitHub Agent")` creates a new MCP server named "GitHub Agent".

`connect("github")` does four things for you:

- Reads `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` from the environment.
- Defaults to the `"default"` workspace, which is where the web app stores credentials unless you change it.
- Returns a typed `GithubConnector` bound to the authenticated GitHub connector you added earlier.
- Routes every `github.execute(...)` call through Airbyte's hosted API, which holds the GitHub OAuth tokens and refreshes them for you.

You never register an OAuth app, copy a GitHub token into your code, or write token-refresh logic.

If you want to connect to a different workspace or pass credentials explicitly, use `connect("github", workspace_name="my-workspace", client_id=..., client_secret=...)` or pass an `AirbyteAuthConfig`. See the [SDK reference](https://github.com/airbytehq/airbyte-agent-sdk) for details.

### Register the tool

Rather than one tool per GitHub endpoint, the Airbyte agent SDK exposes the entire GitHub API through a single `execute(entity, action, params)` entry point. The `@GithubConnector.tool_utils` decorator fills in the entity and action catalog as part of the tool description, so the agent knows what's available without you writing a schema.

```python title="server.py"
@mcp.tool()
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute GitHub connector operations."""
    result = await github.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

The decorator stack is the whole tool definition. No per-action `docstring`, no `GITHUB_LIST_COMMITS` or `GITHUB_GET_PR` sprawl, one entry point that covers the full connector. `@GithubConnector.tool_utils` appends the full entity and action catalog to the tool description so the MCP client sees every entity, action, and enum value the connector supports. As the connector grows, the tool signature stays the same.

Each `execute` call returns a structured result with `data` (the records) and `meta` (pagination cursors). MCP tools return strings, so this tutorial serializes the whole result with `json.dumps` so the MCP client can reason about both the records and the pagination state.

### Add the server entry point

Add the following at the bottom of `server.py` to start the server when run directly:

```python title="server.py"
if __name__ == "__main__":
    mcp.run()
```

## Part 6: Register with your agent

Register the MCP server with your preferred agent. Provide the full path to your project's `server.py` file. Replace `/path/to/my-mcp-agent` with the actual path to your project directory.

<Tabs>
<TabItem value="claude-code" label="Claude Code" default>

```bash
claude mcp add github-agent -- uv run --directory /path/to/my-mcp-agent server.py
```

</TabItem>
<TabItem value="claude-desktop" label="Claude Desktop">

Add the following to your Claude Desktop configuration file (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "github-agent": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/my-mcp-agent", "server.py"]
    }
  }
}
```

On macOS, the config file is at `~/Library/Application Support/Claude/claude_desktop_config.json`. On Windows, it's at `%APPDATA%\Claude\claude_desktop_config.json`.

</TabItem>
<TabItem value="cursor" label="Cursor">

Add the following to your Cursor MCP configuration file (`.cursor/mcp.json` in your project directory, or `~/.cursor/mcp.json` for global configuration):

```json
{
  "mcpServers": {
    "github-agent": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/my-mcp-agent", "server.py"]
    }
  }
}
```

</TabItem>
</Tabs>

## Part 7: Use the MCP server

1. Restart your agent so it picks up the new MCP server registration.

2. Once restarted, prompt your agent with natural language questions about your GitHub data. Try prompts like:

    - "List the 10 most recent open issues in airbytehq/airbyte"
    - "What are the 10 most recent pull requests that are still open in airbytehq/airbyte?"
    - "Are there any open issues that might be fixed by a pending PR?"

Your agent discovers the MCP server's tools automatically and calls them based on your prompts. The MCP server hands each tool call off to Airbyte, which executes the operation against GitHub and returns the result.

### Troubleshooting

If your agent fails to retrieve GitHub data, check the following:

- **Server not found**: Ensure the path in your MCP configuration points to the correct `server.py` file and that `uv` is available on your system PATH.
- **HTTP 401/403 errors from Airbyte**: Verify that `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` are copied correctly from your [Profile page](https://app.airbyte.ai/profile).
- **"No connector found" or "connector not configured"**: Make sure you've added a GitHub connector in the [Credentials](https://app.airbyte.ai/credentials) page of the Airbyte Agents web app. `connect("github")` defaults to the `"default"` workspace; if you added the connector to a different workspace, pass `workspace_name="your-workspace-name"` to `connect()`.
- **HTTP 401/403 errors from GitHub**: The GitHub token or OAuth credentials stored in your connector are invalid or missing required scopes. Open your GitHub connector in the web app and reauthenticate with a valid token that has `repo` scope.
- **Empty `data=[]` responses from filtered queries**: Most GitHub filters use case-sensitive values. Confirm the agent is sending uppercase values (for example, `states=["OPEN"]` rather than `states=["open"]`). The tool description's rules nudge the model to do that by default; you can also reinforce the rules in your client's system prompt.

## Summary

In this tutorial, you learned how to:

- Set up a new Python project with uv
- Add FastMCP and Airbyte's GitHub agent connector to your project
- Configure environment variables for your Airbyte Agents credentials
- Register a single MCP tool that covers the entire GitHub API
- Register your MCP server with an agent and use natural language to interact with GitHub data through Airbyte

## Next steps

- **Add another connector.** The same `connect(...)` + `execute(...)` pattern covers the full [Airbyte agent connectors catalog](../../connectors). Add Slack, Stripe, Salesforce, or any other connector in the web app, then call `slack = connect("slack")` in your server and register a second tool with another `@mcp.tool()` / `@SlackConnector.tool_utils` stack. Your MCP client now reads GitHub and posts to Slack with no additional OAuth setup.
- **Use write actions.** Connectors expose create, update, and post actions alongside the read ones. Ask your client to file an issue, comment on a PR, or send a Slack message, and `execute` carries the write through with the stored OAuth token.
- **Let your AI assistant scaffold the next server.** The Airbyte agent SDK ships skills for Claude Code and Codex that carry the patterns above, so you can ask your assistant to build a new MCP server without retyping them. See the [airbyte-agent-sdk repository](https://github.com/airbytehq/airbyte-agent-sdk) for installation instructions.
- **Reach the same connectors from a hosted MCP endpoint.** Airbyte Agents exposes the same connectors through a hosted MCP endpoint that works with Claude Code, Cursor, and ChatGPT, with one OAuth flow per provider shared across clients. Use this when you don't want to run and maintain your own MCP server.
