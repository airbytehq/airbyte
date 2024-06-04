# Json to Avro Conversion for Blob Storage Destinations

When an Airbyte data stream is synced to the Avro or Parquet format (e.g. Parquet on S3), the source Json schema is converted to an Avro schema, then the Json object is converted to an Avro record based on the Avro schema (and further to Parquet if necessary). Because the data stream can come from any data source, the Json to Avro conversion process has the following rules and limitations.

## Conversion Rules

### Type Mapping

Json schema types are mapped to Avro types as follows:

| Json Data Type | Avro Data Type |
| :------------: | :------------: |
|     string     |     string     |
|     number     |     double     |
|    integer     |      int       |
|    boolean     |    boolean     |
|      null      |      null      |
|     object     |     record     |
|     array      |     array      |

### Nullable Fields

All fields are nullable. For example, a `string` Json field will be typed as `["null", "string"]` in Avro. This is necessary because the incoming data stream may have optional fields.

### Built-in Formats

The following built-in Json formats will be mapped to Avro logical types.

| Json Type | Json Built-in Format | Avro Type | Avro Logical Type  | Meaning                                                                                                                                                 |
| --------- | -------------------- | --------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `string`  | `date`               | `int`     | `date`             | Number of epoch days from 1970-01-01 ([reference](https://avro.apache.org/docs/current/spec.html#Date)).                                                |
| `string`  | `time`               | `long`    | `time-micros`      | Number of microseconds after midnight ([reference](https://avro.apache.org/docs/current/spec.html#Time+%28microsecond+precision%29)).                   |
| `string`  | `date-time`          | `long`    | `timestamp-micros` | Number of microseconds from `1970-01-01T00:00:00Z` ([reference](https://avro.apache.org/docs/current/spec.html#Timestamp+%28microsecond+precision%29)). |

In the final Avro schema, these Avro logical type fields will be a union of the logical type and string. The rationale is that the incoming Json objects may contain invalid Json built-in formats. If that's the case, and the conversion from the Json built-in format to Avro built-in format fails, the field will fall back to a string. The extra string type can cause problem for some users in the destination. We may re-evaluate this conversion rule in the future. This issue is tracked [here](https://github.com/airbytehq/airbyte/issues/17011).

**Date**

The date logical type represents a date within the calendar, with no reference to a particular time zone or time of day.

A date logical type annotates an Avro int, where the int stores the number of days from the unix epoch, 1 January 1970 (ISO calendar).

```json
{
  "type": "string",
  "format": "date"
}
```

is mapped to:

```json
{
  "type": "int",
  "logicalType": "date"
}
```

and the Avro schema is:

```json
{
  "type": [
    "null",
    {
      "type": "int",
      "logicalType": "date"
    },
    "string"
  ]
}
```

**Time (microsecond precision)**

The time-micros logical type represents a time of day, with no reference to a particular calendar, time zone or date, with a precision of one microsecond.

A time-micros logical type annotates an Avro long, where the long stores the number of microseconds after midnight, 00:00:00.000000.

```json
{
  "type": "string",
  "format": "time"
}
```

is mapped to:

```json
{
  "type": "long",
  "logicalType": "time-micros"
}
```

and the Avro schema is:

```json
{
  "type": [
    "null",
    {
      "type": "long",
      "logicalType": "time-micros"
    },
    "string"
  ]
}
```

**Timestamp (microsecond precision)**

The timestamp-micros logical type represents an instant on the global timeline, independent of a particular time zone or calendar, with a precision of one microsecond.

A timestamp-micros logical type annotates an Avro long, where the long stores the number of microseconds from the unix epoch, 1 January 1970 00:00:00.000000 UTC.

```json
{
  "type": "string",
  "format": "date-time"
}
```

is mapped to:

```json
{
  "type": "long",
  "logicalType": "timestamp-micros"
}
```

and the Avro schema is:

```json
{
  "type": [
    "null",
    {
      "type": "long",
      "logicalType": "timestamp-micros"
    },
    "string"
  ]
}
```

### Combined Restrictions

Combined restrictions \(`allOf`, `anyOf`, and `oneOf`\) will be converted to type unions. The corresponding Avro schema can be less stringent. For example, the following Json schema

```json
{
  "oneOf": [{ "type": "string" }, { "type": "integer" }]
}
```

will become this in Avro schema:

```json
{
  "type": ["null", "string", "int"]
}
```

### Keyword `not`

Keyword `not` is not supported, as there is no equivalent validation mechanism in Avro schema.

### Filed Name

Only alphanumeric characters and underscores \(`/a-zA-Z0-9_/`\) are allowed in a stream or field name. Any special character will be converted to an alphabet or underscore. For example, `spécial:character_names` will become `special_character_names`. The original names will be stored in the `doc`property in this format: `_airbyte_original_name:<original-name>`.

Field name cannot start with a number, so an underscore will be added to those field names at the beginning.

### Array Types

For array fields in Json schema, when the `items` property is an array, it means that each element in the array should follow its own schema sequentially. For example, the following specification means the first item in the array should be a string, and the second a number.

```json
{
  "array_field": {
    "type": "array",
    "items": [{ "type": "string" }, { "type": "number" }]
  }
}
```

This is not supported in Avro schema. As a compromise, the converter creates a union, `["null", "string", "number"]`, which is less stringent:

```json
{
  "name": "array_field",
  "type": [
    "null",
    {
      "type": "array",
      "items": ["null", "string", "number"]
    }
  ],
  "default": null
}
```

If the Json array has multiple object items, these objects will be recursively merged into one Avro record. For example, the following Json array expects two different objects. The first object has an `id` field, and second has an `id` and `message` field. Their `id` fields have slightly different types.

Json schema:

```json
{
  "array_field": {
    "type": "array",
    "items": [
      {
        "type": "object",
        "properties": {
          "id": {
            "type": "object",
            "properties": {
              "id_part_1": { "type": "integer" },
              "id_part_2": { "type": "string" }
            }
          }
        }
      },
      {
        "type": "object",
        "properties": {
          "id": {
            "type": "object",
            "properties": {
              "id_part_1": { "type": "string" },
              "id_part_2": { "type": "integer" }
            }
          },
          "message": {
            "type": "string"
          }
        }
      }
    ]
  }
}
```

Json object:

```json
{
  "array_field": [
    {
      "id": {
        "id_part_1": 1000,
        "id_part_2": "abcde"
      }
    },
    {
      "id": {
        "id_part_1": "wxyz",
        "id_part_2": 2000
      },
      "message": "test message"
    }
  ]
}
```

After conversion, the two object schemas will be merged into one. Furthermore, the fields under the `id` record, `id_part_1` and `id_part_2`, will also be merged. In this way, all possible valid elements from the Json array can be converted to Avro records.

Avro schema:

```json
{
  "name": "array_field",
  "type": [
    "null",
    {
      "type": "array",
      "items": [
        "boolean",
        {
          "type": "record",
          "name": "array_field",
          "fields": [
            {
              "name": "id",
              "type": [
                "null",
                {
                  "type": "record",
                  "name": "id",
                  "fields": [
                    {
                      "name": "id_part_1",
                      "type": ["null", "int", "string"],
                      "default": null
                    },
                    {
                      "name": "id_part_2",
                      "type": ["null", "string", "int"],
                      "default": null
                    }
                  ]
                }
              ],
              "default": null
            },
            {
              "name": "message",
              "type": ["null", "string"],
              "default": null
            }
          ]
        }
      ]
    }
  ],
  "default": null
}
```

Note that `id_part_1` is a union of `int` and `string`, which comes from the first and second `id` definitions, respectively, in the original Json `items` specification.

Avro object:

```json
{
  "array_field": [
    {
      "id": {
        "id_part_1": 1000,
        "id_part_2": "abcde"
      },
      "message": null
    },
    {
      "id": {
        "id_part_1": "wxyz",
        "id_part_2": 2000
      },
      "message": "test message"
    }
  ]
}
```

Note that the first object in `array_field` originally does not have a `message` field. However, because its schema is merged with the second object definition, it has a null `message` field in the Avro record.

### Untyped Array

When a Json array field has no `items`, the element in that array field may have any type. However, Avro requires that each array has a clear type specification. To solve this problem, the elements in the array are forced to be `string`s.

For example, given the following Json schema and object:

```json
{
  "type": "object",
  "properties": {
    "identifier": {
      "type": "array"
    }
  }
}
```

```json
{
  "identifier": ["151", 152, true, { "id": 153 }, null]
}
```

the corresponding Avro schema and object will be:

```json
{
  "type": "record",
  "fields": [
    {
      "name": "identifier",
      "type": [
        "null",
        {
          "type": "array",
          "items": ["null", "string"]
        }
      ],
      "default": null
    }
  ]
}
```

```json
{
  "identifier": ["151", "152", "true", "{\"id\": 153}", null]
}
```

Note that every non-null element inside the `identifier` array field is converted to string.

### Airbyte-Specific Fields

Three Airbyte specific fields will be added to each Avro record:

| Field                            | Schema             |                                          Document                                           |
| :------------------------------- | :----------------- | :-----------------------------------------------------------------------------------------: |
| `_airbyte_ab_id`                 | `uuid`             |                 [link](http://avro.apache.org/docs/current/spec.html#UUID)                  |
| `_airbyte_emitted_at`            | `timestamp-millis` | [link](http://avro.apache.org/docs/current/spec.html#Timestamp+%28millisecond+precision%29) |
| `_airbyte_additional_properties` | `map` of `string`  |                                   See explanation below.                                    |

### Additional Properties

A Json object can have additional properties of unknown types, which is not compatible with the Avro schema. To solve this problem during Json to Avro object conversion, we introduce a special field: `_airbyte_additional_properties` typed as a nullable `map` from `string` to `string`:

```json
{
  "name": "_airbyte_additional_properties",
  "type": ["null", { "type": "map", "values": "string" }],
  "default": null
}
```

For example, given the following Json schema:

```json
{
  "type": "object",
  "properties": {
    "username": {
      "type": ["null", "string"]
    }
  }
}
```

this Json object

```json
{
  "username": "admin",
  "active": true,
  "age": 21,
  "auth": {
    "auth_type": "ssl",
    "api_key": "abcdefg/012345",
    "admin": false,
    "id": 1000
  }
}
```

will be converted to the following Avro object:

```json
{
  "username": "admin",
  "_airbyte_additional_properties": {
    "active": "true",
    "age": "21",
    "auth": "{\"auth_type\":\"ssl\",\"api_key\":\"abcdefg/012345\",\"admin\":false,\"id\":1000}"
  }
}
```

Note that all fields other than the `username` is moved under `_ab_additional_properties` as serialized strings, including the original object `auth`.

### Untyped Object

If an `object` field has no `properties` specification, all fields within this `object` will be put into the aforementioned `_airbyte_additional_properties` field.

For example, given the following Json schema and object:

```json
{
  "type": "object"
}
```

```json
{
  "username": "343-guilty-spark",
  "password": 1439,
  "active": true
}
```

the corresponding Avro schema and record will be:

```json
{
  "type": "record",
  "name": "record_without_properties",
  "fields": [
    {
      "name": "_airbyte_additional_properties",
      "type": ["null", { "type": "map", "values": "string" }],
      "default": null
    }
  ]
}
```

```json
{
  "_airbyte_additional_properties": {
    "username": "343-guilty-spark",
    "password": "1439",
    "active": "true"
  }
}
```

### Untyped Field

Any field without property type specification will default to a `string` field, and its value will be serialized to string.

## Example

Based on the above rules, here is an overall example. Given the following Json schema:

```json
{
  "type": "object",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "properties": {
    "id": {
      "type": "integer"
    },
    "user": {
      "type": ["null", "object"],
      "properties": {
        "id": {
          "type": "integer"
        },
        "field_with_spécial_character": {
          "type": "integer"
        }
      }
    },
    "created_at": {
      "type": ["null", "string"],
      "format": "date-time"
    }
  }
}
```

Its corresponding Avro schema will be:

```json
{
  "name": "stream_name",
  "type": "record",
  "fields": [
    {
      "name": "_airbyte_ab_id",
      "type": {
        "type": "string",
        "logicalType": "uuid"
      }
    },
    {
      "name": "_airbyte_emitted_at",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      }
    },
    {
      "name": "id",
      "type": ["null", "int"],
      "default": null
    },
    {
      "name": "user",
      "type": [
        "null",
        {
          "type": "record",
          "name": "user",
          "fields": [
            {
              "name": "id",
              "type": ["null", "int"],
              "default": null
            },
            {
              "name": "field_with_special_character",
              "type": ["null", "int"],
              "doc": "_airbyte_original_name:field_with_spécial_character",
              "default": null
            },
            {
              "name": "_airbyte_additional_properties",
              "type": ["null", { "type": "map", "values": "string" }],
              "default": null
            }
          ]
        }
      ],
      "default": null
    },
    {
      "name": "created_at",
      "type": [
        "null",
        { "type": "long", "logicalType": "timestamp-micros" },
        "string"
      ],
      "default": null
    },
    {
      "name": "_airbyte_additional_properties",
      "type": ["null", { "type": "map", "values": "string" }],
      "default": null
    }
  ]
}
```

More examples can be found in the Json to Avro conversion [test cases](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/bases/base-java-s3/src/test/resources/parquet/json_schema_converter).

## Implementation

- Schema conversion: [JsonToAvroSchemaConverter](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/bases/base-java-s3/src/main/java/io/airbyte/integrations/destination/s3/avro/JsonToAvroSchemaConverter.java)
- Object conversion: [airbytehq/json-avro-converter](https://github.com/airbytehq/json-avro-converter) (forked and modified from [allegro/json-avro-converter](https://github.com/allegro/json-avro-converter)).
