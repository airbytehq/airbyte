# Contributing to source-apple-search-ads

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

This is a manifest-only connector: all behavior lives in `manifest.yaml`. It reads the Apple Ads
(formerly Apple Search Ads) Campaign Management API v5.

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

### 1. Authentication is two-legged only; there is no user-consent OAuth flow

Apple's API only offers machine-to-machine OAuth: a self-signed ES256 JWT acts as the
`client_secret` and tokens come from `grant_type=client_credentials`. There is no consent redirect,
so the connector uses a plain `OAuthAuthenticator` and intentionally has no `advanced_auth` or
declarative OAuth spec.

### 2. The four `*_report_daily` streams are genuinely keyless

Apple's reporting endpoints return metric aggregations with no record identifier. A row is
identified by the reporting entity id plus `date` plus `countryorregion` — all three assembled by
the connector from its own request parameters — so no stable API-provided primary key exists to
declare. Dedupe on that tuple in the destination if needed.

### 3. Deletions are replicated as a `deleted` flag on the entity streams

The canonical pattern for this connector is a deletion flag on the primary streams
(`campaigns`, `adgroups`, `keywords`, `ads` all carry Apple's `deleted` boolean), not dedicated
`deleted_*` streams. The connector does not explicitly request deleted records, and whether Apple's
`GET` list endpoints include soft-deleted rows is unverified.

### 4. Entity streams are full refresh even though records carry `modificationTime`

Apple's `modificationTime` records changes to the object itself, but `servingStatus`,
`servingStateReasons` and `displayStatus` change when Apple's system reacts to dates, budgets and
billing. A cursor on `modificationTime` would leave those fields stale, and `Keyword` and `AdGroup`
document no range filter on it. The entity streams stay full refresh; see
[AGENTS.md](./AGENTS.md#4-entity-streams-are-full-refresh-even-though-records-carry-modificationtime).

### 5. No `api_budget`: the Campaign Management API publishes no numeric quota

Apple publishes only backoff advice for v5, so there is no `api_budget`. Campaign Management API v5
sunsets on 2027-01-26 and the Platform API that replaces it publishes `RateLimit-*` headers, so
revisit this during that migration.

### 6. Stream coverage versus Fivetran (parity table)

Eight of Fivetran's ten Apple Search Ads tables have a matching stream. Two are genuinely missing:
`organization` (`GET /acls`) and `search_term_report`
(`POST /reports/campaigns/{campaignId}/searchterms`). Implementing them belongs in its own issue; see
the parity table in [AGENTS.md](./AGENTS.md) for the row-by-row verdicts and caveats.
