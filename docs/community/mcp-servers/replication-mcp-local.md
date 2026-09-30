---
sidebar_label: Run Replication MCP locally
---

# Run the Replication MCP server locally

:::note
This MCP server implementation is experimental and may change without notice between minor versions of PyAirbyte.
:::

Most users should connect to the [hosted Replication MCP server](replication-mcp.md) instead. Run the server locally if you want to run connectors on your own machine or manage Airbyte Cloud with API credentials from a dotenv file.

1. Install `uv`: `brew install uv`
2. Create a dotenv secrets file with your Airbyte Cloud credentials and connector configurations
3. Register the MCP server with your MCP client using `uvx --python=3.11 --from=airbyte@latest airbyte-mcp`
4. Test the connection using your MCP client

For complete setup instructions, environment configuration, the security model, and troubleshooting, see the [Airbyte Replication MCP Server documentation](https://airbytehq.github.io/PyAirbyte/airbyte/mcp.html).

## Helpful prompts

1. "Use your MCP tools to list all variables you have access to in the dotenv secrets file."
2. "Use your MCP tools to get information about the Airbyte Stripe connector."
