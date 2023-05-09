# Schema Reference

This document gives instructions how to create a static schema for your stream.
You can check all data types supported and example [here](./understanding-airbyte/supported-data-types.md)

Example from the record response is:
```
{
  "id": "hashidstring",
  "date_created": "2022-11-22T01:23:45",
  "date_updated": 2023-12-22T01:12:00",
  "total": 1000,
  "status": "published",
  "example_obj": {
    "steps": "walking",
    "count_steps": 30
  },
  "example_string_array": ["first_string", "second_string"]
}
```

And the schema is translated to the following. Make sure your schema has the `$schema`, `type` and `additionalProperties: true`. Usually Airbyte schemas requires `null` to each field to make the stream more reliable if the field don't receive data.
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "id": {
      "type": ["null", "string"]
    },
    "date_created": {
      "format": "date-time",
      "type": ["null", "string"]
    },
    "date_updated": {
      "format": "date-time",
      "type": ["null", "string"]
    },
    "total": {
      "type": ["null", "integer"]
    },
    "status": {
      "type": ["string", "null"],
      "enum": ["published", "draft"]
    },
    "example_obj": {
      "type": ["null", "object"],
      "additionalProperties": true,
      "properties": {
        "steps": { 
            "type": ["null", "string"] 
        },
        "count_steps": {
            "type": ["null", "integer"]
        }
      }
    },
    "example_string_array": {
        "items": {
            "type": ["null", "string"]
        }
    }
  }
}

```