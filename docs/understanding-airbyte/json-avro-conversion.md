# Json to Avro Conversion for Blob Storage Destinations

When an Airbyte data stream is synced to the Avro or Parquet format (e.g. Parquet on S3), the source Json schema is converted to an Avro schema, then the Json object is converted to an Avro record based on the Avro schema (and further to Parquet if necessary). Because the data stream can come from any data source, the Json to Avro conversion process has the following rules and limitations.

1. Json schema types are mapped to Avro types as follows:

   | Json Data Type | Avro Data Type |
   | :---: | :---: |
   | string | string |
   | number | double |
   | integer | int |
   | boolean | boolean |
   | null | null |
   | object | record |
   | array | array |

2. Built-in Json schema formats are not mapped to Avro logical types at this moment.
3. Combined restrictions \("allOf", "anyOf", and "oneOf"\) will be converted to type unions. The corresponding Avro schema can be less stringent. For example, the following Json schema

   ```json
   {
    "oneOf": [
      { "type": "string" },
      { "type": "integer" }
    ]
   }
   ```

   will become this in Avro schema:

   ```json
   {
    "type": ["null", "string", "int"]
   }
   ```

4. Keyword `not` is not supported, as there is no equivalent validation mechanism in Avro schema.
5. Only alphanumeric characters and underscores \(`/a-zA-Z0-9_/`\) are allowed in a stream or field name. Any special character will be converted to an alphabet or underscore. For example, `spécial:character_names` will become `special_character_names`. The original names will be stored in the `doc` property in this format: `_airbyte_original_name:<original-name>`.
6. The field name cannot start with a number, so an underscore will be added to the field name at the beginning.
7. All field will be nullable. For example, a `string` Json field will be typed as `["null", "string"]` in Avro. This is necessary because the incoming data stream may have optional fields.
8. For array fields in Json schema, when the `items` property is an array, it means that each element in the array should follow its own schema sequentially. For example, the following specification means the first item in the array should be a string, and the second a number.

   ```json
   {
    "array_field": {
      "type": "array",
      "items": [
        { "type": "string" },
        { "type": "number" }
      ]
    }
   }
   ```

   This is not supported in Avro schema. As a compromise, the converter creates a union, \["string", "number"\], which is less stringent:

   ```json
   {
    "name": "array_field",
    "type": [
      "null",
      {
        "type": "array",
        "items": ["null", "string"]
      }
    ],
    "default": null
   }
   ```

9. Three Airbyte specific fields will be added to each Avro record:

   | Field | Schema | Document |
      | :--- | :--- | :---: |
   | `_airbyte_ab_id` | `uuid` | [link](http://avro.apache.org/docs/current/spec.html#UUID) |
   | `_airbyte_emitted_at` | `timestamp-millis` | [link](http://avro.apache.org/docs/current/spec.html#Timestamp+%28millisecond+precision%29) |
   | `_airbyte_additional_properties` | `map` of `string` | See explanation below. |

10. A Json object can have additional properties of unknown types, which is not compatible with the Avro schema. To solve this problem during Json to Avro object conversion, we introduce a special field: `_airbyte_additional_properties` typed as a nullable `map` from `string` to `string`:

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
  "$schema": "http://json-schema.org/draft-07/schema#",
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

11. Based on the above rules, here is an overall example. Given the following Json schema:

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
      "type": ["null", "string"],
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
