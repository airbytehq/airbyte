---
id: airbyte-mcp-cloud
title: "airbyte.mcp.cloud Module"
sidebar_label: "airbyte.mcp.cloud"
---

# `airbyte.mcp.cloud` Module

Airbyte Cloud MCP operations.

# cloud module

MCP primitives registered by the `cloud` module of the `airbyte-mcp` server: **39** tool(s), **0** prompt(s), **0** resource(s).

## Tools (39)

<a id="cancel_cloud_sync"></a>

### cancel_cloud_sync

**Hints:** `destructive` · `open-world`

Cancel a running sync job on an Airbyte Cloud connection.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `connection_id` | `string` | yes | — | The ID of the Airbyte Cloud connection. |
| `job_id` | `integer \| null` | no | `null` | Optional job ID to cancel. If not provided, the connection's most recent sync job will be cancelled. Other job types require an explicit job ID. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "connection_id": {
      "description": "The ID of the Airbyte Cloud connection.",
      "type": "string"
    },
    "job_id": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional job ID to cancel. If not provided, the connection's most recent sync job will be cancelled. Other job types require an explicit job ID."
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "required": [
    "connection_id"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "description": "Information about a sync job.",
  "properties": {
    "job_id": {
      "type": "integer"
    },
    "status": {
      "type": "string"
    },
    "bytes_synced": {
      "type": "integer"
    },
    "records_synced": {
      "type": "integer"
    },
    "start_time": {
      "type": "string"
    },
    "job_url": {
      "type": "string"
    }
  },
  "required": [
    "job_id",
    "status",
    "bytes_synced",
    "records_synced",
    "start_time",
    "job_url"
  ],
  "type": "object"
}
```

</details>

<a id="check_airbyte_cloud_workspace"></a>

### check_airbyte_cloud_workspace

**Hints:** `read-only` · `idempotent` · `open-world`

Check if we have a valid Airbyte Cloud connection and return workspace info.

    Returns workspace details including workspace ID, name, organization info, and billing status.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "description": "Information about a workspace in Airbyte Cloud.",
  "properties": {
    "workspace_id": {
      "type": "string"
    },
    "workspace_name": {
      "type": "string"
    },
    "workspace_url": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "organization_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ]
    },
    "organization_name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "payment_status": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "subscription_status": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "is_account_locked": {
      "default": false,
      "type": "boolean"
    }
  },
  "required": [
    "workspace_id",
    "workspace_name",
    "organization_id"
  ],
  "type": "object"
}
```

</details>

<a id="check_cloud_destination"></a>

### check_cloud_destination

**Hints:** `read-only` · `idempotent` · `open-world`

Check the configuration and credentials of a deployed destination connector.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `destination_id` | `string` | yes | — | The ID of the deployed destination connector to check. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "destination_id": {
      "description": "The ID of the deployed destination connector to check.",
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "required": [
    "destination_id"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "description": "Result of a connection check against a deployed Cloud connector.",
  "properties": {
    "connector_id": {
      "type": "string"
    },
    "connector_type": {
      "enum": [
        "source",
        "destination"
      ],
      "type": "string"
    },
    "succeeded": {
      "type": "boolean"
    },
    "message": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ]
    }
  },
  "required": [
    "connector_id",
    "connector_type",
    "succeeded",
    "message"
  ],
  "type": "object"
}
```

</details>

<a id="check_cloud_source"></a>

### check_cloud_source

**Hints:** `read-only` · `idempotent` · `open-world`

Check the configuration and credentials of a deployed source connector.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `source_id` | `string` | yes | — | The ID of the deployed source connector to check. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "source_id": {
      "description": "The ID of the deployed source connector to check.",
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "required": [
    "source_id"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "description": "Result of a connection check against a deployed Cloud connector.",
  "properties": {
    "connector_id": {
      "type": "string"
    },
    "connector_type": {
      "enum": [
        "source",
        "destination"
      ],
      "type": "string"
    },
    "succeeded": {
      "type": "boolean"
    },
    "message": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ]
    }
  },
  "required": [
    "connector_id",
    "connector_type",
    "succeeded",
    "message"
  ],
  "type": "object"
}
```

</details>

<a id="create_connection_on_cloud"></a>

### create_connection_on_cloud

**Hints:** `open-world`

Create a connection between a deployed source and destination on Airbyte Cloud.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `connection_name` | `string` | yes | — | The name of the connection. |
| `source_id` | `string` | yes | — | The ID of the deployed source. |
| `destination_id` | `string` | yes | — | The ID of the deployed destination. |
| `selected_streams` | `string \| array<string>` | yes | — | The selected stream names to sync within the connection. Must be an explicit stream name or list of streams. Cannot be empty or '*'. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |
| `table_prefix` | `string \| null` | no | `null` | Optional table prefix to use when syncing to the destination. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "connection_name": {
      "description": "The name of the connection.",
      "type": "string"
    },
    "source_id": {
      "description": "The ID of the deployed source.",
      "type": "string"
    },
    "destination_id": {
      "description": "The ID of the deployed destination.",
      "type": "string"
    },
    "selected_streams": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "items": {
            "type": "string"
          },
          "type": "array"
        }
      ],
      "description": "The selected stream names to sync within the connection. Must be an explicit stream name or list of streams. Cannot be empty or '*'."
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    },
    "table_prefix": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional table prefix to use when syncing to the destination."
    }
  },
  "required": [
    "connection_name",
    "source_id",
    "destination_id",
    "selected_streams"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="deploy_destination_to_cloud"></a>

### deploy_destination_to_cloud

**Hints:** `open-world`

Deploy a destination connector to Airbyte Cloud.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `destination_name` | `string` | yes | — | The name to use when deploying the destination. |
| `destination_connector_name` | `string` | yes | — | The name of the destination connector (e.g., 'destination-postgres'). |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |
| `config` | `object \| string \| null` | no | `null` | The configuration for the destination connector. |
| `config_secret_name` | `string \| null` | no | `null` | The name of the secret containing the configuration. |
| `unique` | `boolean` | no | `true` | Whether to require a unique name. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "destination_name": {
      "description": "The name to use when deploying the destination.",
      "type": "string"
    },
    "destination_connector_name": {
      "description": "The name of the destination connector (e.g., 'destination-postgres').",
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    },
    "config": {
      "anyOf": [
        {
          "additionalProperties": true,
          "type": "object"
        },
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "The configuration for the destination connector."
    },
    "config_secret_name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "The name of the secret containing the configuration."
    },
    "unique": {
      "default": true,
      "description": "Whether to require a unique name.",
      "type": "boolean"
    }
  },
  "required": [
    "destination_name",
    "destination_connector_name"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="deploy_noop_destination_to_cloud"></a>

### deploy_noop_destination_to_cloud

**Hints:** `open-world`

Deploy the No-op destination to Airbyte Cloud for testing purposes.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `name` | `string` | no | `"No-op Destination"` |  |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |
| `unique` | `boolean` | no | `true` |  |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "name": {
      "default": "No-op Destination",
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    },
    "unique": {
      "default": true,
      "type": "boolean"
    }
  },
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="deploy_source_to_cloud"></a>

