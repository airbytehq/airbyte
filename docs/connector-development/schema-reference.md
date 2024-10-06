# Schema Reference

:::note
You only need this if you're building a connector with Python or Java CDKs.
If you're using Connector Builder, you can use [declared schemas](./connector-builder-ui/record-processing#declared-schema) instead.
:::

This document provides instructions on how to create a static schema for your Airbyte stream, which is necessary for integrating data from various sources.
You can check out all the supported data types and examples at [this link](../understanding-airbyte/supported-data-types.md).

For instance, the example record response for the schema is shown below:

```json
{
  "id": "hashidstring",
  "date_created": "2022-11-22T01:23:45",
  "date_updated": "2023-12-22T01:12:00",
  "total": 1000,
  "status": "published",
  "example_obj": {
    "steps": "walking",
    "count_steps": 30
  },
  "example_string_array": ["first_string", "second_string"]
}
```

The schema is then translated into the following JSON format. Please note that it's essential to include `$schema`, `type`, and `additionalProperties: true` fields in your schema. Typically, Airbyte schemas require null values for each field to make the stream more reliable if the field doesn't receive any data.

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
