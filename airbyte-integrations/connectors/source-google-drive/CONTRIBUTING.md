# source-google-drive: Unique Behaviors

## 1. File-Based CDK Architecture

This connector extends `FileBasedSource` from the Airbyte CDK (`airbyte_cdk.sources.file_based`). It does not use a declarative manifest. Instead, stream generation is handled entirely by the CDK's file-based framework:

1. User configures one or more **stream definitions** in the connector spec, each specifying a glob pattern, file format, and optional schema.
2. At runtime, `SourceGoogleDriveStreamReader` traverses Google Drive folders recursively (starting from the configured `folder_url`) and yields `GoogleDriveRemoteFile` objects with `last_modified` timestamps from the Drive API's `modifiedTime` field.
3. The CDK creates one stream per configured stream definition. Each stream reads all matching files and parses their contents according to the configured format (CSV, JSON, Avro, Parquet, Excel, or unstructured document).

## 2. Google Apps Document Export

Google Docs, Sheets, Presentations, and Drawings are not directly downloadable as binary files. The connector detects these by MIME type and uses the Google Drive `export_media` API to convert them to standard formats (DOCX, XLSX, PPTX, PDF) before parsing. See `stream_reader.py:DOWNLOADABLE_DOCUMENTS_MIME_TYPES` for the mapping.

## 3. Shared Drive Support

The connector supports both personal (My Drive) and shared (Team) drives via `supportsAllDrives=True` and `includeItemsFromAllDrives=True` flags. For shared drive items, the `driveId` is captured to construct correct URLs.

## Incremental Stream Considerations

This connector generates streams at runtime via the CDK's `FileBasedSource` framework. User inputs that drive stream generation are: the `folder_url` config, one or more stream definitions with glob patterns and format settings. The connector's incremental story is **fully handled by the CDK's `DefaultFileBasedCursor`**, which tracks per-file `last_modified` timestamps. On incremental syncs, only files modified since the last sync's cursor value are re-read.

| Stream Type / Pattern | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| `gdrive_file` (any user-configured file stream) | medium–large (varies by folder size) | top-level dynamic (one stream per configured stream definition) | `_ab_source_file_last_modified` | `modified_since` — Drive API exposes `modifiedTime` per file in list responses (`stream_reader.py:151`) | `incremental` | File-level incremental is fully supported. The cursor tracks the latest `modifiedTime` seen across all files in the stream. On warm syncs, only files with `modifiedTime` after the cursor are re-read and re-parsed. Note: this is **file-level** incremental, not **row-level** — if a CSV file is modified, all rows in that file are re-emitted. |
| `gdrive_file_permissions` (permissions stream) | small | child of file stream | `_ab_source_file_last_modified` | `modified_since` (inherits from parent file listing) | `incremental` | Permissions are fetched per-file. The stream inherits the file-level cursor behavior: permissions are re-fetched only for files modified since the last sync. |

### Deferred & framework-level work

1. **Row-level incremental within files is not supported.** The CDK's file-based cursor operates at the file level. If a single row in a large CSV changes, the entire file is re-read and all rows are re-emitted. This is a CDK-level limitation, not specific to Google Drive. True row-level incremental would require content-diffing capabilities in the CDK's file parsers.
2. **No server-side file-list filtering by modifiedTime.** The Google Drive API supports `modifiedTime` in file metadata responses, but the connector currently fetches all files and filters client-side via the CDK cursor. A potential optimization would be to add a `modifiedTime > '{cursor_value}'` clause to the Drive API `q` parameter in the file list request, reducing API response size for large folders. This would require changes to `stream_reader.py:get_matching_files()`.
3. **Google Sheets export limitation.** Google Sheets exported as XLSX have a 10 million cell limit imposed by the export API. Very large sheets may fail or be truncated during export.