### deploy_source_to_cloud

**Hints:** `open-world`

Deploy a source connector to Airbyte Cloud.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `source_name` | `string` | yes | — | The name to use when deploying the source. |
| `source_connector_name` | `string` | yes | — | The name of the source connector (e.g., 'source-faker'). |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |
| `config` | `object \| string \| null` | no | `null` | The configuration for the source connector. |
| `config_secret_name` | `string \| null` | no | `null` | The name of the secret containing the configuration. |
| `unique` | `boolean` | no | `true` | Whether to require a unique name. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "source_name": {
      "description": "The name to use when deploying the source.",
      "type": "string"
    },
    "source_connector_name": {
      "description": "The name of the source connector (e.g., 'source-faker').",
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    },
    "config": {
      "anyOf": [
        {
          "additionalProperties": true,
          "type": "object"
        },
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "The configuration for the source connector."
    },
    "config_secret_name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "The name of the secret containing the configuration."
    },
    "unique": {
      "default": true,
      "description": "Whether to require a unique name.",
      "type": "boolean"
    }
  },
  "required": [
    "source_name",
    "source_connector_name"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="describe_cloud_connection"></a>

### describe_cloud_connection

**Hints:** `read-only` · `idempotent` · `open-world`

Get detailed information about a specific deployed connection.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `connection_id` | `string` | yes | — | The ID of the connection to describe. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "connection_id": {
      "description": "The ID of the connection to describe.",
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "required": [
    "connection_id"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "description": "Detailed information about a deployed connection in Airbyte Cloud.",
  "properties": {
    "connection_id": {
      "type": "string"
    },
    "connection_name": {
      "type": "string"
    },
    "connection_url": {
      "type": "string"
    },
    "source_id": {
      "type": "string"
    },
    "source_name": {
      "type": "string"
    },
    "destination_id": {
      "type": "string"
    },
    "destination_name": {
      "type": "string"
    },
    "selected_streams": {
      "items": {
        "type": "string"
      },
      "type": "array"
    },
    "table_prefix": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ]
    }
  },
  "required": [
    "connection_id",
    "connection_name",
    "connection_url",
    "source_id",
    "source_name",
    "destination_id",
    "destination_name",
    "selected_streams",
    "table_prefix"
  ],
  "type": "object"
}
```

</details>

<a id="describe_cloud_destination"></a>

### describe_cloud_destination

**Hints:** `read-only` · `idempotent` · `open-world`

Get detailed information about a specific deployed destination connector.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `destination_id` | `string` | yes | — | The ID of the destination to describe. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "destination_id": {
      "description": "The ID of the destination to describe.",
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "required": [
    "destination_id"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "description": "Detailed information about a deployed destination connector in Airbyte Cloud.",
  "properties": {
    "destination_id": {
      "type": "string"
    },
    "destination_name": {
      "type": "string"
    },
    "destination_url": {
      "type": "string"
    },
    "connector_definition_id": {
      "type": "string"
    }
  },
  "required": [
    "destination_id",
    "destination_name",
    "destination_url",
    "connector_definition_id"
  ],
  "type": "object"
}
```

</details>

<a id="describe_cloud_organization"></a>

### describe_cloud_organization

**Hints:** `read-only` · `idempotent` · `open-world`

Get details about a specific organization including billing status.

    Requires either organization_id OR organization_name (exact match) to be provided.
    This tool is useful for looking up an organization's ID from its name, or vice versa.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `organization_id` | `string \| null` | no | `null` | Organization ID. Required if organization_name is not provided. |
| `organization_name` | `string \| null` | no | `null` | Organization name (exact match). Required if organization_id is not provided. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "organization_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Organization ID. Required if organization_name is not provided."
    },
    "organization_name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Organization name (exact match). Required if organization_id is not provided."
    }
  },
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "description": "Information about an organization in Airbyte Cloud.",
  "properties": {
    "id": {
      "type": "string"
    },
    "name": {
      "type": "string"
    },
    "email": {
      "type": "string"
    },
    "payment_status": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "subscription_status": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "is_account_locked": {
      "default": false,
      "type": "boolean"
    }
  },
  "required": [
    "id",
    "name",
    "email"
  ],
  "type": "object"
}
```

</details>

<a id="describe_cloud_source"></a>

### describe_cloud_source

**Hints:** `read-only` · `idempotent` · `open-world`

Get detailed information about a specific deployed source connector.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `source_id` | `string` | yes | — | The ID of the source to describe. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "source_id": {
      "description": "The ID of the source to describe.",
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "required": [
    "source_id"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "description": "Detailed information about a deployed source connector in Airbyte Cloud.",
  "properties": {
    "source_id": {
      "type": "string"
    },
    "source_name": {
      "type": "string"
    },
    "source_url": {
      "type": "string"
    },
    "connector_definition_id": {
      "type": "string"
    }
  },
  "required": [
    "source_id",
    "source_name",
    "source_url",
    "connector_definition_id"
  ],
  "type": "object"
}
```

