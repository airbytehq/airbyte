#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Mapping

import numpy as np
import pandas as pd
import pyarrow as pa
from destination_aws_datalake import DestinationAwsDatalake
from destination_aws_datalake.aws import AwsHandler
from destination_aws_datalake.config_reader import ConnectorConfig
from destination_aws_datalake.stream_writer import DictEncoder, StreamWriter

from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteStream, DestinationSyncMode, FailureType, SyncMode
from airbyte_cdk.utils import AirbyteTracedException


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


def test_build_type_mismatch_exception_identifies_nested_field():
    writer = get_big_schema_writer(get_config())
    df = pd.DataFrame(
        [
            {
                "location": {
                    "city": "Paris",
                    "country": "FR",
                    "latitude": "48.8566;2.3522",
                    "longitude": 2.3522,
                    "state": "",
                    "zipcode": "75000",
                }
            }
        ]
    )
    ex = pa.ArrowTypeError(
        "object of type <class 'str'> cannot be converted to int",
        "Conversion failed for column location with type object",
    )

    traced = writer._build_type_mismatch_exception(df, ex)

    assert isinstance(traced, AirbyteTracedException)
    assert traced.failure_type == FailureType.config_error
    assert 'Stream "append_stream_big"' in traced.message
    assert 'field "location.latitude"' in traced.message
    assert "type str" in traced.message
    assert "declared type number" in traced.message


def test_build_type_mismatch_exception_identifies_array_field():
    writer = get_big_schema_writer(get_config())
    df = pd.DataFrame(
        [
            {
                "questions": [
                    {"id": 1, "question": "q1", "answer": "a1"},
                    {"id": "not-an-int", "question": "q2", "answer": "a2"},
                ]
            }
        ]
    )
    ex = pa.ArrowInvalid("Conversion failed for column questions with type object")

    traced = writer._build_type_mismatch_exception(df, ex)

    assert isinstance(traced, AirbyteTracedException)
    # Array elements are aggregated under `[]` rather than indexed,
    # because pyarrow's per-column type inference is also position-agnostic.
    assert "questions[].id" in traced.message
    assert "int" in traced.message
    assert "str" in traced.message


def test_build_type_mismatch_exception_falls_back_to_column_when_no_leaf_mismatch():
    writer = get_big_schema_writer(get_config())
    df = pd.DataFrame([{"location": {"city": "Paris"}}])
    ex = pa.ArrowInvalid("Conversion failed for column location with type object")

    traced = writer._build_type_mismatch_exception(df, ex)

    assert isinstance(traced, AirbyteTracedException)
    assert "location" in traced.message


def test_build_type_mismatch_exception_when_column_unknown():
    writer = get_big_schema_writer(get_config())
    df = pd.DataFrame([{"sourceId": "abc"}])
    ex = pa.ArrowInvalid("some other pyarrow failure we cannot parse")

    traced = writer._build_type_mismatch_exception(df, ex)

    assert isinstance(traced, AirbyteTracedException)


def test_build_type_mismatch_exception_filters_to_pyarrow_type_pair():
    """When the pyarrow error names a (observed, target) pair, the walker
    should skip unrelated mismatches in the same struct and report the field
    that actually matches that pair."""
    writer = get_big_schema_writer(get_config())
    df = pd.DataFrame(
        [
            {
                "location": {
                    "city": pd.Timestamp("2023-01-01"),
                    "country": "FR",
                    "latitude": "48.8566",
                    "longitude": 2.3522,
                    "state": "",
                    "zipcode": "75000",
                }
            }
        ]
    )
    ex = pa.ArrowTypeError(
        "object of type <class 'str'> cannot be converted to int",
        "Conversion failed for column location with type object",
    )

    traced = writer._build_type_mismatch_exception(df, ex)

    assert isinstance(traced, AirbyteTracedException)
    assert 'field "location.latitude"' in traced.message
    assert "type str" in traced.message
    assert "declared type number" in traced.message


