---

products: embedded

---

# Authentication & Token Management

## Overview

Airbyte Embedded uses a two-tier authentication system:

1. **Organization-level tokens**: Your main API credentials for managing templates and connections
2. **User-scoped tokens**: Temporary tokens that allow end-users to configure sources in their isolated workspaces

For complete authentication documentation including widget tokens and region selection, see [Authentication](./authentication.md).

## Generating user-scoped tokens

When collecting credentials from your users, generate a scoped access token that only has permissions to read and modify integrations in their specific workspace. This follows the principle of least privilege and ensures user data isolation.

This can be done by submitting a request to:

```bash
curl --location 'https://api.airbyte.ai/api/v1/embedded/scoped-token' \

  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer <your_access_token>' \
  --header 'X-Organization-Id: <your_organization_id>' \
  --data '{

    "workspace_name": "your_workspace_name",
    "region_id": "optional_region_id"
  }'

```

Where:

- `workspace_name` is a unique identifier within your organization for each customer's tenant
- `region_id` (optional) is the region where the workspace should be created:
  - US region: `645a183f-b12b-4c6e-8ad3-99e165603450` (default)
  - EU region: `b9e48d61-f082-4a14-a8d0-799a907938cb`

The API will return a JSON object with a token string:

```json
{
  "token": "eyJ0b2tlbiI6ImV5SmhiR2NpT2lKSVV6STFOaUo5..."
}

```

## Understanding the token response

The response contains a scoped JWT token that can be used to:

- Create and manage sources in the workspace
- List available source templates
- Create connections from sources

### Using the scoped token

Use the token as a Bearer token in subsequent API calls:

```bash
curl https://api.airbyte.ai/api/v1/embedded/sources \

  -H 'Authorization: Bearer <scoped_token>'

```

