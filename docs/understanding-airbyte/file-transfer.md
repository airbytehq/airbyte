# Airbyte File Sync

Airbyte File Sync is a capability that allows you to move unstructured data, non-text data, and compressed files between sources and destinations without parsing their contents. This document explains how File Sync works, which connectors support it, and how to use it.

## Overview

Traditional data integration in Airbyte involves extracting structured data as individual records, which are then processed and loaded into a destination. However, many use cases require transferring raw files without parsing their contents:

- Moving binary files (images, videos, PDFs)
- Transferring compressed files (ZIP, GZIP)
- Migrating unstructured text data
- Preserving file formats for specialized processing

File Sync addresses these needs by copying files exactly as they appear in the source to the destination, preserving their original format and content.

## How File Sync Works

When using File Sync:

1. The source connector identifies files to be transferred
2. Instead of parsing file contents into records, the file is transferred as-is
3. The destination connector writes the raw file to the target location
4. File metadata (name, path, size, etc.) is preserved

This differs from standard Airbyte syncs where files would be parsed into individual records.

## Supported Connectors

File Sync is currently supported by the following connectors:

### Sources
- [SFTP Bulk](../integrations/sources/sftp-bulk.md)
- [Microsoft SharePoint](../integrations/sources/microsoft-sharepoint.md)
- [S3](../integrations/sources/s3.md)

### Destinations
- [S3](../integrations/destinations/s3.md)
- [Deepset](../integrations/destinations/deepset.md)

## Using File Sync

To use File Sync:

1. Configure a connection using a source and destination that both support File Sync
2. The File Sync mode will be automatically enabled when compatible connectors are used
3. Files will be transferred without parsing their contents

### Configuration Example

When configuring a connection between SFTP Bulk (source) and S3 (destination):

1. Set up the SFTP Bulk source with your server credentials and file paths
2. Configure the S3 destination with your bucket information
3. The connection will automatically use File Sync mode

## Limitations

- Both the source and destination must support File Sync
- File Sync is designed for raw file movement, not for transforming data
- Maximum file size limits may apply depending on the connectors

## Technical Implementation

File Sync is implemented in the Airbyte CDK (Connector Development Kit) version 0.48.0 and above. Connectors that support this feature have the `supportsFileTransfer: true` flag in their metadata.yaml file.

## Future Enhancements

The File Sync capability is being expanded to support more source and destination connectors. Check the documentation of specific connectors to see if they support File Sync.
