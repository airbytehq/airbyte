# Contributing to source-zip

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

This is a manifest-only connector: all behavior lives in `manifest.yaml`. It reads Zip's public procurement API.

## Unique behaviors (summary)

1. **Every field except `id` and `updated_at` is discovered at runtime and typed as a nullable string.**
   Each stream lists two schema loaders: an `InlineSchemaLoader` that pins `id` (string) and `updated_at`
   (integer), then a `DynamicSchemaLoader` that reads the first record of the endpoint and declares each of
   its top-level keys as `["null", "string"]`. The inline loader comes first so its types win. Zip returns
   every key on every record (null when unset), so the first record carries the full field set. Nested
   objects and arrays land as JSON strings; parse them downstream. `DynamicSchemaLoader` is marked
   experimental in the CDK.
2. **The incremental filter has a different name per endpoint.** `/invoices` filters on `updated_after`;
   `/requests` and `/purchase_orders` filter on `last_updated_after`. Sending the other name returns
   HTTP 400 `INVALID_PARAM`. Keep the per-stream `start_time_option`.
3. **`/requests` caps the page size at 30.** The other two endpoints accept 50. Asking `/requests` for more
   is silently reduced, so the connector asks for 30 there and 50 elsewhere.
4. **Timestamps are Unix epoch seconds.** The cursor uses `datetime_format: "%s"` and the saved state looks
   like `{"updated_at": "1718000000"}`. Zip's filter is inclusive, so the record at the cursor is re-read.
5. **Custom fields need `include_attributes=true`.** Without that parameter the `attributes` array is empty.
   Records are requested newest first (`sort_by=updated_at&sort_order=desc`) so schema discovery sees the
   most recently written record.
6. **On `/purchase_orders`, `last_updated_after` matches `last_activity_at`, not `updated_at`.** A read from a
   given cursor returns purchase orders with an older `updated_at` whenever they had activity after the
   cursor. The connector passes them through; the cursor still advances on `updated_at`. `/requests` and
   `/invoices` bound `updated_at` as expected.
7. **Incremental reads were only safe after Zip fixed its pagination.** Zip's cursor did not tie-break on
   `updated_at`, so records sharing one timestamp fell through page boundaries under the date filters
   (Zip support ticket 110091). Zip deployed the fix for `/invoices` and `/purchase_orders` on
   2026-08-07 and for `/requests` on 2026-08-25.

## Testing

- Unit tests in `unit_tests/` mock Zip's API with `requests_mock` and run without credentials:

  ```bash
  cd unit_tests && poetry install --no-root && poetry run pytest -q
  ```

- Zip's API reference is only readable with a Zip login (https://developer.zip.com), so the behaviors
  above were confirmed against the live API rather than public documentation.
