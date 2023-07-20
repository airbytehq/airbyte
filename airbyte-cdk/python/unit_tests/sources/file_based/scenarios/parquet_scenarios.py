#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import decimal

import pyarrow as pa
from unit_tests.sources.file_based.in_memory_files_source import TemporaryParquetFilesStreamReader
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenarioBuilder

_single_parquet_file = {
    "a.parquet": {
        "contents": [
            ("col1", "col2"),
            ("val11", "val12"),
            ("val21", "val22"),
        ],
        "last_modified": "2023-06-05T03:54:07.000Z",
    }
}

_parquet_file_with_decimal = {
    "a.parquet": {
        "contents": [
            ("col1", ),
            (decimal.Decimal("13.00"),),
        ],
        "schema": pa.schema([
            pa.field("col1", pa.decimal128(5, 2)),
        ]),
        "last_modified": "2023-06-05T03:54:07.000Z",
    }
}

_multiple_parquet_file = {
    "a.parquet": {
        "contents": [
            ("col1", "col2"),
            ("val11a", "val12a"),
            ("val21a", "val22a"),
        ],
        "last_modified": "2023-06-05T03:54:07.000Z",
    },
    "b.parquet": {
        "contents": [
            ("col1", "col2", "col3"),
            ("val11b", "val12b", "val13b"),
            ("val21b", "val22b", "val23b"),
        ],
        "last_modified": "2023-06-05T03:54:07.000Z",
    },
}

_parquet_file_with_various_types = {
    "a.parquet": {
        "contents": [
            ("col_bool",

             "col_int8",
             "col_int16",
             "col_int32",

             "col_uint8",
             "col_uint16",
             "col_uint32",
             "col_uint64",

             "col_float32",
             "col_float64",

             "col_string",

             "col_date32",
             "col_date64",

             "col_timestamp_without_tz",
             "col_timestamp_with_tz",

             "col_time32s",
             "col_time32ms",
             "col_time64us",

             "col_struct",
             "col_list",
             "col_duration",
             "col_binary",
             ),
            (True,

             -1,
             1,
             2,

             2,
             3,
             4,
             5,

             3.14,
             5.0,

             "2020-01-01",

             datetime.date(2021, 1, 1),
             datetime.date(2022, 1, 1),
             datetime.datetime(2023, 1, 1, 1, 2, 3),
             datetime.datetime(2024, 3, 4, 5, 6, 7, tzinfo=datetime.timezone.utc),

             datetime.time(1, 2, 3),
             datetime.time(2, 3, 4),
             datetime.time(1, 2, 3, 4),
             {"struct_key": "struct_value"},
             [1, 2, 3, 4],
             12345,
             b"binary string. Hello world!",
             ),
        ],
        "schema": pa.schema([
            pa.field("col_bool", pa.bool_()),

            pa.field("col_int8", pa.int8()),
            pa.field("col_int16", pa.int16()),
            pa.field("col_int32", pa.int32()),

            pa.field("col_uint8", pa.uint8()),
            pa.field("col_uint16", pa.uint16()),
            pa.field("col_uint32", pa.uint32()),
            pa.field("col_uint64", pa.uint64()),

            pa.field("col_float32", pa.float32()),
            pa.field("col_float64", pa.float64()),

            pa.field("col_string", pa.string()),

            pa.field("col_date32", pa.date32()),
            pa.field("col_date64", pa.date64()),
            pa.field("col_timestamp_without_tz", pa.timestamp("s")),
            pa.field("col_timestamp_with_tz", pa.timestamp("s", tz="UTC")),

            pa.field("col_time32s", pa.time32("s")),
            pa.field("col_time32ms", pa.time32("ms")),
            pa.field("col_time64us", pa.time64("us")),

            pa.field("col_struct", pa.struct([pa.field("struct_key", pa.string())])),
            pa.field("col_list", pa.list_(pa.int32())),
            pa.field("col_duration", pa.duration("s")),
            pa.field("col_binary", pa.binary())
        ]),
        "last_modified": "2023-06-05T03:54:07.000Z",
    }
}

