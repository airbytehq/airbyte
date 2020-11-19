# AirbyteCatalog & ConfiguredAirbyteCatalog

## Overview
An `AirbyteCatalog` is a struct that is produced by the `discover` action of a source. It is a list of `AirbyteStream`s. Each `AirbyteStream` describes the data available to be synced from the source. After a source produces an `AirbyteCatalog` or `AirbyteStream`, they should be treated as read only. An `ConfiguredAirbyteCatalog` is a list of `ConfiguredAirbyteStream`s. Each `ConfiguredAirbyteStream` describes how to sync a given stream.

## AirbyteStream
This section will document the meaning of each field in an `AirbyteStream`
* `json_schema` - This field contains a [JsonSchema](https://json-schema.org/understanding-json-schema) representation of the schema of the stream.
* `supported_sync_modes` - The sync modes that the stream supports. By default, all sources support `FULL_REFRESH`. Even if this array is empty, it can be assumed that a source supports `FULL_REFRESH`. The allowed sync modes are `FULL_REFRESH` and `INCREMENTAL`.
* `default_cursor_field` - If a source supports the `INCREMENTAL` sync mode, it may, optionally, set this field. It is an array of keys to a field in the schema. If it set, by default, this field will be used to determine if a record is new or updated since the last sync.
    * e.g. if the structure of a stream is `{ value: 2, metadata { updated_at: 2020-11-01 } }` the `default_cursor_field` might be `["metdata", "updated_at]`.

## ConfiguredAirbyteStream
This section will document the meaning of each field in an `ConfiguredAirbyteStream`
* `json_schema` - This field contains a [JsonSchema](https://json-schema.org/understanding-json-schema) representation of the schema of the stream.
* `sync_mode` - The sync mode that will be used to sync that stream. The value in this field MUST be present in the `supported_sync_modes` array for the discovered `AirbyteStream` of this stream.
* `cursor_field` - This field is an array of keys to a field in the schema that in the `INCREMENTAL` sync mode will be used to determine if a record is new or updated since the last sync.
    * If a stream is using the `INCREMENTAL` sync mode, the `ConfiguredAirbyteStream` must set this field (even if the source has a `default_cursor_field`).
    * If the stream is not using `INCREMENTAL` then this field is ignored.
