import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Outreach Migration Guide

## Upgrading to 2.0.0

Version 2.0.0 corrects the types of five fields to match what the Outreach API returns. Each was declared a string, but the API returns an array of strings, as the [Outreach OpenAPI spec](https://api.outreach.io/api/v2/schema/openapi.json) documents.

| Stream | Fields | Old type | New type |
| :--- | :--- | :--- | :--- |
| `snippets` | `tags` | string | array of strings |
| `templates` | `tags`, `toRecipients`, `ccRecipients`, `bccRecipients` | string | array of strings |

The values the connector reads don't change. Other streams are unaffected.

### Impact on destination column types

- Destinations that type their columns, such as data warehouses, change each of these columns from a string type to a JSON or array type. Rows synced before the upgrade hold the array as serialized text, for example `["prospecting","q4"]`, so until the streams are refreshed one column holds text for old rows and a JSON array for new rows.
- Avro and Parquet files change each field from a nullable `string` to a nullable list of `string`. Files written before the upgrade keep the `string` field, so readers that merge schemas across files see two types for the same field.
- Destinations that store each record as JSON see the same values with the new type in the stream schema.

### Steps

1. Upgrade the connector to 2.0.0.
2. In each connection that syncs `snippets` or `templates`, open **Schema**, select **Refresh source schema**, review and save.
3. Refresh the `snippets` and `templates` streams, removing their existing records, so that every row is written with the new type.

<MigrationGuide />

## Upgrading to 1.0.0
The verison migrates the Outreach connector to the low-code framework for greater maintainability. 
Important update: The sequence_steps stream schema from API has a breaking change to the creator field to an array containing integers instead of strings.
Destination should adapt to this change if needed.
You may need to refresh the connection schema (with the reset), and run a sync.