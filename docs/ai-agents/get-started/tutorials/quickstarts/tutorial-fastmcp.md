---
sidebar_label: "FastMCP"
sidebar_position: 3
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Agent connector tutorial: FastMCP

In this tutorial, you'll create a new Python project with uv, build a FastMCP server that exposes one of Airbyte's agent connectors as an MCP tool, and use it to query GitHub data from any MCP-compatible agent. This tutorial uses GitHub, but if you don't have a GitHub account you can swap in any other agent connector and perform different operations.

Your MCP server executes through Airbyte, so the third-party credentials you use (for GitHub or any other service) never leave your Airbyte Agents account. Your Python code only ever sees your Airbyte client ID and client secret.

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
- Your Airbyte API credentials. Copy `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` from the [Profile page](https://app.airbyte.ai/profile) in the Airbyte Agents web app. See [Manage your user profile](../../../admin/profile) for details.
- A GitHub connector added to your Airbyte Agents workspace. Add one of these two ways:
    - **Web app (recommended)**: Go to [Credentials](https://app.airbyte.ai/credentials) in the Airbyte Agents web app, add a GitHub connector, and authenticate it with a [GitHub personal access token](https://github.com/settings/tokens) (a classic token with `repo` scope is sufficient for this tutorial) or OAuth. See [Add a connector](../../../interfaces/ui/add-connector) for details.
    - **API**: Create a connector with `POST /api/v1/integrations/connectors` and store your GitHub credentials. See [Add a connector](../../../interfaces/api/add-connector) for details.
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

Install the GitHub connector and FastMCP:

```bash
uv add airbyte-agent-sdk fastmcp python-dotenv
```

This command installs:

- `airbyte-agent-sdk`: The Airbyte Agents Python SDK, which provides type-safe access to every agent connector.
- `fastmcp`: A Python framework for building MCP servers with minimal boilerplate.
- `python-dotenv`: A library you can use to load environment variables from a `.env` file.

## Part 3: Import FastMCP and the GitHub agent connector

1. Create a `server.py` file for your MCP server definition:

   ```bash
   touch server.py
   ```

2. Add the following imports to `server.py`:

    ```python title="server.py"
    import os
    import json

    from dotenv import load_dotenv
    from fastmcp import FastMCP
    from airbyte_agent_sdk import AirbyteAuthConfig
    from airbyte_agent_sdk.connectors.github import GithubConnector
    ```

    These imports provide:

    - `os` and `json`: Access environment variables and serialize connector results.
    - `load_dotenv`: Load environment variables from your `.env` file.
    - `FastMCP`: The FastMCP server class that handles MCP protocol communication.
    - `AirbyteAuthConfig`: The auth object that tells the connector which Airbyte workspace and client credentials to use.
    - `GithubConnector`: The Airbyte agent connector that executes GitHub operations through Airbyte Agents.

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

connector = GithubConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="default",
        airbyte_client_id=os.environ["AIRBYTE_CLIENT_ID"],
        airbyte_client_secret=os.environ["AIRBYTE_CLIENT_SECRET"],
    ),
)
```

- `FastMCP("GitHub Agent")` creates a new MCP server named "GitHub Agent".
- The connector authenticates to Airbyte with your Airbyte client credentials. Airbyte uses the GitHub credentials you already stored with your connector to talk to GitHub.
- `workspace_name` is the Airbyte workspace where the SDK looks up your connector. `"default"` points to your Airbyte Agents default workspace, which is where the web app stores credentials unless you change it.

### Register the tool

Register the connector's `execute` method as an MCP tool. The `@GithubConnector.tool_utils` decorator automatically generates a comprehensive tool description from the connector's metadata. This tells the agent what entities are available (issues, pull requests, repositories, etc.), what actions it can perform on each entity, and what parameters each action requires.

```python title="server.py"
@mcp.tool()
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute GitHub connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

With this single tool, your MCP server exposes all of the connector's capabilities. The agent decides which entity and action to use based on your natural language questions.

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

    - "List the 5 most recent open issues in airbytehq/airbyte"
    - "Show me the latest pull requests in my-org/my-repo"
    - "What are the open issues assigned to octocat?"

Your agent discovers the MCP server's tools automatically and calls them based on your prompts. The MCP server hands each tool call off to Airbyte, which executes the operation against GitHub and returns the result.

### Troubleshooting

If your agent fails to retrieve GitHub data, check the following:

- **Server not found**: Ensure the path in your MCP configuration points to the correct `server.py` file and that `uv` is available on your system PATH.
- **HTTP 401/403 errors from Airbyte**: Verify that `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` are copied correctly from your [Profile page](https://app.airbyte.ai/profile).
- **"No connector found" or "connector not configured"**: Make sure you've added a GitHub connector in the [Credentials](https://app.airbyte.ai/credentials) page of the Airbyte Agents web app, and that `external_user_id` in your code matches the workspace where you added it (`"default"` if you haven't changed workspaces).
- **HTTP 401/403 errors from GitHub**: The GitHub token or OAuth credentials stored in your connector are invalid or missing required scopes. Open your GitHub connector in the web app and reauthenticate with a valid token that has `repo` scope.

## Summary

In this tutorial, you learned how to:

- Set up a new Python project with uv
- Add FastMCP and Airbyte's GitHub agent connector to your project
- Configure environment variables for your Airbyte Agents credentials
- Build a FastMCP server that exposes the GitHub connector as an MCP tool
- Register the MCP server with your agent and query data using natural language through Airbyte

## Next steps

- Add more agent connectors to your project. Explore other agent connectors in the [Airbyte agent connectors catalog](../../../connectors/) to give your MCP server access to more services like Stripe, HubSpot, and Salesforce. You can register multiple tools on the same FastMCP server. Each connector works the same way: add it in the web app, then initialize it in your code with your Airbyte client credentials.

- Consider how you might like to expand your MCP server. For example, you can add [MCP prompts](https://gofastmcp.com/servers/prompts) to provide reusable prompt templates, or [MCP resources](https://gofastmcp.com/servers/resources) to expose data directly. See the [FastMCP documentation](https://gofastmcp.com) for more options.
