> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-bing-ads: Unique Behaviors

## 1. Duplicate Records from Predicate-Based Filtering

When the connector is configured with `account_names` predicates (e.g., filter accounts containing "Airbyte" AND accounts containing "Plumbing"), a single account matching multiple predicates will be returned once per matching predicate. The `DuplicatedRecordsFilter` component deduplicates these by tracking seen record IDs and only emitting each record once.

**Why this matters:** Without this filter, users with multiple account name predicates would see duplicate records in their destination. The deduplication only activates when predicates are configured, so it is invisible during testing without predicates.

## 2. Bulk Report Downloads May Arrive Uncompressed Despite Gzip Content-Type

Bing Ads bulk report streams download files from Azure Blob Storage URLs. These files are expected to be gzip-compressed CSV, but the `BingAdsGzipCsvDecoder` includes fallback logic to handle cases where the file arrives uncompressed despite the expected gzip format. The decoder attempts gzip decompression first and falls back to reading the raw content if decompression fails.

**Why this matters:** If you assume all bulk downloads are properly gzip-compressed, you will encounter intermittent failures. Azure Blob Storage does not always apply compression consistently, so the decoder must handle both compressed and uncompressed responses for the same stream.

## 3. Download URLs Expire and Are Refreshed Before Each Download

Report (`GenerateReport/Poll`) and bulk (`BulkDownloadStatus/Query`) jobs return pre-signed Azure Blob Storage SAS URLs that expire minutes after they are issued. Large syncs queue many downloads, so the URL captured at job completion is often expired by the time it is used. `BingAdsReportDownloadRequester` and `BingAdsBulkDownloadRequester` re-poll for a fresh URL immediately before each download, and the manifest's `download_url_error_handler` hands a `403` back to them so they can re-poll and retry (up to `max_download_attempts`) instead of failing with a generic permission error.

**Why this matters:** An expired SAS URL returns `403 AuthenticationFailed` ("Signature not valid in the specified time frame"), which looks like a credentials problem but is not. Retrying the same URL never succeeds; only a new poll returns a usable URL.
