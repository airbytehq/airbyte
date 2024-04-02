# Discover

Run a discover command
```
poetry run source-survey-monkey-demo discover --config secrets/config.json
```

The command should succeed, but the schema is wrong
> {"type": "CATALOG", "catalog": {"streams": [{"name": "surveys", "json_schema": {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": {"id": {"type": ["null", "string"]}, "name": {"type": ["null", "string"]}, "signup_date": {"type": ["null", "string"], "format": "date-time"}}}, "supported_sync_modes": ["full_refresh"], "source_defined_primary_key": [["id"]]}]}}

The easiest way to extract the schema from a HTTP response is to use the Connector Builder.
```json
{
  "$schema": "http://json-schema.org/schema#",
  "properties": {
    "analyze_url": {
      "type": "string"
    },
    "collect_stats": {
      "properties": {
        "status": {
          "properties": {
            "open": {
              "type": "number"
            }
          },
          "type": "object"
        },
        "total_count": {
          "type": "number"
        },
        "type": {
          "properties": {
            "weblink": {
              "type": "number"
            }
          },
          "type": "object"
        }
      },
      "type": "object"
    },
    "date_created": {
      "type": "string"
    },
    "date_modified": {
      "type": "string"
    },
    "href": {
      "type": "string"
    },
    "id": {
      "type": "string"
    },
    "language": {
      "type": "string"
    },
    "nickname": {
      "type": "string"
    },
    "preview": {
      "type": "string"
    },
    "question_count": {
      "type": "number"
    },
    "response_count": {
      "type": "number"
    },
    "title": {
      "type": "string"
    }
  },
  "type": "object"
}
```

**NOTE**
If the connector you're building has a dynamic schema, you'll need to overwrite the `AbstractSource::streams`.

---

The three connector operations work as expected. In the [next section](5-incremental-reads.md), we'll add the connector to our local Airbyte instance.