def test_build_type_mismatch_exception_falls_back_when_no_filter_match():
    """If the pyarrow error names a (observed, target) pair but no field in
    the struct matches that pair, the walker should fall back to the first
    mismatch instead of returning nothing."""
    writer = get_big_schema_writer(get_config())
    df = pd.DataFrame(
        [
            {
                "location": {
                    "city": pd.Timestamp("2023-01-01"),
                    "country": "FR",
                    "latitude": 48.8566,
                    "longitude": 2.3522,
                    "state": "",
                    "zipcode": "75000",
                }
            }
        ]
    )
    ex = pa.ArrowTypeError(
        "object of type <class 'str'> cannot be converted to int",
        "Conversion failed for column location with type object",
    )

    traced = writer._build_type_mismatch_exception(df, ex)

    assert isinstance(traced, AirbyteTracedException)
    assert 'field "location.city"' in traced.message
    assert "Timestamp" in traced.message
    assert "declared type string" in traced.message


def test_parse_pyarrow_type_hint():
    """Direct tests for the pyarrow error parser covering both message
    shapes and the unparseable case."""
    observed, declared = StreamWriter._parse_pyarrow_type_hint("object of type <class 'str'> cannot be converted to int")
    assert observed == "str"
    assert declared == ("integer", "number")

    observed, declared = StreamWriter._parse_pyarrow_type_hint("Could not convert 'foo' with type str: tried to convert to double")
    assert observed == "str"
    assert declared == ("number",)

    observed, declared = StreamWriter._parse_pyarrow_type_hint("completely unrelated error message")
    assert observed is None
    assert declared is None


def test_build_type_mismatch_exception_finds_mixed_type_subfield_not_in_schema():
    """The real production case: pyarrow's struct-inference fails on a sub-field
    of `properties` that is NOT in the declared JSON schema (so the json-schema
    cast skips it), but for which different records have different Python types.
    The mixed-type discoverer should pinpoint that field even though the
    json-schema walker cannot."""
    writer = get_big_schema_writer(get_config())
    df = pd.DataFrame(
        [
            # Note: `mystery_id` is not in the declared schema's `location.properties`.
            # Without mixed-type discovery, the walker would never find it.
            {"location": {"city": pd.Timestamp("2023-01-01"), "mystery_id": 12345}},
            {"location": {"city": pd.Timestamp("2023-01-02"), "mystery_id": "9876;5432"}},
        ]
    )
    ex = pa.ArrowTypeError(
        "object of type <class 'str'> cannot be converted to int",
        "Conversion failed for column location with type object",
    )

    traced = writer._build_type_mismatch_exception(df, ex)

    assert isinstance(traced, AirbyteTracedException)
    assert 'field "location.mystery_id"' in traced.message
    assert "int" in traced.message
    assert "str" in traced.message


def test_build_type_mismatch_exception_prefers_observed_type_match_over_other_mixed_paths():
    """When several sub-paths have mixed Python types but only some contain
    the observed type from the pyarrow error, the discoverer should prefer
    the ones that contain that observed type."""
    writer = get_big_schema_writer(get_config())
    df = pd.DataFrame(
        [
            {"location": {"foo": 1, "bar": 1.5}},
            {"location": {"foo": 2.5, "bar": "this-is-a-str"}},
        ]
    )
    ex = pa.ArrowTypeError(
        "object of type <class 'str'> cannot be converted to int",
        "Conversion failed for column location with type object",
    )

    traced = writer._build_type_mismatch_exception(df, ex)

    assert isinstance(traced, AirbyteTracedException)
    # `location.bar` contains `str` (matches the observed type from pyarrow);
    # `location.foo` is mixed int/float but does not contain `str`, so it
    # must NOT be ranked first.
    assert 'field "location.bar"' in traced.message
    assert 'field "location.foo"' not in traced.message


def test_build_type_mismatch_exception_identifies_uniform_offender_subfield():
    """When every record has the same offending Python type (for example `str`)
    at a sub-path but pyarrow wants a different type (for example `int`), the
    walker should still flag that path as the culprit. Mixed-type detection
    alone misses this case because only one type is observed at the path."""
    writer = get_big_schema_writer(get_config())
    df = pd.DataFrame(
        [
            {"location": {"city": pd.Timestamp("2023-01-01"), "mystery_id": "9876;5432"}},
            {"location": {"city": pd.Timestamp("2023-01-02"), "mystery_id": "1234;abcd"}},
            {"location": {"city": pd.Timestamp("2023-01-03"), "mystery_id": "0000;0001"}},
        ]
    )
    ex = pa.ArrowTypeError(
        "object of type <class 'str'> cannot be converted to int",
        "Conversion failed for column location with type object",
    )

    traced = writer._build_type_mismatch_exception(df, ex)

    assert isinstance(traced, AirbyteTracedException)
    assert 'field "location.mystery_id"' in traced.message
    assert "str" in traced.message
    assert "int" in traced.message


