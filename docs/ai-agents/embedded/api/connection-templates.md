---

products: embedded

---

# Connection Templates

A *connection template* pre-defines the **destination side** of every pipeline your customers spin up through the API or Embedded Widget. It answers two questions up-front:

1. Where should the data land?
2. How often should it sync?

When a customer finishes configuring a source, Airbyte automatically creates the connection by combining their source settings with *your* template.

## Creating connection templates

You'll need the following to create a connection template:

- Your organization ID
- The destination definition ID
- The destination configuration
- The destination name: We'll automatically create a destination with the given name in your user's workspaces
- (Optional) A cron expression describing when to run syncs. The cron expression must follow the Quartz syntax. You can use [freeformatter.com](https://www.freeformatter.com/cron-expression-generator-quartz.html) to help validate the expression
- (Optional) Tags to organize and filter templates

### Example request

```bash
curl --request POST 'https://api.airbyte.ai/api/v1/integrations/templates/connections' \

  --header "Content-Type: application/json" \
  --header "Authorization: Bearer <bearer_token>" \
  --data-raw '{

    "organization_id": "<organization_id>",
    "destination_name": "string",
    "destination_definition_id": "<destination_definition_id>",
    "destination_config": {
      "access_key_id": "<aws_access_key>",
      "secret_access_key": "<aws_secret_key>",
      "s3_bucket_name": "<s3_bucket>",
      "s3_bucket_path": "<s3_prefix>",
      "s3_bucket_region": "<s3_region>",
      "format": {
        "format_type": "CSV",
        "compression": {
          "compression_type": "No Compression"
        },
        "flattening": "Root level flattening"
      }
    },
    "cron_expression": "0 0 12 * * ?",
    "non_breaking_changes_preference": "propagate_columns",
    "sync_on_create": true,
    "tags": ["analytics", "standard-sync"]
  }'

```

You can find the full connector specification in the [Connector Registry](https://connectors.airbyte.com/files/registries/v0/cloud_registry.json).

Alternatively, if you want to view the full JSON for a given connector when creating a source or destination from scratch in Airbyte Cloud. After configuring the connector to your desired specifications (partially complete if you want an end user to complete the rest), you can select "Copy JSON". This will give you necessary details like the configuration and the `destination_definition_id`.

You can find [the reference docs for creating a connection template here](https://api.airbyte.ai/api/v1/docs#tag/Template-Connections/operation/create_integrations_templates_connections).

## Configuration options

### sync_on_create

Controls whether the connection should automatically start syncing immediately after creation.

- `true` (default) - Connection starts syncing as soon as it's created
- `false` - Connection is created but won't sync until its scheduled time or a manual trigger

**Example:**

```json
{
  "sync_on_create": false
}

```

Use `sync_on_create: false` when you want users to review the connection configuration before the first sync runs.

### non_breaking_changes_preference

Controls how Airbyte handles non-breaking schema changes (for example, new columns added to a table).

**Available Options:**

| Value | Behavior |
|-------|----------|
| `ignore` | Ignore schema changes; continue syncing only previously configured columns |
| `disable` | Disable the connection when schema changes are detected |
| `propagate_columns` | Automatically add new columns to the sync but don't update data types |
| `propagate_fully` | Automatically propagate all schema changes including column additions and data type updates |

**Example:**

```json
{
  "non_breaking_changes_preference": "propagate_columns"
}

```

**Use Cases:**

- **`ignore`**: Use when you have strict schema requirements and don't want unexpected columns
- **`disable`**: Use when schema changes require manual review
- **`propagate_columns`**: Best for most use cases; adds new columns automatically
- **`propagate_fully`**: Use when you want complete automation of schema evolution

### Cron expression validation

Airbyte provides an endpoint to validate and describe cron expressions:

```bash
curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/connections/cron/describe \

  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{

    "cron_expression": "0 0 12 * * ?"
  }'

```

This endpoint returns a human-readable description of when the cron will execute.

## Managing connection templates

### List connection templates

```bash
curl 'https://api.airbyte.ai/api/v1/integrations/templates/connections' \

  -H 'Authorization: Bearer <token>'

```

### Filter by tags

You can filter connection templates by tags:

```bash
curl 'https://api.airbyte.ai/api/v1/integrations/templates/connections?tags=analytics&tags=standard-sync&tags_mode=all' \

  -H 'Authorization: Bearer <token>'

```

**Tag Selection Modes:**

- `any` - Template must have at least one of the specified tags
- `all` - Template must have all of the specified tags

### Get connection template

```bash
curl 'https://api.airbyte.ai/api/v1/integrations/templates/connections/{id}' \

  -H 'Authorization: Bearer <token>'

```

### Update connection template

Use the PATCH endpoint to update an existing connection template:

```bash
curl -X PATCH 'https://api.airbyte.ai/api/v1/integrations/templates/connections/{id}' \

  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{

    "cron_expression": "0 0 6 * * ?",
    "non_breaking_changes_preference": "propagate_fully"
  }'

```

### Delete connection template

```bash
curl -X DELETE 'https://api.airbyte.ai/api/v1/integrations/templates/connections/{id}' \

  -H 'Authorization: Bearer <token>'

```

## Managing template tags

### Add tag to connection template

```bash
curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/connections/{id}/tags \

  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{

    "tag": "premium-features"
  }'

```

### Remove tag from connection template

```bash
curl -X DELETE https://api.airbyte.ai/api/v1/integrations/templates/connections/{id}/tags/{tag_name} \

  -H 'Authorization: Bearer <token>'

```

For complete tag management documentation, see [Template Tags](./tags.md).

## Using connection templates with sources

When a user creates a source from a source template, Airbyte automatically:

1. Creates the destination configured in your connection template
2. Creates a connection between the source and destination
3. Applies the schedule (cron expression) to the connection
4. Applies the schema change preference
5. Starts syncing if `sync_on_create` is `true`

### Filter connection templates by tags

You can control which connection templates are available when creating sources by using tag filtering in widget tokens or scoped tokens:

```bash
curl -X POST https://api.airbyte.ai/api/v1/embedded/widget-token \

  -H 'Authorization: Bearer <operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{

    "workspace_name": "customer_workspace",
    "allowed_origin": "https://yourapp.com",
    "selected_connection_template_tags": ["standard-sync"],
    "selected_connection_template_tags_mode": "any"
  }'

```

This ensures that only connection templates tagged with "standard-sync" are available when the user creates a source.

## Common patterns

### Multi-tenant destinations

Create separate connection templates for different customer tiers:

**Free tier - Basic S3 sync:**

```json
{
  "destination_name": "Free Tier S3",
  "destination_definition_id": "s3-definition-id",
  "destination_config": {
    "s3_bucket_name": "free-tier-bucket",
    "format": { "format_type": "CSV" }
  },
  "cron_expression": "0 0 12 * * ?",
  "non_breaking_changes_preference": "ignore",
  "tags": ["free-tier"]
}

```

**Enterprise tier - Optimized BigQuery sync:**

```json
{
  "destination_name": "Enterprise BigQuery",
  "destination_definition_id": "bigquery-definition-id",
  "destination_config": {
    "project_id": "enterprise-project",
    "dataset_id": "enterprise_data"
  },
  "cron_expression": "0 */4 * * * ?",
  "non_breaking_changes_preference": "propagate_fully",
  "sync_on_create": true,
  "tags": ["enterprise"]
}

```

### Testing vs production

Create separate templates for different environments:

```bash
# Development template - hourly syncs
{
  "destination_name": "Dev Database",
  "cron_expression": "0 0 * * * ?",
  "tags": ["development", "testing"]
}

# Production template - daily syncs
{
  "destination_name": "Prod Database",
  "cron_expression": "0 0 2 * * ?",
  "tags": ["production"]
}

```

### Compliance-based templates

Create templates for different compliance requirements:

```bash
# HIPAA-compliant template
{
  "destination_name": "HIPAA Compliant Warehouse",
  "destination_definition_id": "snowflake-definition-id",
  "destination_config": {
    "encryption": "enabled",
    "region": "us-west-2"
  },
  "tags": ["hipaa-compliant", "healthcare"]
}

# GDPR-compliant template
{
  "destination_name": "GDPR Compliant Warehouse",
  "destination_definition_id": "bigquery-definition-id",
  "destination_config": {
    "region": "europe-west1"
  },
  "tags": ["gdpr-compliant", "eu-region"]
}

```

## Related documentation

- [Template Tags](./tags.md) - Organize and filter templates with tags
- [Source Templates](./source-templates.md) - Configure which sources are available
- [Authentication](./authentication.md) - Generate tokens with template filtering
- [Configuring Sources](./configuring-sources.md) - How sources and connections work together
