---
products: cloud
---

# Advanced Airbyte MCP configuration

The hosted [Airbyte MCP](readme.md) works without any extra configuration. These optional request headers let you narrow which tools your agent can see and use, or set a default workspace. They apply to the hosted server at `https://mcp.airbyte.com/mcp`. If your client can't send custom headers, like Claude, some settings are also available as [URL parameters](#url-parameters).

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

## Read-only mode

Read-only mode shows only read-only tools. In addition to restricting pipeline edits, it hides tools for running and cancelling syncs.

| Header                | URL parameter | Allowed values                | Effect                                                         |
| :-------------------- | :------------ | :---------------------------- | :------------------------------------------------------------- |
| `X-MCP-Readonly-Mode` | `read-only`   | `1` (enabled), `0` (disabled) | Disabled by default. When set to `1`, turns on read-only mode. |

The header also accepts `true` for `1`. If your client can't send headers, use the `read-only` URL parameter instead. For how URL parameters work, see [URL parameters](#url-parameters) below. The URL parameter accepts `true`, `false`, `1`, or `0`. The Airbyte MCP rejects common misspellings of the URL parameter, like `readonly` or `read_only`, with an error.

## URL parameters

Some clients, like Claude, can't send custom headers. Some settings also accept a URL parameter, which you add to the server URL instead of sending a header. For example:

```text
https://mcp.airbyte.com/mcp?read-only=true
```

- Each setting's section on this page names its URL parameter, if it has one. All other settings are only available as headers.
- Parameter names and values aren't case sensitive. To set more than one parameter, join them with `&`.
- If you set both a header and its URL parameter, the header takes precedence.
- The Airbyte MCP rejects the request with an error if a value isn't one the parameter accepts. An empty value, like `?read-only=`, is ignored.
- The Airbyte MCP ignores URL parameters it doesn't recognize.

## Tool restrictions

| Header                          | Allowed values                | Effect                                                                                                                                                                                                              |
| :------------------------------ | :---------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `X-MCP-Allow-Pipeline-Changes`  | `1` (enabled), `0` (disabled) | Enabled by default. When set to `0`, hides tools that create, update, rename, or delete sources, destinations, and connections. Running and cancelling syncs stay available.                                        |
| `X-MCP-Allow-External-Access`   | `1` (enabled), `0` (disabled) | Enabled by default. When set to `0`, hides tools that read data directly from sources and destinations, like SQL and API passthrough queries.                                                                       |
| `X-MCP-Readonly-Mode`           | `1` (enabled), `0` (disabled) | Disabled by default. When set to `1`, shows only read-only tools. In addition to restricting pipeline edits, this setting also hides tools for running and cancelling syncs. See [Read-only mode](#read-only-mode). |
| `X-MCP-Allow-Destructive-Tools` | `1` (enabled), `0` (disabled) | Enabled by default. When set to `0`, hides destructive tools, like deleting a source, destination, or connection.                                                                                                   |
| `X-MCP-Exclude-Tools`           | Comma-separated tool names    | When set, hides the named tools. For tool names, see [Airbyte MCP tools](tools.md).                                                                                                                                 |
| `X-MCP-Include-Modules`         | Comma-separated modules       | When set, shows only tools from these modules: `cloud`, `registry`, `guidance`, `interactive`. Can't be combined with `X-MCP-Exclude-Modules`.                                                                      |
| `X-MCP-Exclude-Modules`         | Comma-separated modules       | When set, hides tools from these modules. Can't be combined with `X-MCP-Include-Modules`.                                                                                                                           |

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

## Insiders mode

Insiders mode shows insiders tools, which are new tools that are still in development, like the Connector Builder project tools. Insiders tools are hidden by default.

:::warning
Some insiders tools can be unsafe or have side effects. Only use insiders mode on clients which support tool approval.
:::

| Header           | URL parameter | Allowed values                | Effect                                                        |
| :--------------- | :------------ | :---------------------------- | :------------------------------------------------------------ |
| `X-MCP-Insiders` | `insiders`    | `1` (enabled), `0` (disabled) | Disabled by default. When set to `1`, turns on insiders mode. |

`1` can also be written as `true` or `yes`, and `0` as `false` or `no`, for both the header and the URL parameter. For how URL parameters work, see [URL parameters](#url-parameters). Insiders tools follow the same tool restrictions as other tools. For example, read-only mode still hides insiders tools that change data.

## See also

- [Connect the Airbyte MCP to your agent](install.md)
- [Airbyte MCP tools](tools.md)
