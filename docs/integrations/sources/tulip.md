# Tulip

This page contains the setup guide and reference information for the Tulip source connector.

## Prerequisites

- A Tulip instance (e.g., `yourcompany.tulip.co`)
- An API token with the **tables:read** scope

## Setup Guide

### Step 1: Create a Tulip API Token

1. Log in to your Tulip instance.
2. Navigate to **Account Settings > API Tokens**.
3. Click **Create API Token**.
4. Grant the **tables:read** scope.
5. Copy the **API Key** and **API Secret**.

### Step 2: Configure the Connector

| Field | Required | Description |
|-------|----------|-------------|
| Tulip Subdomain | Yes | Your Tulip instance subdomain (e.g., `acme` for `acme.tulip.co`). |
| API Key | Yes | The API key from Step 1. |
| API Secret | Yes | The API secret from Step 1. |
| Workspace ID | No | Provide this for workspace-scoped API keys. Found in your workspace settings URL. |
| Sync Start Date | No | ISO 8601 timestamp (e.g., `2025-01-01T00:00:00Z`). Records updated before this date are skipped during the initial sync. |
| Custom Filter JSON | No | A JSON array of Tulip API filter objects applied to every request. See the [Tulip API documentation](https://support.tulip.co/docs/tulip-api) for filter syntax. |

## Supported Sync Modes

| Feature | Supported |
|---------|-----------|
| Full Refresh | Yes |
| Incremental - Append + Dedup | Yes |
| Namespaces | No |

## Supported Streams

This connector dynamically discovers all Tulip Tables accessible to the configured API token. Each table is exposed as an independent, selectable stream. Stream names use the format `label__id` (e.g., `production_orders__abc123`).

### Schema Discovery

Schemas are fetched live from the Tulip API on every discover run. When columns are added or removed in Tulip, the schema updates automatically on the next sync.

### System Fields

Every stream includes these fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Record primary key |
| `_createdAt` | string (date-time) | Record creation timestamp |
| `_updatedAt` | string (date-time) | Last update timestamp |
| `_sequenceNumber` | integer | Monotonically increasing sequence number |

### Type Mapping

| Tulip Type | Airbyte Type |
|-----------|-------------|
| integer | integer |
| float | number |
| boolean | boolean |
| timestamp | string (date-time) |
| datetime | string (date-time) |
| interval | integer (milliseconds) |
| color | string (JSON-serialized) |
| user | string |
| tableLink | *excluded* |
| All others | string |

All fields are nullable.

## Incremental Sync Details

The connector uses a two-phase incremental strategy:

1. **BOOTSTRAP** — On the first sync, fetches all historical records ordered by `_sequenceNumber`. Completes when a batch returns fewer than 100 records.
2. **INCREMENTAL** — On subsequent syncs, fetches records where `_updatedAt` is greater than the last sync timestamp (with a 60-second lookback to catch concurrent updates). This captures both new and updated records.

State is checkpointed every 500 records. The `_updatedAt` cursor is frozen during a sync run and only advanced after the sync completes, ensuring no data loss if the sync is interrupted.

## Rate Limiting

The connector respects Tulip's 50 requests/second API rate limit using:

- **Proactive throttling** — A shared rate limiter (45 req/s with headroom) across all streams.
- **Reactive backoff** — Automatic retry with `Retry-After` header parsing on HTTP 429 responses.

## Changelog

| Version | Date | Description |
|---------|------|-------------|
| 0.1.0 | 2026-02-13 | Initial release: multi-table sync, dynamic schema discovery, incremental sync, rate limiting |
