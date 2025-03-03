# Airbyte Metadata fields

In addition to the fields declared in a stream's schema, Airbyte destinations
append additional columns to your data. These fields are intended to aid in
understanding your data, as well as debugging various errors.

| Airbyte field            | Description                                                                                       | Column type               |
| ------------------------ | ------------------------------------------------------------------------------------------------- | ------------------------- |
| `_airbyte_raw_id`        | A random UUID assigned to each incoming record                                                    | String                    |
| `_airbyte_generation_id` | Incremented each time a [refresh](https://docs.airbyte.com/operator-guides/refreshes) is executed | String                    |
| `_airbyte_extracted_at`  | A timestamp for when the event was pulled from the data source                                    | Timestamp with timezone   |
| `_airbyte_loaded_at`     | Timestamp to indicate when the record was loaded into the destination                             | Timestamp with timezone   |
| `_airbyte_meta`          | Additional information about the record; see [below](#the-_airbyte_meta-field)                    | Object                    |

Note that not all destinations populate the `_airbyte_loaded_at` field; it is
typically only useful for destinations that execute [typing and deduping](https://docs.airbyte.com/using-airbyte/core-concepts/typing-deduping).

## The `_airbyte_meta` field

This field contains additional information about the record. It is written as a JSON object.
All records have a `sync_id` field on this object. This ID has no inherent meaning, but is guaranteed
to increase monotonically across syncs.

There is also a `changes` field, which is used to record any modifications that Airbyte performed on
the record. For example, if a record contained a value which did not match the stream's schema,
the destination connector could write `null` to the destination and add an entry to the `changes`
list.

Each entry in the `changes` list is itself an object; the schema for these objects is defined in the
[Airbyte protocol](https://github.com/airbytehq/airbyte-protocol/blob/master/protocol-models/src/main/resources/airbyte_protocol/airbyte_protocol.yaml#L88),
as the `AirbyteRecordMessageMetaChange` struct.

For example, if you saw this value in `_airbyte_meta`:
```json
{
  "sync_id": 1234,
  "changes": [
    {
      "field": "foo",
      "change": "NULLED",
      "reason": "DESTINATION_SERIALIZATION_ERROR"
    }
  ]
}
```
You would know:
* This record was written during sync 1234
* The `foo` column was nulled out, because it was not a valid value for the destination

## Pre-Destinations V2

Destinations which predate [Destinations V2](https://docs.airbyte.com/release_notes/upgrading_to_destinations_v2/)
have a different set of metadata fields: some fields are not supported pre-DV2,
and other fields are present under a different name.

| Airbyte field         | Destinations V2 equivalent |
| --------------------- | -------------------------- |
| `_airbyte_ab_id`      | `_airbyte_raw_id`          |
| `_airbyte_emitted_at` | `_airbyte_extracted_at`    |
| `_airbyte_loaded_at`  | `_airbyte_loaded_at`       |
