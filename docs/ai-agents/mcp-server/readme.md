---
sidebar_position: 6
---

# Airbyte MCP server

The Airbyte MCP server connects your AI agent to your business data through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/). It gives agents authenticated access to the SaaS platforms you use every day, such as your CRM, support desk, analytics tools, and more, so they can read and query data on your behalf.

Airbyte hosts and manages a remote MCP server with OAuth authentication, so there's nothing to install.

## Requirements

Before you begin, make sure you have the following:

- **An Agent Engine account.** Sign up at [app.airbyte.ai](https://app.airbyte.ai) if you don't have one.
- **An AI agent that supports MCP.** For example, Claude Desktop, Claude Code, Cursor, Codex, or any client that supports the Model Context Protocol.
- **Credentials for the connectors you want to use.** Each data source requires its own authentication. For example, you need a Gong API key to connect Gong, or Salesforce OAuth credentials to connect Salesforce.

## Add the MCP server to your agent

Add the Airbyte MCP server to your client by placing this in your client's MCP configuration:

```json
{
  "mcpServers": {
    "Airbyte": {
      "url": "https://mcp.airbyte.ai/mcp"
    }
  }
}
```

Most clients support this configuration format. When you first connect, a browser window opens and prompts you to:

1. Log in with your Airbyte account.
2. Accept the OAuth authorization.

After you authenticate, the MCP server's tools are available to your agent.

### Claude Code

Run the following command in your terminal:

```bash
claude mcp add --transport http airbyte https://mcp.airbyte.ai/mcp
```

Then launch Claude Code with `claude`. You'll be prompted to authenticate with OAuth to Airbyte.

### Cursor

Go to **Cursor** > **Settings** > **Cursor Settings** > **MCP** and add the Airbyte MCP server. Cursor 1.0 and later include native OAuth and Streamable HTTP support.

You can also add the server manually by editing your `mcp.json` file:

```json
{
  "mcpServers": {
    "Airbyte": {
      "url": "https://mcp.airbyte.ai/mcp"
    }
  }
}
```

### Claude Desktop

Open developer settings with **CMD + ,** > **Developer** > **Edit Config**, then add the server to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "Airbyte": {
      "url": "https://mcp.airbyte.ai/mcp"
    }
  }
}
```

Restart Claude Desktop after making changes.

### Codex

Run the following command in your terminal:

```bash
codex mcp add airbyte --url https://mcp.airbyte.ai/mcp
```

Then launch Codex with `codex`. You'll be prompted to authenticate with Airbyte using OAuth.

### VS Code and GitHub Copilot

Open the Command Palette with **CMD+Shift+P** and select **MCP: Add Server**. Enter the Airbyte MCP server URL:

```text
https://mcp.airbyte.ai/mcp
```

### Other clients

The Airbyte MCP server works with any client that supports OAuth authentication and Streamable HTTP transport. Use the server URL `https://mcp.airbyte.ai/mcp` in your client's MCP configuration.

## Example usage

After you connect the MCP server, your agent can discover and call its tools automatically based on your prompts. The following examples show common workflows.

### Add a connector

To connect a new data source, prompt your agent with what you want to connect. The agent handles the setup, including starting a browser-based credential flow where you enter your credentials securely.

```text
Connect my Gong account
```

The agent:

1. Lists the available connector types.
2. Starts a credential flow and gives you a URL to visit.
3. You visit the URL and enter your credentials in the browser.
4. The agent confirms the connector was created and is ready to query.

:::note
Credentials are always entered in the browser, never in the chat. The agent gives you a link to visit.
:::

### Remove a connector

To remove a connector you no longer need:

```text
Delete my Gong connector
```

### Query data

After you connect a data source, prompt your agent with natural language questions. The agent discovers the available entities, understands their schemas, and executes the right queries.

```text
Show me the 10 most recent Gong calls
```

```text
Find all open deals in Salesforce worth more than $50,000
```

```text
List HubSpot contacts who were created this week
```

```text
How many Zendesk tickets are in "open" status?
```

The agent uses field selection to return only the data you need, which reduces token usage and improves response quality.

## Troubleshooting

### Authentication fails

- Make sure your Airbyte account is active at [app.airbyte.ai](https://app.airbyte.ai).
- Try logging out of your agent's MCP integration and reconnecting to trigger a fresh OAuth flow.
- If you joined a new Airbyte organization, reauthenticate to refresh your access.

### Agent can't find the MCP server

- Restart your agent after adding the MCP server configuration.
- Verify the server URL is exactly `https://mcp.airbyte.ai/mcp` in your configuration.
- Check that your client supports Streamable HTTP or OAuth-based MCP servers.

### Connector credential flow doesn't complete

- Make sure you visited the credential URL the agent provided and completed the form in the browser.
- If the flow timed out, ask the agent to start a new credential flow.

### Queries return unexpected results

- Ask the agent to describe the available entities before querying, so it picks the right one.
- For time-based queries, the agent resolves relative dates like "this week" or "last month" automatically.
