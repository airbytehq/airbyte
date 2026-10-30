> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-bing-ads: Unique Behaviors

## 1. Duplicate Records from Predicate-Based Filtering

When the connector is configured with `account_names` predicates (e.g., filter accounts containing "Airbyte" AND accounts containing "Plumbing"), a single account matching multiple predicates will be returned once per matching predicate. The `DuplicatedRecordsFilter` component deduplicates these by tracking seen record IDs and only emitting each record once.

**Why this matters:** Without this filter, users with multiple account name predicates would see duplicate records in their destination. The deduplication only activates when predicates are configured, so it is invisible during testing without predicates.

## 2. Bulk Report Downloads May Arrive Uncompressed Despite Gzip Content-Type

Bing Ads bulk report streams download files from Azure Blob Storage URLs. These files are expected to be gzip-compressed CSV, but the `BingAdsGzipCsvDecoder` includes fallback logic to handle cases where the file arrives uncompressed despite the expected gzip format. The decoder attempts gzip decompression first and falls back to reading the raw content if decompression fails.

**Why this matters:** If you assume all bulk downloads are properly gzip-compressed, you will encounter intermittent failures. Azure Blob Storage does not always apply compression consistently, so the decoder must handle both compressed and uncompressed responses for the same stream.

## 3. Campaigns Are Only Returned for Explicitly Requested Campaign Types

The `campaigns` stream calls `GetCampaignsByAccountId`, which only returns campaigns whose type is listed in the `CampaignType` request field (and only `Search` campaigns when the field is omitted). The manifest therefore sends every documented [CampaignType](https://learn.microsoft.com/en-us/advertising/campaign-management-service/campaigntype?view=bingads-13) value. When Microsoft adds a new campaign type, it must be added to this list.

**Why this matters:** A missing type is silent data loss. Campaigns of that type are never returned, there is no error or warning, and their ad groups and ads are also missing because `ad_groups` and `ads` are child streams of `campaigns`.
