# Gutendex

## Overview

The Gutendex source can sync data from the [Gutendex API](https://gutendex.com/)

## Requirements

Gutendex requires no access token/API key to make requests.

## Output schema

Lists of book information in the Project Gutenberg database are queried using the API at /books (e.g. gutendex.com/books). Book data will be returned in the format:-

    {
        "count": <number>,
        "next": <string or null>,
        "previous": <string or null>,
        "results": <array of Books>
    }

where `results` is an array of 0-32 book objects, next and previous are URLs to the next and previous pages of results, and count in the total number of books for the query on all pages combined.

By default, books are ordered by popularity, determined by their numbers of downloads from Project Gutenberg.

The source is capable of syncing the results stream.

## Setup guide

## Step 1: Set up the Gutendex connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, select **Gutendex** from the Source type dropdown.
4. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source (Gutendex).
3. Click **Set up source**.

## Supported sync modes

The Gutendex source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| Namespaces        | No         |

## Performance considerations

There is no published rate limit. However, since this data updates infrequently, it is recommended to set the update cadence to 24hr or higher.

## Changelog

| Version | Date       | Pull Request | Subject              |
| :------ | :--------- | :----------- | :------------------- |
| 0.1.0   | 2022-10-17 |              | New Source: Gutendex |
