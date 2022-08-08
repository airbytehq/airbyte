# Data Types in Records

AirbyteRecords are required to conform to the Airbyte type system. This means that all sources must produce schemas and records within these types, and all destinations must handle records that conform to this type system.

Because Airbyte's interfaces are JSON-based, this type system is realized using [JSON schemas](https://json-schema.org/). In order to work around some limitations of JSON schemas, schemas may declare an additional `airbyte_type` annotation. This is used to disambiguate certain types that JSON schema does not explicitly differentiate between. See the [specific types](#specific-types) section for details.

This type system does not (generally) constrain values. Sources may declare streams using additional features of JSON schema (such as the `length` property for strings), but those constraints will be ignored by all other Airbyte components. The exception is in numeric types; `integer` and `number` fields must be representable within 64-bit primitives.

## The types

This table summarizes the available types. See the [Specific Types](#specific-types) section for explanation of optional parameters.

| Airbyte type                                                   | JSON Schema                                                                              | Examples                                                                        |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| String                                                         | `{"type": "string"}`                                                                     | `"foo bar"`                                                                     |
| Date                                                           | `{"type": "string", "format": "date"}`                                                   | `"2021-01-23"`                                                                  |
| Datetime with timezone                                         | `{"type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone"}`    | `"2022-11-22T01:23:45+05:00"`                                                   |
| Datetime without timezone                                      | `{"type": "string", "format": "date-time", "airbyte_type": "timestamp_without_timezone"}` | `"2022-11-22T01:23:45"`                                                         |
| Integer                                                        | `{"type": "integer"}`                                                                    | `42`                                                                            |
| Big integer (unrepresentable as a 64-bit two's complement int) | `{"type": "string", "airbyte_type": "big_integer"}`                                      | `"12345678901234567890123456789012345678"` |
| Number                                                         | `{"type": "number"}`                                                                     | `1234.56`                                                                       |
| Big number (unrepresentable as a 64-bit IEEE 754 float)        | `{"type": "string", "airbyte_type": "big_number"}`                                       | `"1,000,000,...,000.1234"` with 500 0's                                         |
| Array                                                          | `{"type": "array"}`; optionally `items` and `additionalItems`                            | `[1, 2, 3]`                                                                     |
| Object                                                         | `{"type": "object"}`; optionally `properties` and `additionalProperties`                 | `{"foo": "bar"}`                                                                |
| Untyped (i.e. any value is valid)                              | `{}`                                                                                     |                                                                                 |
| Union                                                          | `{"anyOf": [...]}` or `{"oneOf": [...]}`                                                 |                                                                                 |

Note that some of these may be destination-dependent. For example, Snowflake `NUMERIC` columns can be at most 38 digits wide, but Postgres `NUMERIC` columns may have up to 131072 digits before the decimal point.

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
        "items": "string",
        "airbyte_type": "timestamp_with_timezone"
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
Many sources cannot guarantee that all fields are present on all records. As such, they may replace the `type` entry in the schema with `["null", "the_real_type"]`. For example, this schema is the correct way for a source to declare that the `age` field may be missing from some records:
```json
{
  "type": "object",
  "properties": {
    "username": {
      "type": "string"
    },
    "age": {
      "type": ["null", "integer"]
    }
  }
}
```
This would then be a valid record:
```json
{"username": "someone42"}
```

Nullable fields are actually the more common case, but this document omits them in other examples for the sake of clarity.

#### Unsupported types
As an escape hatch, destinations which cannot handle a certain type should just fall back to treating those values as strings. For example, let's say a source discovers a stream with this schema:
```json
{
  "type": "object",
  "properties": {
    "appointments": {
      "type": "array",
      "items": {
        "type": "string",
        "airbyte_type": "timestamp_with_timezone"
      }
    }
  }
}
```
Along with records that look like this:
```json
{"appointments": ["2021-11-22T01:23:45+00:00", "2022-01-22T14:00:00+00:00"]}
```

The user then connects this source to a destination that cannot handle `array` fields. The destination connector should simply JSON-serialize the array back to a string when pushing data into the end platform. In other words, the destination connector should behave as though the source declared this schema:
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

### Specific types

#### Dates and timestamps
Airbyte has three temporal types: `date`, `timestamp_with_timezone`, and `timestamp_without_timezone`. These are represented as strings with specific `format` (either `date` or `date-time`).

However, JSON schema does not have a built-in way to indicate whether a field includes timezone information. For example, given the schema
```json
{
  "type": "object",
  "properties": {
    "created_at": {
      "type": "string",
      "format": "date-time",
      "airbyte_type": "timestamp_with_timezone"
    }
  }
}
```
Both `{"created_at": "2021-11-22T01:23:45+00:00"}` and `{"created_at": "2021-11-22T01:23:45"}` are valid records. The `airbyte_type` annotation resolves this ambiguity; sources producing `date-time` fields **must** set the `airbyte_type` to either `timestamp_with_timezone` or `timestamp_without_timezone`.

#### Unrepresentable numbers
64-bit integers and floating-point numbers (AKA `long` and `double`) cannot represent every number in existence. The `big_integer` and `big_number` types indicate that the source may produce numbers outside the ranges of `long` and `double`s.

Note that these are declared as `"type": "string"`. This is intended to make parsing more safe by preventing accidental overflow/loss-of-precision.

#### Arrays
Arrays contain 0 or more items, which must have a defined type. These types should also conform to the type system. Arrays may require that all of their elements be the same type (`"items": {whatever type...}`), or they may require specific types for the first N entries (`"items": [{first type...}, {second type...}, ... , {Nth type...}]`, AKA tuple-type).

Tuple-typed arrays can configure the type of any additional elements using the `additionalItems` field; by default, any type is allowed. They may also pass a boolean to enable/disable additional elements, with `"additionalItems": true` being equivalent to `"additionalItems": {}` and `"additionalItems": false` meaning that only the tuple-defined items are allowed.

Destinations may have a difficult time supporting tuple-typed arrays without very specific handling, and as such are permitted to somewhat loosen their requirements. For example, many Avro-based destinations simply declare an array of a union of all allowed types, rather than requiring the correct type in each position of the array.

#### Objects
As with arrays, objects may declare `properties`, each of which should have a type which conforms to the type system. Objects may additionally accept `additionalProperties`, as `true` (any type is acceptable), a specific type (all additional properties must be of that type), or `false` (no additonal properties are allowed).

#### Unions
In some cases, sources may want to use multiple types for the same field. For example, a user might have a property which holds either an object, or a `string` explanation of why that data is missing. This is supported with JSON schema's  `oneOf` and `anyOf` types.

#### Untyped values
In some unusual cases, a property may not have type information associated with it. This is represented by the empty schema `{}`. As many destinations do not allow untyped data, this will frequently trigger the [string-typed escape hatch](#unsupported-types).
