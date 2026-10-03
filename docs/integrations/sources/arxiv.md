# arXiv

## Overview

The arXiv source connector syncs academic paper metadata from the public [arXiv API](https://arxiv.org/help/api/index). The API does not require authentication and returns Atom/XML feeds for user-provided search queries.

## Features

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental - Append Sync     | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Prerequisites

No API key or credentials are required. You only need an arXiv `search_query`, such as `cat:cs.AI`, `all:electron`, or `au:del_maestro`.

## Setup

Configure the source with:

| Field                  | Type    | Required | Description |
| :--------------------- | :------ | :------- | :---------- |
| `search_query`         | string  | Yes      | arXiv API search query. |
| `start_date`           | string  | No       | ISO-8601 timestamp. Records with `updated` at or before this value are skipped. |
| `max_results_per_page` | integer | No       | Number of records requested per page. Defaults to 100. Maximum is 2000. |

## Supported Streams

| Stream       | Sync mode                 | Primary key | Cursor    |
| :----------- | :------------------------ | :---------- | :-------- |
| `papers`     | Full refresh, Incremental | `id`        | `updated` |
| `categories` | Full refresh              | `id`        | None      |

## Field Reference

### `papers`

| Field         | Type     | Description |
| :------------ | :------- | :---------- |
| `id`          | string   | arXiv paper identifier, including version when provided by the API. |
| `title`       | string   | Paper title. |
| `authors`     | array    | Paper author names. |
| `abstract`    | string   | Paper abstract. |
| `published`   | date-time | Initial publication timestamp. |
| `updated`     | date-time | Most recent update timestamp. |
| `categories`  | array    | arXiv subject category identifiers. |
| `doi`         | string   | Digital Object Identifier when present. |
| `journal_ref` | string   | Journal reference when present. |
| `links`       | array    | Atom links for the paper, including abstract and PDF links when present. |

### `categories`

| Field   | Type   | Description |
| :------ | :----- | :---------- |
| `id`    | string | arXiv subject category identifier. |
| `name`  | string | Human-readable arXiv subject category name. |
| `group` | string | Top-level category group. |

## Rate Limiting & Performance Considerations

The arXiv API asks clients to make no more than about three requests per second. This connector throttles requests to that cadence and retries HTTP 429 responses with backoff.

## Data Type Mapping

The connector parses arXiv Atom/XML into Airbyte JSON records. Datetime fields are emitted as ISO-8601 strings with the `date-time` format.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject |
| :------ | :--------- | :----------- | :------ |
| 0.1.0   | 2026-05-26 | [PR #]       | Initial release of arXiv source connector. |

</details>
