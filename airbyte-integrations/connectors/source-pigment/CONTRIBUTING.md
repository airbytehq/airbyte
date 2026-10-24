# Contributing to source-pigment

Connector-specific notes for working on the Pigment source. For general guidance, see the shared [README](./README.md).

## Authentication

- All requests use a bearer token. The metadata streams use `metadata_api_key` and `export_view` uses `export_api_key`.
- The API key needs the **Modeling Metadata** scope for the metadata streams and the **Export** scope for `export_view`. One key with both scopes works for both fields.
- Metadata endpoints are under `https://pigment.app/api/v1`. The view export endpoint is `https://pigment.app/api/export/view/{viewId}` (no `/v1`).

## Rate limits

- Pigment allows 500 requests per 5 minutes per IP address across public endpoints, and returns HTTP 429 when exceeded.
- The manifest defines an API budget of 400 calls per 5 minutes and retries 429 responses with a 60-second backoff.
- Substreams (`blocks`, `views`, `import_configurations`) make one request per parent record, so large workspaces consume the budget quickly.

## Known behaviors

- `import_configurations` and `data_flows` skip HTTP 403 responses. Some applications and blocks (for example the built-in `User` list in one application) return 403 for these endpoints even with a valid key. A 403 on the other streams still fails the sync.
- `export_view` reads view IDs from the `export_view_ids` config list. Enter one view ID per list item, with no brackets or quotes.
- The view export is `;`-delimited CSV with a UTF-8 byte-order mark before the first header. The CSV decoder uses `utf-8-sig` so the first column name is not prefixed with an invisible character.
- All exported values are strings, and exports include subtotal and total rows.

## Testing

- Use a Pigment trial or sandbox workspace with at least one application, a few blocks and one view.
- In the Connector Builder test panel, check that each stream returns records, and check that `export_view` returns one record per CSV row.
- When testing with a typed destination such as Postgres, refresh the source schema on the connection after publishing a new version of the connector.
