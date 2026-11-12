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

## 4. Campaigns Are Only Returned for Explicitly Requested Campaign Types

The `campaigns` stream calls `GetCampaignsByAccountId`, which only returns campaigns whose type is listed in the `CampaignType` request field (and only `Search` campaigns when the field is omitted). The manifest therefore sends every documented [CampaignType](https://learn.microsoft.com/en-us/advertising/campaign-management-service/campaigntype?view=bingads-13) value. When Microsoft adds a new campaign type, it must be added to this list.

The `ads` stream has the same behavior: `GetAdsByAdGroupId` only returns ads whose type is listed in the required `AdTypes` request field, so the manifest sends every documented [AdType](https://learn.microsoft.com/en-us/advertising/campaign-management-service/adtype?view=bingads-13) value. Keep both lists in sync with Microsoft's value sets.

**Why this matters:** A missing type is silent data loss. Campaigns or ads of that type are never returned, there is no error or warning, and their ad groups and ads are also missing because `ad_groups` and `ads` are child streams of `campaigns`.

## 5. Report and Bulk Files Are Downloaded from Short-Lived Microsoft Storage Links

Report and bulk streams download their files from pre-signed Azure Blob Storage links that Microsoft returns once the file is ready. Azure rejects a link outside its validity window with `403` (`AuthenticationFailed`). The download requesters fail any `403` as a `transient_error` that names the stream, because the link is issued by Microsoft and the download sends no user credentials. The filter matches on status code only: a `predicate` makes the CDK parse the body of every response, which consumes the streamed file before the decoder reads it. The stream name reaches the message through the `stream_name` parameter that each dynamic stream template sets.

**Why this matters:** The CDK default for `403` is a `config_error` telling the user they lack permission, which stops retries and points them at credentials that are fine. Report downloads re-poll for a new link before downloading; bulk downloads do not, so a slow bulk download can still hit this error.
