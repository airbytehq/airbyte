# Lexio Rent

This source syncs data from [Lexio Rent](https://lexio.rent/logiciel-location-voiture), rental management software for car, van and two-wheeler rental companies, through the [Lexio Rent API v1](https://docs.lexio.rent). It loads the fleet, the catalogue (categories, options, excesses, deposits, mileage packages), customers, rentals and maintenance records, plus the rental change feed.

## Prerequisites

- A Lexio Rent organization on a plan that includes the API (Business plan).
- An API key. In Lexio, go to **Settings > Developer > API tokens** and create a token. Keys start with `lck_`. See [Authentication](https://docs.lexio.rent/authentification) for scopes: the connector only reads, so the `*.read` scopes are enough.

Lexio has no public sandbox. Test against a dedicated organization.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Lexio API key (starts with lck_), from Settings > Developer > API tokens. |  |
| `api_url` | `string` | API URL. Base URL of the Lexio Rent API v1. | `https://api.lexio.rent/api/external/v1` |

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| vehicles | id | CursorPagination | ✅ |  ❌  |
| categories | id | CursorPagination | ✅ |  ❌  |
| locations | id | CursorPagination | ✅ |  ❌  |
| options | id | CursorPagination | ✅ |  ❌  |
| deductibles | id | CursorPagination | ✅ |  ❌  |
| deposits | id | CursorPagination | ✅ |  ❌  |
| mileage_packages | id | CursorPagination | ✅ |  ❌  |
| customers | id | CursorPagination | ✅ |  ❌  |
| rentals | id | CursorPagination | ✅ |  ❌  |
| maintenance_records | id | CursorPagination | ✅ |  ❌  |
| events | id | CursorPagination | ✅ |  ✅  |

`vehicles` excludes archived vehicles. `rentals` includes cancelled rentals.

`events` is the rental change feed (`rental.created`, `rental.updated`, `rental.cancelled`, `rental.deleted`), incremental on `occurredAt`. The API keeps 29 days of events and has no webhooks: sync at least weekly, and use the feed to see which rentals changed between two full syncs. See [Synchronisation](https://docs.lexio.rent/synchronisation).

## Limits

Lexio applies a per-key rate limit and returns `Retry-After` on `429`; the connector waits and retries. See [Rate limits](https://docs.lexio.rent/limites).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-11-12 | | Initial release: 11 streams |

</details>
