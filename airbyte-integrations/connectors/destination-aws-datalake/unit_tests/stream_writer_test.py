#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime
from typing import Any, Dict, Mapping

import pandas as pd
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode
from destination_aws_datalake import DestinationAwsDatalake
from destination_aws_datalake.aws import AwsHandler
from destination_aws_datalake.config_reader import ConnectorConfig
from destination_aws_datalake.stream_writer import StreamWriter


def get_config() -> Mapping[str, Any]:
    with open("unit_tests/fixtures/config.json", "r") as f:
        return json.loads(f.read())


def get_configured_stream():
    stream_name = "append_stream"
    stream_schema = {
        "type": "object",
        "properties": {
            "string_col": {"type": "str"},
            "int_col": {"type": "integer"},
            "datetime_col": {"type": "string", "format": "date-time"},
            "date_col": {"type": "string", "format": "date"},
        },
    }

    return ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=stream_name,
            json_schema=stream_schema,
            default_cursor_field=["datetime_col"],
            supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
        cursor_field=["datetime_col"],
    )


def get_writer(config: Dict[str, Any]):
    connector_config = ConnectorConfig(**config)
    aws_handler = AwsHandler(connector_config, DestinationAwsDatalake())
    return StreamWriter(aws_handler, connector_config, get_configured_stream())


def get_big_schema_configured_stream():
    stream_name = "append_stream_big"
    stream_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": ["null", "object"],
        "properties": {
            "appId": {"type": ["null", "integer"]},
            "appName": {"type": ["null", "string"]},
            "bounced": {"type": ["null", "boolean"]},
            "browser": {
                "type": ["null", "object"],
                "properties": {
                    "family": {"type": ["null", "string"]},
                    "name": {"type": ["null", "string"]},
                    "producer": {"type": ["null", "string"]},
                    "producerUrl": {"type": ["null", "string"]},
                    "type": {"type": ["null", "string"]},
                    "url": {"type": ["null", "string"]},
                    "version": {"type": ["null", "array"], "items": {"type": ["null", "string"]}},
                },
            },
            "causedBy": {
                "type": ["null", "object"],
                "properties": {"created": {"type": ["null", "integer"]}, "id": {"type": ["null", "string"]}},
            },
            "percentage": {"type": ["null", "number"]},
            "location": {
                "type": ["null", "object"],
                "properties": {
                    "city": {"type": ["null", "string"]},
                    "country": {"type": ["null", "string"]},
                    "latitude": {"type": ["null", "number"]},
                    "longitude": {"type": ["null", "number"]},
                    "state": {"type": ["null", "string"]},
                    "zipcode": {"type": ["null", "string"]},
                },
            },
            "nestedJson": {
                "type": ["null", "object"],
                "properties": {
                    "city": {"type": "object", "properties": {"name": {"type": "string"}}},
                },
            },
            "sentBy": {
                "type": ["null", "object"],
                "properties": {"created": {"type": ["null", "integer"]}, "id": {"type": ["null", "string"]}},
            },
            "sentAt": {"type": ["null", "string"], "format": "date-time"},
            "receivedAt": {"type": ["null", "string"], "format": "date"},
            "sourceId": {"type": "string"},
            "status": {"type": "integer"},
            "read": {"type": "boolean"},
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"id": {"type": ["null", "integer"]}, "question": {"type": "string"}, "answer": {"type": "string"}},
                },
            },
            "questions_nested": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": ["null", "integer"]},
                        "questions": {"type": "object", "properties": {"title": {"type": "string"}, "option": {"type": "integer"}}},
                        "answer": {"type": "string"},
                    },
                },
            },
            "nested_mixed_types": {
                "type": ["null", "object"],
                "properties": {
                    "city": {"type": ["string", "integer", "null"]},
                },
            },
            "nested_bad_object": {
                "type": ["null", "object"],
                "properties": {
                    "city": {"type": "object", "properties": {}},
                },
            },
            "nested_nested_bad_object": {
                "type": ["null", "object"],
                "properties": {
                    "city": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "object", "properties": {}},
                        },
                    },
                },
            },
            "answers": {
                "type": "array",
                "items": {
                    "type": "string",
                },
            },
            "answers_nested_bad": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": ["string", "integer"]},
                    },
                },
            },
            "phone_number_ids": {"type": ["null", "array"], "items": {"type": ["string", "integer"]}},
            "mixed_type_simple": {
                "type": ["integer", "number"],
            },
            "empty_array": {"type": ["null", "array"]},
            "airbyte_type_object": {"type": "number", "airbyte_type": "integer"},
            "airbyte_type_array": {"type": "array", "items": {"type": "number", "airbyte_type": "integer"}},
            "airbyte_type_array_not_integer": {
                "type": "array",
                "items": {"type": "string", "format": "date-time", "airbyte_type": "timestamp_without_timezone"},
            },
            "airbyte_type_object_not_integer": {"type": "string", "format": "date-time", "airbyte_type": "timestamp_without_timezone"},
            "object_with_additional_properties": {
                "type": ["null", "object"],
                "properties": {"id": {"type": ["null", "integer"]}, "name": {"type": ["null", "string"]}},
                "additionalProperties": True,
            },
            "object_no_additional_properties": {
                "type": ["null", "object"],
                "properties": {"id": {"type": ["null", "integer"]}, "name": {"type": ["null", "string"]}},
                "additionalProperties": False,
            },
        },
    }

    return ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=stream_name,
            json_schema=stream_schema,
            default_cursor_field=["datetime_col"],
            supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
        cursor_field=["datetime_col"],
    )


