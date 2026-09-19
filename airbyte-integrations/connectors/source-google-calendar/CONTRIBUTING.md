# Contributing to source-google-calendar

Manifest-only declarative connector built on `source-declarative-manifest`. All behavior lives in `manifest.yaml`.

## Authentication

Two options under `credentials`: OAuth (recommended — backed by `advanced_auth` for the Airbyte Cloud "Authenticate your Google account" flow, scopes `calendar.readonly` and `calendar.acls.readonly`) and a manual refresh-token option for OSS users who mint their own token. Legacy flat configs (`client_id`/`client_secret`/`client_refresh_token_2`) are transparently migrated by `config_normalization_rules`.

## Design choices

- **Incremental `events` uses `updatedMin` + `showDeleted` rather than `syncToken`.** `syncToken` is an opaque token that expires unpredictably and cannot be expressed as a `DatetimeBasedCursor` state; Google already requires a full resync when a sync token expires (410), the same failure mode a saved `updatedMin` cursor older than ~30 days has. `showDeleted=true` means deletions arrive as `status: "cancelled"` records. With no `start_date` configured, the first sync fetches all events; `updatedMin` is only sent when resuming from a saved cursor.
- **Per-calendar partitioning:** a hidden `calendar_partitions` stream (a copy of `calendarlist` filtered by the optional `calendarid` config) is the parent partition for `events`, `acl`, and `freebusy` (`partition_field: calendar_id`). Setting `calendarid` narrows those streams to one calendar; `primary` is accepted.
- **`channels` is intentionally excluded** — it is push-notification infrastructure (watch/stop), not data to replicate.
- **`acl` returns nothing under `calendar.readonly`** — `acl.list` needs the `calendar.acls.readonly` scope, and ACLs are only readable for calendars the account owns. 403/404 responses are IGNOREd so non-owned calendars don't fail the sync.
- **Rate budget:** a 500 requests/minute moving-window API budget sits under Google's documented 600/min/user quota; 403 rate-limit and 429 responses are retried with exponential backoff.

## Running locally

```bash
# creds go in secrets/config.json (never commit it)
source-declarative-manifest spec --manifest-path manifest.yaml
source-declarative-manifest check --config secrets/config.json --manifest-path manifest.yaml
source-declarative-manifest discover --config secrets/config.json --manifest-path manifest.yaml
source-declarative-manifest read --config secrets/config.json --catalog integration_tests/configured_catalog.json --manifest-path manifest.yaml
poe test-integration-tests   # connector acceptance tests
```
