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

## Controlling which streams are synced

Stream selection is configured at the **source template level** using the `customization` field. This allows you to control which streams from a connector are included when connections are created from that template.

### Stream selection modes

There are three stream selection modes available:

- `suggested` (default) - Only sync streams marked as "suggested" by the connector. If no streams are marked as suggested, all streams are synced.
- `all` - Sync all available streams from the source
- `whitelist` - Only sync specific streams that you explicitly list

### Whitelisting specific streams

To whitelist specific streams, configure your source template with the `whitelist` mode and provide a list of stream names:

```bash
curl --location 'https://api.airbyte.ai/api/v1/embedded/templates/sources' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer <your_access_token>' \
  --header 'X-Organization-Id: <your_organization_id>' \
  --data '{
    "name": "PostgreSQL Analytics Template",
    "actor_definition_id": "decd338e-5647-4c0b-adf4-da0e75f5a750",
    "partial_default_config": {
      "ssl_mode": {"mode": "require"}
    },
    "customization": {
      "stream_selection_mode": "whitelist",
      "stream_whitelist": ["orders", "customers", "products"]
    }
  }'
```

**Important notes:**

- Syncing all streams can cause perceived performance issues depending on the source
- When using `whitelist` mode, you must provide a non-empty `stream_whitelist` array
- Stream names must exactly match the stream names provided by the connector
- When a source is created from this template, only the whitelisted streams will be available for syncing
- To find available stream names for a connector, use the [discover endpoint](https://api.airbyte.ai/api/v1/docs#tag/Sources/operation/get_source_catalog)

For more information about creating and configuring source templates, see [Source Templates](./source-templates.md).

## Related documentation

- [Source Templates](./source-templates.md) - Create and manage source templates
- [Connection Templates](./connection-templates.md) - Configure sync behavior
- [Template Tags](./tags.md) - Organize templates with tags
- [Authentication](./authentication.md) - Token generation and management
