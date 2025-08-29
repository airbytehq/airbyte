---
products: embedded
---

# Connection Templates


A *connection template* pre-defines the **Destination side** of every pipeline your customers spin up through the Embedded widget. It answers two questions up-front:

1. Where should the data land?  
2. How often should it sync?

When a customer finishes configuring a Source, Airbyte automatically creates the connection by combining their source settings with *your* template.


You'll need the following to create a connection template:
- Your organization ID
- The destination definition ID
- The destination configuration
- The destination name: We'll automatically create a destination with the given name in your user's workspaces
- (optional) A cron expression describing when to run syncs. The cron expression must follow the Quartz syntax. You can use [freeformatter.com](https://www.freeformatter.com/cron-expression-generator-quartz.html) to help validate the expression

:::info
Blob storage like ABS, GCS, and S3 are the only destinations we currently support for Airbyte Embedded.
:::

Here is an example request for creating a connection template:
```
curl --request POST 'https://api.airbyte.ai/api/v1/integrations/templates/connections' \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer <bearer_token>" -H 'Content-Type: application/json' \
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
    }
  "cron_expression": "string",
  "non_breaking_changes_preference": "ignore",
  "sync_on_create": true
}'
```

You can find the full connector specification in the [Connector Registry](https://connectors.airbyte.com/files/registries/v0/cloud_registry.json).

You can find [the reference docs for creating a connection template here](https://api.airbyte.ai/api/v1/docs#tag/Template-Connections/operation/create_integrations_templates_connections).
