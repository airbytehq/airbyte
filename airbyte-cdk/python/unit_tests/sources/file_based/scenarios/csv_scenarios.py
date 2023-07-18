#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.file_based.exceptions import ConfigValidationError, FileBasedSourceError, SchemaInferenceError
from unit_tests.sources.file_based.helpers import EmptySchemaParser, LowInferenceLimitDiscoveryPolicy
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenarioBuilder

single_csv_scenario = (
    TestScenarioBuilder()
    .set_name("single_csv_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ],
            "start_date": "2023-06-04T03:54:07Z"
        }
    )
    .set_files(
        {
            "a.csv": {
                "contents": [
                    ("col1", "col2"),
                    ("val11", "val12"),
                    ("val21", "val22"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            }
        }
    )
    .set_file_type("csv")
    .set_expected_spec(
        {
            "documentationUrl": "https://docs.airbyte.com/integrations/sources/in_memory_files",
            "connectionSpecification": {
                "title": "InMemorySpec",
                "description": "Used during spec; allows the developer to configure the cloud provider specific options\nthat are needed when users configure a file-based source.",
                "type": "object",
                "properties": {
                    "streams": {
                        "title": "The list of streams to sync",
                        "description": "Each instance of this configuration defines a <a href=\"https://docs.airbyte.com/cloud/core-concepts#stream\">stream</a>. Use this to define which files belong in the stream, their format, and how they should be parsed and validated. When sending data to warehouse destination such as Snowflake or BigQuery, each stream is a separate table.",
                        "order": 10,
                        "type": "array",
                        "items": {
                            "title": "FileBasedStreamConfig",
                            "type": "object",
                            "properties": {
                                "name": {
                                    "title": "Name",
                                    "description": "The name of the stream.",
                                    "type": "string"
                                },
                                "file_type": {
                                    "title": "File Type",
                                    "description": "The data file type that is being extracted for a stream.",
                                    "type": "string"
                                },
                                "globs": {
                                    "title": "Globs",
                                    "description": "The pattern used to specify which files should be selected from the file system. For more information on glob pattern matching look <a href=\"https://en.wikipedia.org/wiki/Glob_(programming)\">here</a>.",
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                },
                                "validation_policy": {
                                    "title": "Validation Policy",
                                    "description": "The name of the validation policy that dictates sync behavior when a record does not adhere to the stream schema.",
                                    "type": "string"
                                },
                                "input_schema": {
                                    "title": "Input Schema",
                                    "description": "The schema that will be used to validate records extracted from the file. This will override the stream schema that is auto-detected from incoming files.",
                                    "oneOf": [
                                        {
                                            "type": "string"
                                        },
                                        {
                                            "type": "object"
                                        }
                                    ]
                                },
                                "primary_key": {
                                    "title": "Primary Key",
                                    "description": "The column or columns (for a composite key) that serves as the unique identifier of a record.",
                                    "oneOf": [
                                        {
                                            "type": "string"
                                        },
                                        {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        }
                                    ]
                                },
                                "days_to_sync_if_history_is_full": {
                                    "title": "Days To Sync If History Is Full",
                                    "description": "When the state history of the file store is full, syncs will only read files that were last modified in the provided day range.",
                                    "default": 3,
                                    "type": "integer"
                                },
                                "format": {
                                    "oneOf": [
                                        {
                                            "title": "Format",
                                            "description": "The configuration options that are used to alter how to read incoming files that deviate from the standard formatting.",
                                            "type": "object",
                                            "additionalProperties": {
                                                "oneOf": [
                                                    {
                                                        "title": "CsvFormat",
                                                        "type": "object",
                                                        "properties": {
                                                            "filetype": {
                                                                "title": "Filetype",
                                                                "default": "csv",
                                                                "enum": [
                                                                    "csv"
                                                                ],
                                                                "type": "string"
                                                            },
                                                            "delimiter": {
                                                                "title": "Delimiter",
                                                                "description": "The character delimiting individual cells in the CSV data. This may only be a 1-character string. For tab-delimited data enter '\\t'.",
                                                                "default": ",",
                                                                "type": "string"
                                                            },
                                                            "quote_char": {
                                                                "title": "Quote Character",
                                                                "description": "The character used for quoting CSV values. To disallow quoting, make this field blank.",
                                                                "default": "\"",
                                                                "type": "string"
                                                            },
                                                            "escape_char": {
                                                                "title": "Escape Character",
                                                                "description": "The character used for escaping special characters. To disallow escaping, leave this field blank.",
                                                                "type": "string"
                                                            },
                                                            "encoding": {
                                                                "title": "Encoding",
                                                                "description": "The character encoding of the CSV data. Leave blank to default to <strong>UTF8</strong>. See <a href=\"https://docs.python.org/3/library/codecs.html#standard-encodings\" target=\"_blank\">list of python encodings</a> for allowable options.",
                                                                "default": "utf8",
                                                                "type": "string"
                                                            },
                                                            "double_quote": {
                                                                "title": "Double Quote",
                                                                "description": "Whether two quotes in a quoted CSV value denote a single quote in the data.",
                                                                "default": True,
                                                                "type": "boolean"
                                                            },
                                                            "quoting_behavior": {
                                                                "title": "Quoting Behavior",
                                                                "description": "The quoting behavior determines when a value in a row should have quote marks added around it. For example, if Quote Non-numeric is specified, while reading, quotes are expected for row values that do not contain numbers. Or for Quote All, every row value will be expecting quotes.",
                                                                "default": "Quote Special Characters",
                                                                "enum": [
                                                                    "Quote All",
                                                                    "Quote Special Characters",
                                                                    "Quote Non-numeric",
                                                                    "Quote None"
                                                                ]
                                                            }
                                                        }
                                                    },
                                                    {
                                                        "title": "ParquetFormat",
                                                        "type": "object",
                                                        "properties": {
                                                            "filetype": {
                                                                "title": "Filetype",
                                                                "default": "parquet",
                                                                "enum": [
                                                                    "parquet"
                                                                ],
                                                                "type": "string"
                                                            },
                                                            "decimal_as_float": {
                                                                "title": "Convert Decimal Fields to Floats",
                                                                "description": "Whether to convert decimal fields to floats. There is a loss of precision when converting decimals to floats, so this is not recommended.",
                                                                "default": False,
                                                                "type": "boolean"
                                                            }
                                                        }
                                                    },
                                                    {
                                                        "title": "JsonlFormat",
                                                        "type": "object",
                                                        "properties": {
                                                            "filetype": {
                                                                "title": "Filetype",
                                                                "default": "jsonl",
                                                                "enum": [
                                                                    "jsonl"
                                                                ],
                                                                "type": "string"
                                                            }
                                                        }
                                                    }
                                                ]
                                            }
                                        },
                                        {
                                            "title": "Legacy Format",
                                            "required": [
                                                "filetype"
                                            ],
                                            "type": "object",
                                            "properties": {
                                                "filetype": {
                                                    "title": "Filetype",
                                                    "type": "string"
                                                }
                                            }
                                        }
                                    ]
                                },
                                "schemaless": {
                                    "title": "Schemaless",
                                    "description": "When enabled, syncs will not validate or structure records against the stream's schema.",
                                    "default": False,
                                    "type": "boolean"
                                }
                            },
                            "required": [
                                "name",
                                "file_type",
                                "validation_policy"
                            ]
                        }
                    },
                    "start_date": {
                        "title": "Start Date",
                        "description": "UTC date and time in the format 2017-01-25T00:00:00Z. Any file modified before this date will not be replicated.",
                        "examples": [
                            "2021-01-01T00:00:00Z"
                        ],
                        "format": "date-time",
                        "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
                        "order": 1,
                        "type": "string"
                    }
                },
                "required": [
                    "streams"
                ]
            }
        }
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
            {"data": {"col1": "val11", "col2": "val12", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"col1": "val21", "col2": "val22", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
        ]
    )
).build()

multi_csv_scenario = (
    TestScenarioBuilder()
    .set_name("multi_csv_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_files(
        {
            "a.csv": {
                "contents": [
                    ("col1", "col2"),
                    ("val11a", "val12a"),
                    ("val21a", "val22a"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11b", "val12b", "val13b"),
                    ("val21b", "val22b", "val23b"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
        }
    )
    .set_file_type("csv")
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
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"col1": "val21a", "col2": "val22a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"col1": "val11b", "col2": "val12b", "col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "b.csv"}, "stream": "stream1"},
            {"data": {"col1": "val21b", "col2": "val22b", "col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "b.csv"}, "stream": "stream1"},
        ]
    )
).build()

multi_csv_stream_n_file_exceeds_limit_for_inference = (
    TestScenarioBuilder()
    .set_name("multi_csv_stream_n_file_exceeds_limit_for_inference")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_files(
        {
            "a.csv": {
                "contents": [
                    ("col1", "col2"),
                    ("val11a", "val12a"),
                    ("val21a", "val22a"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11b", "val12b", "val13b"),
                    ("val21b", "val22b", "val23b"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
        }
    )
    .set_file_type("csv")
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
                            }, "col2": {
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
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"col1": "val21a", "col2": "val22a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"col1": "val11b", "col2": "val12b", "col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "b.csv"}, "stream": "stream1"},
            {"data": {"col1": "val21b", "col2": "val22b", "col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "b.csv"}, "stream": "stream1"},
        ]
    )
    .set_expected_logs({
        "discover": [{"level": "WARN", "message": "Refusing to infer schema for all 2 files; using 1 files."}]})
    .set_discovery_policy(LowInferenceLimitDiscoveryPolicy())
).build()

invalid_csv_scenario = (
    TestScenarioBuilder()
    .set_name("invalid_csv_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_files(
        {
            "a.csv": {
                "contents": [
                    ("col1",),
                    ("val11", "val12"),
                    ("val21", "val22"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            }
        }
    )
    .set_file_type("csv")
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
                            }, "col2": {
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
    .set_expected_records([])
    .set_expected_discover_error(SchemaInferenceError, FileBasedSourceError.SCHEMA_INFERENCE_ERROR.value)
    .set_expected_logs({
        "read": [
            {
                "level": "ERROR",
                "message": f"{FileBasedSourceError.ERROR_PARSING_RECORD.value} stream=stream1 file=a.csv line_no=1 n_skipped=0",
            },
        ]
    })
).build()

csv_single_stream_scenario = (
    TestScenarioBuilder()
    .set_name("csv_single_stream_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*.csv"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_files(
        {
            "a.csv": {
                "contents": [
                    ("col1", "col2"),
                    ("val11a", "val12a"),
                    ("val21a", "val22a"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b.jsonl": {
                "contents": [
                    {"col1": "val11b", "col2": "val12b", "col3": "val13b"},
                    {"col1": "val12b", "col2": "val22b", "col3": "val23b"},
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
        }
    )
    .set_file_type("csv")
    .set_expected_catalog(
        {
            "streams": [
                {
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
                        },
                    },
                    "name": "stream1",
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                }
            ]
        }
    )
    .set_expected_records(
        [
            {"data": {"col1": "val11a", "col2": "val12a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"col1": "val21a", "col2": "val22a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
        ]
    )
).build()

csv_multi_stream_scenario = (
    TestScenarioBuilder()
    .set_name("csv_multi_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*.csv"],
                    "validation_policy": "emit_record",
                },
                {
                    "name": "stream2",
                    "file_type": "csv",
                    "globs": ["b.csv"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_files(
        {
            "a.csv": {
                "contents": [
                    ("col1", "col2"),
                    ("val11a", "val12a"),
                    ("val21a", "val22a"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b.csv": {
                "contents": [
                    ("col3",),
                    ("val13b",),
                    ("val23b",),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
        }
    )
    .set_file_type("csv")
    .set_expected_catalog(
        {
            "streams": [
                {
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
                        },
                    },
                    "name": "stream1",
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                },
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col3": {
                                "type": "string"
                            },
                            "_ab_source_file_last_modified": {
                                "type": "string"
                            },
                            "_ab_source_file_url": {
                                "type": "string"
                            },
                        },
                    },
                    "name": "stream2",
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                },
            ]
        }
    )
    .set_expected_records(
        [
            {"data": {"col1": "val11a", "col2": "val12a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"col1": "val21a", "col2": "val22a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "b.csv"},
             "stream": "stream1"},
            {"data": {"col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "b.csv"},
             "stream": "stream1"},
            {"data": {"col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "b.csv"},
             "stream": "stream2"},
            {"data": {"col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "b.csv"},
             "stream": "stream2"},
        ]
    )
).build()


csv_custom_format_scenario = (
    TestScenarioBuilder()
    .set_name("csv_custom_format")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                    "format": {
                        "csv": {
                            "filetype": "csv",
                            "delimiter": "#",
                            "quote_char": "|",
                            "escape_char": "!",
                            "double_quote": True,
                            "quoting_behavior": "Quote Special Characters"
                        }
                    }
                }
            ]
        }
    )
    .set_files(
        {
            "a.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11", "val12", "val |13|"),
                    ("val21", "val22", "val23"),
                    ("val,31", "val |,32|", "val, !!!! 33"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            }
        }
    )
    .set_file_type("csv")
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": "string",
                            },
                            "col2": {
                                "type": "string",
                            },
                            "col3": {
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
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
    .set_expected_records(
        [
            {"data": {"col1": "val11", "col2": "val12", "col3": "val |13|", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"col1": "val21", "col2": "val22", "col3": "val23", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"col1": "val,31", "col2": "val |,32|", "col3": "val, !! 33", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
        ]
    )
    .set_file_write_options(
        {
            "delimiter": "#",
            "quotechar": "|",
        }
    )
).build()


csv_legacy_format_scenario = (
    TestScenarioBuilder()
    .set_name("csv_legacy_format")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                    "format": {
                        "filetype": "csv",
                        "delimiter": "#",
                        "quote_char": "|",
                        "escape_char": "!",
                        "double_quote": True,
                        "quoting_behavior": "Quote All"
                    }
                }
            ]
        }
    )
    .set_files(
        {
            "a.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11", "val12", "val |13|"),
                    ("val21", "val22", "val23"),
                    ("val,31", "val |,32|", "val, !!!! 33"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            }
        }
    )
    .set_file_type("csv")
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": "string",
                            },
                            "col2": {
                                "type": "string",
                            },
                            "col3": {
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
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
    .set_expected_records(
        [
            {"data": {"col1": "val11", "col2": "val12", "col3": "val |13|", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"col1": "val21", "col2": "val22", "col3": "val23", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"col1": "val,31", "col2": "val |,32|", "col3": "val, !! 33", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
        ]
    )
    .set_file_write_options(
        {
            "delimiter": "#",
            "quotechar": "|",
        }
    )
).build()


multi_stream_custom_format = (
    TestScenarioBuilder()
    .set_name("multi_stream_custom_format_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*.csv"],
                    "validation_policy": "emit_record",
                    "format": {
                        "csv": {
                            "filetype": "csv",
                            "delimiter": "#",
                            "escape_char": "!",
                            "double_quote": True,
                            "newlines_in_values": False
                        }
                    }
                },
                {
                    "name": "stream2",
                    "file_type": "csv",
                    "globs": ["b.csv"],
                    "validation_policy": "emit_record",
                    "format": {
                        "csv": {
                            "filetype": "csv",
                            "delimiter": "#",
                            "escape_char": "@",
                            "double_quote": True,
                            "newlines_in_values": False,
                            "quoting_behavior": "Quote All"
                        }
                    }
                }
            ]
        }
    )
    .set_files(
        {
            "a.csv": {
                "contents": [
                    ("col1", "col2"),
                    ("val11a", "val !! 12a"),
                    ("val !! 21a", "val22a"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b.csv": {
                "contents": [
                    ("col3",),
                    ("val @@@@ 13b",),
                    ("val23b",),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
        }
    )
    .set_file_type("csv")
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": "string",
                            },
                            "col2": {
                                "type": "string",
                            },
                            "col3": {
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                },
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col3": {
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
                    "name": "stream2",
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                },
            ]
        }
    )
    .set_expected_records(
        [
            {"data": {"col1": "val11a", "col2": "val ! 12a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"col1": "val ! 21a", "col2": "val22a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"col3": "val @@@@ 13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "b.csv"},
             "stream": "stream1"},
            {"data": {"col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "b.csv"},
             "stream": "stream1"},
            {"data": {"col3": "val @@ 13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "b.csv"},
             "stream": "stream2"},
            {"data": {"col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "b.csv"},
             "stream": "stream2"},
        ]
    )
    .set_file_write_options(
        {
            "delimiter": "#",
        }
    )
).build()


empty_schema_inference_scenario = (
    TestScenarioBuilder()
    .set_name("empty_schema_inference_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_files(
        {
            "a.csv": {
                "contents": [
                    ("col1", "col2"),
                    ("val11", "val12"),
                    ("val21", "val22"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            }
        }
    )
    .set_file_type("csv")
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
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
    .set_parsers({'csv': EmptySchemaParser()})
    .set_expected_discover_error(SchemaInferenceError, FileBasedSourceError.SCHEMA_INFERENCE_ERROR.value)
    .set_expected_records(
        [
            {"data": {"col1": "val11", "col2": "val12", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"col1": "val21", "col2": "val22", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
        ]
    )
).build()


schemaless_csv_scenario = (
    TestScenarioBuilder()
    .set_name("schemaless_csv_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*"],
                    "validation_policy": "skip_record",
                    "schemaless": True,
                }
            ]
        }
    )
    .set_files(
        {
            "a.csv": {
                "contents": [
                    ("col1", "col2"),
                    ("val11a", "val12a"),
                    ("val21a", "val22a"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11b", "val12b", "val13b"),
                    ("val21b", "val22b", "val23b"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
        }
    )
    .set_file_type("csv")
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "object"
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
            {"data": {"data": {"col1": "val11a", "col2": "val12a"}, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"data": {"col1": "val21a", "col2": "val22a"}, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"data": {"col1": "val11b", "col2": "val12b", "col3": "val13b"}, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "b.csv"}, "stream": "stream1"},
            {"data": {"data": {"col1": "val21b", "col2": "val22b", "col3": "val23b"}, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "b.csv"}, "stream": "stream1"},
        ]
    )
).build()


schemaless_csv_multi_stream_scenario = (
    TestScenarioBuilder()
    .set_name("schemaless_csv_multi_stream_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["a.csv"],
                    "validation_policy": "skip_record",
                    "schemaless": True,
                },
                {
                    "name": "stream2",
                    "file_type": "csv",
                    "globs": ["b.csv"],
                    "validation_policy": "skip_record",
                }
            ]
        }
    )
    .set_files(
        {
            "a.csv": {
                "contents": [
                    ("col1", "col2"),
                    ("val11a", "val12a"),
                    ("val21a", "val22a"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b.csv": {
                "contents": [
                    ("col3",),
                    ("val13b",),
                    ("val23b",),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
        }
    )
    .set_file_type("csv")
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "object"
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                },
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col3": {
                                "type": "string"
                            },
                            "_ab_source_file_last_modified": {
                                "type": "string"
                            },
                            "_ab_source_file_url": {
                                "type": "string"
                            },
                        },
                    },
                    "name": "stream2",
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                },
            ]
        }
    )
    .set_expected_records(
        [
            {"data": {"data": {"col1": "val11a", "col2": "val12a"}, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"data": {"col1": "val21a", "col2": "val22a"}, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.csv"}, "stream": "stream1"},
            {"data": {"col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "b.csv"},
             "stream": "stream2"},
            {"data": {"col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "b.csv"},
             "stream": "stream2"},
        ]
    )
).build()


schemaless_with_user_input_schema_fails_connection_check_scenario = (
    TestScenarioBuilder()
    .set_name("schemaless_with_user_input_schema_fails_connection_check_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*"],
                    "validation_policy": "skip_record",
                    "input_schema": {"col1": "string", "col2": "string", "col3": "string"},
                    "schemaless": True,
                }
            ]
        }
    )
    .set_files(
        {
            "a.csv": {
                "contents": [
                    ("col1", "col2"),
                    ("val11a", "val12a"),
                    ("val21a", "val22a"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11b", "val12b", "val13b"),
                    ("val21b", "val22b", "val23b"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
        }
    )
    .set_file_type("csv")
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "object"
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
    .set_expected_check_status("FAILED")
    .set_expected_check_error(ConfigValidationError, FileBasedSourceError.CONFIG_VALIDATION_ERROR.value)
    .set_expected_discover_error(ConfigValidationError, FileBasedSourceError.CONFIG_VALIDATION_ERROR.value)
    .set_expected_read_error(ConfigValidationError, FileBasedSourceError.CONFIG_VALIDATION_ERROR.value)
).build()


schemaless_with_user_input_schema_fails_connection_check_multi_stream_scenario = (
    TestScenarioBuilder()
    .set_name("schemaless_with_user_input_schema_fails_connection_check_multi_stream_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["a.csv"],
                    "validation_policy": "skip_record",
                    "schemaless": True,
                    "input_schema": {"col1": "string", "col2": "string", "col3": "string"},
                },
                {
                    "name": "stream2",
                    "file_type": "csv",
                    "globs": ["b.csv"],
                    "validation_policy": "skip_record",
                }
            ]
        }
    )
    .set_files(
        {
            "a.csv": {
                "contents": [
                    ("col1", "col2"),
                    ("val11a", "val12a"),
                    ("val21a", "val22a"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b.csv": {
                "contents": [
                    ("col3",),
                    ("val13b",),
                    ("val23b",),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
        }
    )
    .set_file_type("csv")
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "object"
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                },
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col3": {
                                "type": "string"
                            },
                            "_ab_source_file_last_modified": {
                                "type": "string"
                            },
                            "_ab_source_file_url": {
                                "type": "string"
                            },
                        },
                    },
                    "name": "stream2",
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                },
            ]
        }
    )
    .set_expected_check_status("FAILED")
    .set_expected_check_error(ConfigValidationError, FileBasedSourceError.CONFIG_VALIDATION_ERROR.value)
    .set_expected_discover_error(ConfigValidationError, FileBasedSourceError.CONFIG_VALIDATION_ERROR.value)
    .set_expected_read_error(ConfigValidationError, FileBasedSourceError.CONFIG_VALIDATION_ERROR.value)
).build()
