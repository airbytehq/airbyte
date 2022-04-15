# AirbyteCatalog Reference

## Overview

An `AirbyteCatalog` is a struct that is produced by the `discover` action of a source. It is a list of `AirbyteStream`s. Each `AirbyteStream` describes the data available to be synced from the source. After a source produces an `AirbyteCatalog` or `AirbyteStream`, they should be treated as read only. A `ConfiguredAirbyteCatalog` is a list of `ConfiguredAirbyteStream`s. Each `ConfiguredAirbyteStream` describes how to sync an `AirbyteStream`.

## Cursor

* The cursor is how sources track which records are new or updated since the last sync. 
* A "cursor field" is the field that is used as a comparable for making this determinations.
  * If a configuration requires a cursor field, it requires an array of strings that serves as a path to the desired field. e.g. if the structure of a stream is `{ value: 2, metadata: { updated_at: 2020-11-01 } }` the `default_cursor_field` might be `["metadata", "updated_at"]`.

## AirbyteStream

This section will document the meaning of each field in an `AirbyteStream`

* `json_schema` - This field contains a [JsonSchema](https://json-schema.org/understanding-json-schema) representation of the schema of the stream.
* `supported_sync_modes` - The sync modes that the stream supports. By default, all sources support `FULL_REFRESH`. Even if this array is empty, it can be assumed that a source supports `FULL_REFRESH`. The allowed sync modes are `FULL_REFRESH` and `INCREMENTAL`.
* `source_defined_cursor` - If a source supports the `INCREMENTAL` sync mode, and it sets this field to true, it is responsible for determining internally how it tracks which records in a source are new or updated since the last sync. When set to `true`, `default_cursor_field` should also be set.
* `default_cursor_field` - If a source supports the `INCREMENTAL` sync mode, it may, optionally, set this field. If this field is set, and the user does not override it with the `cursor_field` attribute in the `ConfiguredAirbyteStream` \(described below\), this field will be used as the cursor. It is an array of keys to a field in the schema.

## ConfiguredAirbyteStream

This section will document the meaning of each field in an `ConfiguredAirbyteStream`

* `stream` - This field contains the `AirbyteStream` that it is configured.
* `sync_mode` - The sync mode that will be used to sync that stream. The value in this field MUST be present in the `supported_sync_modes` array for the discovered `AirbyteStream` of this stream.
* `cursor_field` - This field is an array of keys to a field in the schema that in the `INCREMENTAL` sync mode will be used to determine if a record is new or updated since the last sync.
  * If an `AirbyteStream` has `source_defined_cursor` set to `true`, then the `cursor_field` attribute in `ConfiguredAirbyteStream` will be ignored.
  * If an `AirbyteStream` defines a `default_cursor_field`, then the `cursor_field` attribute in `ConfiguredAirbyteStream` is not required, but if it is set, it will override the default value.
  * If an `AirbyteStream` does not define a `cursor_field` or a `default_cursor_field`, then `ConfiguredAirbyteStream` must define a `cursor_field`.

## Logic for resolving the Cursor Field

This section lays out how a cursor field is determined in the case of a Stream that is doing an `incremental` sync.

* If `source_defined_cursor` in `AirbyteStream` is true, then the source determines the cursor field internally. It cannot be overriden. If it is false, continue...
* If `cursor_field` in `ConfiguredAirbyteStream` is set, then the source uses that field as the cursor. If it is not set, continue...
* If `default_cursor_field` in `AirbyteStream` is set, then the sources use that field as the cursor. If it is not set, continue...
* Illegal - If `source_defined_cursor`, `cursor_field`, and `default_cursor_field` are all falsey, this is an invalid configuration.

