# Data Types in Records

AirbyteRecords are required to conform to the Airbyte type system. This means that all sources must produce schemas and records within these types, and all destinations must handle records that conform to this type system.

Because Airbyte's interfaces are JSON-based, this type system is realized using [JSON schemas](https://json-schema.org/). In order to work around some limitations of JSON schemas, we add an additional `airbyte_type` parameter to define more narrow types.

This type system does not constrain values. However, destinations may not fully support all values - for example, Avro-based destinations may reject numeric values outside the standard 64-bit representations, or databases may reject timestamps in the BC era.

## The types

This table summarizes the available types. See the [Specific Types](#specific-types) section for explanation of optional parameters.

| Airbyte type                                                   | JSON Schema                                                                               | Examples                                                                        |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| String                                                         | `{"type": "string""}`                                                                     | `"foo bar"`                                                                     |
| Boolean                                                        | `{"type": "boolean"}`                                                                     | `true` or `false`                                                               |
| Date                                                           | `{"type": "string", "format": "date"}`                                                    | `"2021-01-23"`, `"2021-01-23 BC"`                                               |
| Timestamp with timezone                                        | `{"type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone"}`    | `"2022-11-22T01:23:45.123456+05:00"`, `"2022-11-22T01:23:45Z BC"`               |
| Timestamp without timezone                                     | `{"type": "string", "format": "date-time", "airbyte_type": "timestamp_without_timezone"}` | `"2022-11-22T01:23:45"`, `"2022-11-22T01:23:45.123456 BC"`                      |
| Time without timezone                                          | `{"type": "string", "airbyte_type": "time_with_timezone"}`                                | `"01:23:45.123456"`, `"01:23:45"`                                               |
| Time with timezone                                             | `{"type": "string", "airbyte_type": "time_without_timezone"}`                             | `"01:23:45.123456+05:00"`, `"01:23:45Z"`                                        |
| Integer                                                        | `{"type": "integer"}` or `{"type": "number", "airbyte_type": "integer"}`                  | `42`                                                                            |
| Number                                                         | `{"type": "number"}`                                                                      | `1234.56`                                                                       |
| Array                                                          | `{"type": "array"}`; optionally `items`                                                   | `[1, 2, 3]`                                                                     |
| Object                                                         | `{"type": "object"}`; optionally `properties`                                             | `{"foo": "bar"}`                                                                |
| Union                                                          | `{"oneOf": [...]}`                                                                        |                                                                                 |ß

### Record structure
As a reminder, sources expose a `discover` command, which returns a list of [`AirbyteStreams`](https://github.com/airbytehq/airbyte/blob/111131a193359027d0081de1290eb4bb846662ef/airbyte-protocol/models/src/main/resources/airbyte_protocol/airbyte_protocol.yaml#L122), and a `read` method, which emits a series of [`AirbyteRecordMessages`](https://github.com/airbytehq/airbyte/blob/111131a193359027d0081de1290eb4bb846662ef/airbyte-protocol/models/src/main/resources/airbyte_protocol/airbyte_protocol.yaml#L46-L66). The type system determines what a valid `json_schema` is for an `AirbyteStream`, which in turn dictates what messages `read` is allowed to emit.

For example, a source could produce this `AirbyteStream` (remember that the `json_schema` must declare `"type": "object"` at the top level):
```json
{
  "name": "users",
  "json_schema": {
    "type": "object",
    "properties": {
      "username": {
        "type": "string"
      },
      "age": {
        "type": "integer"
      },
      "appointments": {
        "type": "array",
        "items": {
          "type": "string",
          "format": "date-time",
          "airbyte_type": "timestamp_with_timezone"
        }
      }
    }
  }
}
```
Along with this `AirbyteRecordMessage` (observe that the `data` field conforms to the `json_schema` from the stream):
```json
{
  "stream": "users",
  "data": {
    "username": "someone42",
    "age": 84,
    "appointments": ["2021-11-22T01:23:45+00:00", "2022-01-22T14:00:00+00:00"]
  },
  "emitted_at": 1623861660
}
```

The top-level `object` must conform to the type system. This [means](#objects) that all of the fields must also conform to the type system.

#### Nulls
Many sources cannot guarantee that all fields are present on all records. In these cases, sources should simply not list them as `required` fields. In most cases, sources do not need to list fields as required; by default, all fields are treated as nullable.

#### Unsupported types
Destinations must have handling for all types, but they are free to cast types to a convenient representation. For example, let's say a source discovers a stream with this schema:
```json
{
  "type": "object",
  "properties": {
    "appointments": {
      "type": "array",
      "items": {
        "type": "string",
        "format": "date-time",
        "airbyte_type": "timestamp_with_timezone"
      }
    }
  }
}
```
Along with records which contain data that looks like this:
```json
{"appointments": ["2021-11-22T01:23:45+00:00", "2022-01-22T14:00:00+00:00"]}
```

The user then connects this source to a destination that cannot natively handle `array` fields. The destination connector is free to simply JSON-serialize the array back to a string when pushing data into the end platform. In other words, the destination connector could behave as though the source declared this schema:
```json
{
  "type": "object",
  "properties": {
    "appointments": {
      "type": "string"
    }
  }
}
```
And emitted this record:
```json
{"appointments": "[\"2021-11-22T01:23:45+00:00\", \"2022-01-22T14:00:00+00:00\"]"}
```

Of course, destinations are free to choose the most convenient/reasonable representation for any given value. JSON serialization is just one possible strategy. For example, many SQL destinations will fall back to a native JSON type (e.g. Postgres' JSONB type, or Snowflake's VARIANT).

### Specific types
These sections explain how each specific type should be used.

#### Boolean
Boolean values are represented as native JSON booleans (i.e. `true` or `false`, case-sensitive). Note that "truthy" and "falsy" values are _not_ acceptable: `"true"`, `"false"`, `1`, and `0` are not valid booleans.

#### Dates and timestamps
Airbyte has five temporal types: `date`, `timestamp_with_timezone`, `timestamp_without_timezone`, `time_with_timezone`, and `time_without_timezone`. These are represented as strings with specific `format` (either `date` or `date-time`).

However, JSON schema does not have a built-in way to indicate whether a field includes timezone information. For example, given this JsonSchema:
```json
{
  "type": "object",
  "properties": {
    "created_at": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```
Both `{"created_at": "2021-11-22T01:23:45+00:00"}` and `{"created_at": "2021-11-22T01:23:45"}` are valid records.

The `airbyte_type` field resolves this ambiguity; sources producing timestamp-ish fields should choose either `timestamp_with_timezone` or `timestamp_without_timezone` (or time with/without timezone).

Many sources (which were written before this system was formalized) do not specify the timezone-ness of their fields. Destinations should default to using the `with_timezone` variant in these cases.

All of these must be represented as RFC 3339§5.6 strings, extended with BC era support. See the type definition descriptions for specifics.

#### Numeric values
The number and integer types can accept any value, without constraint on range. However, this is still subject to compatibility with the destination: the destination (or normalization) _may_ throw an error if it attempts to write a value outside the range supported by the destination warehouse / storage medium.

Airbyte does not currently support infinity/NaN values.

#### Arrays
Arrays contain 0 or more items, which must have a defined type. These types should also conform to the type system. Arrays may require that all of their elements be the same type (`"items": {whatever type...}`). They may instead require each element to conform to one of a list of types (`"items": [{first type...}, {second type...}, ... , {Nth type...}]`).

Note that Airbyte's usage of the `items` field is slightly different than JSON schema's usage, in which an `"items": [...]` actually constrains the element correpsonding to the index of that item (AKA tuple-typing). This is becase destinations may have a difficult time supporting tuple-typed arrays without very specific handling, and as such are permitted to somewhat loosen their requirements.

#### Objects
As with arrays, objects may declare `properties`, each of which should have a type which conforms to the type system.

#### Unions
Sources may want to mix different types in a single field, e.g. `"type": ["string", "object"]`. Destinations must handle this case, either using a native union type, or by finding a native type that can accept all of the source's types (this frequently will be `string` or `json`).

In some cases, sources may want to use multiple types for the same field. For example, a user might have a property which holds one of two object schemas. This is supported with JSON schema's  `oneOf` type. Note that many destinations do not currently support these types, and may not behave as expected.
