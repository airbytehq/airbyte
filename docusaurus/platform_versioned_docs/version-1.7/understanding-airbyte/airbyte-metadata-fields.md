# Airbyte metadata fields

In addition to the fields declared in a stream's schema, Airbyte destinations append additional columns to your data. These fields can aid in understanding your data and debugging errors.

## Available metadata fields

| Airbyte field            | Description                                                                                       | Column type             |
| ------------------------ | ------------------------------------------------------------------------------------------------- | ----------------------- |
| `_airbyte_raw_id`        | A random UUID assigned to each incoming record                                                    | String                  |
| `_airbyte_generation_id` | Incremented each time you execute a [refresh](https://docs.airbyte.com/operator-guides/refreshes) | String                  |
| `_airbyte_extracted_at`  | A timestamp for when Airbyte pulled the event from the data source                                | Timestamp with timezone |
| `_airbyte_loaded_at`     | Timestamp to indicate when Airbyte loaded the record into the destination                         | Timestamp with timezone |
| `_airbyte_meta`          | Additional information about the record; see [below](#the-_airbyte_meta-field)                    | Object                  |

Note that not all destinations populate the `_airbyte_loaded_at` field. It's typically only useful for destinations that execute [typing and deduping](https://docs.airbyte.com/using-airbyte/core-concepts/typing-deduping).

## The `_airbyte_meta` field

This field contains additional information about the record. Airbyte writes it as a JSON object. It has two fields.

- A `sync_id` field on this object. This ID has no inherent meaning, but increases monotonically across syncs.

- A `changes` field, which records any modifications that Airbyte performed on the record. For example, if a record contained a value which didn't match the stream's schema, the destination connector could write `null` to the destination and add an entry to the `changes` list.

Each entry in the `changes` list is itself an object. The
[Airbyte protocol](https://github.com/airbytehq/airbyte-protocol/blob/master/protocol-models/src/main/resources/airbyte_protocol/airbyte_protocol.yaml#L88) defines the schema for these objects, as the `AirbyteRecordMessageMetaChange` struct.

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

- Airbyte wrote this record during sync 1234
- Airbyte nulled the `foo` column because it wasn't a valid value for the destination

## Connectors that Predate Destinations V2

Destinations that predate [Destinations V2](https://docs.airbyte.com/release_notes/upgrading_to_destinations_v2/) have a different set of metadata fields. Some fields aren't supported pre-DV2, and other fields are present under a different name.

| Airbyte field         | Destinations V2 equivalent |
| --------------------- | -------------------------- |
| `_airbyte_ab_id`      | `_airbyte_raw_id`          |
| `_airbyte_emitted_at` | `_airbyte_extracted_at`    |
| `_airbyte_loaded_at`  | `_airbyte_loaded_at`       |
|                       |                            |
