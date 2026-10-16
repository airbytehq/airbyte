# SpecStream

[SpecStream](https://specstream.ai) is a live web data engine. You ask in plain words for companies, local businesses, people at companies, job posts, SEC filings, tenders or grants, and it returns every match as structured data, each value with the page it was read from. Each request becomes a list in your SpecStream workspace.

This source syncs the lists your API key can open and their records, including lists from scheduled requests, lists you imported and lists you combined. It only reads: it never starts a request or spends from your SpecStream balance.

## Prerequisites

- A SpecStream account. New accounts get $10 of work free, no card.
- A SpecStream API key. In SpecStream, open **Agents & API** and create a key. The source only reads, so the key can have a spending limit of $0.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API key. A SpecStream API key from Agents & API. |  |
| `start_date` | `string` | Start date. Sync only lists created on or after this date, for example 2026-01-01T00:00:00Z. Leave empty to sync every list. |  |

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| lists | id | DefaultPaginator | ✅ |  ✅  |
| records | list_id.record_id | No pagination | ✅ |  ✅  |

### lists

One row per list: its ID, name, kind (`find`, `snapshot`, `import` or `combined`), whether you imported it, when it was created and how many rows it has. Incremental syncs use `created_at`.

### records

One row per record, read per list:

- `list_id`, `record_id` and `list_created_at`.
- `entity_id`: stable across lists for the same company, place, person or posting.
- `cells`: one cell per column with `label`, `display`, `value` and `provenance`, which holds the page the value came from (`source_url`) and when it was read (`observed_at`). A value SpecStream couldn't read has an `absence` and no value.
- `provided`: the columns you provided, for rows of a list you imported.
- `field_values` and `also_in`: each column's values and the lists a row also appears in, for rows of a combined list.

Incremental syncs read only the lists created since the last sync. A SpecStream schedule delivers new and changed records as a new list, so they arrive on the next sync.

## Rate limits

The source retries rate limits (`429`) and server errors with exponential backoff, and waits as long as a `Retry-After` header asks.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-10-16 | | Initial release by [@Specstreamai](https://github.com/Specstreamai) |

</details>