</details>

<a id="get_cloud_sync_logs"></a>

### get_cloud_sync_logs

**Hints:** `read-only` · `idempotent` · `open-world`

Get the logs from a sync job attempt on Airbyte Cloud.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `connection_id` | `string` | yes | — | The ID of the Airbyte Cloud connection. |
| `job_id` | `integer \| null \| null` | no | `null` |  |
| `attempt_number` | `integer \| null \| null` | no | `null` |  |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |
| `max_lines` | `integer` | no | `4000` | Maximum number of lines to return. Defaults to 4000 if not specified. If '0' is provided, no limit is applied. |
| `from_tail` | `boolean \| null` | no | `null` | Pull from the end of the log text if total lines is greater than 'max_lines'. Defaults to True if `line_offset` is not specified. Cannot combine `from_tail=True` with `line_offset`. |
| `line_offset` | `integer \| null` | no | `null` | Number of lines to skip from the beginning of the logs. Cannot be combined with `from_tail=True`. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "connection_id": {
      "description": "The ID of the Airbyte Cloud connection.",
      "type": "string"
    },
    "job_id": {
      "anyOf": [
        {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "description": "Optional job ID. If not provided, the latest job will be used."
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "attempt_number": {
      "anyOf": [
        {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "description": "Optional attempt number. If not provided, the latest attempt will be used."
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    },
    "max_lines": {
      "default": 4000,
      "description": "Maximum number of lines to return. Defaults to 4000 if not specified. If '0' is provided, no limit is applied.",
      "type": "integer"
    },
    "from_tail": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Pull from the end of the log text if total lines is greater than 'max_lines'. Defaults to True if `line_offset` is not specified. Cannot combine `from_tail=True` with `line_offset`."
    },
    "line_offset": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Number of lines to skip from the beginning of the logs. Cannot be combined with `from_tail=True`."
    }
  },
  "required": [
    "connection_id"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "description": "Result of reading sync logs with pagination support.",
  "properties": {
    "job_id": {
      "type": "integer"
    },
    "attempt_number": {
      "type": "integer"
    },
    "log_text": {
      "type": "string"
    },
    "log_text_start_line": {
      "type": "integer"
    },
    "log_text_line_count": {
      "type": "integer"
    },
    "total_log_lines_available": {
      "type": "integer"
    }
  },
  "required": [
    "job_id",
    "attempt_number",
    "log_text",
    "log_text_start_line",
    "log_text_line_count",
    "total_log_lines_available"
  ],
  "type": "object"
}
```

</details>

<a id="get_cloud_sync_status"></a>

### get_cloud_sync_status

**Hints:** `read-only` · `idempotent` · `open-world`

Get the status of a sync job from the Airbyte Cloud.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `connection_id` | `string` | yes | — | The ID of the Airbyte Cloud connection. |
| `job_id` | `integer \| null` | no | `null` | Optional job ID. If not provided, the latest job will be used. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |
| `include_attempts` | `boolean` | no | `false` | Whether to include detailed attempts information. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "connection_id": {
      "description": "The ID of the Airbyte Cloud connection.",
      "type": "string"
    },
    "job_id": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional job ID. If not provided, the latest job will be used."
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    },
    "include_attempts": {
      "default": false,
      "description": "Whether to include detailed attempts information.",
      "type": "boolean"
    }
  },
  "required": [
    "connection_id"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "additionalProperties": true,
  "type": "object"
}
```

</details>

<a id="get_connection_artifact"></a>

### get_connection_artifact

**Hints:** `read-only` · `idempotent` · `open-world`

Get a connection artifact (state or catalog) from Airbyte Cloud.

    By default, returns artifacts in Airbyte protocol format (snake_case,
    suitable for passing to connector CLI flags like `--state` or `--catalog`).

    Retrieves the specified artifact for a connection:
    - `state`: Returns a list of protocol-format `AirbyteStateMessage` dicts,
      or `{"ERROR": "..."}` if no state is set.
    - `catalog`: Returns the protocol-format `ConfiguredAirbyteCatalog` dict,
      or `{"ERROR": "..."}` if not found.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `connection_id` | `string` | yes | — | The ID of the Airbyte Cloud connection. |
| `artifact_type` | `enum("state", "catalog")` | yes | — | The type of artifact to retrieve: 'state' or 'catalog'. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "connection_id": {
      "description": "The ID of the Airbyte Cloud connection.",
      "type": "string"
    },
    "artifact_type": {
      "description": "The type of artifact to retrieve: 'state' or 'catalog'.",
      "enum": [
        "state",
        "catalog"
      ],
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "required": [
    "connection_id",
    "artifact_type"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "anyOf": [
        {
          "additionalProperties": true,
          "type": "object"
        },
        {
          "items": {
            "additionalProperties": true,
            "type": "object"
          },
          "type": "array"
        }
      ]
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="get_connector_builder_draft_manifest"></a>

### get_connector_builder_draft_manifest

**Hints:** `read-only` · `idempotent` · `open-world`

Get the Connector Builder draft manifest for a custom source definition.

Returns the working draft manifest that has been saved in the Connector Builder UI
but not yet published. This is useful for inspecting what a user is currently working
on before they publish their changes.

If no draft exists, 'has_draft' will be False and 'draft_manifest' will be None.
The published manifest is always included for comparison.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `definition_id` | `string` | yes | — | The ID of the custom source definition to retrieve the draft for. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "definition_id": {
      "description": "The ID of the custom source definition to retrieve the draft for.",
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "required": [
    "definition_id"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "additionalProperties": true,
  "type": "object"
}
```

</details>

<a id="get_custom_source_definition"></a>

### get_custom_source_definition

**Hints:** `read-only` · `idempotent` · `open-world`

Get a custom YAML source definition from Airbyte Cloud, including its manifest.

Returns the full definition details including the published manifest YAML content.
Optionally includes the Connector Builder draft manifest (unpublished changes)
when include_draft=True.

Note: Only YAML (declarative) connectors are currently supported.
Docker-based custom sources are not yet available.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `definition_id` | `string` | yes | — | The ID of the custom source definition to retrieve. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |
| `include_draft` | `boolean` | no | `false` | Whether to include the Connector Builder draft manifest in the response. If True and a draft exists, the response will include 'has_draft' and 'draft_manifest' fields. Defaults to False. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "definition_id": {
      "description": "The ID of the custom source definition to retrieve.",
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    },
    "include_draft": {
      "default": false,
      "description": "Whether to include the Connector Builder draft manifest in the response. If True and a draft exists, the response will include 'has_draft' and 'draft_manifest' fields. Defaults to False.",
      "type": "boolean"
    }
  },
  "required": [
    "definition_id"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "additionalProperties": true,
  "type": "object"
}
```

</details>

<a id="list_cloud_organizations"></a>

### list_cloud_organizations

**Hints:** `read-only` · `idempotent` · `open-world`

List organizations visible to the authenticated Airbyte Cloud credentials.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

_No parameters._

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {},
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "description": "Result of discovering organizations in Airbyte Cloud.",
  "properties": {
    "organizations": {
      "items": {
        "description": "Information about an organization in Airbyte Cloud.",
        "properties": {
          "id": {
            "type": "string"
          },
          "name": {
            "type": "string"
          },
          "email": {
            "type": "string"
          },
          "payment_status": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "default": null
          },
          "subscription_status": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "default": null
          },
          "is_account_locked": {
            "default": false,
            "type": "boolean"
          }
        },
        "required": [
          "id",
          "name",
          "email"
        ],
        "type": "object"
      },
      "type": "array"
    },
    "message": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    }
  },
  "required": [
    "organizations"
  ],
  "type": "object"
}
```

</details>

<a id="list_cloud_sync_jobs"></a>

### list_cloud_sync_jobs

**Hints:** `read-only` · `idempotent` · `open-world`

List sync jobs for a connection with limit support.

    This tool allows you to retrieve a list of sync jobs for a connection,
    with control over ordering and result limit. By default, jobs are returned
    newest-first (`from_tail=True`).

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `connection_id` | `string` | yes | — | The ID of the Airbyte Cloud connection. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |
| `max_jobs` | `integer` | no | `20` | Maximum number of jobs to return. Defaults to 20 if not specified. Maximum allowed value is 500. |
| `from_tail` | `boolean \| null` | no | `null` | When True, jobs are ordered newest-first (createdAt DESC). When False, jobs are ordered oldest-first (createdAt ASC). Defaults to True. |
| `job_type` | `enum("sync", "reset", "refresh", "clear") \| null` | no | `null` | Filter by job type. Options: 'sync', 'reset', 'refresh', 'clear'. If not specified, defaults to sync and reset jobs only (API default). Use 'refresh' to find refresh jobs or 'clear' to find clear jobs. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "connection_id": {
      "description": "The ID of the Airbyte Cloud connection.",
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    },
    "max_jobs": {
      "default": 20,
      "description": "Maximum number of jobs to return. Defaults to 20 if not specified. Maximum allowed value is 500.",
      "type": "integer"
    },
    "from_tail": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "When True, jobs are ordered newest-first (createdAt DESC). When False, jobs are ordered oldest-first (createdAt ASC). Defaults to True."
    },
    "job_type": {
      "anyOf": [
        {
          "description": "Job type values for Airbyte Cloud jobs.",
          "enum": [
            "sync",
            "reset",
            "refresh",
            "clear"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Filter by job type. Options: 'sync', 'reset', 'refresh', 'clear'. If not specified, defaults to sync and reset jobs only (API default). Use 'refresh' to find refresh jobs or 'clear' to find clear jobs."
    }
  },
  "required": [
    "connection_id"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "description": "Result of listing sync jobs with limit support.",
  "properties": {
    "jobs": {
      "items": {
        "description": "Information about a sync job.",
        "properties": {
          "job_id": {
            "type": "integer"
          },
          "status": {
            "type": "string"
          },
          "bytes_synced": {
            "type": "integer"
          },
          "records_synced": {
            "type": "integer"
          },
          "start_time": {
            "type": "string"
          },
          "job_url": {
            "type": "string"
          }
        },
        "required": [
          "job_id",
          "status",
          "bytes_synced",
          "records_synced",
          "start_time",
          "job_url"
        ],
        "type": "object"
      },
      "type": "array"
    },
    "jobs_count": {
      "type": "integer"
    },
    "from_tail": {
      "type": "boolean"
    }
  },
  "required": [
    "jobs",
    "jobs_count",
    "from_tail"
  ],
  "type": "object"
}
```

</details>

<a id="list_cloud_workspaces"></a>

### list_cloud_workspaces

**Hints:** `read-only` · `idempotent` · `open-world`

List all workspaces visible to the authenticated credentials.

    When an organization ID or exact organization name is provided, the Config API
    lists workspaces in that organization. When neither is provided and the client
    has no default organization, the public API lists workspaces across organizations
    visible to the current credentials. Otherwise, results are scoped to the client's
    default organization.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `organization_id` | `string \| null` | no | `null` | Optional organization ID to list workspaces within. |
| `organization_name` | `string \| null` | no | `null` | Optional organization name (exact match) to list workspaces within. |
| `name_contains` | `string \| null` | no | `null` | Optional substring to filter workspaces by name (server-side filtering) |
| `limit` | `integer \| null` | no | `null` | Optional maximum number of items to return (default: no limit) |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "organization_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional organization ID to list workspaces within."
    },
    "organization_name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional organization name (exact match) to list workspaces within."
    },
    "name_contains": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional substring to filter workspaces by name (server-side filtering)"
    },
    "limit": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional maximum number of items to return (default: no limit)"
    }
  },
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "description": "Result of discovering workspaces in Airbyte Cloud.",
  "properties": {
    "workspaces": {
      "items": {
        "description": "Information about a workspace in Airbyte Cloud.",
        "properties": {
          "workspace_id": {
            "type": "string"
          },
          "workspace_name": {
            "type": "string"
          },
          "workspace_url": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "default": null
          },
          "organization_id": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ]
          },
          "organization_name": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "default": null
          },
          "payment_status": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "default": null
          },
          "subscription_status": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "default": null
          },
          "is_account_locked": {
            "default": false,
            "type": "boolean"
          }
        },
        "required": [
          "workspace_id",
          "workspace_name",
          "organization_id"
        ],
        "type": "object"
      },
      "type": "array"
    },
    "message": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    }
  },
  "required": [
    "workspaces"
  ],
  "type": "object"
}
```

</details>

<a id="list_custom_source_definitions"></a>

### list_custom_source_definitions

**Hints:** `read-only` · `idempotent` · `open-world`

List custom YAML source definitions in the Airbyte Cloud workspace.

Note: Only YAML (declarative) connectors are currently supported.
Docker-based custom sources are not yet available.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "items": {
        "additionalProperties": true,
        "type": "object"
      },
      "type": "array"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="list_deployed_cloud_connections"></a>

### list_deployed_cloud_connections

**Hints:** `read-only` · `idempotent` · `open-world`

List all deployed connections in the Airbyte Cloud workspace.

    When with_connection_status is True, each connection result will include
    information about the most recent sync job status, skipping over any
    currently in-progress syncs to find the last completed job.

    When failing_connections_only is True, only connections where the most
    recent completed sync job failed or was cancelled will be returned.
    This implicitly enables with_connection_status.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |
| `name_contains` | `string \| null` | no | `null` | Optional case-insensitive substring to filter connections by name |
| `limit` | `integer \| null` | no | `null` | Optional maximum number of items to return (default: no limit) |
| `with_connection_status` | `boolean \| null` | no | `false` | If True, include status info for each connection's most recent sync job |
| `failing_connections_only` | `boolean \| null` | no | `false` | If True, only return connections with failed/cancelled last sync |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    },
    "name_contains": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional case-insensitive substring to filter connections by name"
    },
    "limit": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional maximum number of items to return (default: no limit)"
    },
    "with_connection_status": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "null"
        }
      ],
      "default": false,
      "description": "If True, include status info for each connection's most recent sync job"
    },
    "failing_connections_only": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "null"
        }
      ],
      "default": false,
      "description": "If True, only return connections with failed/cancelled last sync"
    }
  },
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "items": {
        "description": "Information about a deployed connection in Airbyte Cloud.",
        "properties": {
          "id": {
            "type": "string"
          },
          "name": {
            "type": "string"
          },
          "url": {
            "type": "string"
          },
          "source_id": {
            "type": "string"
          },
          "destination_id": {
            "type": "string"
          },
          "last_job_status": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "default": null
          },
          "last_job_id": {
            "anyOf": [
              {
                "type": "integer"
              },
              {
                "type": "null"
              }
            ],
            "default": null
          },
          "last_job_time": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "default": null
          },
          "currently_running_job_id": {
            "anyOf": [
              {
                "type": "integer"
              },
              {
                "type": "null"
              }
            ],
            "default": null
          },
          "currently_running_job_start_time": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "default": null
          }
        },
        "required": [
          "id",
          "name",
          "url",
          "source_id",
          "destination_id"
        ],
        "type": "object"
      },
      "type": "array"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="list_deployed_cloud_destination_connectors"></a>

### list_deployed_cloud_destination_connectors

**Hints:** `read-only` · `idempotent` · `open-world`

List all deployed destination connectors in the Airbyte Cloud workspace.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |
| `name_contains` | `string \| null` | no | `null` | Optional case-insensitive substring to filter destinations by name |
| `limit` | `integer \| null` | no | `null` | Optional maximum number of items to return (default: no limit) |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    },
    "name_contains": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional case-insensitive substring to filter destinations by name"
    },
    "limit": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional maximum number of items to return (default: no limit)"
    }
  },
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "items": {
        "description": "Information about a deployed destination connector in Airbyte Cloud.",
        "properties": {
          "id": {
            "type": "string"
          },
          "name": {
            "type": "string"
          },
          "url": {
            "type": "string"
          }
        },
        "required": [
          "id",
          "name",
          "url"
        ],
        "type": "object"
      },
      "type": "array"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="list_deployed_cloud_source_connectors"></a>

### list_deployed_cloud_source_connectors

**Hints:** `read-only` · `idempotent` · `open-world`

List all deployed source connectors in the Airbyte Cloud workspace.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |
| `name_contains` | `string \| null` | no | `null` | Optional case-insensitive substring to filter sources by name |
| `limit` | `integer \| null` | no | `null` | Optional maximum number of items to return (default: no limit) |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    },
    "name_contains": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional case-insensitive substring to filter sources by name"
    },
    "limit": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional maximum number of items to return (default: no limit)"
    }
  },
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "items": {
        "description": "Information about a deployed source connector in Airbyte Cloud.",
        "properties": {
          "id": {
            "type": "string"
          },
          "name": {
            "type": "string"
          },
          "url": {
            "type": "string"
          }
        },
        "required": [
          "id",
          "name",
          "url"
        ],
        "type": "object"
      },
      "type": "array"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="permanently_delete_cloud_connection"></a>

### permanently_delete_cloud_connection

**Hints:** `destructive` · `open-world`

Permanently delete a connection from Airbyte Cloud.

    IMPORTANT: This operation requires the connection name to contain "delete-me" or "deleteme"
    (case insensitive).

    If the connection does not meet this requirement, the deletion will be rejected with a
    helpful error message. Instruct the user to rename the connection appropriately to authorize
    the deletion.

    The provided name must match the actual name of the connection for the operation to proceed.
    This is a safety measure to ensure you are deleting the correct resource.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `connection_id` | `string` | yes | — | The ID of the connection to delete. |
| `name` | `string` | yes | — | The expected name of the connection (for verification). |
| `cascade_delete_source` | `boolean` | no | `false` | Whether to also delete the source connector associated with this connection. |
| `cascade_delete_destination` | `boolean` | no | `false` | Whether to also delete the destination connector associated with this connection. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "connection_id": {
      "description": "The ID of the connection to delete.",
      "type": "string"
    },
    "name": {
      "description": "The expected name of the connection (for verification).",
      "type": "string"
    },
    "cascade_delete_source": {
      "default": false,
      "description": "Whether to also delete the source connector associated with this connection.",
      "type": "boolean"
    },
    "cascade_delete_destination": {
      "default": false,
      "description": "Whether to also delete the destination connector associated with this connection.",
      "type": "boolean"
    }
  },
  "required": [
    "connection_id",
    "name"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="permanently_delete_cloud_destination"></a>

### permanently_delete_cloud_destination

**Hints:** `destructive` · `open-world`

Permanently delete a deployed destination connector from Airbyte Cloud.

    IMPORTANT: This operation requires the destination name to contain "delete-me" or "deleteme"
    (case insensitive).

    If the destination does not meet this requirement, the deletion will be rejected with a
    helpful error message. Instruct the user to rename the destination appropriately to authorize
    the deletion.

    The provided name must match the actual name of the destination for the operation to proceed.
    This is a safety measure to ensure you are deleting the correct resource.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `destination_id` | `string` | yes | — | The ID of the deployed destination to delete. |
| `name` | `string` | yes | — | The expected name of the destination (for verification). |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "destination_id": {
      "description": "The ID of the deployed destination to delete.",
      "type": "string"
    },
    "name": {
      "description": "The expected name of the destination (for verification).",
      "type": "string"
    }
  },
  "required": [
    "destination_id",
    "name"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="permanently_delete_cloud_source"></a>

### permanently_delete_cloud_source

**Hints:** `destructive` · `open-world`

Permanently delete a deployed source connector from Airbyte Cloud.

    IMPORTANT: This operation requires the source name to contain "delete-me" or "deleteme"
    (case insensitive).

    If the source does not meet this requirement, the deletion will be rejected with a
    helpful error message. Instruct the user to rename the source appropriately to authorize
    the deletion.

    The provided name must match the actual name of the source for the operation to proceed.
    This is a safety measure to ensure you are deleting the correct resource.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `source_id` | `string` | yes | — | The ID of the deployed source to delete. |
| `name` | `string` | yes | — | The expected name of the source (for verification). |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "source_id": {
      "description": "The ID of the deployed source to delete.",
      "type": "string"
    },
    "name": {
      "description": "The expected name of the source (for verification).",
      "type": "string"
    }
  },
  "required": [
    "source_id",
    "name"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="permanently_delete_custom_source_definition"></a>

### permanently_delete_custom_source_definition

**Hints:** `destructive` · `open-world`

Permanently delete a custom YAML source definition from Airbyte Cloud.

IMPORTANT: This operation requires the connector name to contain "delete-me" or "deleteme"
(case insensitive).

If the connector does not meet this requirement, the deletion will be rejected with a
helpful error message. Instruct the user to rename the connector appropriately to authorize
the deletion.

The provided name must match the actual name of the definition for the operation to proceed.
This is a safety measure to ensure you are deleting the correct resource.

Note: Only YAML (declarative) connectors are currently supported.
Docker-based custom sources are not yet available.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `definition_id` | `string` | yes | — | The ID of the custom source definition to delete. |
| `name` | `string` | yes | — | The expected name of the custom source definition (for verification). |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "definition_id": {
      "description": "The ID of the custom source definition to delete.",
      "type": "string"
    },
    "name": {
      "description": "The expected name of the custom source definition (for verification).",
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "required": [
    "definition_id",
    "name"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="publish_custom_source_definition"></a>

### publish_custom_source_definition

**Hints:** `open-world`

Publish a custom YAML source connector definition to Airbyte Cloud.

    Note: Only YAML (declarative) connectors are currently supported.
    Docker-based custom sources are not yet available.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `name` | `string` | yes | — | The name for the custom connector definition. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |
| `manifest_yaml` | `string \| string \| null \| null` | no | `null` |  |
| `unique` | `boolean` | no | `true` | Whether to require a unique name. |
| `pre_validate` | `boolean` | no | `true` | Whether to validate the manifest client-side before publishing. |
| `testing_values` | `object \| string \| null` | no | `null` | Optional testing configuration values for the Builder UI. Can be provided as a JSON object or JSON string. Supports inline secret refs via 'secret_reference::ENV_VAR_NAME' syntax. If provided, these values replace any existing testing values for the connector builder project, allowing immediate test read operations. |
| `testing_values_secret_name` | `string \| null` | no | `null` | Optional name of a secret containing testing configuration values in JSON or YAML format. The secret will be resolved by the MCP server and merged into testing_values, with secret values taking precedence. This lets the agent reference secrets without sending raw values as tool arguments. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "name": {
      "description": "The name for the custom connector definition.",
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    },
    "manifest_yaml": {
      "anyOf": [
        {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "format": "path",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The Low-code CDK manifest as a YAML string or file path. Required for YAML connectors."
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "unique": {
      "default": true,
      "description": "Whether to require a unique name.",
      "type": "boolean"
    },
    "pre_validate": {
      "default": true,
      "description": "Whether to validate the manifest client-side before publishing.",
      "type": "boolean"
    },
    "testing_values": {
      "anyOf": [
        {
          "additionalProperties": true,
          "type": "object"
        },
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional testing configuration values for the Builder UI. Can be provided as a JSON object or JSON string. Supports inline secret refs via 'secret_reference::ENV_VAR_NAME' syntax. If provided, these values replace any existing testing values for the connector builder project, allowing immediate test read operations."
    },
    "testing_values_secret_name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional name of a secret containing testing configuration values in JSON or YAML format. The secret will be resolved by the MCP server and merged into testing_values, with secret values taking precedence. This lets the agent reference secrets without sending raw values as tool arguments."
    }
  },
  "required": [
    "name"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="rename_cloud_connection"></a>

### rename_cloud_connection

**Hints:** `open-world`

Rename a connection on Airbyte Cloud.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `connection_id` | `string` | yes | — | The ID of the connection to rename. |
| `name` | `string` | yes | — | New name for the connection. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "connection_id": {
      "description": "The ID of the connection to rename.",
      "type": "string"
    },
    "name": {
      "description": "New name for the connection.",
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "required": [
    "connection_id",
    "name"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="rename_cloud_destination"></a>

### rename_cloud_destination

**Hints:** `open-world`

Rename a deployed destination connector on Airbyte Cloud.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `destination_id` | `string` | yes | — | The ID of the deployed destination to rename. |
| `name` | `string` | yes | — | New name for the destination. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "destination_id": {
      "description": "The ID of the deployed destination to rename.",
      "type": "string"
    },
    "name": {
      "description": "New name for the destination.",
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "required": [
    "destination_id",
    "name"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="rename_cloud_source"></a>

### rename_cloud_source

**Hints:** `open-world`

Rename a deployed source connector on Airbyte Cloud.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `source_id` | `string` | yes | — | The ID of the deployed source to rename. |
| `name` | `string` | yes | — | New name for the source. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "source_id": {
      "description": "The ID of the deployed source to rename.",
      "type": "string"
    },
    "name": {
      "description": "New name for the source.",
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "required": [
    "source_id",
    "name"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="run_cloud_sync"></a>

### run_cloud_sync

**Hints:** `open-world`

Run a sync job on Airbyte Cloud.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `connection_id` | `string` | yes | — | The ID of the Airbyte Cloud connection. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |
| `wait` | `boolean` | no | `false` | Whether to wait for the sync to complete. Since a sync can take between several minutes and several hours, this option is not recommended for most scenarios. |
| `wait_timeout` | `integer` | no | `300` | Maximum time to wait for sync completion (seconds). |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "connection_id": {
      "description": "The ID of the Airbyte Cloud connection.",
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    },
    "wait": {
      "default": false,
      "description": "Whether to wait for the sync to complete. Since a sync can take between several minutes and several hours, this option is not recommended for most scenarios.",
      "type": "boolean"
    },
    "wait_timeout": {
      "default": 300,
      "description": "Maximum time to wait for sync completion (seconds).",
      "type": "integer"
    }
  },
  "required": [
    "connection_id"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="set_cloud_connection_selected_streams"></a>

### set_cloud_connection_selected_streams

**Hints:** `destructive` · `open-world`

Set the selected streams for a connection on Airbyte Cloud.

    This is a destructive operation that can break existing connections if the
    stream selection is changed incorrectly. Use with caution.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `connection_id` | `string` | yes | — | The ID of the connection to update. |
| `stream_names` | `string \| array<string>` | yes | — | The selected stream names to sync within the connection. Must be an explicit stream name or list of streams. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "connection_id": {
      "description": "The ID of the connection to update.",
      "type": "string"
    },
    "stream_names": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "items": {
            "type": "string"
          },
          "type": "array"
        }
      ],
      "description": "The selected stream names to sync within the connection. Must be an explicit stream name or list of streams."
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "required": [
    "connection_id",
    "stream_names"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="set_cloud_connection_table_prefix"></a>

### set_cloud_connection_table_prefix

**Hints:** `destructive` · `open-world`

Set the table prefix for a connection on Airbyte Cloud.

    This is a destructive operation that can break downstream dependencies if the
    table prefix is changed incorrectly. Use with caution.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `connection_id` | `string` | yes | — | The ID of the connection to update. |
| `prefix` | `string` | yes | — | New table prefix to use when syncing to the destination. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "connection_id": {
      "description": "The ID of the connection to update.",
      "type": "string"
    },
    "prefix": {
      "description": "New table prefix to use when syncing to the destination.",
      "type": "string"
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "required": [
    "connection_id",
    "prefix"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="update_cloud_connection"></a>

### update_cloud_connection

**Hints:** `destructive` · `open-world`

Update a connection's settings on Airbyte Cloud.

    This tool allows updating multiple connection settings in a single call:
    - Enable or disable the connection
    - Set a cron schedule for automatic syncs
    - Switch to manual scheduling (no automatic syncs)

    At least one setting must be provided. The 'cron_expression' and 'manual_schedule'
    parameters are mutually exclusive.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `connection_id` | `string` | yes | — | The ID of the connection to update. |
| `enabled` | `boolean \| null` | no | `null` | Set the connection's enabled status. True enables the connection (status='active'), False disables it (status='inactive'). Leave unset to keep the current status. |
| `cron_expression` | `string \| null` | no | `null` | A cron expression defining when syncs should run. Examples: '0 0 * * *' (daily at midnight UTC), '0 */6 * * *' (every 6 hours), '0 0 * * 0' (weekly on Sunday at midnight UTC). Leave unset to keep the current schedule. Cannot be used together with 'manual_schedule'. |
| `manual_schedule` | `boolean \| null` | no | `null` | Set to True to disable automatic syncs (manual scheduling only). Syncs will only run when manually triggered. Cannot be used together with 'cron_expression'. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "connection_id": {
      "description": "The ID of the connection to update.",
      "type": "string"
    },
    "enabled": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Set the connection's enabled status. True enables the connection (status='active'), False disables it (status='inactive'). Leave unset to keep the current status."
    },
    "cron_expression": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "A cron expression defining when syncs should run. Examples: '0 0 * * *' (daily at midnight UTC), '0 */6 * * *' (every 6 hours), '0 0 * * 0' (weekly on Sunday at midnight UTC). Leave unset to keep the current schedule. Cannot be used together with 'manual_schedule'."
    },
    "manual_schedule": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Set to True to disable automatic syncs (manual scheduling only). Syncs will only run when manually triggered. Cannot be used together with 'cron_expression'."
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "required": [
    "connection_id"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="update_cloud_destination_config"></a>

### update_cloud_destination_config

**Hints:** `destructive` · `open-world`

Update a deployed destination connector's configuration on Airbyte Cloud.

    This is a destructive operation that can break existing connections if the
    configuration is changed incorrectly. Use with caution.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `destination_id` | `string` | yes | — | The ID of the deployed destination to update. |
| `config` | `object \| string` | yes | — | New configuration for the destination connector. |
| `config_secret_name` | `string \| null` | no | `null` | The name of the secret containing the configuration. |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "destination_id": {
      "description": "The ID of the deployed destination to update.",
      "type": "string"
    },
    "config": {
      "anyOf": [
        {
          "additionalProperties": true,
          "type": "object"
        },
        {
          "type": "string"
        }
      ],
      "description": "New configuration for the destination connector."
    },
    "config_secret_name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "The name of the secret containing the configuration."
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "required": [
    "destination_id",
    "config"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="update_cloud_source_config"></a>

### update_cloud_source_config

**Hints:** `destructive` · `open-world`

Update a deployed source connector's configuration on Airbyte Cloud.

    This is a destructive operation that can break existing connections if the
    configuration is changed incorrectly. Use with caution.

When connecting to a hosted MCP server, provide a bearer token via the `Authorization` header, or client credentials via the transport `Client-Id` and `Client-Secret` headers. To discover available organizations and workspaces, call `list_cloud_organizations` and `list_cloud_workspaces` before asking the user for an ID. For local or stdio connections, set the `AIRBYTE_CLOUD_BEARER_TOKEN` environment variable, or both `AIRBYTE_CLOUD_CLIENT_ID` and `AIRBYTE_CLOUD_CLIENT_SECRET`. If discovery returns multiple candidates, ask the user to choose one; do not select automatically.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `source_id` | `string` | yes | — | The ID of the deployed source to update. |
| `config` | `object \| string` | yes | — | New configuration for the source connector. |
| `config_secret_name` | `string \| null \| null` | no | `null` |  |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "source_id": {
      "description": "The ID of the deployed source to update.",
      "type": "string"
    },
    "config": {
      "anyOf": [
        {
          "additionalProperties": true,
          "type": "object"
        },
        {
          "type": "string"
        }
      ],
      "description": "New configuration for the source connector."
    },
    "config_secret_name": {
      "anyOf": [
        {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The name of the secret containing the configuration."
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    }
  },
  "required": [
    "source_id",
    "config"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>

<a id="update_custom_source_definition"></a>

### update_custom_source_definition

**Hints:** `destructive` · `open-world`

Update a custom YAML source definition in Airbyte Cloud.

Updates the manifest and/or testing values for an existing custom source definition.
At least one of manifest_yaml, testing_values, or testing_values_secret_name must be provided.

#### Parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `definition_id` | `string` | yes | — | The ID of the definition to update. |
| `manifest_yaml` | `string \| string \| null \| null` | no | `null` |  |
| `workspace_id` | `string \| null` | no | `null` | Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable. |
| `pre_validate` | `boolean` | no | `true` | Whether to validate the manifest client-side before updating. |
| `testing_values` | `object \| string \| null` | no | `null` | Optional testing configuration values for the Builder UI. Can be provided as a JSON object or JSON string. Supports inline secret refs via 'secret_reference::ENV_VAR_NAME' syntax. If provided, these values replace any existing testing values for the connector builder project. The entire testing values object is overwritten, so pass the full set of values you want to persist. |
| `testing_values_secret_name` | `string \| null` | no | `null` | Optional name of a secret containing testing configuration values in JSON or YAML format. The secret will be resolved by the MCP server and merged into testing_values, with secret values taking precedence. This lets the agent reference secrets without sending raw values as tool arguments. |

<details>
<summary>Show input JSON schema</summary>

```json
{
  "additionalProperties": false,
  "properties": {
    "definition_id": {
      "description": "The ID of the definition to update.",
      "type": "string"
    },
    "manifest_yaml": {
      "anyOf": [
        {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "format": "path",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "New manifest as YAML string or file path. Optional; omit to update only testing values."
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "workspace_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Workspace ID. Hosted MCP connections pass it via the `X-Airbyte-Workspace-Id` header; local or stdio connections use the `AIRBYTE_CLOUD_WORKSPACE_ID` environment variable."
    },
    "pre_validate": {
      "default": true,
      "description": "Whether to validate the manifest client-side before updating.",
      "type": "boolean"
    },
    "testing_values": {
      "anyOf": [
        {
          "additionalProperties": true,
          "type": "object"
        },
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional testing configuration values for the Builder UI. Can be provided as a JSON object or JSON string. Supports inline secret refs via 'secret_reference::ENV_VAR_NAME' syntax. If provided, these values replace any existing testing values for the connector builder project. The entire testing values object is overwritten, so pass the full set of values you want to persist."
    },
    "testing_values_secret_name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional name of a secret containing testing configuration values in JSON or YAML format. The secret will be resolved by the MCP server and merged into testing_values, with secret values taking precedence. This lets the agent reference secrets without sending raw values as tool arguments."
    }
  },
  "required": [
    "definition_id"
  ],
  "type": "object"
}
```

</details>

<details>
<summary>Show output JSON schema</summary>

```json
{
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": [
    "result"
  ],
  "type": "object",
  "x-fastmcp-wrap-result": true
}
```

</details>