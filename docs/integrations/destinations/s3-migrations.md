# S3 Migration Guide

## Upgrading to 1.0.0

This version introduces changes to the schema of data written to S3, which make it isomorphic to our [V2 certified database destinations](https://docs.airbyte.com/release_notes/upgrading_to_destinations_v2/#what-is-destinations-v2), as well as various improvements to format conversion.

* Conversion failures are captured: values not matching the client schema will no longer break syncs using Avro or Parquet formats.
* Changes introduced by the source or platform, such as NULLing bad values or truncating long ones, are visible in the metadata.
* There is improved handling of various types in Avro and Parquet formats, including simplification of date and time types, more human-readable schemaless objects and arrays, and better support for unions in Parquet.
* Sync and generation ids are made available, providing more information for debugging.

## Schema Changes

The schema changes are as follows:

| Old field name        | New field name           | JSON Type          | Avro Type                                                 | Parquet Type                                 | Description                                                                                            |
|-----------------------|--------------------------|--------------------|-----------------------------------------------------------|----------------------------------------------|--------------------------------------------------------------------------------------------------------|
| `_airbyte_ab_id`      | `_airbyte_raw_id`        | string (UUID)      | `{ "type": "string", "logicalType": "uuid" }`             | `String`                                     | Airbyte-added unique identifier.                                                                       |
| `_airbyte_emitted_at` | `_airbyte_extracted_at`  | integer (epoch ms) | `{ "type": "string", "logicalType": "timestamp-millis" }` | `Int64(logicalType=Timestamp(Milliseconds))` | Time at which the data was extracted from the source.                                                  |
| [NONEXISTENT]         | `_airbyte_generation_id` | integer            | `{ "type": "long" }`                                      | `Int64`                                      | Monotonically-increasing refresh id, if applicable.                                                    |
| [NONEXISTENT]         | `_airbyte_meta`          | object (see below) | Record (see below)                                        | Record (see below)                           | Additional metadata, including change data capture info and sync id.                                   |
| `_airbyte_data`       | [UNCHANGED]              | optional object    | (from client schema)                                      | (from client schema)                         | Data payload when [flattening is disabled](https://docs.airbyte.com/integrations/destinations/s3#csv). |

The `_airbyte_meta` field is an object that currently has one field:

| Field Name     | JSON Type | Description                                                                                |
|----------------|-----------|--------------------------------------------------------------------------------------------|

| `changes`      | list      | A record of any changes Airbyte made to the data for compatibility and/or to handle errors |
| `sync_id`      | integer   | Monotonically-increasing integer representing the current sync                             |

The `changes` field is a list of objects, each of which represents a change to the data. Each object has the following fields:

| Field Name | JSON Type* | Description                                                                        |
|------------|------------|------------------------------------------------------------------------------------|
| `field`    | string     | The name of the field that was affected                                            |
| `change`   | string     | The type of change (currently only `NULLED` or `TRUNCATED`)                        |
| `reason`   | string     | The reason for the change, including its origin (source, platform, or destination) |

These schemas are subject to change, however any change that is not backward compatible (ie, additive) will be accompanied by a breaking change notice.

## Data Changes

This version introduces changes to the data types used when writing to S3 in Avro or Parquet. The changes are as follows:

### Primitive Types

All primitive types are unchanged:

| Airbyte JSON Schema Type | Old Avro Type            | Old Parquet Type      | New Avro Type   | New Parquet Type |
|--------------------------|--------------------------|-----------------------|-----------------|------------------|
| string                   | `["null", "string"]`     | `Optional String`     | [UNCHANGED]     | [UNCHANGED]      |
| boolean                  | `["null", "boolean"]`    | `Optional Boolean`    | [UNCHANGED]     | [UNCHANGED]      |
| integer                  | `["null", "long"]`       | `Optional Int64`      | [UNCHANGED]     | [UNCHANGED]      |
| number                   | `["null", "double"]`     | `Optional Double`     | [UNCHANGED]     | [UNCHANGED]      |

### Date and Time Types

This change introduces [simplification of the handling of dates, times, and timestamps in Parquet and Avro](https://github.com/airbytehq/airbyte-internal-issues/issues/8973). Date and time types were stored in Avro as unions of integral logical types and strings, which in Parquet were represented as disjoint records. In practice, the date and time types were always converted, making the unions redundant. The resulting disjoint records were confusing.

Now all time types are converted to integral logical types. Values that cannot be converted will be nulled and tracked in `_airbyte_meta.changes[]`. 

#### Resulting Avro Changes

Avro users should only see changes at the schema level, the resulting data will appear the same.

| Airbyte Time Type            | Old Avro Type                                                               | New Avro Type                                  |  
|------------------------------|-----------------------------------------------------------------------------|------------------------------------------------|
| date                         | `["null", { "type": "int", "logicalType": "date" }, "string"]`              | `[null, int(logicalType="date")]`              |
| time without timezone        | `["null", { "type": "long", "logicalType": "time-micros" }, "string"]`      | `[null, long(logicalType="time-micros")]`      |
| time with timezone           | `["null", { "type": "long", "logicalType": "time-micros" }, "string"]`      | `[null, long(logicalType="time-micros")]`      |
| timestamp without timezone   | `["null", { "type": "long", "logicalType": "timestamp-micros" }, "string"]` | `[null, long(logicalType="timestamp-micros")]` |
| timestamp with timezone      | `["null", { "type": "long", "logicalType": "timestamp-micros" }, "string"]` | `[null, long(logicalType="timestamp-micros")]` |

#### Resulting Parquet Changes

| Airbyte Time Type             | Old Parquet Type                                                                                              | New Parquet Type                                       | 
|-------------------------------|---------------------------------------------------------------------------------------------------------------|--------------------------------------------------------|
| date                          | `Optional Record { member0: Optional Int32(logical_type=Date), member1: Optional String }`                    | `Optional Int32(logical_type=Date)`                    |
| time without timezone         | `Optional Record { member0: Optional Int64(logical_type=Time(Microseconds)), member1: Optional String }`      | `Optional Int64(logical_type=Time(Microseconds))`      |
| time with timezone            | `Optional Record { member0: Optional Int64(logical_type=Time(Microseconds)), member1: Optional String }`      | `Optional Int64(logical_type=Time(Microseconds))`      |
| timestamp without timezone    | `Optional Record { member0: Optional Int64(logical_type=Timestamp(Microseconds)), member1: Optional String }` | `Optional Int64(logical_type=Timestamp(Microseconds))` |
| timestamp with timezone       | `Optional Record { member0: Optional Int64(logical_type=Timestamp(Microseconds)), member1: Optional String }` | `Optional Int64(logical_type=Timestamp(Microseconds))` |

Note: the times and timestamps with timezones are converted to UTC. In Parquet, the field metadata `is_adjusted_to_utc` will always be `true`.

#### Time of Day Conversion Bugfix

Formerly, for the Airbyte type `time_of_day_with_timezone`, [timezones were not respected when converting](https://github.com/airbytehq/airbyte/issues/43019). This has been fixed.

| Input Data         | Old Output Data              | New Output Data              |
|--------------------|------------------------------|------------------------------|
| `"12:00:00-01:00"` | `43200000000` (12:00:00 UTC) | `46800000000` (13:00:00 UTC) |
| `"04:00:00+02:00"` | `14400000000` (04:00:00 UTC) | `720000000` (02:00:00 UTC)   |
| `"04:00:00+05:30"` | `14400000000` (04:00:00 UTC) | `81000000000` (22:30:00 UTC) |

### Object Types

Formerly, in both Avro and Parquet formats, objects without schemas (`"type": "object"` without `properties`), and properties not listed in the `properties` field, were accumulated in `_airbyte_additional_properties`. The new behavior is

* undocumented fields in object with schemas are silently dropped
* objects without schemas are serialized into a JSON string
* `_airbyte_additional_properties` is dropped entirely

For example, the following input schemas and data will result in the following outputs:

| Input Schema                                                          | Input Data                     | Output Schema                                                         | Output Data                          |
|-----------------------------------------------------------------------|--------------------------------|-----------------------------------------------------------------------|--------------------------------------|
| `{ "type": "object", "properties": { "id": { "type": "integer" } } }` | `{ "id": 1, "name": "Alice" }` | `{ "type": "object", "properties": { "id": { "type": "integer" } } }` | `{ "id": 1 }`                        |
| `{ "type": "object" }`                                                | `{ "id": 1, "name": "Alice" }` | `{ "type": "string" }`                                                | `"{\"id\": 1, \"name\": \"Alice\"}"` |

Note: dropped fields will not appear in `_airbyte_meta.changes[]`. Additionally, n object with null or empty properties (`"properties": {}`) will be treated as a schemaless object. This is because this usually indicates an upstream source is failing to report its schema properly, and the data is not actually extraneous.


### Array Types

Formerly, arrays without types (`"type": "array"` with no `items` field) were converted to native arrays of string serializations of the underlying types. The same behavior was applied to arrays of union types (`{ "type": "array", "items": { "oneOf": [ /* various types */ ] }`).

Now:

* Arrays without types are serialized into JSON array strings.
* Arrays of unions are treated as arrays of mixed types.

For example, the following input schemas and data formerly resulted in:

| Input Schema                                                                           | Input Data     | Old Output Schema                                    | Old Output Data  |
|----------------------------------------------------------------------------------------|----------------|------------------------------------------------------|------------------|
| `{ "type": "array", "items": { "type": "integer" } }`                                  | `[1, "Alice"]` | `{ "type": "array", "items": ["null", "integer"] }`  | [SYNC FAILED]    |
| `{ "type": "array" }`                                                                  | `[1, "Alice"]` | `{ "type": "array", "items": [ "null", "string" ] }` | `["1", "Alice"]` |
| `{ "type": "array", "items": { "oneOf": [ {"type": "integer", "type": "string"} ] } }` | `[1, "Alice"]` | `{ "type": "array", "items": [ "null", "string" ] }` | `["1", "Alice"]` |
| `{ "type": "array", "items": { "oneOf": [ {"type": "integer", "type": "string"} ] } }` | `[1, false]`   | `{ "type": "array", "items": [ "null", "string" ] }` | `["1", "false"]` |

Now:

| Input Schema                                                                           | Input Data     | New Output Schema                                               | New Output Data    |
|----------------------------------------------------------------------------------------|----------------|-----------------------------------------------------------------|--------------------|
| `{ "type": "array", "items": { "type": "integer" } }`                                  | `[1, "Alice"]` | `{ "type": "array", "items": ["null", "integer"] }`             | `[1, null*]`       |
| `{ "type": "array" }`                                                                  | `[1, "Alice"]` | `{ "type": "string" }`                                          | `"[1, \"Alice\"]"` |
| `{ "type": "array", "items": { "oneOf": [ {"type": "integer", "type": "string"} ] } }` | `[1, "Alice"]` | `{ "type": "array", "items": [ "null", "integer", "string" ] }` | `[1, "Alice"]`     |
| `{ "type": "array", "items": { "oneOf": [ {"type": "integer", "type": "string"} ] } }` | `[1, false]`   | `{ "type": "array", "items": [ "null", "integer", "string" ] }` | `[1, null*]`       |

*The nulled fields represent conversion failures and will appear in `_airbyte_meta.changes[]`.

This behavior will be applied to both Avro and Parquet formats.

### Union Types (Parquet Only)

#### Disjoint Record Improvements

Formerly, unions in Parquet were represented as anonymous disjoint records. For example:

| Airbyte Union Type                                                                                                                     | Old Parquet Type                                                                                                         |
|----------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| `{"oneOf": [ {"type": "integer"}, {"type": "string"} ] }`                                                                              | `Optional Record { member0: Optional Int32, member1: Optional String }`                                                  |
| `{"oneOf": [ {"type": "boolean"}, {"type": "object", "properties": { "id": { "type": "integer" }, "name": { "type": string" } } } ] }` | `Optional Record { member0: Optional Boolean, member1: Optional Record { id: Optional Uint32, name: Optional String } }` |

Now unions will be represented as typed disjoint records with named fields. For example:

| Airbyte Union Type                                                                                                                     | New Parquet Type                                                                                                                      |
|----------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| `{"oneOf": [ {"type": "integer"}, {"type": "string"} ] }`                                                                              | `Optional Record { type: String, integer: Optional Int32, string: Optional String }`                                                  |
| `{"oneOf": [ {"type": "boolean"}, {"type": "object", "properties": { "id": { "type": "integer" }, "name": { "type": string" } } } ] }` | `Optional Record { type: String, boolean: Optional Boolean, object: Optional Record { id: Optional Uint32, name: Optional String } }` |

Where
* Only one field will always be set.
* The `type` field will always be set and always be equal to the name of the field that was set.

Following the examples above:

| Input Data                    | New Output Data                                                 |
|-------------------------------|-----------------------------------------------------------------|
| `1`                           | `{ "type": "integer", "integer": 1 }`                           |
| `{"id": 10, "name": "Alice"}` | `{ "type": "object", "object": { "id": 10, "name": "Alice" } }` |

#### Disjoint Record Type Names

The following type and field names will be used for each Airbyte type:

| Airbyte Type                                                                               | Parquet Type                                                           | Field Name                   |
|--------------------------------------------------------------------------------------------|------------------------------------------------------------------------|------------------------------|
| `{"type": "integer" }`                                                                     | `Optional Int64`                                                       | `integer`                    |
| `{"type": "string" }`                                                                      | `Optional String`                                                      | `string`                     |
| `{"type": "boolean" }`                                                                     | `Optional Boolean`                                                     | `boolean`                    |
| `{"type": "object" }`                                                                      | `Optional Record`                                                      | `object`                     |
| `{"type": "array" }`                                                                       | `Optional List`                                                        | `array`                      |
| `{"type": "string", "format": "date" }`                                                    | `Optional Int32(logicalType=Date)`                                     | `date`                       |
| `{"type": "string", "format": "time", "airbyte_type": "time_with_timezone" }`              | `Optional Int64(Optional Int64(logical_type=Time(Microseconds))`       | `time_with_timezone`         |
| `{"type": "string", "format": "time", "airbyte_type": "time_without_timezone" }`           | `Optional Int64(Optional Int64(logical_type=Time(Microseconds))`       | `time_without_timezone`      |
| `{"type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone" }`    | `Optional Int64(logical_type=Timestamp(Microseconds)))`                | `timestamp_with_timezone`    |
| `{"type": "string", "format": "date-time", "airbyte_type": "timestamp_without_timezone" }` | `Optional Int64(Optional Int64(logical_type=Timestamp(Microseconds)))` | `timestamp_without_timezone` |

#### Merging Like Options in Unions

The above behavior applies only to unions of distinct types. Unions of the same type will continue to be merged. If the result is a single option, the union will be demoted to a field of that type. For example:

| Airbyte Union Type                                                              | Avro Type                       | Parquet Type                                                                                  |
|---------------------------------------------------------------------------------|---------------------------------|-----------------------------------------------------------------------------------------------|
| `{"oneOf": [ {"type": "integer"}, {"type": "integer"} ] }`                      | `["null", "integer"]`           | `Optional Int64`                                                                              |
| `{"oneOf": [ {"type": "integer"}, {"type": "string"}, {"type": "integer" } ] }` | `["null", "integer", "string"]` | `Optional Record { type: Optional String, integer: Optional Int64, string: Optional String }` |

Unions of objects will continue to be merged into a single object with a union schema. If this is not possible due to field type conflicts, an exception will be thrown and the sync will fail.

| Object 1 Properties           | Object 2 Properties             | Merged Object                                 |
|-------------------------------|---------------------------------|-----------------------------------------------|
| `{id: integer}`               | `{name: string}`                | `{id: integer, name: string}`                 |
| `{id: integer, name: string}` | `{id: integer, birthday: date}` | `{id: integer, name: string, birthday: date}` |
| `{id: integer}`               | `{id: string}`                  | [SYNC FAILED]                                 |

Unions of arrays with different item schemas continue not to be supported.