def get_big_schema_writer(config: Dict[str, Any]):
    connector_config = ConnectorConfig(**config)
    aws_handler = AwsHandler(connector_config, DestinationAwsDatalake())
    return StreamWriter(aws_handler, connector_config, get_big_schema_configured_stream())


def test_get_date_columns():
    writer = get_writer(get_config())
    assert writer._get_date_columns() == ["datetime_col", "date_col"]


def test_append_messsage():
    writer = get_writer(get_config())
    message = {"string_col": "test", "int_col": 1, "datetime_col": "2021-01-01T00:00:00Z", "date_col": "2021-01-01"}
    writer.append_message(message)
    assert len(writer._messages) == 1
    assert writer._messages[0] == message


def test_get_cursor_field():
    writer = get_writer(get_config())
    assert writer._cursor_fields == ["datetime_col"]


def test_add_partition_column():
    tests = {
        "NO PARTITIONING": {},
        "DATE": {"datetime_col_date": "date"},
        "MONTH": {"datetime_col_month": "bigint"},
        "YEAR": {"datetime_col_year": "bigint"},
        "DAY": {"datetime_col_day": "bigint"},
        "YEAR/MONTH/DAY": {"datetime_col_year": "bigint", "datetime_col_month": "bigint", "datetime_col_day": "bigint"},
    }

    for partitioning, expected_columns in tests.items():
        config = get_config()
        config["partitioning"] = partitioning

        writer = get_writer(config)
        df = pd.DataFrame(
            {
                "datetime_col": [datetime.now()],
            }
        )
        assert writer._add_partition_column("datetime_col", df) == expected_columns
        assert all([col in df.columns for col in expected_columns])


def test_get_glue_dtypes_from_json_schema():
    writer = get_big_schema_writer(get_config())
    result, json_casts = writer._get_glue_dtypes_from_json_schema(writer._schema)
    assert result == {
        "airbyte_type_array": "array<bigint>",
        "airbyte_type_object": "bigint",
        "airbyte_type_array_not_integer": "array<string>",
        "airbyte_type_object_not_integer": "timestamp",
        "answers": "array<string>",
        "answers_nested_bad": "string",
        "appId": "bigint",
        "appName": "string",
        "bounced": "boolean",
        "browser": "struct<family:string,name:string,producer:string,producerUrl:string,type:string,url:string,version:array<string>>",
        "causedBy": "struct<created:bigint,id:string>",
        "empty_array": "string",
        "location": "struct<city:string,country:string,latitude:double,longitude:double,state:string,zipcode:string>",
        "mixed_type_simple": "string",
        "nestedJson": "struct<city:struct<name:string>>",
        "nested_bad_object": "string",
        "nested_mixed_types": "string",
        "nested_nested_bad_object": "string",
        "object_with_additional_properties": "string",
        "object_no_additional_properties": "struct<id:bigint,name:string>",
        "percentage": "double",
        "phone_number_ids": "string",
        "questions": "array<struct<id:bigint,question:string,answer:string>>",
        "questions_nested": "array<struct<id:bigint,questions:struct<title:string,option:bigint>,answer:string>>",
        "read": "boolean",
        "receivedAt": "date",
        "sentAt": "timestamp",
        "sentBy": "struct<created:bigint,id:string>",
        "sourceId": "string",
        "status": "bigint",
    }

    assert json_casts == {
        "answers_nested_bad",
        "empty_array",
        "nested_bad_object",
        "nested_mixed_types",
        "nested_nested_bad_object",
        "phone_number_ids",
        "object_with_additional_properties",
    }


def test_has_objects_with_no_properties_good():
    writer = get_big_schema_writer(get_config())
    assert writer._is_invalid_struct_or_array(
        {
            "nestedJson": {
                "type": ["null", "object"],
                "properties": {
                    "city": {"type": "object", "properties": {"name": {"type": "string"}}},
                },
            }
        }
    )


def test_has_objects_with_no_properties_bad():
    writer = get_big_schema_writer(get_config())
    assert not writer._is_invalid_struct_or_array(
        {
            "nestedJson": {
                "type": ["null", "object"],
            }
        }
    )


def test_has_objects_with_no_properties_nested_bad():
    writer = get_big_schema_writer(get_config())
    assert not writer._is_invalid_struct_or_array(
        {
            "nestedJson": {
                "type": ["null", "object"],
                "properties": {
                    "city": {"type": "object", "properties": {}},
                },
            }
        }
    )
