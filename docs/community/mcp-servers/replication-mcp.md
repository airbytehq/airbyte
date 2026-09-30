---
sidebar_label: Replication MCP Server
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Airbyte Replication MCP Server

:::note
This MCP server implementation is experimental and may change without notice between minor versions of PyAirbyte. The API may be modified or entirely refactored in future versions.
:::

The Airbyte Replication MCP (Model Context Protocol) server provides a standardized interface for managing Airbyte data replication connections through MCP-compatible clients. This PyAirbyte-powered experimental feature allows you to list connectors, validate configurations, and run sync operations using the MCP protocol.

Use it to manage Airbyte replication workflows. It is not the primary interface agents should use to work with data. The [Agent MCP](/ai-agents/interfaces/mcp/) is the primary way agents use Airbyte to work with data.

## Connect to the hosted server

Give this URL to your agent or MCP client:

```text
https://mcp.airbyte.com/mcp
```

When prompted, sign in with your [Airbyte Cloud](https://cloud.airbyte.com) account.

### Client setup

<Tabs>
<TabItem value="claude" label="Claude" default>

In Claude or Claude Desktop, go to **Settings** > **Connectors** > **Add custom connector**, paste `https://mcp.airbyte.com/mcp`, and connect.

</TabItem>
<TabItem value="claude-code" label="Claude Code">

```bash
claude mcp add --transport http airbyte https://mcp.airbyte.com/mcp
```

Then run `claude`, type `/mcp`, select **airbyte**, and select **Authenticate**.

</TabItem>
<TabItem value="cursor" label="Cursor">

[Install in Cursor](cursor://anysphere.cursor-deeplink/mcp/install?name=airbyte&config=eyJ1cmwiOiJodHRwczovL21jcC5haXJieXRlLmNvbS9tY3AifQ%3D%3D)

Or add the [JSON config](#json-config) to `.cursor/mcp.json`.

</TabItem>
<TabItem value="vscode" label="VS Code">

[Install in VS Code](https://vscode.dev/redirect?url=vscode%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522airbyte%2522%252C%2522type%2522%253A%2522http%2522%252C%2522url%2522%253A%2522https%253A%252F%252Fmcp.airbyte.com%252Fmcp%2522%257D) or [Install in VS Code Insiders](https://insiders.vscode.dev/redirect?url=vscode-insiders%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522airbyte%2522%252C%2522type%2522%253A%2522http%2522%252C%2522url%2522%253A%2522https%253A%252F%252Fmcp.airbyte.com%252Fmcp%2522%257D)

Or run:

```bash
code --add-mcp '{"name":"airbyte","type":"http","url":"https://mcp.airbyte.com/mcp"}'
```

</TabItem>
<TabItem value="chatgpt" label="ChatGPT">

Add `https://mcp.airbyte.com/mcp` as a custom connector in ChatGPT's connector settings.

</TabItem>
<TabItem value="other" label="Other clients">

Paste `https://mcp.airbyte.com/mcp` into your client's remote MCP server settings, or add the [JSON config](#json-config) to its MCP config file. For Windsurf, use `~/.codeium/windsurf/mcp_config.json`.

</TabItem>
</Tabs>

### JSON config

Most clients, including Cursor and Windsurf, use this format:

```json
{
  "mcpServers": {
    "airbyte": {
      "url": "https://mcp.airbyte.com/mcp"
    }
  }
}
```

VS Code (`.vscode/mcp.json`) uses a `servers` key instead:

```json
{
  "servers": {
    "airbyte": {
      "type": "http",
      "url": "https://mcp.airbyte.com/mcp"
    }
  }
}
```

## Helpful prompts

Here are some things you can ask your agent to do with the Airbyte Replication MCP server:

1. "Use your MCP tools to list all available Airbyte connectors."
2. "Use your MCP tools to get information about the Airbyte Stripe connector."
3. "Use your MCP tools to check your connection to your Airbyte Cloud workspace."
4. "Use your MCP tools to list all available destinations in my Airbyte Cloud workspace."

To run the server on your own machine instead, see [Run the Replication MCP server locally](replication-mcp-local.md).

## Contributing to the Airbyte MCP Server

- [PyAirbyte Contributing Guide](https://github.com/airbytehq/PyAirbyte/blob/main/docs/CONTRIBUTING.md)

### Additional resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

For issues and questions:

- [PyAirbyte GitHub Issues](https://github.com/airbytehq/pyairbyte/issues)
- [PyAirbyte Discussions](https://github.com/airbytehq/pyairbyte/discussions)
