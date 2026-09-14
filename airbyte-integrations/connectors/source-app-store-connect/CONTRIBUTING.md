# Contributing to source-app-store-connect

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

This is a manifest-only connector: all behavior lives in `manifest.yaml`. It reads the
[App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi) at
`https://api.appstoreconnect.apple.com/v1`.

## Unique behaviors

### Authentication is a self-signed ES256 JWT

Apple has no OAuth flow for this API. The connector uses `JwtAuthenticator` with the `.p8` private
key from config (`secret_key`), the Key ID as the `kid` header, the Issuer ID as `iss`, and
`aud: appstoreconnect-v1`. Tokens are valid for 20 minutes (`token_duration: 1200`).

A `403 FORBIDDEN.REQUIRED_AGREEMENTS_MISSING_OR_EXPIRED` response means the JWT is valid but the
team's Paid Apps agreement has lapsed; it is not an auth bug.

### Report streams decode gzip-compressed TSV

`salesReports` and `financeReports` return a gzip archive containing a tab-delimited file. The
Sales and Trends streams use a nested `GzipDecoder -> GzipDecoder -> CsvDecoder` chain
(`SalesReportCsvDecoder`) because the HTTP layer may or may not have already inflated the payload;
the analytics download streams use a single `GzipDecoder -> CsvDecoder`. Keep the CDK version at or
above the one in `manifest.yaml` (`7.28.2`), which includes the gzip decoder fix from
[airbyte-python-cdk PR 1124](https://github.com/airbytehq/airbyte-python-cdk/pull/1124).

`filter[version]` values such as `1_3` must stay quoted in YAML; unquoted, YAML parses `1_3` as the
integer `13` and the manifest fails schema validation.

### Analytics reports are a five-level parent/child chain with an async download

For each of the two report types (App Store Installation and Deletion, App Downloads) and each
access type (`ONGOING`, `ONE_TIME_SNAPSHOT`), the manifest declares:

`list_id_apps -> analytics_report_requests_* -> analytics_*_reports -> analytics_*_instances ->
analytics_*_segments -> analytics_*_segment_details` and a final `AsyncRetriever` stream that polls
`/analyticsReportSegments/{id}` for a download URL and streams the TSV.

`max_concurrent_async_job_count: 1` is set at the top level because Apple rejects concurrent report
downloads. Segments with `sizeInBytes == 0` are filtered out before download.

### Incremental cursors are synthesized

Sales/finance report rows have no timestamp Apple guarantees, so each stream adds a `_sync_cursor`
field (slice start plus one step) via `AddFields` and uses it as the `DatetimeBasedCursor` field.
Analytics rows use `processing_date`, copied from the `Date` column.

## Testing

There is currently no sandbox App Store Connect account with an in-effect developer agreement, so
`acceptance-test-config.yml` only runs `spec`, `connection`, and `discovery`. To test locally,
create `secrets/config.json` with `iss`, `kid`, `secret_key`, `vendorID`, and
`analytics_reports_start_date`, then:

```bash
airbyte-cdk connector test  # from this directory
```

or use the Connector Builder MCP `validate_manifest` and `execute_stream_test_read` tools against
`manifest.yaml`.
