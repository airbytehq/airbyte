> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-bing-ads: Unique Behaviors

## 1. Duplicate Records from Predicate-Based Filtering

When the connector is configured with `account_names` predicates (e.g., filter accounts containing "Airbyte" AND accounts containing "Plumbing"), a single account matching multiple predicates will be returned once per matching predicate. The `DuplicatedRecordsFilter` component deduplicates these by tracking seen record IDs and only emitting each record once.

**Why this matters:** Without this filter, users with multiple account name predicates would see duplicate records in their destination. The deduplication only activates when predicates are configured, so it is invisible during testing without predicates.

## 2. Bulk Report Downloads May Arrive Uncompressed Despite Gzip Content-Type

Bing Ads bulk report streams download files from Azure Blob Storage URLs. These files are expected to be gzip-compressed CSV, but the `BingAdsGzipCsvDecoder` includes fallback logic to handle cases where the file arrives uncompressed despite the expected gzip format. The decoder attempts gzip decompression first and falls back to reading the raw content if decompression fails.

**Why this matters:** If you assume all bulk downloads are properly gzip-compressed, you will encounter intermittent failures. Azure Blob Storage does not always apply compression consistently, so the decoder must handle both compressed and uncompressed responses for the same stream.

## 3. Bulk Delta Downloads Have a 30-Day Limit

The eight bulk entity streams request `EntityData` through [DownloadCampaignsByAccountIds](https://learn.microsoft.com/en-us/advertising/bulk-service/downloadcampaignsbyaccountids?view=bingads-13). `LastSyncTimeInUTC` selects entity changes, and Microsoft rejects timestamps older than 30 days. The connector omits this parameter when the slice starts before the 30-day cutoff, causing a full download. The reporting `lookback_window` does not apply to these streams because rewinding entity deltas adds redundant reads and can trigger this fallback.

The connector currently saves the maximum record `Modified Time`, so inactive accounts can still fall back to full downloads. Microsoft recommends using the account record's `Sync Time` from the previous download; adopting that would require a separate cursor/state change.

**Why this matters:** Applying a report conversion window to bulk entities can turn every sync into a full download. Report streams, including budget summary and custom reports, retain lookback to re-read dated metrics that may change later.