def test_build_type_mismatch_exception_prefers_mixed_over_uniform_offender():
    """When both a mixed-type path and a uniform-offender path exist under the
    same column, mixed-type takes priority because it's the stronger signal of
    pyarrow's struct-inference tripping."""
    writer = get_big_schema_writer(get_config())
    df = pd.DataFrame(
        [
            {"location": {"uniform_str_field": "aaa", "ambiguous": 1}},
            {"location": {"uniform_str_field": "bbb", "ambiguous": "two"}},
        ]
    )
    ex = pa.ArrowTypeError(
        "object of type <class 'str'> cannot be converted to int",
        "Conversion failed for column location with type object",
    )

    traced = writer._build_type_mismatch_exception(df, ex)

    assert isinstance(traced, AirbyteTracedException)
    # `ambiguous` is mixed str/int (contains both observed and target) → rank 0.
    # `uniform_str_field` is uniform str (rank 2). Mixed should win.
    assert 'field "location.ambiguous"' in traced.message


def test_build_type_mismatch_exception_uniform_field_of_target_type_is_not_flagged():
    """A uniform sub-path whose single type matches the target type (for
    example `Decimal` when target wants `int`) is a valid field, not a
    culprit, and must not be reported."""
    writer = get_big_schema_writer(get_config())
    df = pd.DataFrame(
        [
            {"location": {"numeric_id": 12345}},
            {"location": {"numeric_id": 67890}},
        ]
    )
    ex = pa.ArrowTypeError(
        "object of type <class 'str'> cannot be converted to int",
        "Conversion failed for column location with type object",
    )

    traced = writer._build_type_mismatch_exception(df, ex)

    # No `str` sub-paths exist, so the mixed-type walker has nothing; the
    # walker falls back to the JSON-schema walker and reports on the column
    # as a whole.
    assert isinstance(traced, AirbyteTracedException)
    assert 'field "location.numeric_id"' not in traced.message


def test_collect_observed_types_aggregates_arrays_under_bracket_path():
    """Lists are walked as a single position-agnostic group: every element
    contributes its types to the same `<prefix>[]` path."""
    type_map: dict = {}
    StreamWriter._collect_observed_types(
        {"items": [{"id": 1}, {"id": "two"}, None]},
        prefix="root",
        type_map=type_map,
    )
    assert type_map == {"root.items[].id": {"int", "str"}}


def test_parse_pyarrow_target_python_types():
    assert StreamWriter._parse_pyarrow_target_python_types("object of type <class 'str'> cannot be converted to int") == ("int", "Decimal")
    assert StreamWriter._parse_pyarrow_target_python_types("Could not convert 'foo' with type str: tried to convert to double") == (
        "float",
        "Decimal",
    )
    assert StreamWriter._parse_pyarrow_target_python_types("unrelated message") is None


def test_build_type_mismatch_exception_probe_uses_glue_dtype_to_pinpoint_culprit():
    """The production case: every sub-path under `properties` is uniformly
    `str`, so neither the mixed-type walker nor the JSON-schema walker
    pinpoints a culprit. The brute-force probe should fall back to the Glue
    dtype dict (the actual oracle pyarrow validated against) to identify
    which sub-field expected `bigint`/`int` and verify that pyarrow's error
    reproduces there."""
    writer = get_big_schema_writer(get_config())
    # Simulate awswrangler being told to expect `bigint` for `properties.foo`
    # — for example because the existing Glue table has that column as
    # bigint from a prior sync.
    writer._last_flush_dtype = {"properties": "struct<foo:bigint,bar:string,baz:string>"}
    writer._schema = {"properties": {"type": ["null", "object"], "additionalProperties": True}}
    df = pd.DataFrame(
        [
            {"properties": {"foo": "abc", "bar": "x", "baz": "y"}},
            {"properties": {"foo": "def", "bar": "x", "baz": "y"}},
        ]
    )
    ex = pa.ArrowTypeError(
        "object of type <class 'str'> cannot be converted to int",
        "Conversion failed for column properties with type object",
    )

    traced = writer._build_type_mismatch_exception(df, ex)

    assert isinstance(traced, AirbyteTracedException)
    assert 'field "properties.foo"' in traced.message
    # `bar` and `baz` are declared as `string` in the dtype dict — even
    # though they are uniform-str like `foo`, pyarrow would not have
    # rejected them, and the probe must NOT misattribute them.
    assert 'field "properties.bar"' not in traced.message
    assert 'field "properties.baz"' not in traced.message
    assert "probe_path=properties.foo" in traced.internal_message
    assert "column_glue_type=struct<foo:bigint,bar:string,baz:string>" in traced.internal_message


