# Exa full reference

This is the full reference documentation for the Exa agent connector.

## Supported entities and actions

The Exa connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Search Results | [List](#search-results-list) |
| Contents | [List](#contents-list) |
| Similar Results | [List](#similar-results-list) |

## Search Results

### Search Results List

Perform a search with an Exa prompt-engineered query and retrieve a list
of relevant results. Optionally request contents (text, highlights, summary)
inline with the search results. Supports filtering by domain, date, category,
and number of results.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "exa",
  "entity": "search_results",
  "action": "list",
  "params": {
    "query": "<str>"
  }
}'
```

#### Python SDK

```python
await exa.search_results.list(
    query="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "search_results",
    "action": "list",
    "params": {
        "query": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | The search query string. |
| `type` | `"auto" \| "instant" \| "fast" \| "deep-lite" \| "deep" \| "deep-reasoning"` | No | The type of search. auto intelligently selects the best mode, instant provides lowest latency, fast uses lower-latency models, deep-lite provides lightweight synthesis, deep performs in-depth research with synthesis, and deep-reasoning adds more reasoning for complex searches. |
| `category` | `"company" \| "research paper" \| "news" \| "personal site" \| "financial report" \| "people"` | No | A data category to focus on for improved result quality. |
| `numResults` | `integer` | No | Number of results to return (max 100). |
| `includeDomains` | `array<string>` | No | List of domains to include. If specified, results will only come from these domains. |
| `excludeDomains` | `array<string>` | No | List of domains to exclude. If specified, no results will be returned from these domains. |
| `startPublishedDate` | `string` | No | Only return links published after this date. ISO 8601 format. |
| `endPublishedDate` | `string` | No | Only return links published before this date. ISO 8601 format. |
| `startCrawlDate` | `string` | No | Only return links crawled by Exa after this date. ISO 8601 format. |
| `endCrawlDate` | `string` | No | Only return links crawled by Exa before this date. ISO 8601 format. |
| `contents` | `object` | No | Options for requesting page contents inline with search results. |
| `contents.text` | `boolean \| object` | No | Text extraction options. Pass true for defaults or an object for advanced options. |
| `contents.highlights` | `boolean \| object` | No | Highlight extraction options. Pass true for defaults or an object for advanced options. |
| `contents.summary` | `object` | No | Summary generation options. |
| `contents.summary.query` | `string` | No | Custom query for the LLM-generated summary. |
| `moderation` | `boolean` | No | Enable content moderation to filter unsafe content. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `title` | `string` |  |
| `url` | `string` |  |
| `id` | `string` |  |
| `publishedDate` | `string` |  |
| `author` | `string \| null` |  |
| `image` | `string` |  |
| `favicon` | `string` |  |
| `text` | `string` |  |
| `highlights` | `array<string>` |  |
| `highlightScores` | `array<number>` |  |
| `summary` | `string` |  |
| `score` | `number` |  |


</details>

## Contents

### Contents List

Get the full page contents, summaries, and metadata for a list of URLs.
Returns instant results from Exa's cache, with automatic live crawling
as fallback for uncached pages. Use this to retrieve text, highlights,
and summaries for specific URLs.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "exa",
  "entity": "contents",
  "action": "list",
  "params": {
    "urls": []
  }
}'
```

#### Python SDK

```python
await exa.contents.list(
    urls=[]
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contents",
    "action": "list",
    "params": {
        "urls": []
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `urls` | `array<string>` | Yes | Array of URLs to retrieve contents for. |
| `text` | `boolean \| object` | No | Text extraction options. Pass true for defaults or an object for advanced options. |
| `highlights` | `boolean \| object` | No | Highlight extraction options. Pass true for defaults or an object for advanced options. |
| `summary` | `object` | No | Summary generation options. |
| `summary.query` | `string` | No | Custom query for the LLM-generated summary. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `title` | `string` |  |
| `url` | `string` |  |
| `id` | `string` |  |
| `publishedDate` | `string` |  |
| `author` | `string \| null` |  |
| `image` | `string` |  |
| `favicon` | `string` |  |
| `text` | `string` |  |
| `highlights` | `array<string>` |  |
| `highlightScores` | `array<number>` |  |
| `summary` | `string` |  |
| `score` | `number` |  |


</details>

## Similar Results

### Similar Results List

Find web pages similar to a given URL. Uses Exa's embeddings to find
semantically similar content. Supports filtering by domains and dates.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "exa",
  "entity": "similar_results",
  "action": "list",
  "params": {
    "url": "<str>"
  }
}'
```

#### Python SDK

```python
await exa.similar_results.list(
    url="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "similar_results",
    "action": "list",
    "params": {
        "url": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `url` | `string` | Yes | The URL to find similar pages for. |
| `numResults` | `integer` | No | Number of similar results to return (max 100). |
| `includeDomains` | `array<string>` | No | List of domains to include. If specified, results will only come from these domains. |
| `excludeDomains` | `array<string>` | No | List of domains to exclude. If specified, no results will be returned from these domains. |
| `startPublishedDate` | `string` | No | Only return links published after this date. ISO 8601 format. |
| `endPublishedDate` | `string` | No | Only return links published before this date. ISO 8601 format. |
| `startCrawlDate` | `string` | No | Only return links crawled by Exa after this date. ISO 8601 format. |
| `endCrawlDate` | `string` | No | Only return links crawled by Exa before this date. ISO 8601 format. |
| `contents` | `object` | No | Options for requesting page contents inline with similar page results. |
| `contents.text` | `boolean \| object` | No | Text extraction options. Pass true for defaults or an object for advanced options. |
| `contents.highlights` | `boolean \| object` | No | Highlight extraction options. Pass true for defaults or an object for advanced options. |
| `contents.summary` | `object` | No | Summary generation options. |
| `contents.summary.query` | `string` | No | Custom query for the LLM-generated summary. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `title` | `string` |  |
| `url` | `string` |  |
| `id` | `string` |  |
| `publishedDate` | `string` |  |
| `author` | `string \| null` |  |
| `image` | `string` |  |
| `favicon` | `string` |  |
| `text` | `string` |  |
| `highlights` | `array<string>` |  |
| `highlightScores` | `array<number>` |  |
| `summary` | `string` |  |
| `score` | `number` |  |


</details>

