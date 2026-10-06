# Peec AI

[Peec AI](https://peec.ai) tracks how brands appear in answers from AI assistants —
ChatGPT, Google AI Overview, Perplexity and others. This connector reads the
[Peec AI Customer API](https://docs.peec.ai/api/introduction) and brings that AI search
visibility data into your warehouse.

## Prerequisites

An API key, created at [app.peec.ai/api-keys](https://app.peec.ai/api-keys).

Peec issues two kinds of key and they behave differently:

- **Project-scoped** (prefix `skp-`, the usual case) — resolves its own project. Leave
  `Project ID` empty.
- **Company-scoped** — has no implicit project, so `Project ID` is required.

## Setup guide

| Field | Required | Description |
| --- | --- | --- |
| `API Key` | yes | Your Peec AI API key. Sent as the `x-api-key` header. |
| `Start Date` | yes | Earliest month to sync, as `YYYY-MM-DD`. The day is ignored — the sync always starts on the 1st of that month. |
| `Project ID` | no | Only for a company-scoped key. Leave empty for a project-scoped key. |

## Supported sync modes

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Namespaces | No |

## Supported streams

| Stream | Grain | Sync mode | Cursor |
| --- | --- | --- | --- |
| `brands` | one row per tracked brand | Full refresh | — |
| `model_channels` | one row per model/channel | Full refresh | — |
| `brands_report` | brand × model channel × month | Incremental | `month` |
| `domains_report` | domain × model channel × month | Incremental | `month` |
| `urls_report` | url × model channel × month | Incremental | `month` |

### Where the common metrics live

- **Visibility score** — `visibility_count / visibility_total` in `brands_report`. The
  API returns numerator and denominator separately rather than a ratio, which keeps the
  percentage aggregatable across periods and channels.
- **Source retrievals** — `retrievals` / `retrieval_count` in `domains_report` (per
  cited domain) and `urls_report` (per cited URL).
- `brands` carries `is_own`, marking which tracked brand is your own rather than a
  competitor.

## Important modelling notes

### Months are restated, so the same month arrives more than once

Peec keeps revising a month while chats are still landing in it. The connector re-reads
the previous month on every sync (`lookback_window: P1M`), so a given month will appear
in several extracts.

Downstream, keep the rows from the **newest extract** for a given month rather than
deduplicating on a key across extracts — the latter mixes restated and stale numbers for
the same period.

### `urls_report` has no primary key, deliberately

Peec can return two rows sharing the same `(month, url, model_channel_id)`. Measured on
one month of real data: 4 such pairs in 37,844 rows, carrying 16 of 203,774 retrievals.
Three pairs are identical on every exposed dimension and differ only in their metrics;
the fourth also differs in `classification`. No subset of the returned fields separates
all four.

**Sum these rows, do not deduplicate them.** A dedup on a synthetic key silently drops
the second row of each pair. `domains_report` and `brands_report` are unique on their
declared keys.

## Performance considerations

The API allows 200 requests per minute per project and returns the seconds remaining in
the window via `X-RateLimit-Reset`; the connector waits exactly that long on a 429.

Report requests page with `limit`/`offset`, with `limit` capped at 10000.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :------ | :--------- | :----------------------------------------------------- | :---------------------- |
| 0.1.0 | 2026-09-17 | [86421](https://github.com/airbytehq/airbyte/pull/86421) | Initial release |

</details>
