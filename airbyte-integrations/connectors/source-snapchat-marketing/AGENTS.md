> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-snapchat-marketing

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## 1. Organizations and Ad Accounts ignore Start Date

`organizations` and `adaccounts` are client-side incremental on `updated_at`, and the CDK applies that filter to a stream even when it is read as a parent through `SubstreamPartitionRouter`. Organizations and ad accounts are rarely edited, so filtering them by `start_date` dropped any organization or ad account last updated before it, and every stream under it returned 0 records while the sync succeeded ([#47834](https://github.com/airbytehq/airbyte/issues/47834)). Both streams therefore use a fixed `start_datetime` of `2011-09-01`. Setting `organization_ids` or `ad_account_ids` doesn't bypass the filter, because it applies to the records those requests return too.

Known gaps: `ads`, `adsquads` and `campaigns` still filter by `start_date` when read as parents of the stats streams, so an entity not edited since `start_date` gets no stats. An explicit `end_date` still drops organizations and ad accounts updated after it.

**Why this matters:** Pointing these two `start_datetime` values back at `config.start_date` for consistency silently empties every stream for accounts whose organization or ad accounts weren't edited recently. When a fix makes hidden parents visible, existing connections pick up the new partitions from the stream's saved state, not from `start_date`, so partly affected connections need a refresh to backfill.

## Incremental Stream Considerations

The Snapchat Marketing API supports date-based filtering on stats endpoints and `updated_at` ordering on entity endpoints, which the connector already uses for 16 incremental streams. The 4 remaining streams are children partitioned via `SubstreamPartitionRouter` (ad_squad_stats, ad_stats, campaign_stats, organization_stats). No FR parent streams remain.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| organizations | medium | top-level parent | updated_at | updated_at | incremental |  |
| adaccounts | medium | child | updated_at | updated_at | incremental |  |
| adaccounts_stats_daily | medium | child | start_time | start_time | incremental |  |
| adaccounts_stats_hourly | medium | child | start_time | start_time | incremental |  |
| adaccounts_stats_lifetime | medium | child | none | none | deferred_child |  |
| ads | medium | child | updated_at | updated_at | incremental |  |
| ads_stats_daily | medium | child | start_time | start_time | incremental |  |
| ads_stats_hourly | medium | child | start_time | start_time | incremental |  |
| ads_stats_lifetime | medium | child | none | none | deferred_child |  |
| adsquads | medium | child | updated_at | updated_at | incremental |  |
| adsquads_stats_daily | medium | child | start_time | start_time | incremental |  |
| adsquads_stats_hourly | medium | child | start_time | start_time | incremental |  |
| adsquads_stats_lifetime | medium | child | none | none | deferred_child |  |
| campaigns | medium | child | updated_at | updated_at | incremental |  |
| campaigns_stats_daily | medium | child | start_time | start_time | incremental |  |
| campaigns_stats_hourly | medium | child | start_time | start_time | incremental |  |
| campaigns_stats_lifetime | medium | child | none | none | deferred_child |  |
| creatives | medium | child | updated_at | updated_at | incremental |  |
| media | medium | child | updated_at | updated_at | incremental |  |
| segments | medium | child | updated_at | updated_at | incremental |  |

### Future incremental stream candidates

- **Child streams (4 streams):** `adaccounts_stats_lifetime`, `ads_stats_lifetime`, `adsquads_stats_lifetime`, `campaigns_stats_lifetime` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate incremental support.