def test_probe_pyarrow_culprit_uses_glue_oracle_to_disambiguate_uniform_str_paths():
    """When multiple sub-paths are uniform-str, the probe must use the Glue
    dtype dict to identify which one was declared as the target type
    (for example `bigint` for `int` target). Without this oracle, every
    uniform-str path raises and the probe would return the first
    iteration-order match."""
    writer = get_big_schema_writer(get_config())
    writer._last_flush_dtype = {"properties": "struct<a:string,b:bigint,c:string>"}
    writer._schema = {"properties": {"type": ["null", "object"], "additionalProperties": True}}
    values = [
        {"a": "x", "b": "9876", "c": "z"},
        {"a": "x", "b": "5432", "c": "z"},
    ]
    type_map = {
        "properties.a": {"str"},
        "properties.b": {"str"},
        "properties.c": {"str"},
    }
    path, err = writer._probe_pyarrow_culprit(
        values=values,
        column_prefix="properties",
        target_pa_type=pa.int64(),
        observed_type_map=type_map,
        observed_filter="str",
        target_glue_types=("bigint", "int", "smallint", "tinyint", "long"),
    )
    assert path == "properties.b"
    assert err is not None
    assert "convert" in err


def test_probe_pyarrow_culprit_returns_none_when_no_glue_target_path_reproduces_error():
    """If every Glue-declared int sub-path converts cleanly to the target
    type, the probe must return `(None, None)` rather than a false positive."""
    writer = get_big_schema_writer(get_config())
    writer._last_flush_dtype = {"properties": "struct<a:bigint,b:string>"}
    writer._schema = {"properties": {"type": ["null", "object"], "additionalProperties": True}}
    values = [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]
    type_map = {"properties.a": {"int"}, "properties.b": {"str"}}
    path, err = writer._probe_pyarrow_culprit(
        values=values,
        column_prefix="properties",
        target_pa_type=pa.int64(),
        observed_type_map=type_map,
        observed_filter="str",
        target_glue_types=("bigint",),
    )
    assert path is None
    assert err is None


def test_collect_glue_paths_matching_target_handles_nested_struct_and_array():
    paths = StreamWriter._collect_glue_paths_matching_target(
        glue_type="struct<a:bigint,b:string,nested:struct<n:bigint>,arr:array<struct<m:bigint>>>",
        prefix="props",
        target_glue_types=("bigint",),
    )
    assert paths == {"props.a", "props.nested.n", "props.arr[].m"}


def test_extract_values_at_path_walks_dotted_keys():
    values = [{"a": {"b": 1}}, {"a": {"b": 2}}, {"a": {}}]
    extracted = StreamWriter._extract_values_at_path(values, "props.a.b", "props")
    assert extracted == [1, 2, None]


def test_extract_values_at_path_walks_array_marker():
    values = [{"items": [{"id": 1}, {"id": 2}]}, {"items": [{"id": 3}]}]
    extracted = StreamWriter._extract_values_at_path(values, "props.items[].id", "props")
    assert extracted == [1, 2, 3]


def test_parse_pyarrow_target_pa_type():
    assert StreamWriter._parse_pyarrow_target_pa_type("object of type <class 'str'> cannot be converted to int") == pa.int64()
    assert StreamWriter._parse_pyarrow_target_pa_type("Could not convert 'foo' with type str: tried to convert to double") == pa.float64()
    assert StreamWriter._parse_pyarrow_target_pa_type("unrelated message") is None


