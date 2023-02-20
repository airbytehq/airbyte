# Data Types in Records

AirbyteRecords are required to conform to the Airbyte type system. This means that all sources must produce schemas and records within these types, and all destinations must handle records that conform to this type system.

Because Airbyte's interfaces are JSON-based, this type system is realized using [JSON schemas](https://json-schema.org/). In order to work around some limitations of JSON schemas, we define our own types - see [well_known_types.yaml](https://github.com/airbytehq/airbyte/blob/111131a193359027d0081de1290eb4bb846662ef/airbyte-protocol/protocol-models/src/main/resources/airbyte_protocol/well_known_types.yaml). Sources should use `$ref` to reference these types, rather than directly defining JsonSchema entries.

In an older version of the protocol, we relied on an `airbyte_type` property in schemas. This has been replaced by the well-known type schemas. All "old-style" types map onto well-known types. For example, a legacy connector producing a field of type `{"type": "string", "airbyte_type": "timestamp_with_timezone"}` is treated as producing `{"$ref": "WellKnownTypes.json#/definitions/TimestampWithTimezone"}`.

This type system does not (generally) constrain values. The exception is in numeric types; `integer` and `number` fields must be representable within 64-bit primitives.

## The types

This table summarizes the available types. See the [Specific Types](#specific-types) section for explanation of optional parameters.

| Airbyte type                                                   | JSON Schema                                                              | Examples                                                                        |
| -------------------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| String                                                         | `{"$ref": "WellKnownTypes.json#/definitions/String"}`                     | `"foo bar"`                                                                     |
| Binary data, represented as a base64 string                    | `{"$ref": "WellKnownTypes.json#/definitions/BinaryData"}`                 | `"Zm9vIGJhcgo="`                                                                |
| Boolean                                                        | `{"$ref": "WellKnownTypes.json#/definitions/Boolean"}`                    | `true` or `false`                                                               |
| Date                                                           | `{"$ref": "WellKnownTypes.json#/definitions/Date"}`                       | `"2021-01-23"`, `"2021-01-23 BC"`                                               |
| Timestamp with timezone                                        | `{"$ref": "WellKnownTypes.json#/definitions/TimestampWithTimezone"}`      | `"2022-11-22T01:23:45.123456+05:00"`, `"2022-11-22T01:23:45Z BC"`               |
| Timestamp without timezone                                     | `{"$ref": "WellKnownTypes.json#/definitions/TimestampWithoutTimezone"}`   | `"2022-11-22T01:23:45"`, `"2022-11-22T01:23:45.123456 BC"`                      |
| Time with timezone                                             | `{"$ref": "WellKnownTypes.json#/definitions/TimeWithTimezone"}`           | `"01:23:45.123456+05:00"`, `"01:23:45Z"`                                        |
| Time without timezone                                          | `{"$ref": "WellKnownTypes.json#/definitions/TimeWithoutTimezone"}`        | `"01:23:45.123456"`, `"01:23:45"`                                               |
| Integer                                                        | `{"$ref": "WellKnownTypes.json#/definitions/Integer"}`                    | `42`, `NaN`, `Infinity`, `-Infinity`                                            |
| Number                                                         | `{"$ref": "WellKnownTypes.json#/definitions/Number"}`                     | `1234.56`, `NaN`, `Infinity`, `-Infinity`                                       |
| Array                                                          | `{"type": "array"}`; optionally `items` and `additionalItems`            | `[1, 2, 3]`                                                                     |
| Object                                                         | `{"type": "object"}`; optionally `properties` and `additionalProperties` | `{"foo": "bar"}`                                                                |
| Union                                                          | `{"anyOf": [...]}` or `{"oneOf": [...]}`                                 |                                                                                 |

Note that some of these may be destination-dependent. For example, different warehouses may impose different limits on string column length.

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
        "$ref": "WellKnownTypes.json#/definitions/String"
      },
      "age": {
        "$ref": "WellKnownTypes.json#/definitions/Integer"
      },
      "appointments": {
        "type": "array",
        "items": {
          "$ref": "WellKnownTypes.json#/definitions/TimestampWithTimezone"
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
As an escape hatch, destinations which cannot handle a certain type should just fall back to treating those values as strings. For example, let's say a source discovers a stream with this schema:
```json
{
  "type": "object",
  "properties": {
    "appointments": {
      "type": "array",
      "items": {
        "$ref": "WellKnownTypes.json#/definitions/TimestampWithTimezone"
      }
    }
  }
}
```
Along with records which contain data that looks like this:
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

Of course, destinations are free to choose the most convenient/reasonable stringification for any given value. JSON serialization is just one possible strategy.

### Specific types
#### Boolean
Airbyte boolean type represents one of the two values `true` or `false` and they are are lower case. Note that values that evaluate to true or false such as data type String `"true"` or `"false"` or Integer like `1` or `0` are not accepted by the Schema.

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

The protocol's type definitions resolve this ambiguity; sources producing timestamp-ish fields **must** choose either `TimestampWithTimezone` or `TimestampWithoutTimezone` (or time with/without timezone).

All of these must be represented as RFC 3339§5.6 strings, extended with BC era support. See the type definition descriptions for specifics.

#### Numeric values
Integers are extended to accept infinity/-infinity/NaN values. Most sources will not actually produce those values, and destinations may not fully support them.

64-bit integers and floating-point numbers (AKA `long` and `double`) cannot represent every number in existence. Sources should use the string type if their fields may exceed `int64`/`float64` ranges.

#### Arrays
Arrays contain 0 or more items, which must have a defined type. These types should also conform to the type system. Arrays may require that all of their elements be the same type (`"items": {whatever type...}`), or they may require specific types for the first N entries (`"items": [{first type...}, {second type...}, ... , {Nth type...}]`, AKA tuple-type).

Tuple-typed arrays can configure the type of any additional elements using the `additionalItems` field; by default, any type is allowed. They may also pass a boolean to enable/disable additional elements, with `"additionalItems": true` being equivalent to `"additionalItems": {"$ref": "WellKnownTypes.json#/definitions/String"}` and `"additionalItems": false` meaning that only the tuple-defined items are allowed.

Destinations may have a difficult time supporting tuple-typed arrays without very specific handling, and as such are permitted to somewhat loosen their requirements. For example, many Avro-based destinations simply declare an array of a union of all allowed types, rather than requiring the correct type in each position of the array.

#### Objects
As with arrays, objects may declare `properties`, each of which should have a type which conforms to the type system. Objects may additionally accept `additionalProperties`, as `true` (any type is acceptable), a specific type (all additional properties must be of that type), or `false` (no additonal properties are allowed).

#### Unions
In some cases, sources may want to use multiple types for the same field. For example, a user might have a property which holds either an object, or a `string` explanation of why that data is missing. This is supported with JSON schema's  `oneOf` and `anyOf` types.

Note that JsonSchema's `allOf` combining structure is not accepted within the protocol, because all of the protocol type definitions are mutually exclusive.

#### Untyped values
In some unusual cases, a property may not have type information associated with it. Sources must cast these properties to string, and discover them as `{"$ref": "WellKnownTypes.json#/definitions/String"}`.
