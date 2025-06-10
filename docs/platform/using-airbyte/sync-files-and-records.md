---
products: all
---

import ConfigureMetadata from './_configure_file_metadata.mdx';

# Sync files and records together

Airbyte supports moving files and records together in the same connection. Some sources are a mix of structured data and unstructured attachments. The combination of structured and unstructured data drives more robust knowledge systems with more context, something critical to successful AI systems.

## How it works

The process to move files and records depends on whether your data source is structured with unstructured attachments, or is unstructured/file-based.

- **Structured sources with unstructured attachments**: Files are a stream. When you set up your connection, you select and deselect this stream as you normally would. This stream includes structured metadata describing those files. The columns you choose in the stream are the metadata Airbyte syncs to your destination.

- **Unstructured/file-based sources**: Files and records aren't synced together and you must choose to copy files. When you set up the source, choose the **Copy raw files** delivery method. Airbyte syncs your raw files and includes structured metadata describing those files. When you set up your connection, the columns you choose in the stream represent the metadata Airbyte adds to that file.

## Which connectors support file transfers

Connectors that support file transfers have `supportsFileTransfer: true` in their metadata. Airbyte's UI doesn't currently make this obvious, but the following sources support file transfers.

- Zendesk Support
- S3
- Sharepoint
- Google Drive
- SFTP Bulk

The following destination supports file transfers.

- S3

## Unstructured/file-based sources

For file-based sources, use the [copy raw files](delivery-methods#copy-raw-files) delivery method to move files with structured metadata.

## Structured/mixed sources

In the case of structured data sources with unstructured attachments, you sync your files the same way you sync your data.

1. Add your [source](getting-started/add-a-source), if you haven't already.

2. Add your [destination](getting-started/add-a-destination), if you haven't already. While configuring the destination connector, choose the file format of your log by setting the **Output Format** option. For help, see [Change the metadata format](#metadata-format) below.

3. Add your [connection](getting-started/set-up-a-connection), if you haven't already. In the schema, enable the stream(s) containing the files you want to sync, and select which fields you want in your metadata. For help, see [Change what's in the metadata](#metadata-content), below.

<ConfigureMetadata />
