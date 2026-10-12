---
products: cloud
---

# Advanced configuration

:::info Private beta
The Airbyte MCP is in private beta. Features and tools may change.
:::

The hosted Airbyte MCP works without any extra configuration. These optional request headers let you narrow which tools your agent can see and use, or set a default workspace. They apply to the hosted server at `https://mcp.airbyte.com/mcp`.

Your MCP client still controls tool approval. Most clients can require your approval before tools that change data, using each tool's read-only, destructive, and open-world annotations.

## Add headers to your client

Add headers to your client's MCP configuration. Key names vary by client, so check your client's documentation.

```json
{
  "mcpServers": {
    "airbyte": {
      "url": "https://mcp.airbyte.com/mcp",
      "headers": {
        "X-MCP-Allow-External-Access": "0",
        "X-MCP-No-Destructive-Tools": "1"
      }
    }
  }
}
```

Headers can only hide tools. They can't give your agent permissions your Airbyte role doesn't have.

## Tool restrictions

| Header | Value | Effect |
| :--- | :--- | :--- |
| `X-MCP-Allow-Pipeline-Changes` | `0` | Hides tools that create, update, rename, or delete sources, destinations, and connections. Running and cancelling syncs stay available. |
| `X-MCP-Allow-External-Access` | `0` | Hides tools that read data directly from sources and destinations, like SQL and API passthrough queries. |
| `X-MCP-Readonly-Mode` | `1` | Shows only read-only tools. Also hides running and cancelling syncs. Direct reads stay available unless you also set `X-MCP-Allow-External-Access: 0`. |
| `X-MCP-No-Destructive-Tools` | `1` | Hides destructive tools, like deleting a source, destination, or connection. |
| `X-MCP-Exclude-Tools` | Comma-separated tool names | Hides the named tools. For tool names, see [Airbyte MCP tools](tools.md). |
| `X-MCP-Include-Modules` | Comma-separated modules | Shows only tools from these modules: `cloud`, `registry`, `guidance`. |
| `X-MCP-Exclude-Modules` | Comma-separated modules | Hides tools from these modules. |

`X-MCP-Allow-Pipeline-Changes` and `X-MCP-Allow-External-Access` accept `0`, `false`, or `no`. `X-MCP-Readonly-Mode` and `X-MCP-No-Destructive-Tools` accept `1` or `true`.

## Default workspace and organization

| Header | Value | Effect |
| :--- | :--- | :--- |
| `X-Airbyte-Workspace-Id` | Workspace ID | Workspace to use when your agent doesn't name one. |
| `X-Airbyte-Organization-Id` | Organization ID | Organization to use for organization-level tools when your agent doesn't name one. |

## Application name

| Header | Value | Effect |
| :--- | :--- | :--- |
| `X-Airbyte-Application-Name` | Your app's name, like `support-agent` | Identifies your agent or app in Airbyte's usage telemetry. |

## See also

- [Connect the Airbyte MCP to your agent](install.md)
- [Airbyte MCP tools](tools.md)
