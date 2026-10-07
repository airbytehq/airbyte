# Firecrawl

## Overview

This connector pulls web content from [Firecrawl](https://www.firecrawl.dev/?utm_source=airbyte&utm_medium=integration), the context API to search, scrape, and interact with the web at scale. It returns pages as clean Markdown, ready for warehouses, vector stores, and RAG pipelines.

### Streams

- `scrape`: one record per URL in `urls`, with the page content as Markdown plus page metadata. Uses the [scrape](https://www.firecrawl.dev/scrape?utm_source=airbyte&utm_medium=integration) endpoint.
- `search`: one record per web search result for each query in `search_queries`, with the result page's Markdown included. Uses the [search](https://www.firecrawl.dev/search?utm_source=airbyte&utm_medium=integration) endpoint. If `search_queries` is empty, this stream returns no records.

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| scrape | source_url | No pagination | ✅ | ❌ |
| search | query, url | No pagination | ✅ | ❌ |

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | Yes        |
| Namespaces        | No         |

## Getting started

### Prerequisites

- A Firecrawl API key. Create one at [firecrawl.dev/app/api-keys](https://www.firecrawl.dev/app/api-keys?utm_source=airbyte&utm_medium=integration). The free plan includes 1,000 credits a month.

### Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | Your Firecrawl API key. |  |
| `urls` | `array` | Pages to scrape into Markdown. |  |
| `search_queries` | `array` | Web searches to run. Each result includes the page content as Markdown. |  |
| `search_limit` | `integer` | Maximum number of results for each search query (1 to 20). | 5 |
| `only_main_content` | `boolean` | Return only the main content of each scraped page. | true |

## Rate limits and credits

Each page returned by `scrape` costs 1 credit. Each `search` request costs 2 credits per 10 results, plus 1 credit for every result page that is scraped. The connection check scrapes the first URL, so it uses 1 credit. When the monthly credits run out, the API returns a 402 and the sync fails with "Firecrawl credits exhausted". Requests that hit a rate limit (429), time out (408) or fail with a 5xx are retried, waiting for the `Retry-After` header when present and backing off otherwise. Each result scraped by `search` costs 1 credit, and PDF pages cost 1 more credit per page, so a query with a high `search_limit` costs more.

## Known behaviour

- An invalid URL in `urls` (for example one without a domain) or a request the API rejects fails the sync. Fix the input and run it again.
- A page that answers with an error such as 404 is still returned as a record. Check `metadata.statusCode` to filter these downstream.
- Firecrawl may serve a recently cached copy of a page.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject         |
|---------|------------|--------------|-----------------|
| 0.0.1   | 2026-10-07 | [PR_NUMBER](https://github.com/airbytehq/airbyte/pull/PR_NUMBER) | Initial release |

</details>