For widget integration, see [Authentication - Widget Token](./authentication.md#widget-token).

## Creating a Source

You'll need 3 pieces of information to create a source for your users:

1. Their workspace ID
2. The ID of the [Source Template](./source-templates.md) used
3. The connection configuration

## Basic source creation

Here is an example request:

```bash
curl --location 'https://api.airbyte.ai/api/v1/embedded/sources' \

  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer <scoped_token>' \
  --header 'X-Organization-Id: <your_organization_id>' \
  --data '{

    "name": "your_source_name",
    "workspace ID": "your_workspace ID",
    "source_template_id": "your_source_template_id",
    "source_config": {
      // your source configuration fields here
    }
  }'

```

The connection configuration should include all required fields from the connector specification, except for the ones included as default values in your source template.

You can find the full connector specification in the [Connector Registry](https://connectors.airbyte.com/files/registries/v0/cloud_registry.json).

You can find [the reference docs for creating a source here](https://api.airbyte.ai/api/v1/docs#tag/Sources/operation/create_integrations_sources).

## Filtering connection templates with tags

When creating a source, you can control which connection templates are available by using tag filtering:

```bash
curl --location 'https://api.airbyte.ai/api/v1/embedded/sources' \

  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer <scoped_token>' \
  --header 'X-Organization-Id: <your_organization_id>' \
  --data '{

    "name": "your_source_name",
    "workspace ID": "your_workspace ID",
    "source_template_id": "your_source_template_id",
    "source_config": {},
    "selected_connection_template_tags": ["analytics", "standard-sync"],
    "selected_connection_template_tags_mode": "any"
  }'

```

**Tag Selection Modes:**

- `any` - Connection template must have at least one of the specified tags
- `all` - Connection template must have all of the specified tags

This allows you to customize which sync configurations are available based on customer tier, compliance requirements, or other criteria. See [Template Tags](./tags.md) for more information.

## Advanced: Stream Management

After creating a source, you can manage individual streams (tables/collections) within that source. This allows fine-grained control over which data is synced.

## Discover source catalog

Discover all available streams for a source:

```bash
curl https://api.airbyte.ai/api/v1/integrations/sources/{source_id}/discover \

  -H 'Authorization: Bearer <scoped_token>'

```

This returns the complete catalog of streams available from the source connector, including:

- Stream names
- Available sync modes
- Schema information
- Primary keys and cursors

### Example response

```json
{
  "catalog": {
    "streams": [
      {
        "name": "users",
        "supported_sync_modes": ["full_refresh", "incremental"],
        "source_defined_cursor": true,
        "default_cursor_field": ["updated_at"],
        "json_schema": {
          "type": "object",
          "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string"},
            "updated_at": {"type": "string", "format": "date-time"}
          }
        }
      },
      {
        "name": "orders",
        "supported_sync_modes": ["full_refresh", "incremental"],
        "source_defined_cursor": true,
        "default_cursor_field": ["created_at"]
      }
    ]
  }
}

```

## Query catalog with jmespath

For advanced filtering and transformation of the catalog, use JMESPath queries:

```bash
curl -X POST https://api.airbyte.ai/api/v1/integrations/sources/{source_id}/catalog/query \

  -H 'Authorization: Bearer <scoped_token>' \
  -H 'Content-Type: application/json' \
  -d '{

    "jmes_query": "streams[?name==`users` || name==`orders`]"
  }'

```

### Jmespath query examples

**Filter by stream name:**

```json
{
  "jmes_query": "streams[?name==`users`]"
}

```

**Find streams with incremental support:**

```json
{
  "jmes_query": "streams[?contains(supported_sync_modes, 'incremental')]"
}

```

**Get only stream names:**

```json
{
  "jmes_query": "streams[*].name"
}

```

**Complex filtering:**

```json
{
  "jmes_query": "streams[?source_defined_cursor==`true` && contains(supported_sync_modes, 'incremental')]"
}

```

See [JMESPath specification](https://jmespath.org/) for complete query syntax.

## Add stream to source

Add a specific stream to an existing source:

```bash
curl -X POST https://api.airbyte.ai/api/v1/integrations/sources/{source_id}/streams \

  -H 'Authorization: Bearer <scoped_token>' \
  -H 'Content-Type: application/json' \
  -d '{

    "stream_name": "users",
    "sync_mode": "incremental",
    "destination_sync_mode": "append_dedup",
    "cursor_field": ["updated_at"],
    "primary_key": [["id"]]
  }'

```

### Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `stream_name` | string | Yes | Name of the stream to add |
| `sync_mode` | string | No | Source sync mode: `full_refresh` or `incremental` |
| `destination_sync_mode` | string | No | Destination sync mode: `append`, `overwrite`, `append_dedup` |
| `cursor_field` | array | No | Field to use as cursor for incremental syncs |
| `primary_key` | array | No | Primary key fields for deduplication |

## Update stream configuration

Update stream settings using JSON Patch (RFC 6902):

```bash
curl -X PATCH https://api.airbyte.ai/api/v1/integrations/sources/{source_id}/streams/{stream_name} \

  -H 'Authorization: Bearer <scoped_token>' \
  -H 'Content-Type: application/json' \
  -d '[

    {
      "op": "replace",
      "path": "/sync_mode",
      "value": "incremental"
    },
    {
      "op": "replace",
      "path": "/cursor_field",
      "value": ["last_modified"]
    }
  ]'

```

### JSON patch operations

The request body is a JSON Patch array following [RFC 6902](https://datatracker.ietf.org/doc/html/rfc6902).

**Supported operations:**

- `replace` - Replace a field value
- `add` - Add a new field
- `remove` - Remove a field

**Common patch examples:**

**Change sync mode:**

```json
[
  {
    "op": "replace",
    "path": "/sync_mode",
    "value": "incremental"
  }
]

```

**Update cursor field:**

```json
[
  {
    "op": "replace",
    "path": "/cursor_field",
    "value": ["updated_at"]
  }
]

```

**Change destination sync mode:**

```json
[
  {
    "op": "replace",
    "path": "/destination_sync_mode",
    "value": "append_dedup"
  }
]

```

**Multiple changes:**

```json
[
  {
    "op": "replace",
    "path": "/sync_mode",
    "value": "incremental"
  },
  {
    "op": "replace",
    "path": "/destination_sync_mode",
    "value": "append_dedup"
  },
  {
    "op": "replace",
    "path": "/cursor_field",
    "value": ["updated_at"]
  },
  {
    "op": "replace",
    "path": "/primary_key",
    "value": [["id"]]
  }
]

```

## Remove stream from source

Remove a stream from a source:

```bash
curl -X DELETE https://api.airbyte.ai/api/v1/integrations/sources/{source_id}/streams/{stream_name} \

  -H 'Authorization: Bearer <scoped_token>'

```

This stops syncing the specified stream but does not delete historical data.

## Common stream management workflows

### Workflow 1: add multiple streams

```bash
# Discover available streams
CATALOG=$(curl https://api.airbyte.ai/api/v1/integrations/sources/$SOURCE_ID/discover \

  -H "Authorization: Bearer $SCOPED_TOKEN")

# Add users stream with incremental sync
curl -X POST https://api.airbyte.ai/api/v1/integrations/sources/$SOURCE_ID/streams \

  -H "Authorization: Bearer $SCOPED_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{

    "stream_name": "users",
    "sync_mode": "incremental",
    "cursor_field": ["updated_at"]
  }'

# Add orders stream with full refresh
curl -X POST https://api.airbyte.ai/api/v1/integrations/sources/$SOURCE_ID/streams \

  -H "Authorization: Bearer $SCOPED_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{

    "stream_name": "orders",
    "sync_mode": "full_refresh",
    "destination_sync_mode": "overwrite"
  }'

```

### Workflow 2: optimize existing streams

```bash
# Change from full_refresh to incremental for better performance
curl -X PATCH https://api.airbyte.ai/api/v1/integrations/sources/$SOURCE_ID/streams/users \

  -H "Authorization: Bearer $SCOPED_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[

    {
      "op": "replace",
      "path": "/sync_mode",
      "value": "incremental"
    },
    {
      "op": "replace",
      "path": "/cursor_field",
      "value": ["updated_at"]
    }
  ]'

```

### Workflow 3: find and add incremental streams

```bash
# Find all streams that support incremental sync
INCREMENTAL_STREAMS=$(curl -X POST \
  https://api.airbyte.ai/api/v1/integrations/sources/$SOURCE_ID/catalog/query \

  -H "Authorization: Bearer $SCOPED_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{

    "jmes_query": "streams[?contains(supported_sync_modes, '\''incremental'\'')].name"
  }')

# Add each incremental stream
# (In a real implementation, you would parse the JSON response and iterate)
```

## Best practices

### Stream selection

- **Start selective**: Add only the streams you need rather than syncing everything
- **Use incremental when possible**: Reduces data transfer and processing time
- **Monitor stream performance**: Remove or optimize slow streams

### Sync mode selection

| Sync Mode | Use Case | Performance | Data Usage |
|-----------|----------|-------------|------------|
| `full_refresh` + `overwrite` | Small tables, dimension tables | Lower (replaces all data) | High |
| `full_refresh` + `append` | Audit logs, immutable events | Lower | Very High |
| `incremental` + `append` | Event streams, logs | High | Low |
| `incremental` + `append_dedup` | Mutable tables with updates | Medium | Low |

### Cursor field selection

- **Use indexed fields**: Choose cursor fields that are indexed in the source
- **Prefer immutable fields**: Use `created_at` over `updated_at` when possible
- **Validate cursor coverage**: Ensure the cursor field is present in all records

### Performance optimization

1. **Discover once, reuse**: Cache catalog discovery results
2. **Batch stream operations**: Add multiple streams in quick succession
3. **Use JMESPath filtering**: Reduce data transfer when querying catalogs
4. **Monitor sync performance**: Use stream-level metrics to identify bottlenecks

## Error handling

### 404 stream not found

```json
{
  "detail": "Stream 'invalid_stream' not found in source catalog"
}

```

**Solution**: discover the catalog to verify stream names

### 422 validation error

```json
{
  "detail": "Sync mode 'invalid_mode' not supported for stream 'users'"
}

```

**Solution**: check the stream's `supported_sync_modes` in the catalog

### 400 invalid JSON patch

```json
{
  "detail": "Invalid JSON Patch operation"
}

```

**Solution**: verify JSON Patch syntax follows RFC 6902

## Related documentation

- [Source Templates](./source-templates.md) - Create and manage source templates
- [Connection Templates](./connection-templates.md) - Configure sync behavior
- [Template Tags](./tags.md) - Organize templates with tags
- [Authentication](./authentication.md) - Token generation and management
