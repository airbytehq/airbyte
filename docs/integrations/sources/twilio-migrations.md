# Twilio Migration Guide

## Upgrading to 1.0.0

### Migration Description for Connector Update to Low Code

As part of the migration to a low code, we are updating the connector state format. The previous state format will no longer be supported, and all streams must be re-executed to update the state to a valid format.

- For each affected connector, re-run all streams to ensure the state is updated to the new format.
- Verify that the data is correctly processed and the state is properly updated.

#### Previous State Format

```json
{
  "type": "STREAM",
  "stream": {
    "stream_state": {
      "end_time": "2022-06-11T00:00:00Z"
    },
    "stream_descriptor": {
      "name": "calls"
    }
  }
}
```

#### New State Format

```json
{
  "type": "STATE",
  "state": {
    "type": "STREAM",
    "stream": {
      "stream_descriptor": {
        "name": "calls",
        "namespace": null
      },
      "stream_state": {
        "states": [
          {
            "partition": {
              "account_sid": "<account_sid>",
              "parent_slice": {}
            },
            "cursor": {
              "end_time": "Tue, 25 Jun 2024 20:19:28 +0000"
            }
          }
        ]
      }
    },
    "sourceStats": {
      "recordCount": 0.0
    }
  }
}
```