single_parquet_scenario = (
    TestScenarioBuilder()
    .set_name("single_parquet_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "parquet",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_stream_reader(TemporaryParquetFilesStreamReader(files=_single_parquet_file, file_type="parquet"))
    .set_file_type("parquet")
    .set_expected_records(
        [
            {"data": {"col1": "val11", "col2": "val12", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.parquet"}, "stream": "stream1"},
            {"data": {"col1": "val21", "col2": "val22", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.parquet"}, "stream": "stream1"},
        ]
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": "string"
                            },
                            "col2": {
                                "type": "string"
                            },
                            "_ab_source_file_last_modified": {
                                "type": "string"
                            },
                            "_ab_source_file_url": {
                                "type": "string"
                            },
                        }
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
).build()

multi_parquet_scenario = (
    TestScenarioBuilder()
    .set_name("multi_parquet_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "parquet",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_file_type("parquet")
    .set_stream_reader(TemporaryParquetFilesStreamReader(files=_multiple_parquet_file, file_type="parquet"))
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": "string"
                            },
                            "col2": {
                                "type": "string"
                            },
                            "col3": {
                                "type": "string"
                            },
                            "_ab_source_file_last_modified": {
                                "type": "string"
                            },
                            "_ab_source_file_url": {
                                "type": "string"
                            },
                        }
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
    .set_expected_records(
        [
            {"data": {"col1": "val11a", "col2": "val12a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.parquet"}, "stream": "stream1"},
            {"data": {"col1": "val21a", "col2": "val22a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.parquet"}, "stream": "stream1"},
            {"data": {"col1": "val11b", "col2": "val12b", "col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "b.parquet"}, "stream": "stream1"},
            {"data": {"col1": "val21b", "col2": "val22b", "col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "b.parquet"}, "stream": "stream1"},
        ]
    )
).build()

parquet_various_types_scenario = (
    TestScenarioBuilder()
    .set_name("parquet_various_types")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "parquet",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_stream_reader(TemporaryParquetFilesStreamReader(files=_parquet_file_with_various_types, file_type="parquet"))
    .set_file_type("parquet")
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col_bool": {
                                "type": "boolean"
                            },
                            "col_int8": {
                                "type": "integer"
                            },
                            "col_int16": {
                                "type": "integer"
                            },
                            "col_int32": {
                                "type": "integer"
                            },
                            "col_uint8": {
                                "type": "integer"
                            },
                            "col_uint16": {
                                "type": "integer"
                            },
                            "col_uint32": {
                                "type": "integer"
                            },
                            "col_uint64": {
                                "type": "integer"
                            },
                            "col_float32": {
                                "type": "number"
                            },
                            "col_float64": {
                                "type": "number"
                            },
                            "col_string": {
                                "type": "string"
                            },
                            "col_date32": {
                                "type": "string",
                                "format": "date"
                            },
                            "col_date64": {
                                "type": "string",
                                "format": "date"
                            },
                            "col_timestamp_without_tz": {
                                "type": "string",
                                "format": "date-time"
                            },
                            "col_timestamp_with_tz": {
                                "type": "string",
                                "format": "date-time"
                            },
                            "col_time32s": {
                                "type": "string",
                            },
                            "col_time32ms": {
                                "type": "string",
                            },
                            "col_time64us": {
                                "type": "string",
                            },
                            "col_struct": {
                                "type": "object",
                            },
                            "col_list": {
                                "type": "array",
                            },
                            "col_duration": {
                                "type": "integer",
                            },
                            "col_binary": {
                                "type": "string",
                            },
                            "_ab_source_file_last_modified": {
                                "type": "string"
                            },
                            "_ab_source_file_url": {
                                "type": "string"
                            },
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
    .set_expected_records(
        [
            {"data": {"col_bool": True,
                      "col_int8": -1,
                      "col_int16": 1,
                      "col_int32": 2,
                      "col_uint8": 2,
                      "col_uint16": 3,
                      "col_uint32": 4,
                      "col_uint64": 5,
                      "col_float32": 3.14,
                      "col_float64": 5.0,
                      "col_string": "2020-01-01",
                      "col_date32": "2021-01-01",
                      "col_date64": "2022-01-01",
                      "col_timestamp_without_tz": "2023-01-01T01:02:03",
                      "col_timestamp_with_tz": "2024-03-04T05:06:07+00:00",
                      "col_time32s": "01:02:03",
                      "col_time32ms": "02:03:04",
                      "col_time64us": "01:02:03.000004",
                      "col_struct": {"struct_key": "struct_value"},
                      "col_list": [1, 2, 3, 4],
                      "col_duration": 12345,
                      "col_binary": "binary string. Hello world!",
                      "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.parquet"}, "stream": "stream1"
             },
        ]
    )
).build()

parquet_file_with_decimal_no_config_scenario = (
    TestScenarioBuilder()
    .set_name("parquet_file_with_decimal_no_config")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "parquet",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_stream_reader(TemporaryParquetFilesStreamReader(files=_parquet_file_with_decimal, file_type="parquet"))
    .set_file_type("parquet")
    .set_expected_records(
        [
            {"data": {"col1": "13.00", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.parquet"}, "stream": "stream1"},
        ]
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": "string"
                            },
                            "_ab_source_file_last_modified": {
                                "type": "string"
                            },
                            "_ab_source_file_url": {
                                "type": "string"
                            },
                        }
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
).build()

parquet_file_with_decimal_as_string_scenario = (
    TestScenarioBuilder()
    .set_name("parquet_file_with_decimal_as_string")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "parquet",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                    "format": {
                        "parquet": {
                            "filetype": "parquet",
                            "decimal_as_float": False
                        }
                    }
                }
            ]
        }
    )
    .set_stream_reader(TemporaryParquetFilesStreamReader(files=_parquet_file_with_decimal, file_type="parquet"))
    .set_file_type("parquet")
    .set_expected_records(
        [
            {"data": {"col1": "13.00", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.parquet"}, "stream": "stream1"},
        ]
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": "string"
                            },
                            "_ab_source_file_last_modified": {
                                "type": "string"
                            },
                            "_ab_source_file_url": {
                                "type": "string"
                            },
                        }
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
).build()

parquet_file_with_decimal_as_float_scenario = (
    TestScenarioBuilder()
    .set_name("parquet_file_with_decimal_as_float")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "parquet",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                    "format": {
                        "parquet": {
                            "filetype": "parquet",
                            "decimal_as_float": True
                        }
                    }
                }
            ]
        }
    )
    .set_stream_reader(TemporaryParquetFilesStreamReader(files=_parquet_file_with_decimal, file_type="parquet"))
    .set_file_type("parquet")
    .set_expected_records(
        [
            {"data": {"col1": 13.00, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.parquet"}, "stream": "stream1"},
        ]
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": "number"
                            },
                            "_ab_source_file_last_modified": {
                                "type": "string"
                            },
                            "_ab_source_file_url": {
                                "type": "string"
                            },
                        }
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
).build()

parquet_file_with_decimal_legacy_config_scenario = (
    TestScenarioBuilder()
    .set_name("parquet_file_with_decimal_legacy_config")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "parquet",
                    "format": {
                        "filetype": "parquet",
                    },
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_stream_reader(TemporaryParquetFilesStreamReader(files=_parquet_file_with_decimal, file_type="parquet"))
    .set_file_type("parquet")
    .set_expected_records(
        [
            {"data": {"col1": 13.00, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.parquet"}, "stream": "stream1"},
        ]
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": "number"
                            },
                            "_ab_source_file_last_modified": {
                                "type": "string"
                            },
                            "_ab_source_file_url": {
                                "type": "string"
                            },
                        }
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
).build()
