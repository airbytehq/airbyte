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

You can use the Replication MCP server in two ways:

- **Hosted by Airbyte Cloud** at `https://mcp.airbyte.com/mcp`. There's nothing to install. You sign in with your Airbyte Cloud account, and the server works with the workspaces you can access.
- **Run locally** with `uvx`. Use this to run connectors on your own machine or to manage Airbyte Cloud with API credentials from a dotenv file.

## Connect to the hosted server

Airbyte hosts the Replication MCP server for Airbyte Cloud users at the following streamable-HTTP endpoint:

```text
https://mcp.airbyte.com/mcp
```

This URL is an MCP endpoint, not a web page. Add it to an MCP client rather than opening it in a browser.

The first time your client connects, it opens your browser so you can sign in to [Airbyte Cloud](https://cloud.airbyte.com) and grant access. If your organization uses SSO, choose the SSO option on the sign-in page and enter your company identifier.

Choose one method to connect.

<Tabs>
<TabItem value="url" label="Paste a URL" default>

Use this method with Claude, Claude Desktop, ChatGPT, or any client that has a URL field for remote MCP servers.

1. Open your client's MCP or connector settings. In Claude and Claude Desktop, go to **Settings** > **Connectors** > **Add custom connector**.

2. Paste the server URL: `https://mcp.airbyte.com/mcp`

3. Save, then connect. Your browser opens so you can sign in to Airbyte Cloud and grant access.

</TabItem>
<TabItem value="json" label="JSON config file">

Use this method with VS Code, Cursor, or Windsurf. Add an entry to your client's MCP config file. Key names vary by client, so check your client's documentation if the examples below don't match.

**VS Code** (`.vscode/mcp.json`):

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

**Cursor** (`.cursor/mcp.json`) or **Windsurf** (`~/.codeium/windsurf/mcp_config.json`):

```json
{
  "mcpServers": {
    "airbyte": {
      "url": "https://mcp.airbyte.com/mcp"
    }
  }
}
```

Save the file. Your client detects that the server requires OAuth and prompts you to sign in to Airbyte Cloud.

</TabItem>
<TabItem value="cli" label="CLI command">

Use this method with Claude Code or VS Code. Run a one-line command in your terminal, and it writes the config for you.

**Claude Code:**

```bash
claude mcp add --transport http airbyte https://mcp.airbyte.com/mcp
```

Then run `claude`, type `/mcp`, select **airbyte**, and select **Authenticate** to sign in to Airbyte Cloud.

**VS Code:**

```bash
code --add-mcp '{"name":"airbyte","type":"http","url":"https://mcp.airbyte.com/mcp"}'
```

</TabItem>
<TabItem value="one-click" label="One-click install">

Use this method with Cursor or VS Code. Click a link that opens the client and pre-fills the config.

- [Install in Cursor](cursor://anysphere.cursor-deeplink/mcp/install?name=airbyte&config=eyJ1cmwiOiJodHRwczovL21jcC5haXJieXRlLmNvbS9tY3AifQ%3D%3D)
- [Install in VS Code](https://vscode.dev/redirect?url=vscode%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522airbyte%2522%252C%2522type%2522%253A%2522http%2522%252C%2522url%2522%253A%2522https%253A%252F%252Fmcp.airbyte.com%252Fmcp%2522%257D)
- [Install in VS Code (Insiders edition)](https://insiders.vscode.dev/redirect?url=vscode-insiders%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522airbyte%2522%252C%2522type%2522%253A%2522http%2522%252C%2522url%2522%253A%2522https%253A%252F%252Fmcp.airbyte.com%252Fmcp%2522%257D)

After the client opens, confirm the install and sign in to Airbyte Cloud when prompted.

</TabItem>
</Tabs>

## Run the server locally

To run the Airbyte Replication MCP server on your own machine:

1. Install `uv`: `brew install uv`
2. Create a dotenv secrets file with your Airbyte Cloud credentials and connector configurations
3. Register the MCP server with your MCP client using `uvx --python=3.11 --from=airbyte@latest airbyte-mcp`
4. Test the connection using your MCP client

For complete setup instructions, environment configuration, the security model, and troubleshooting, see the [Airbyte Replication MCP Server documentation](https://airbytehq.github.io/PyAirbyte/airbyte/mcp.html).

## Helpful Prompts

Here are some things you can do with the Airbyte Replication MCP server, across local and Airbyte Cloud use cases:

1. "Use your MCP tools to list all available Airbyte connectors."
2. "Use your MCP tools to get information about the Airbyte Stripe connector."
3. "Use your MCP tools to list all variables you have access to in the dotenv secrets file."
4. "Use your MCP tools to check your connection to your Airbyte Cloud workspace."
5. "Use your MCP tools to list all available destinations in my Airbyte Cloud workspace."

## Contributing to the Airbyte MCP Server

- [PyAirbyte Contributing Guide](https://github.com/airbytehq/PyAirbyte/blob/main/docs/CONTRIBUTING.md)

### Additional resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

For issues and questions:

- [PyAirbyte GitHub Issues](https://github.com/airbytehq/pyairbyte/issues)
- [PyAirbyte Discussions](https://github.com/airbytehq/pyairbyte/discussions)
