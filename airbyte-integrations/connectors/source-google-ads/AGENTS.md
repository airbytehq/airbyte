> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-google-ads

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Connector type

Low-code: the streams are declared in `source_google_ads/manifest.yaml`, and `source_google_ads/components.py` holds the custom components the manifest references (requesters that build GAQL queries, the streaming decoder, `GoogleAdsRetriever`, state migrations, transformations). `source_google_ads/streams.py` still contains the older Python stream classes (`IncrementalGoogleAdsStream` and friends); they are not what the manifest runs.

## Incremental Stream Considerations

The Google Ads API supports date-based segmentation in GAQL queries. Incremental streams share `incremental_stream_base` in the manifest: a `DatetimeBasedCursor` on `segments.date` with `datetime_format: "%Y-%m-%d"`, `cursor_granularity: P1D` and `step: P14D`, partitioned per customer account by a `SubstreamPartitionRouter` over `customer_client`, so each customer keeps its own cursor.

## Interrupted report streams (ChunkedEncodingError)

Google Ads streams large reports, and the connection sometimes drops mid-download, which `requests` raises as a `ChunkedEncodingError`. `GoogleAdsRetriever` in `components.py` recovers from it:

- **Incremental streams:** the error is turned into the CDK's `RequestWindowSplitRequiredException`, and the CDK's request window splitting (`SimpleRetriever._read_records_or_split_request_window`, CDK 7.33+) halves the date window with the stream's own cursor and reads each half in turn. A 14-day window reaches the 1-day floor after 4 splits; the CDK caps the depth at 10. Only the partition (customer) whose window dropped is split; other customers are unaffected, and each customer's cursor still advances once, after all of its halves succeed.
- **At the 1-day floor, and on full refresh streams** (no date window to split): the same window is retried in place up to `GoogleAdsRetriever.MAX_RETRIES` (3) times, then the stream fails with a `transient_error`.

The opt-in is wired in Python, not in the manifest. The CDK only builds a `request_window_splitting` block for a plain `SimpleRetriever`, so `GoogleAdsRetriever` takes the stream cursor through its `cursor` field (the factory passes `cursor=` to every retriever) and binds `request_window_splitter` and `request_window_splitting` in `__post_init__`. Two consequences when editing streams:

- Every incremental stream that uses `GoogleAdsRetriever` must keep `cursor_granularity` on its cursor: without it the cursor can never split, and every drop falls through to 3 retries and a failure. `unit_tests/test_components.py::test_custom_retriever_incremental_streams_declare_cursor_granularity` enforces this for every stream in the manifest.
- Records emitted before the drop are re-emitted when the window is split or retried. Streams with a primary key are deduplicated by the destination; `shopping_performance_view` and custom GAQL streams have none, so append-mode destinations can see duplicate rows there.

The criterion streams (`ad_group_criterion`, `campaign_criterion`, `ad_listing_group_criterion`) use `CriterionRetriever` on their incremental branch, which has no `ChunkedEncodingError` handling at all; only their full refresh branch goes through `GoogleAdsRetriever`.

Tests: `unit_tests/test_components.py::TestGoogleAdsRetriever` (unit, with a real daily cursor) and `unit_tests/mock_server/test_chunked_encoding_error.py` (end to end through the CDK, including a two-customer case where only one customer's window is split).
