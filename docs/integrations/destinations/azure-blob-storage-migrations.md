# Azure Blob Storage Migration Guide

## Upgrading to 1.0.0

### Airbyte field names

This version updates the Azure Blob Storage destination connector to use the [DV2 Airbyte metadata field names](/docs/understanding-airbyte/airbyte-metadata-fields.md). You should update any downstream consumers to reference the new field names. Specifically, these two fields have been renamed:

| Old field name        | New field name             |
| --------------------- | -------------------------- |
| `_airbyte_ab_id`      | `_airbyte_raw_id`          |
| `_airbyte_emitted_at` | `_airbyte_extracted_at`    |

### Blob paths

The destination connector now includes the stream namespace in the blob path. For example, if you are syncing a stream `public.users`, the connector will now put blobs into `<container_name>/public/users/**` - previously it was putting blobs into `<container_name>/users/**`.

### Split files

The "Azure Blob Storage file spill size" option has been renamed to "file split size". It also now takes effect on CSV files, which previously ignored the option entirely.

### file extension

This option has been removed. We will now always be adding a file extensions based on the chosen file format.

### Required permissions

The connector no longer attempts to create Azure blob storage containers, and therefore you no longer need to provide the `Microsoft.Storage/storageAccounts/blobServices/containers/write` permission.
