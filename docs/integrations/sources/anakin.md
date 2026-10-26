# Anakin

This page contains the setup guide and reference information for the [Anakin](https://anakin.io) source connector.

Anakin is a web data API. This connector runs Anakin web searches and page scrapes on every sync and writes the results to your destination, and it replicates the change monitors you set up in Anakin together with the changes they detect.

## Prerequisites

- An Anakin account. The free plan includes 300 credits and needs no credit card.
- An Anakin API key

## Setup guide

### Step 1: Create an API key

1. Sign up or log in at [anakin.io](https://anakin.io/signup).
2. Open the [dashboard](https://anakin.io/dashboard) and create an API key. Keys start with `ask_`.

### Step 2: Set up the Anakin connector in Airbyte

1. In Airbyte, go to **Sources** and click **New source**.
2. Search for and select **Anakin**.
3. Enter your **API Key**.
4. Optional: enter **Search Queries** to fill the `search_results` stream, and **URLs to Scrape** to fill the `scraped_pages` stream. Leave either list empty to skip that stream.
5. Click **Set up source**. Airbyte checks the key by listing your monitors, which costs no credits.

## Supported sync modes

| Stream            | Full Refresh | Incremental |
| :---------------- | :----------- | :---------- |
| `monitors`        | Yes          | No          |
| `monitor_changes` | Yes          | Yes         |
| `search_results`  | Yes          | No          |
| `scraped_pages`   | Yes          | No          |

## Supported streams

| Stream            | Endpoint                        | Primary key    | Description                                                                                                                        |
| :---------------- | :------------------------------ | :------------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| `monitors`        | `GET /v1/monitors`              | `id`           | The page, site and Wire monitors in your Anakin account and their settings.                                                        |
| `monitor_changes` | `GET /v1/monitors/{id}/changes` | `id`           | Changes detected by each monitor, with a summary and a structured diff. Incremental on `changedAt`.                                |
| `search_results`  | `POST /v1/search`               | `query`, `url` | Web search results (URL, title, snippet, dates) for each configured query. Each record carries the `query` and a `synced_at` time. |
| `scraped_pages`   | `POST /v1/url-scraper/scrape`   | `id`           | The content of each configured URL as Markdown, with optional HTML and AI-extracted JSON.                                          |

### Notes on streams

- `monitor_changes`: the API returns up to the 200 most recent changes per monitor. Sync more often than a monitor produces 200 changes to keep the full history. Incremental syncs re-read the most recent change of each monitor, so use **Incremental | Append + Deduped**.
- `search_results` and `scraped_pages` call Anakin fresh on every sync, so each sync records what the web returned at that time. Use **Full Refresh | Append** to keep a history across syncs, or **Full Refresh | Overwrite** to keep only the latest results.
- `scraped_pages`: a page that Anakin cannot scrape produces a record with `status` set to `failed` and the reason in `error`, and the sync continues. The `html` and `cleanedHtml` fields are empty unless you turn on **Include HTML**.

## Credits

Every sync of `search_results` and `scraped_pages` uses Anakin credits:

- Search: 3 credits per query
- Scrape: 1 credit per URL, plus 2 credits per URL with **Extract Structured JSON** turned on

`monitors` and `monitor_changes` use no credits. Monitors themselves use credits on their own schedule in Anakin, whether or not you sync them. See [Anakin pricing](https://anakin.io/docs/documentation/pricing) for current prices.

## Performance considerations

Anakin allows 60 search requests and 20 inline scrape requests per minute per user. The connector stays under these limits and retries on HTTP 429 and 5xx responses with exponential backoff. An inline scrape can take up to about 90 seconds. If it does not finish in that time, Anakin returns HTTP 202 and the connector retries the request.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                         | Subject         |
| :------ | :--------- | :--------------------------------------------------- | :-------------- |
| 0.1.0   | 2026-10-26 | [89757](https://github.com/airbytehq/airbyte/pull/89757) | Initial release |

</details>
