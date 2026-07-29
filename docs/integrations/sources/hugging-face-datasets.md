# Hugging Face Datasets

<HideInUI>

This page contains the setup guide and reference information for the [Hugging Face Datasets](https://docs.airbyte.com/integrations/sources/hugging-face-datasets) source connector.

</HideInUI>

## Overview

This source connector allows you to read datasets from [Hugging Face Hub](https://huggingface.co/datasets) using the [datasets](https://huggingface.co/docs/datasets) library. You can access public and private datasets, configure subsets (configs), and specify splits (train, test, validation).

## Prerequisites

- A Hugging Face account
- Access to the dataset you want to read (public datasets require no authentication, private datasets require a token with appropriate permissions)

## Setup Guide

<!-- env:cloud -->

### Set up Hugging Face Datasets in Airbyte Cloud

<!-- /env:cloud -->

### Set up the Hugging Face Datasets connector in Airbyte

<!-- env:cloud -->

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Hugging Face Datasets from the Source type dropdown.
4. Enter a name for the Hugging Face Datasets connector.
<!-- /env:cloud -->

<!-- env:oss -->

#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Hugging Face Datasets from the Source type dropdown.
4. Enter a name for the Hugging Face Datasets connector.
<!-- /env:oss -->

### Step 1: Configure connection settings

1. For **Dataset Name**, enter the _name_ of the dataset on Hugging Face (e.g., `glue`, `squad`, `imdb`).
2. For **Dataset Subsets/Configs** (Optional), enter a _list of configs_ to import. If empty, all configs will be imported.
3. For **Dataset Splits** (Optional), enter a _list of splits_ to import (e.g., `train`, `test`, `validation`). If empty, all splits will be imported.
4. For **Hugging Face Token** (Optional), enter your _token_ for private datasets.
5. For **Streaming Mode** (Optional), set to _true_ to stream datasets on-the-fly without caching to disk. Useful for large datasets where you don't want to fill disk space. Note: streaming mode is slower and less reliable than non-streaming mode.

### Step 2: Select the streams and configure sync modes

1. Click **Set up source** and wait for the tests to complete.

## Supported sync modes

The Hugging Face Datasets source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| Replicate Incremental Deletes | No |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.1.0 | 2026-07-29 | [81357](https://github.com/airbytehq/airbyte/pull/81357) | Initial release |

</details>

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.
