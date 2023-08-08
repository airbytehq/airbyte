#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Mapping

import numpy as np
import pandas as pd
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode
from destination_aws_datalake import DestinationAwsDatalake
from destination_aws_datalake.aws import AwsHandler
from destination_aws_datalake.config_reader import ConnectorConfig
from destination_aws_datalake.stream_writer import DictEncoder, StreamWriter


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


def get_camelcase_configured_stream():
    stream_name = "append_camelcase"
    stream_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": ["null", "object"],
        "properties": {
            "TaxRateRef": {
                "properties": {"name": {"type": ["null", "string"]}, "value": {"type": ["null", "string"]}},
                "type": ["null", "object"],
            },
            "DocNumber": {"type": ["null", "string"]},
            "CurrencyRef": {
                "properties": {"name": {"type": ["null", "string"]}, "value": {"type": ["null", "string"]}},
                "type": ["null", "object"],
            },
            "Id": {"type": ["null", "string"]},
            "domain": {"type": ["null", "string"]},
            "SyncToken": {"type": ["null", "string"]},
            "Line": {
                "items": {
                    "properties": {
                        "Id": {"type": ["null", "string"]},
                        "Amount": {"type": ["null", "number"]},
                        "JournalEntryLineDetail": {
                            "properties": {
                                "AccountRef": {
                                    "properties": {"name": {"type": ["null", "string"]}, "value": {"type": ["null", "string"]}},
                                    "type": ["null", "object"],
                                },
                                "PostingType": {"type": ["null", "string"]},
                            },
                            "type": ["null", "object"],
                        },
                        "DetailType": {"type": ["null", "string"]},
                        "Description": {"type": ["null", "string"]},
                    },
                    "type": ["null", "object"],
                },
                "type": ["null", "array"],
            },
            "TxnDate": {"format": "date", "type": ["null", "string"]},
            "TxnTaxDetail": {
                "type": ["null", "object"],
                "properties": {
                    "TotalTax": {"type": ["null", "number"]},
                    "TxnTaxCodeRef": {
                        "type": ["null", "object"],
                        "properties": {"value": {"type": ["null", "string"]}, "name": {"type": ["null", "string"]}},
                    },
                    "TaxLine": {
                        "type": ["null", "array"],
                        "items": {
                            "type": ["null", "object"],
                            "properties": {
                                "DetailType": {"type": ["null", "string"]},
                                "Amount": {"type": ["null", "number"]},
                                "TaxLineDetail": {
                                    "type": ["null", "object"],
                                    "properties": {
                                        "TaxPercent": {"type": ["null", "number"]},
                                        "OverrideDeltaAmount": {"type": ["null", "number"]},
                                        "TaxInclusiveAmount": {"type": ["null", "number"]},
                                        "PercentBased": {"type": ["null", "boolean"]},
                                        "NetAmountTaxable": {"type": ["null", "number"]},
                                        "TaxRateRef": {
                                            "type": ["null", "object"],
                                            "properties": {"name": {"type": ["null", "string"]}, "value": {"type": ["null", "string"]}},
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            "PrivateNote": {"type": ["null", "string"]},
            "ExchangeRate": {"type": ["null", "number"]},
            "MetaData": {
                "properties": {
                    "CreateTime": {"format": "date-time", "type": ["null", "string"]},
                    "LastUpdatedTime": {"format": "date-time", "type": ["null", "string"]},
                },
                "type": ["null", "object"],
            },
            "Adjustment": {"type": ["null", "boolean"]},
            "sparse": {"type": ["null", "boolean"]},
            "airbyte_cursor": {"type": ["null", "string"]},
        },
    }

    return ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=stream_name,
            json_schema=stream_schema,
            default_cursor_field=["airbyte_cursor"],
            supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
        cursor_field=["airbyte_cursor"],
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


def test_get_glue_types_from_json_schema_camel_case():
    connector_config = ConnectorConfig(**get_config())
    aws_handler = AwsHandler(connector_config, DestinationAwsDatalake())
    writer = StreamWriter(aws_handler, connector_config, get_camelcase_configured_stream())
    result, _ = writer._get_glue_dtypes_from_json_schema(writer._schema)
    assert result == {
        "Adjustment": "boolean",
        "CurrencyRef": "struct<name:string,value:string>",
        "DocNumber": "string",
        "ExchangeRate": "double",
        "Id": "string",
        "Line": "array<struct<Id:string,Amount:double,JournalEntryLineDetail:struct<AccountRef:struct<name:string,value:string>,PostingType:string>,DetailType:string,Description:string>>",
        "MetaData": "struct<CreateTime:timestamp,LastUpdatedTime:timestamp>",
        "PrivateNote": "string",
        "SyncToken": "string",
        "TaxRateRef": "struct<name:string,value:string>",
        "TxnDate": "date",
        "TxnTaxDetail": "struct<TotalTax:double,TxnTaxCodeRef:struct<value:string,name:string>,TaxLine:array<struct<DetailType:string,Amount:double,TaxLineDetail:struct<TaxPercent:double,OverrideDeltaAmount:double,TaxInclusiveAmount:double,PercentBased:boolean,NetAmountTaxable:double,TaxRateRef:struct<name:string,value:string>>>>>",
        "airbyte_cursor": "string",
        "domain": "string",
        "sparse": "boolean",
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


def test_json_schema_cast_value():
    writer = get_big_schema_writer(get_config())
    assert (
        writer._json_schema_cast_value(
            "test",
            {
                "type": "string",
            },
        )
        == "test"
    )
    assert (
        writer._json_schema_cast_value(
            "1",
            {
                "type": "integer",
            },
        )
        == 1
    )


def test_json_schema_cast_decimal():
    config = get_config()
    config["glue_catalog_float_as_decimal"] = True
    connector_config = ConnectorConfig(**config)
    aws_handler = AwsHandler(connector_config, DestinationAwsDatalake())
    writer = StreamWriter(aws_handler, connector_config, get_camelcase_configured_stream())

    assert writer._json_schema_cast(
        {
            "Adjustment": False,
            "domain": "QBO",
            "sparse": "true",
            "Id": "147491",
            "SyncToken": "2",
            "MetaData": {"CreateTime": "2023-02-09T10:36:39-08:00", "LastUpdatedTime": "2023-06-15T16:08:39-07:00"},
            "DocNumber": "wt_JE001032",
            "TxnDate": "2023-01-13",
            "CurrencyRef": {"value": "USD", "name": "United States Dollar"},
            "Line": [
                {
                    "Id": "0",
                    "Description": "Payroll 01/13/23",
                    "Amount": "137973.66",
                    "DetailType": "JournalEntryLineDetail",
                    "JournalEntryLineDetail": {
                        "PostingType": "Debit",
                        "Entity": {"Type": "Vendor", "EntityRef": {"value": "1", "name": "Test"}},
                        "AccountRef": {"value": "234", "name": "Expense"},
                        "ClassRef": {"value": "14", "name": "Business"},
                    },
                },
            ],
            "airbyte_cursor": "2023-06-15T16:08:39-07:00",
        }
    ) == {
        "Adjustment": False,
        "CurrencyRef": {"name": "United States Dollar", "value": "USD"},
        "DocNumber": "wt_JE001032",
        "Id": "147491",
        "ExchangeRate": Decimal("0"),
        "Line": [
            {
                "Amount": Decimal("137973.66"),
                "Description": "Payroll 01/13/23",
                "DetailType": "JournalEntryLineDetail",
                "Id": "0",
                "JournalEntryLineDetail": {
                    "PostingType": "Debit",
                    "Entity": {"Type": "Vendor", "EntityRef": {"value": "1", "name": "Test"}},
                    "AccountRef": {"value": "234", "name": "Expense"},
                    "ClassRef": {"value": "14", "name": "Business"},
                },
            }
        ],
        "MetaData": {
            "CreateTime": pd.to_datetime("2023-02-09T10:36:39-08:00", utc=True),
            "LastUpdatedTime": pd.to_datetime("2023-06-15T16:08:39-07:00", utc=True),
        },
        "PrivateNote": None,
        "SyncToken": "2",
        "TxnDate": "2023-01-13",
        "TaxRateRef": None,
        "TxnTaxDetail": None,
        "airbyte_cursor": "2023-06-15T16:08:39-07:00",
        "domain": "QBO",
        "sparse": True,
    }


def test_json_schema_cast():
    connector_config = ConnectorConfig(**get_config())
    aws_handler = AwsHandler(connector_config, DestinationAwsDatalake())
    writer = StreamWriter(aws_handler, connector_config, get_camelcase_configured_stream())

    input = {
        "Adjustment": False,
        "domain": "QBO",
        "sparse": False,
        "Id": "147491",
        "SyncToken": "2",
        "ExchangeRate": "1.33",
        "MetaData": {"CreateTime": "2023-02-09T10:36:39-08:00", "LastUpdatedTime": "2023-06-15T16:08:39-07:00"},
        "DocNumber": "wt_JE001032",
        "TxnDate": "2023-01-13",
        "CurrencyRef": {"value": "USD", "name": "United States Dollar"},
        "Line": [
            {
                "Id": "0",
                "Description": "Money",
                "Amount": "137973.66",
                "DetailType": "JournalEntryLineDetail",
                "JournalEntryLineDetail": {
                    "PostingType": "Debit",
                    "Entity": {"Type": "Vendor", "EntityRef": {"value": "1", "name": "Test"}},
                    "AccountRef": {"value": "234", "name": "Expense"},
                    "ClassRef": {"value": "14", "name": "Business"},
                },
            },
        ],
        "airbyte_cursor": "2023-06-15T16:08:39-07:00",
    }

    expected = {
        "Adjustment": False,
        "ExchangeRate": 1.33,
        "CurrencyRef": {"name": "United States Dollar", "value": "USD"},
        "DocNumber": "wt_JE001032",
        "Id": "147491",
        "Line": [
            {
                "Amount": 137973.66,
                "Description": "Money",
                "DetailType": "JournalEntryLineDetail",
                "Id": "0",
                "JournalEntryLineDetail": {
                    "PostingType": "Debit",
                    "Entity": {"Type": "Vendor", "EntityRef": {"value": "1", "name": "Test"}},
                    "AccountRef": {"value": "234", "name": "Expense"},
                    "ClassRef": {"value": "14", "name": "Business"},
                },
            }
        ],
        "MetaData": {
            "CreateTime": pd.to_datetime("2023-02-09T10:36:39-08:00", utc=True),
            "LastUpdatedTime": pd.to_datetime("2023-06-15T16:08:39-07:00", utc=True),
        },
        "PrivateNote": None,
        "SyncToken": "2",
        "TxnDate": "2023-01-13",
        "TaxRateRef": None,
        "TxnTaxDetail": None,
        "airbyte_cursor": "2023-06-15T16:08:39-07:00",
        "domain": "QBO",
        "sparse": False,
    }

    assert writer._json_schema_cast(input) == expected


def test_json_schema_cast_empty_values():
    connector_config = ConnectorConfig(**get_config())
    aws_handler = AwsHandler(connector_config, DestinationAwsDatalake())
    writer = StreamWriter(aws_handler, connector_config, get_camelcase_configured_stream())

    input = {
        "Line": [
            {
                "Id": "0",
                "Description": "Money",
                "Amount": "",
                "DetailType": "JournalEntryLineDetail",
                "JournalEntryLineDetail": "",
            },
        ],
        "MetaData": {"CreateTime": "", "LastUpdatedTime": "2023-06-15"},
    }

    expected = {
        "Adjustment": False,
        "CurrencyRef": None,
        "DocNumber": None,
        "Id": None,
        "Line": [
            {
                "Description": "Money",
                "DetailType": "JournalEntryLineDetail",
                "Id": "0",
                "JournalEntryLineDetail": None,
            }
        ],
        "MetaData": {"LastUpdatedTime": pd.to_datetime("2023-06-15", utc=True)},
        "PrivateNote": None,
        "SyncToken": None,
        "TaxRateRef": None,
        "TxnDate": None,
        "TxnTaxDetail": None,
        "airbyte_cursor": None,
        "domain": None,
        "sparse": False,
    }

    result = writer._json_schema_cast(input)
    exchange_rate = result.pop("ExchangeRate")
    created_time = result["MetaData"].pop("CreateTime")
    line_amount = result["Line"][0].pop("Amount")

    assert result == expected
    assert np.isnan(exchange_rate)
    assert np.isnan(line_amount)
    assert pd.isna(created_time)


def test_json_schema_cast_bad_values():
    connector_config = ConnectorConfig(**get_config())
    aws_handler = AwsHandler(connector_config, DestinationAwsDatalake())
    writer = StreamWriter(aws_handler, connector_config, get_camelcase_configured_stream())

    input = {
        "domain": 12,
        "sparse": "true",
        "Adjustment": 0,
        "Line": [
            {
                "Id": "0",
                "Description": "Money",
                "Amount": "hello",
                "DetailType": "JournalEntryLineDetail",
                "JournalEntryLineDetail": "",
            },
        ],
        "MetaData": {"CreateTime": "hello", "LastUpdatedTime": "2023-06-15"},
    }

    expected = {
        "Adjustment": False,
        "CurrencyRef": None,
        "DocNumber": None,
        "Id": None,
        "Line": [
            {
                "Description": "Money",
                "DetailType": "JournalEntryLineDetail",
                "Id": "0",
                "JournalEntryLineDetail": None,
            }
        ],
        "MetaData": {"LastUpdatedTime": pd.to_datetime("2023-06-15", utc=True)},
        "PrivateNote": None,
        "SyncToken": None,
        "TaxRateRef": None,
        "TxnDate": None,
        "TxnTaxDetail": None,
        "airbyte_cursor": None,
        "domain": "12",
        "sparse": True,
    }

    result = writer._json_schema_cast(input)
    exchange_rate = result.pop("ExchangeRate")
    created_time = result["MetaData"].pop("CreateTime")
    line_amount = result["Line"][0].pop("Amount")

    assert result == expected
    assert np.isnan(exchange_rate)
    assert np.isnan(line_amount)
    assert pd.isna(created_time)


def test_json_dict_encoder():
    dt = "2023-08-01T23:32:11Z"
    dt = pd.to_datetime(dt, utc=True)

    input = {
        "boolean": False,
        "integer": 1,
        "float": 2.0,
        "decimal": Decimal("13.232"),
        "datetime": dt.to_pydatetime(),
        "date": dt.date(),
        "timestamp": dt,
        "nested": {
            "boolean": False,
            "datetime": dt.to_pydatetime(),
            "very_nested": {
                "boolean": False,
                "datetime": dt.to_pydatetime(),
            },
        },
    }

    assert (
        json.dumps(input, cls=DictEncoder)
        == '{"boolean": false, "integer": 1, "float": 2.0, "decimal": "13.232", "datetime": "2023-08-01T23:32:11Z", "date": "2023-08-01", "timestamp": "2023-08-01T23:32:11Z", "nested": {"boolean": false, "datetime": "2023-08-01T23:32:11Z", "very_nested": {"boolean": false, "datetime": "2023-08-01T23:32:11Z"}}}'
    )
