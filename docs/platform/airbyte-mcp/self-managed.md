---
products: oss-community
---

# Use the Airbyte MCP with Airbyte Core

:::info Private beta
The Airbyte MCP is in private beta. Features and tools may change.
:::

:::caution Known issues
The Airbyte MCP works with self-managed Airbyte Core, but there are known issues with local deployments. Airbyte has tested it with Airbyte Core 2.3.0 deployed with abctl. Before you start, review the [known issues](#known-issues-in-core-deployments).
:::

The hosted Airbyte MCP server at `https://mcp.airbyte.com/mcp` only works with Airbyte Cloud. To use the Airbyte MCP with a self-managed Airbyte Core deployment, run the Airbyte MCP server locally on your computer and point it at your deployment's API. Your MCP client starts the server for you.

Pipeline management and troubleshooting tools work with self-managed Airbyte. The [Context layer](../context-layer/readme.md), including direct reads and connector skills, is only available in Airbyte Cloud.

## Prerequisites

- A running Airbyte Core deployment. To deploy one, see the [Quickstart](/platform/using-airbyte/getting-started/oss-quickstart).
- [uv](https://docs.astral.sh/uv/getting-started/installation/), which runs the Airbyte MCP server.
- An MCP client that supports local MCP servers over standard input and output (stdio), like Claude Desktop, Claude Code, Cursor, or VS Code.

## Step 1: Finish setting up Airbyte

Open Airbyte in your browser. If this is a new deployment, complete the setup page and enter your email address. The Airbyte MCP can't find your default workspace until your user has an email address.

## Step 2: Get your workspace ID and credentials

1. Get your workspace ID. In Airbyte, open any page in your workspace. The workspace ID is the value after `/workspaces/` in the URL.

2. Get a client ID and client secret.

   - If you deployed Airbyte with abctl, run this command. Copy the `Client-Id` and `Client-Secret` values.

     ```bash
     abctl local credentials
     ```

   - Otherwise, [create an application](/platform/using-airbyte/configuring-api-access) and copy its client ID and client secret.

## Step 3: Add the Airbyte MCP to your client

Add this server to your MCP client's configuration file. Replace the placeholder values with your own.

```json
{
  "mcpServers": {
    "airbyte": {
      "command": "uvx",
      "args": ["--from=airbyte@latest", "airbyte-mcp"],
      "env": {
        "AIRBYTE_CLOUD_API_URL": "http://localhost:8000/api/public/v1",
        "AIRBYTE_CLOUD_CLIENT_ID": "<CLIENT_ID>",
        "AIRBYTE_CLOUD_CLIENT_SECRET": "<CLIENT_SECRET>",
        "AIRBYTE_CLOUD_WORKSPACE_ID": "<WORKSPACE_ID>"
      }
    }
  }
}
```

| Variable | Description |
| :--- | :--- |
| `AIRBYTE_CLOUD_API_URL` | Your deployment's API URL. This is your Airbyte URL followed by `/api/public/v1`. The abctl default is `http://localhost:8000/api/public/v1`. |
| `AIRBYTE_CLOUD_CLIENT_ID` | The client ID from step 2. |
| `AIRBYTE_CLOUD_CLIENT_SECRET` | The client secret from step 2. |
| `AIRBYTE_CLOUD_WORKSPACE_ID` | The workspace ID from step 2. The Airbyte MCP uses this workspace when your agent doesn't specify one. |

The filename and format depend on your client. For example, VS Code uses `.vscode/mcp.json` with a top-level `servers` key instead of `mcpServers`. Check your client's documentation for details.

Restart your client. To test the connection, ask your agent to list the sources in your Airbyte workspace.

Keep your client secret out of the chat and out of version control. Your agent can use the Airbyte MCP without seeing the secret.

## Known issues in Core deployments

- **Links don't open.** Links to Airbyte that the Airbyte MCP returns include `/api/public/v1` in the path, so they return an error in your browser. Remove `/api/public/v1` from the link to open the page. For details, see [PyAirbyte issue #563](https://github.com/airbytehq/PyAirbyte/issues/563).
- **Workspace isn't found by default.** If you don't set `AIRBYTE_CLOUD_WORKSPACE_ID`, tools that need a workspace can fail. Error messages may suggest tools that don't exist, like `list_workspaces`. Set `AIRBYTE_CLOUD_WORKSPACE_ID`, or ask your agent to use `list_cloud_workspaces` and `set_default_cloud_workspace`.
- **Last job status is empty.** When your agent lists connections, the status of the last job may be empty even after a successful sync. Your agent can still check individual jobs and read their logs.
- **Billing and usage tools don't work.** These features only exist in Airbyte Cloud.
- **No Context layer.** Direct reads and connector skills aren't available.
- **No browser sign-in.** The local server signs in with your application's client ID and client secret, not with OAuth or single sign-on.
- **Self-Managed Enterprise isn't tested.** Airbyte has only tested the Airbyte MCP with Airbyte Core.

If you find other problems, [open an Airbyte MCP beta issue](https://github.com/airbytehq/PyAirbyte/issues/new?template=airbyte-mcp-beta.yml). Don't include secrets or credentials in these issues, as they're publicly viewable.
