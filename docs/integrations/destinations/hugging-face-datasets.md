# Hugging Face Datasets

<HideInUI>

This page contains the setup guide and reference information for the [Hugging Face Datasets](https://docs.airbyte.com/integrations/destinations/hugging-face-datasets) destination connector.

</HideInUI>

## Overview

This destination connector allows you to write data to [Hugging Face Datasets](https://huggingface.co/datasets) using the [datasets](https://huggingface.co/docs/datasets) library. You can push data to your own datasets or datasets owned by organizations you have write access to.

## Prerequisites

- A Hugging Face account
- Write access to a dataset (you own the dataset or have been granted write access)
- The dataset name in the format: `{username_or_organization}/{dataset_name}`
- Hugging Face token (required for authentication)

## Setup Guide

<!-- env:cloud -->

### Set up Hugging Face Datasets in Airbyte Cloud

<!-- /env:cloud -->

### Set up the Hugging Face Datasets connector in Airbyte

<!-- env:cloud -->

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Destinations and then click + New destination.
3. On the Set up the destination page, select Hugging Face Datasets from the Destination type dropdown.
4. Enter a name for the Hugging Face Datasets connector.
<!-- /env:cloud -->

<!-- env:oss -->

#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click Destinations and then click + New destination.
3. On the Set up the destination page, select Hugging Face Datasets from the Destination type dropdown.
4. Enter a name for the Hugging Face Datasets connector.
<!-- /env:oss -->

### Step 1: Configure connection settings

1. For **Dataset Name**, enter the _name_ of the dataset (e.g., `{username}/{dataset_name}`).
2. For **Hugging Face Token**, enter your _token_ for authentication. Required for private datasets.

### Step 2: Select the streams and configure sync modes

1. Click **Set up destination** and wait for the tests to complete.

## Supported sync modes

The Hugging Face Datasets destination connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

| Feature | Supported? |
| --- | --- |
| Full Refresh - Overwrite | Yes |
| Full Refresh - Append | Yes |
| Incremental Sync - Append | Yes |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.1.0 | 2026-07-29 | [81357](https://github.com/airbytehq/airbyte/pull/81357) | Initial release |

</details>

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.
