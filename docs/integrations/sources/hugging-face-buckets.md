# Hugging Face Buckets

<HideInUI>

This page contains the setup guide and reference information for the [Hugging Face Buckets](https://docs.airbyte.com/integrations/sources/hugging-face-buckets) source connector.

</HideInUI>

## Overview

This source connector allows you to read data files (Parquet, CSV, JSON, JSONL) from Hugging Face Buckets (file storage on Hugging Face Hub). Hugging Face Buckets provide persistent object storage accessible via the `hf://` protocol.

## Prerequisites

- A Hugging Face account with read access to the bucket
- The bucket path in the format: `hf://buckets/{username}/{bucket}/{path}/`
- Hugging Face token (required for authentication, especially for private buckets)

## Setup Guide

<!-- env:cloud -->

### Set up Hugging Face Buckets in Airbyte Cloud

<!-- /env:cloud -->

### Set up the Hugging Face Buckets connector in Airbyte

<!-- env:cloud -->

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Hugging Face Buckets from the Source type dropdown.
4. Enter a name for the Hugging Face Buckets connector.
<!-- /env:cloud -->

<!-- env:oss -->

#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Hugging Face Buckets from the Source type dropdown.
4. Enter a name for the Hugging Face Buckets connector.
<!-- /env:oss -->

### Step 1: Configure connection settings

1. For **Bucket Path**, enter the _path_ to the Hugging Face Bucket. Format: `hf://buckets/{username}/{bucket}/{path}/`
2. For **File Format**, select the _format_ of files in the bucket (Parquet, CSV, JSON, or JSONL).
3. For **Hugging Face Token**, enter your _token_ for authentication. Required for private buckets.

### Step 2: Select the streams and configure sync modes

1. Click **Set up source** and wait for the tests to complete.

## Supported sync modes

The Hugging Face Buckets source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| Replicate Incremental Deletes | No |

## Supported file formats

| Format | Supported? |
| --- | --- |
| Parquet | Yes |
| CSV | Yes |
| JSON | Yes |
| JSONL | Yes |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.1.0 | 2026-07-29 | [81357](https://github.com/airbytehq/airbyte/pull/81357) | Initial release |

</details>

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.
