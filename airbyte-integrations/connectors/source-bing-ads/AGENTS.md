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

## 5. Download Requesters Must Not Read the Response Body Before the Decoders

Report and bulk files are downloaded from pre-signed Azure Blob Storage URLs as streamed responses, and `BingAdsReportZipCsvDecoder` and `BingAdsGzipCsvDecoder` consume `response.raw`. The built-in `HttpResponseFilter` calls `response.json()` to evaluate `predicate` and reads the body for `error_message_contains`, on every response including successful ones. That drains the stream, so the decoders see an empty file and the stream emits zero records without any error. For this reason the download requesters use the custom `BingAdsDownloadErrorHandler`, which only reads the body of a 403 that carries Azure's `x-ms-error-code: AuthenticationFailed` header.

That handler reports an expired download URL (Azure detail `Signature not valid in the specified time frame`) as a `transient_error` with action `FAIL`: the URL cannot be fixed through configuration, and requesting the same URL again cannot succeed.

**Why this matters:** Adding a declarative `response_filters` entry with a `predicate` or `error_message_contains` to either `download_requester` looks harmless and silently empties every report and bulk stream.
