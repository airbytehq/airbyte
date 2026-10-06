> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-google-ads

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Connector type

Low-code: the streams are declared in `source_google_ads/manifest.yaml`, and `source_google_ads/components.py` holds the custom components the manifest references (requesters that build GAQL queries, the streaming decoder, `GoogleAdsRetriever`, state migrations, transformations). `source_google_ads/streams.py` still contains the older Python stream classes (`IncrementalGoogleAdsStream` and friends); they are not what the manifest runs.

## Incremental Stream Considerations

The Google Ads API supports date-based segmentation in GAQL queries. The 19 incremental report streams share `incremental_stream_base` in the manifest (12 of them through `incremental_non_manager_stream_base`): a `DatetimeBasedCursor` on `segments.date` with `datetime_format: "%Y-%m-%d"`, `cursor_granularity: P1D` and `step: P14D` (`click_view` steps `P1D`), partitioned per customer account by a `SubstreamPartitionRouter` over `customer_client` (`customer_client_non_manager` for the non-manager base), so each customer keeps its own cursor.

## Interrupted report streams (ChunkedEncodingError)

Google Ads streams large reports, and the connection sometimes drops mid-download, which `requests` raises as a `ChunkedEncodingError` (or as a `ConnectionError` when the download stalls past the 300-second idle timeout). `GoogleAdsRetriever` in `components.py` recovers from both:

- **Incremental streams:** the error is turned into the CDK's `RequestWindowSplitRequiredException`, and the CDK's request window splitting (`SimpleRetriever._read_records_or_split_request_window`, CDK 7.33+) halves the date window with the stream's own cursor and reads each half in turn. A 14-day window reaches its first 1-day window after 3 splits (4 at most); the CDK caps the depth at 10. Only the partition (customer) whose window dropped is split; other customers are unaffected, and each customer's cursor still advances once, after all of its halves succeed.
- **At the 1-day floor, on streams without `incremental_sync`, and on the criterion streams' full refresh branch:** the same window gets 3 in-place retries (`GoogleAdsRetriever.MAX_RETRIES`), and the stream fails with a `transient_error` only if all of them fail.

The opt-in is wired in Python, not in the manifest. The CDK only builds a `request_window_splitting` block for a plain `SimpleRetriever`, so `GoogleAdsRetriever` declares `request_window_splitting = RequestWindowSplitting()` as a class default, takes the stream cursor through its `cursor` field (the factory passes `cursor=` to every retriever), and binds `request_window_splitter` to it in `__post_init__`. When editing streams:

- Every incremental stream whose requester filters on `start_time`/`end_time` must keep `cursor_granularity` on its cursor: without it the cursor can never split, so a drop only gets the 3 in-place retries. The criterion streams' full refresh branch must NOT get `cursor_granularity`: `CriterionFullRefreshRequester` ignores the window, so a split would resend the same unfiltered query once per child. `unit_tests/test_components.py::test_custom_retriever_incremental_streams_declare_cursor_granularity` checks the top-level manifest streams (it skips `StateDelegatingStream` branches and dynamic streams); `test_built_google_ads_retriever_streams_split_with_their_own_cursor` checks the wiring on the built streams, including an incremental custom GAQL stream.
- Do not put `request_window_splitting` in the manifest for this `CustomRetriever`: the factory cannot build it there (the default lives on the class).
- Records emitted before the drop are re-emitted when the window is split or retried. Destinations remove them by primary key only in deduplicated sync modes; plain Append keeps them on every stream, and `shopping_performance_view` and custom GAQL streams have no primary key at all.

The criterion streams (`ad_group_criterion`, `campaign_criterion`, `ad_listing_group_criterion`) use `CriterionRetriever` on their incremental branch, which has no `ChunkedEncodingError` handling at all; only their full refresh branch goes through `GoogleAdsRetriever`.

Tests: `unit_tests/test_components.py::TestGoogleAdsRetriever` (unit, with a real daily cursor) and `unit_tests/mock_server/test_chunked_encoding_error.py` (end to end through the CDK, including a two-customer case where only one customer's window is split).
