---
sidebar_label: "FastMCP"
sidebar_position: 3
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Agent connector tutorial: FastMCP

In this tutorial, you'll create a new Python project with uv, build a FastMCP server that exposes one of Airbyte's agent connectors as an MCP tool, and use it to query GitHub data from any MCP-compatible agent. This tutorial uses GitHub, but if you don't have a GitHub account, you can use one of Airbyte's other agent connectors and perform different operations.

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
- A [GitHub personal access token](https://github.com/settings/tokens). For this tutorial, a classic token with `repo` scope is sufficient.
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
uv add airbyte-agent-github fastmcp
```

This command installs:

- `airbyte-agent-github`: The Airbyte agent connector for GitHub, which provides type-safe access to GitHub's API.
- `fastmcp`: A Python framework for building MCP servers with minimal boilerplate.

The GitHub connector also includes `python-dotenv`, which you can use to load environment variables from a `.env` file.

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
    from airbyte_agent_github import GithubConnector
    from airbyte_agent_github.models import GithubPersonalAccessTokenAuthConfig
    ```

    These imports provide:

    - `os` and `json`: Access environment variables and serialize connector results.
    - `load_dotenv`: Load environment variables from your `.env` file.
    - `FastMCP`: The FastMCP server class that handles MCP protocol communication.
    - `GithubConnector`: The Airbyte agent connector that provides type-safe access to GitHub's API.
    - `GithubPersonalAccessTokenAuthConfig`: The authentication configuration for the GitHub connector using a personal access token.

## Part 4: Add a .env file with your secrets

1. Create a `.env` file in your project root and add your GitHub token to it. Replace the placeholder value with your actual credential.

    ```text title=".env"
    GITHUB_ACCESS_TOKEN=your-github-personal-access-token
    ```

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
    auth_config=GithubPersonalAccessTokenAuthConfig(
        token=os.environ["GITHUB_ACCESS_TOKEN"]
    )
)
```

- `FastMCP("GitHub Agent")` creates a new MCP server named "GitHub Agent".
- The connector authenticates using your personal access token.

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

Your agent discovers the MCP server's tools automatically and calls them based on your prompts. The MCP server handles executing the connector operations and returning the results.

### Troubleshooting

If your agent fails to retrieve GitHub data, check the following:

- **Server not found**: Ensure the path in your MCP configuration points to the correct `server.py` file and that `uv` is available on your system PATH.
- **HTTP 401 errors**: Your `GITHUB_ACCESS_TOKEN` is invalid or expired. Generate a new token and update your `.env` file.
- **HTTP 403 errors**: Your `GITHUB_ACCESS_TOKEN` doesn't have the required scopes. Ensure your token has `repo` scope for accessing repository data.

## Summary

In this tutorial, you learned how to:

- Set up a new Python project with uv
- Add FastMCP and Airbyte's GitHub agent connector to your project
- Configure environment variables and authentication
- Build a FastMCP server that exposes the GitHub connector as an MCP tool
- Register the MCP server with your agent and query data using natural language

## Next steps

- Add more agent connectors to your project. Explore other agent connectors in the [Airbyte agent connectors catalog](../../connectors/) to give your MCP server access to more services like Stripe, HubSpot, and Salesforce. You can register multiple tools on the same FastMCP server.

- Consider how you might like to expand your MCP server. For example, you can add [MCP prompts](https://gofastmcp.com/servers/prompts) to provide reusable prompt templates, or [MCP resources](https://gofastmcp.com/servers/resources) to expose data directly. See the [FastMCP documentation](https://gofastmcp.com) for more options.
