# Connection Templates

The first thing to configure when using Airbyte Embedded is a connection template. Connections define where your customer data will be moved, as when as the sync frequency.

When one of your user configures a Source, we'll automatically create a connection to your destination according to the templates your configured.

You'll need the following to create a connection template:
- Your organization ID
- The destination definition ID
- The destination configuration
- The destination name: We'll automatically create a destination with the given name in your user's workspaces
- (optional) A cron expression describing when to run syncs. The cron expression must follow the Quartz syntax. You can use [freeformatter.com](https://www.freeformatter.com/cron-expression-generator-quartz.html) to help validate the expression

:::info
S3 is the only destination we currently support for Airbyte Embedded.
:::

Here is an example request for creating a connection template:
```
curl --request POST 'https://api.airbyte.ai/api/v1/integrations/connections/' \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer <bearer_token>" -H 'Content-Type: application/json' \
  --data-raw '{
    "destination_name": "s3", 
    "cron_expression": "0 15 2 * * *",
    "organization_id": "<organization_id>",
    "destination_actor_definition_id": "4816b78f-1489-44c1-9060-4b19d5fa9362",
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
  }'
```