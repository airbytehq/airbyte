---
sidebar_label: "MCP server"
sidebar_position: 2
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Agent Engine MCP server tutorial

In this tutorial, you install Airbyte's Agent Engine MCP server, configure a connector, and register the server with your agent. Once registered, you can use natural language to query your data sources. You don't have to write any code.

This tutorial uses GitHub as an example, but you can substitute any [agent connector](../../connectors/) that Airbyte supports.

## Overview

This tutorial is for AI engineers and other technical users who work with data and AI tools. You can complete it in about 5 minutes.

The tutorial assumes you have basic familiarity with:

- Python and package management with [uv](https://github.com/astral-sh/uv)
- MCP servers

## Before you start

Before you begin this tutorial, ensure you have the following.

- [Python](https://www.python.org/downloads/) version 3.13 or later

- [uv](https://docs.astral.sh/uv/getting-started/installation/)

- A [GitHub personal access token](https://github.com/settings/tokens). For this tutorial, a classic token with `repo` scope is sufficient.

- An agent that supports MCP servers

## Part 1: Create a project

Create a directory for your MCP server configuration and initialize a uv project:

```bash
mkdir my-mcp-server && cd my-mcp-server
uv init --python 3.13
```

Add `airbyte-agent-mcp` as a dependency:

```bash
uv add --prerelease allow airbyte-agent-mcp
```

This installs the package and makes the `adp` command-line tool available through `uv run`. You use `adp` to discover connectors, generate configurations, and register the MCP server with your agent.

:::note
The `--prerelease allow` flag is required because `airbyte-agent-mcp` depends on a pre-release version of one of its upstream libraries. This flag is only needed during installation.
:::

## Part 2: List available connectors

Run the following command to see the available open source connectors:

```bash
uv run adp connectors list-oss
```

This queries the Airbyte connector registry and displays a table of available connectors, their package names, versions, and definition IDs.

To filter by name, use the `--pattern` flag:

```bash
uv run adp connectors list-oss --pattern github
```

## Part 3: Generate a connector configuration

Generate a configuration file for the GitHub connector:

```bash
uv run adp connectors configure --package airbyte-agent-github
```

This installs the connector package, inspects its authentication requirements, and generates a YAML configuration file called `connector-github-package.yaml`. The file looks like this:

```yaml title="connector-github-package.yaml"
connector:
  package: airbyte-agent-github
credentials:
  access_token: ${env.GITHUB_ACCESS_TOKEN}
```

The `${env.GITHUB_ACCESS_TOKEN}` placeholder tells the MCP server to read the value from an environment variable. You set this in the next step.

:::note
Some connectors support multiple authentication methods. The `configure` command may include commented-out alternatives in the generated file. You only need to configure one method.
:::

## Part 4: Set your credentials

Create a `.env` file in the same directory as your connector configuration:

```text title=".env"
GITHUB_ACCESS_TOKEN=your-github-personal-access-token
```

Replace the placeholder with your actual GitHub personal access token.

The `adp` CLI automatically loads `.env` files from the current directory. The `${env.VAR}` syntax in your YAML configuration resolves to the values in this file.

:::warning
Never commit your `.env` file to version control. If you do this by mistake, rotate your secrets immediately.
:::

## Part 5: Register with your agent

Register the MCP server with your preferred agent.

<Tabs>
<TabItem value="claude-code" label="Claude Code" default>

```bash
uv run adp mcp add-to claude-code connector-github-package.yaml
```

This runs `claude mcp add` under the hood and registers the server at the user scope by default. To register at the project scope instead:

```bash
uv run adp mcp add-to claude-code connector-github-package.yaml --scope project
```

</TabItem>
<TabItem value="claude-desktop" label="Claude Desktop">

```bash
uv run adp mcp add-to claude-desktop connector-github-package.yaml
```

This modifies your Claude Desktop configuration file directly. On macOS, the config file is at `~/Library/Application Support/Claude/claude_desktop_config.json`.

</TabItem>
<TabItem value="cursor" label="Cursor">

```bash
uv run adp mcp add-to cursor connector-github-package.yaml
```

This modifies the Cursor MCP configuration file. To register at the project scope instead of user scope:

```bash
uv run adp mcp add-to cursor connector-github-package.yaml --scope project
```

</TabItem>
<TabItem value="codex" label="Codex">

```bash
uv run adp mcp add-to codex connector-github-package.yaml
```

This runs `codex mcp add` to register the server.

</TabItem>
</Tabs>

You can optionally specify a custom name for the server with `--name`:

```bash
uv run adp mcp add-to claude-code connector-github-package.yaml --name my-github
```

If you don't specify a name, the server is named automatically based on the connector (for example, `airbyte-github`).

## Part 6: Use it

Restart your agent so it picks up the new MCP server registration.

Once restarted, prompt your agent with natural language questions about your GitHub data. Try prompts like:

- "List the 5 most recent open issues in airbytehq/airbyte"
- "Show me the latest pull requests in my-org/my-repo"
- "What are the open issues assigned to octocat?"

Your agent discovers the MCP server's tools automatically and calls them based on your prompts. The MCP server handles executing the connector operations and returning the results.

### Troubleshooting

If your agent fails to retrieve data, check the following:

- **MCP server not found**: Ensure you restarted your agent after registering the server.
- **Environment variable errors**: Verify your `.env` file is in the same directory where you run the `adp` commands and that the variable names match your YAML configuration.
- **HTTP 401 errors**: Your GitHub token is invalid or expired. Generate a new token and update your `.env` file.
- **HTTP 403 errors**: Your GitHub token doesn't have the required scopes. Ensure your token has `repo` scope.

## Summary

In this tutorial, you learned how to:

- Set up a project with the Agent Engine MCP server
- Discover available connectors with the `adp` CLI
- Generate a connector configuration file
- Set credentials using environment variables
- Register the MCP server with an agent
- Query data using natural language prompts

## Next steps

- Try a different connector. Run `uv run adp connectors list-oss` to see all available connectors and repeat these steps with a different data source.

- Learn how to [configure the MCP server](../../mcp-server/configuration) for advanced scenarios like Airbyte Cloud hosted execution, git-based packages, and aggregate configurations with multiple connectors.

- Learn about [field selection, downloads, and other advanced features](../../mcp-server/usage).
