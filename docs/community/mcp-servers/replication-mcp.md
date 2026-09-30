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

If your organization uses [single sign-on](/platform/access-management/sso), select **Sign in with SSO** on the sign-in page and enter your **Company identifier**. This is the same identifier you enter after you select **Continue with SSO** on the Airbyte Cloud login page. If you don't know it, ask your Airbyte organization admin.

### One-click install and JSON config

<Tabs>
<TabItem value="cursor" label="Cursor" default>

[Click to install in Cursor](cursor://anysphere.cursor-deeplink/mcp/install?name=airbyte&config=eyJ1cmwiOiJodHRwczovL21jcC5haXJieXRlLmNvbS9tY3AifQ%3D%3D), or add this to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "airbyte": {
      "url": "https://mcp.airbyte.com/mcp"
    }
  }
}
```

</TabItem>
<TabItem value="vscode" label="VS Code">

[Click to install in VS Code](https://vscode.dev/redirect?url=vscode%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522airbyte%2522%252C%2522type%2522%253A%2522http%2522%252C%2522url%2522%253A%2522https%253A%252F%252Fmcp.airbyte.com%252Fmcp%2522%257D) or [click to install in VS Code Insiders](https://insiders.vscode.dev/redirect?url=vscode-insiders%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522airbyte%2522%252C%2522type%2522%253A%2522http%2522%252C%2522url%2522%253A%2522https%253A%252F%252Fmcp.airbyte.com%252Fmcp%2522%257D), or add this to `.vscode/mcp.json`:

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

</TabItem>
<TabItem value="windsurf" label="Windsurf">

Add this to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "airbyte": {
      "url": "https://mcp.airbyte.com/mcp"
    }
  }
}
```

</TabItem>
</Tabs>

For CLI setup, including Claude Code, or to run the server on your own machine, see [Replication MCP advanced setup](replication-mcp-advanced.md).

## Helpful prompts

Here are some things you can ask your agent to do with the Airbyte Replication MCP server:

1. "Use your MCP tools to list all available Airbyte connectors."
2. "Use your MCP tools to get information about the Airbyte Stripe connector."
3. "Use your MCP tools to check your connection to your Airbyte Cloud workspace."
4. "Use your MCP tools to list all available destinations in my Airbyte Cloud workspace."

## Contributing to the Airbyte MCP Server

- [PyAirbyte Contributing Guide](https://github.com/airbytehq/PyAirbyte/blob/main/docs/CONTRIBUTING.md)

### Additional resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

For issues and questions:

- [PyAirbyte GitHub Issues](https://github.com/airbytehq/pyairbyte/issues)
- [PyAirbyte Discussions](https://github.com/airbytehq/pyairbyte/discussions)
