---
sidebar_label: Replication MCP advanced setup
---

# Replication MCP advanced setup

:::note
This MCP server implementation is experimental and may change without notice between minor versions of PyAirbyte.
:::

Most users only need to give `https://mcp.airbyte.com/mcp` to their agent or MCP client. See [Connect to the hosted server](replication-mcp.md#connect-to-the-hosted-server).

## Add the hosted server from the command line

**Claude Code:**

```bash
claude mcp add --transport http airbyte https://mcp.airbyte.com/mcp
```

Then run `claude`, type `/mcp`, select **airbyte**, and select **Authenticate** to sign in to Airbyte Cloud.

**VS Code:**

```bash
code --add-mcp '{"name":"airbyte","type":"http","url":"https://mcp.airbyte.com/mcp"}'
```

## Run the server locally

Run the server on your own machine if you want to run connectors locally or manage Airbyte Cloud with API credentials from a dotenv file.

1. Install `uv`: `brew install uv`
2. Create a dotenv secrets file with your Airbyte Cloud credentials and connector configurations
3. Register the MCP server with your MCP client using `uvx --python=3.11 --from=airbyte@latest airbyte-mcp`
4. Test the connection using your MCP client

For complete setup instructions, environment configuration, the security model, and troubleshooting, see the [Airbyte Replication MCP Server documentation](https://airbytehq.github.io/PyAirbyte/airbyte/mcp.html).

Example prompt: "Use your MCP tools to list all variables you have access to in the dotenv secrets file."