def test_probe_struct_subkey_culprit_finds_inferred_int_subkey_with_str_value():
    """The first record establishes the inferred subkey type; a later
    record with a `str` value at that subkey makes pyarrow raise. The
    probe must surface that subkey by replaying `pa.array()` on its
    column and matching the error's target type to `target_pa_type`."""
    values = [
        {"alpha": "x", "hs_object_id": 12345},
        {"alpha": "y", "hs_object_id": 67890},
        {"alpha": "z", "hs_object_id": "not-an-int"},
    ]
    culprit, err, sample = StreamWriter._probe_struct_subkey_culprit(
        values=values,
        target_pa_type=pa.int64(),
    )
    assert culprit == "hs_object_id"
    assert err is not None and ("int" in err)
    sample_dict = dict(sample)
    assert sample_dict["alpha"] == "string"
    assert sample_dict["hs_object_id"].startswith("ERR:")


def test_probe_struct_subkey_culprit_returns_none_when_no_subkey_raises():
    """If every subkey infers cleanly, the probe returns no culprit."""
    values = [{"a": "x", "b": 1}, {"a": "y", "b": 2}]
    culprit, err, sample = StreamWriter._probe_struct_subkey_culprit(
        values=values,
        target_pa_type=pa.int64(),
    )
    assert culprit is None
    assert err is None
    sample_dict = dict(sample)
    assert sample_dict["a"] == "string"
    assert sample_dict["b"] == "int64"


def test_probe_struct_subkey_culprit_does_not_match_unrelated_target_type():
    """A subkey that raises for a different target type must NOT be
    surfaced as the culprit. Here pyarrow infers `int64` for `b` and
    fails on the str — the probe is told the original error targeted
    `double`, so the int failure is unrelated."""
    values = [{"a": "x", "b": 1}, {"a": "y", "b": "boom"}]
    culprit, err, _sample = StreamWriter._probe_struct_subkey_culprit(
        values=values,
        target_pa_type=pa.float64(),
    )
    assert culprit is None
    assert err is None


def test_probe_struct_subkey_culprit_skips_all_null_keys():
    """A subkey that's `None` in every record contributes no inference."""
    values = [{"a": "x", "b": None}, {"a": "y", "b": None}]
    _culprit, _err, sample = StreamWriter._probe_struct_subkey_culprit(
        values=values,
        target_pa_type=pa.int64(),
    )
    keys = {k for k, _ in sample}
    assert keys == {"a"}


def test_probe_struct_subkey_culprit_ignores_non_dict_records():
    """`None` records (where the column is null on a row) must not crash
    the probe — they simply don't contribute any sub-keys."""
    values = [None, {"a": 1}, None, {"a": "boom"}]
    culprit, err, sample = StreamWriter._probe_struct_subkey_culprit(
        values=values,
        target_pa_type=pa.int64(),
    )
    assert culprit == "a"
    assert err is not None
    assert dict(sample)["a"].startswith("ERR:")


def test_build_type_mismatch_exception_subkey_probe_overrides_glue_oracle_for_undeclared_subkey():
    """Reproduces the HubSpot scenario: every Glue sub-field is `string`
    so the Glue oracle finds no `bigint` candidate, but pyarrow infers
    `int64` for one undeclared subkey from the data and crashes when
    a later record has `str` there. The new per-subkey probe must
    pinpoint that undeclared subkey."""
    writer = get_big_schema_writer(get_config())
    writer._last_flush_dtype = {"properties": "struct<a:string,c:string>"}
    writer._schema = {"properties": {"type": ["null", "object"], "additionalProperties": True}}
    df = pd.DataFrame(
        {
            "properties": [
                {"a": "x", "hs_object_id": 1},
                {"a": "y", "hs_object_id": 2},
                {"a": "z", "hs_object_id": "boom"},
            ],
        }
    )
    arrow_error = pa.lib.ArrowTypeError(
        "object of type <class 'str'> cannot be converted to int",
        "Conversion failed for column properties with type object",
    )
    traced = writer._build_type_mismatch_exception(df, arrow_error)
    assert 'field "properties.hs_object_id"' in traced.message
    assert "subkey_probe_path=properties.hs_object_id" in traced.internal_message
    assert "subkey_inference_sample=" in traced.internal_message
