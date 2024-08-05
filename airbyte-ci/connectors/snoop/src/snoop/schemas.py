import json

import avro.schema

AIRBYTE_MESSAGE = {
    "type": "record",
    "name": "SnoopAirbyteMessage",
    "fields": [
        {
            "name": "snoop_session_id",
            "type": "string"
        },
        {
            "name": "airbyte_command",
            "type": "string"
        },
        {
            "name": "connector",
            "type": "string"
        },
        {
            "name": "connector_version",
            "type": "string"
        },
        {
            "name": "message_type",
            "type": "string"
        },
        {
            "name": "message_size",
            "type": "int"
        },
        {
            "name": "message_timestamp",
            "type": "long",
            "logicalType": "timestamp-micros"

        },
        {
            "name": "message_content",
            "type": [
                "string",
                "null"
            ]
        }
    ]
}


PRIMARY_KEYS_PER_STREAM = {
    "type": "record",
    "name": "SnoopPrimaryKeysPerStream",
    "fields": [
        {
            "name": "snoop_session_id",
            "type": "string"
        },
        {
            "name": "airbyte_command",
            "type": "string"
        },
        {
            "name": "connector",
            "type": "string"
        },
        {
            "name": "connector_version",
            "type": "string"
        },
        {
            "name": "stream",
            "type": "string"
        },
        {
            "name": "hashed_primary_keys",
            "type": {
                "type": "array",
                "items": "string"
            }
        }
    ]
}

OBSERVED_STREAM_SCHEMAS = {
    "type": "record",
    "name": "SnoopObservedStreamSchemas",
    "fields": [
        {
            "name": "snoop_session_id",
            "type": "string"
        },
        {
            "name": "airbyte_command",
            "type": "string"
        },
        {
            "name": "connector",
            "type": "string"
        },
        {
            "name": "connector_version",
            "type": "string"
        },
        {
            "name": "stream",
            "type": "string"
        },
        {
            "name": "schema",
            "type": "string"
        }
    ]
}

HTTP_FLOWS = {
    "type": "record",
    "name": "SnoopHttpFlow",
    "fields": [
        {
            "name": "snoop_session_id",
            "type": "string"
        },
        {
            "name": "airbyte_command",
            "type": "string"
        },
        {
            "name": "connector",
            "type": "string"
        },
        {
            "name": "connector_version",
            "type": "string"
        },
        {
            "name": "request_url",
            "type": "string"
        },
        {
            "name": "request_method",
            "type": "string"
        },
        {
            "name": "response_status_code",
            "type": "int"
        },
        {
            "name": "response_time",
            "type": "int"
        },
        {
            "name": "response_size",
            "type": "int"
        },
    ]
}

airbyte_message_schema = avro.schema.parse(json.dumps(AIRBYTE_MESSAGE))
http_flows_schema = avro.schema.parse(json.dumps(HTTP_FLOWS))