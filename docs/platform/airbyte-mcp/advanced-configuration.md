---
products: cloud
---

# Advanced Airbyte MCP configuration

The hosted [Airbyte MCP](readme.md) works without any extra configuration. These optional request headers let you narrow which tools your agent can see and use, or set a default workspace. They apply to the hosted server at `https://mcp.airbyte.com/mcp`.

Your MCP client still controls tool approval. Most clients can require your approval before tools that change data, using each tool's read-only, destructive, and open-world annotations.

## Add headers to your client

Add headers to your client's MCP configuration. Configuration syntax can vary by client, so check your client's documentation for the required JSON syntax.

```json
{
  "mcpServers": {
    "airbyte": {
      "url": "https://mcp.airbyte.com/mcp",
      "headers": {
        "X-MCP-Allow-External-Access": "0",
        "X-MCP-Allow-Destructive-Tools": "0"
      }
    }
  }
}
```

Headers can only hide tools and customize tool behaviors. They can't give your agent permissions your Airbyte role doesn't have.

## Tool restrictions

| Header                          | Allowed values                | Effect                                                                                                                                                                       |
| :------------------------------ | :---------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `X-MCP-Allow-Pipeline-Changes`  | `1` (enabled), `0` (disabled) | Enabled by default. When set to `0`, hides tools that create, update, rename, or delete sources, destinations, and connections. Running and cancelling syncs stay available. |
| `X-MCP-Allow-External-Access`   | `1` (enabled), `0` (disabled) | Enabled by default. When set to `0`, hides tools that read data directly from sources and destinations, like SQL and API passthrough queries.                                |
| `X-MCP-Readonly-Mode`           | `1` (enabled), `0` (disabled) | Disabled by default. When set to `1`, shows only read-only tools. In addition to restricting pipeline edits, this setting also hides tools for running and cancelling syncs. |
| `X-MCP-Allow-Destructive-Tools` | `1` (enabled), `0` (disabled) | Enabled by default. When set to `0`, hides destructive tools, like deleting a source, destination, or connection.                                                            |
| `X-MCP-Exclude-Tools`           | Comma-separated tool names    | When set, hides the named tools. For tool names, see [Airbyte MCP tools](tools.md).                                                                                          |
| `X-MCP-Include-Modules`         | Comma-separated modules       | When set, shows only tools from these modules: `cloud`, `registry`, `guidance`, `interactive`. Can't be combined with `X-MCP-Exclude-Modules`.                               |
| `X-MCP-Exclude-Modules`         | Comma-separated modules       | When set, hides tools from these modules. Can't be combined with `X-MCP-Include-Modules`.                                                                                    |

`X-MCP-Allow-Pipeline-Changes`, `X-MCP-Allow-External-Access`, and `X-MCP-Allow-Destructive-Tools` also accept `true` or `yes` for `1`, and `false` or `no` for `0`. `X-MCP-Readonly-Mode` also accepts `true` for `1`.

## Delete guard

By default, the delete tools only delete a source, destination, or connection whose name contains `delete-me` or `deleteme` (case insensitive). Your agent can rename a resource to add the marker, but only after you explicitly agree to the rename.

| Header                       | Allowed values                  | Effect                                                                                         |
| :--------------------------- | :------------------------------ | :--------------------------------------------------------------------------------------------- |
| `X-MCP-Disable-Delete-Guard` | `1` (guard off), `0` (guard on) | The guard is on by default. Set to `1` to let the delete tools delete without the name marker. |

`1` can also be written as `true` or `yes`, and `0` as `false` or `no`. To block deletions entirely, which is the stronger option, set `X-MCP-Allow-Destructive-Tools` to `0` instead.

## Default workspace and organization

| Header                      | Value           | Effect                                                                             |
| :-------------------------- | :-------------- | :--------------------------------------------------------------------------------- |
| `X-Airbyte-Workspace-Id`    | Workspace ID    | Workspace to use when your agent doesn't name one.                                 |
| `X-Airbyte-Organization-Id` | Organization ID | Organization to use for organization-level tools when your agent doesn't name one. |

## Application name

| Header                       | Value                                 | Effect                                                     |
| :--------------------------- | :------------------------------------ | :--------------------------------------------------------- |
| `X-Airbyte-Application-Name` | Your app's name, like `support-agent` | Identifies your agent or app in Airbyte's usage telemetry. |

## See also

- [Connect the Airbyte MCP to your agent](install.md)
- [Airbyte MCP tools](tools.md)
