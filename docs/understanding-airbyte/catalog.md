# AirbyteCatalog Reference

## Overview

An `AirbyteCatalog` is a struct produced by the `discover` action of a source. It is a list of `AirbyteStream`s. Each `AirbyteStream` describes the data available to sync from the source. After a source produces an `AirbyteCatalog` or `AirbyteStream`, they should be treated as read-only. A `ConfiguredAirbyteCatalog` is a list of `ConfiguredAirbyteStream`s. Each `ConfiguredAirbyteStream` describes how to sync an `AirbyteStream`.

## Cursor

* The cursor is how sources track which records are new or updated since the last sync. 
* A "cursor field" is the field used to make this determination.
  * If a configuration requires a cursor field, it requires an array of strings that serve as a path to the desired field. For example, if the structure of a stream is `{ value: 2, metadata: { updated_at: 2020-11-01 } }`, the `default_cursor_field` would be `["metadata", "updated_at"]`.

## AirbyteStream

This section documents the meaning of each field in an `AirbyteStream`.

* `json_schema` - A [JsonSchema](https://json-schema.org/understanding-json-schema) representation of the stream.
* `supported_sync_modes` - The sync modes the stream supports. By default, all sources support `FULL_REFRESH`, even if this array is empty. The allowed sync modes are `FULL_REFRESH` and `INCREMENTAL`.
* `source_defined_cursor` - If a source supports the `INCREMENTAL` sync mode, and this field is set to true, the source is responsible for internally determining how it tracks which records are new or updated since the last sync.
* `default_cursor_field` - An array of keys to a field in the schema. If a source supports the `INCREMENTAL` sync mode, the source may optionally set this field. If this field is set, and the user does not override it with the `cursor_field` attribute in the `ConfiguredAirbyteStream` \(described below\), this field is used as the cursor. 

## ConfiguredAirbyteStream

This section documents the meaning of each field in a `ConfiguredAirbyteStream`.

* `stream` - The configured `AirbyteStream`.
* `sync_mode` - The sync mode used to sync that stream. The value in this field MUST be present in the `supported_sync_modes` array for the discovered `AirbyteStream` of this stream.
* `cursor_field` - An array of keys to a field in the schema that in the `INCREMENTAL` sync mode will be used to determine if a record is new or updated since the last sync.
  * If an `AirbyteStream` has `source_defined_cursor` set to `true`, the `cursor_field` attribute in `ConfiguredAirbyteStream` is ignored.
  * If an `AirbyteStream` defines a `default_cursor_field`, the `cursor_field` attribute in `ConfiguredAirbyteStream` is not required, but if it is set, it overrides the default value.
  * If an `AirbyteStream` does not define a `default_cursor_field` and has `source_defined_cursor` set to `false`, `ConfiguredAirbyteStream` must define a `cursor_field`.

## Logic for resolving the Cursor Field

This section documents how a cursor field is determined for a stream performing an `INCREMENTAL` sync.

* If `source_defined_cursor` in `AirbyteStream` is true, the source determines the cursor field internally. It cannot be overriden. If it is false, continue...
* If `cursor_field` in `ConfiguredAirbyteStream` is set, the source uses that field as the cursor. If it is not set, continue...
* If `default_cursor_field` in `AirbyteStream` is set, the sources use that field as the cursor. If it is not set, continue...
* Illegal - If `source_defined_cursor`, `cursor_field`, and `default_cursor_field` are all false, this is an invalid configuration.

