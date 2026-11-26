# Hugging Face Buckets

## Overview

This destination writes data files (Parquet, JSONL) to Hugging Face Buckets (file storage on Hugging Face Hub). Hugging Face Buckets provide persistent object storage for datasets and models, accessible via the `hf://` protocol.

## Prerequisites

- A Hugging Face account with write access to a bucket
- The bucket path in the format: `hf://buckets/{username}/{bucket}/{path}/`
- Optional: Hugging Face token (required for private buckets)

## Setup Guide

### Set up Hugging Face Buckets in Airbyte

<!-- env:cloud -->

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Destinations and then click + New destination.
3. On the Set up the destination page, select Hugging Face Buckets from the Destination type dropdown.
4. Enter a name for the Hugging Face Buckets connector.
<!-- /env:cloud -->

<!-- env:oss -->

#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click Destinations and then click + New destination.
3. On the Set up the destination page, select Hugging Face Buckets from the Destination type dropdown.
4. Enter a name for the Hugging Face Buckets connector.
<!-- /env:oss -->

### Step 1: Configure connection settings

1. For **Destination Path**, enter the _path_ to the Hugging Face Bucket where data will be written. Format: `hf://buckets/{username}/{bucket}/{path}/`
2. For **File Format**, select the _format_ to write (Parquet or JSONL).
3. For **Hugging Face Token**, enter your _token_ for authentication. This is required to write to a bucket.

### Step 2: Complete the setup

1. Click **Set up destination** and wait for the tests to complete.

## Supported sync modes

The Hugging Face Buckets destination connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

| Sync mode | Supported? |
| --- | --- |
| Full Refresh - Overwrite | Yes |
| Full Refresh - Append | No |
| Incremental Sync - Append | No |

Each sync rewrites the files of the selected streams: a stream is written to a single `{stream}.parquet` or `{stream}.jsonl` file at the configured path. Append and incremental modes would replace the file with the records of the last sync, so they are not supported.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.1.0 | 2026-11-25 | [81357](https://github.com/airbytehq/airbyte/pull/81357) | Initial release |

</details>

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.
