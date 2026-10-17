# Changelog

## 0.1.0 — 2026-09-12

Complete rewrite. The three separate connectors (`source-sapreadtable` plus two
empty placeholders) are replaced by a single `source-sap` covering four SAP
interfaces, selected by a `protocol` choice in the spec.

### Added

- **SAP BW via BICS.** Discovery of InfoProviders and BEx queries, BEx variable
  binding, and slicing on a characteristic — BW materialises the whole result set
  or none of it, so slicing is the only way to bound memory on a large cube.
- **SAP ODP over RFC.** Full extraction and true delta extraction using SAP's own
  server-side pointer. Airbyte state carries only the subscriber process; the
  pointer lives on SAP.
- **SAP ODP over OData** through `erpl_web`, with the delta token round-tripped
  through Airbyte state so a fresh container resumes correctly.
- **Incremental sync for RFC** on a nominated cursor field, pushed down to SAP as
  a `>=` predicate.
- CDC tombstones (`_ab_cdc_deleted_at`) for both ODP protocols.
- Parallelism: row-range `partitions` within an RFC scan, `threads` for ODP full
  extraction, and Concurrent-CDK reading of several streams at once.
- End-to-end tests that run the connector as a subprocess against a real SAP
  system and assert on the protocol messages. Nothing is mocked.

### Changed

- `airbyte-cdk` `^0` (0.85.0) → `^7.28`, and the legacy `airbyte_cdk.sources.Source`
  base class → `ConcurrentSourceAdapter`.
- `duckdb` 0.10.1 → 1.5.5; Python 3.9 → 3.11+; the base image is now
  `airbyte/python-connector-base:4.1.1`.
- The ERPL extensions are **baked into the image** at a pinned version instead of
  being downloaded from `get.erpl.io` during every sync. A sync now needs
  no network access beyond SAP itself.
- Credentials use `CREATE SECRET (TYPE sap_rfc, ...)` with bound parameters,
  replacing session-level `SET sap_*` statements.
- Dependencies are managed with `uv`.

### Fixed

- **SQL injection.** Every config value, including the password, was interpolated
  into SQL with an f-string.
- **Credential leak.** The connector logged the last character of the user name
  and password on every run.
- **Record timestamps.** `emitted_at` was in seconds where the protocol requires
  milliseconds, dating every record to 1970.
- **Throughput.** `fetchmany()` was called with its default size of 1, making one
  round trip per row and silently discarding any extra rows it returned.
- Non-protocol fields (`text`, `table_type`) were being injected into
  `AirbyteStream`.
- An unmapped DDIC type raised `ValueError` and failed the whole `discover`; it
  now degrades to string with a warning.
- `metadata.yaml` carried Airbyte's own `source-duckdb` definition ID, docker
  repository and documentation URL.

### Security

- The ERPL extensions are fetched over HTTPS and verified against pinned
  sha256 checksums; an unpinned or mismatched artifact fails the build.
- ODP OData entity-set URLs are confined to the configured Gateway host, so a
  config value cannot redirect the connector at another host using the
  Gateway's credentials.
- The OData connection check authenticates through the URL-scoped secret rather
  than an inline credential, keeping the password out of DuckDB error text.
- `cursor_field` — the one identifier interpolated into an ABAP WHERE fragment —
  is validated against the field list SAP reported for the table.
- `concurrency`, `partitions`, `threads`, `fetch_size` and `max_page_size` are
  clamped to their documented ranges, so a hand-edited config cannot exhaust the
  SAP system's work processes.
- Two ODP objects that resolve to the same subscriber process are refused: they
  would share one SAP delta subscription and consume each other's changes.
- The connector warns when RFC runs without SNC, or the Gateway URL is plain
  http, because the password then travels in the clear.

### Known limitations

- The image is `linux/amd64` only — ERPL publishes no arm64 build.
- BICS is full-refresh only; the protocol exposes no change tracking.
- ODP OData catalog discovery depends on the SAP Gateway catalog service, which
  is not reachable on every release. Entity-set URLs can be listed explicitly.
