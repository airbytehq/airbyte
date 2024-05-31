#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import AirbyteAnalyticsTraceMessage
from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat
from airbyte_cdk.sources.file_based.exceptions import ConfigValidationError, FileBasedSourceError
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from airbyte_protocol.models import SyncMode
from unit_tests.sources.file_based.helpers import EmptySchemaParser, LowInferenceLimitDiscoveryPolicy
from unit_tests.sources.file_based.in_memory_files_source import InMemoryFilesSource
from unit_tests.sources.file_based.scenarios.file_based_source_builder import FileBasedSourceBuilder
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenario, TestScenarioBuilder

single_csv_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("single_csv_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                }
            ],
            "start_date": "2023-06-04T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
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
    )
    .set_expected_spec(
        {
            "documentationUrl": "https://docs.airbyte.com/integrations/sources/in_memory_files",
            "connectionSpecification": {
                "title": "InMemorySpec",
                "description": "Used during spec; allows the developer to configure the cloud provider specific options\nthat are needed when users configure a file-based source.",
                "type": "object",
                "properties": {
                    "start_date": {
                        "title": "Start Date",
                        "description": "UTC date and time in the format 2017-01-25T00:00:00.000000Z. Any file modified before this date will not be replicated.",
                        "examples": ["2021-01-01T00:00:00.000000Z"],
                        "format": "date-time",
                        "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6}Z$",
                        "pattern_descriptor": "YYYY-MM-DDTHH:mm:ss.SSSSSSZ",
                        "order": 1,
                        "type": "string",
                    },
                    "streams": {
                        "title": "The list of streams to sync",
                        "description": 'Each instance of this configuration defines a <a href="https://docs.airbyte.com/cloud/core-concepts#stream">stream</a>. Use this to define which files belong in the stream, their format, and how they should be parsed and validated. When sending data to warehouse destination such as Snowflake or BigQuery, each stream is a separate table.',
                        "order": 10,
                        "type": "array",
                        "items": {
                            "title": "FileBasedStreamConfig",
                            "type": "object",
                            "properties": {
                                "name": {"title": "Name", "description": "The name of the stream.", "type": "string"},
                                "globs": {
                                    "title": "Globs",
                                    "description": 'The pattern used to specify which files should be selected from the file system. For more information on glob pattern matching look <a href="https://en.wikipedia.org/wiki/Glob_(programming)">here</a>.',
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "order": 1,
                                    "default": ["**"],
                                },
                                "legacy_prefix": {
                                    "title": "Legacy Prefix",
                                    "airbyte_hidden": True,
                                    "type": "string",
                                    "description": "The path prefix configured in v3 versions of the S3 connector. This option is deprecated in favor of a single glob.",
                                },
                                "validation_policy": {
                                    "title": "Validation Policy",
                                    "description": "The name of the validation policy that dictates sync behavior when a record does not adhere to the stream schema.",
                                    "default": "Emit Record",
                                    "enum": ["Emit Record", "Skip Record", "Wait for Discover"],
                                },
                                "input_schema": {
                                    "title": "Input Schema",
                                    "description": "The schema that will be used to validate records extracted from the file. This will override the stream schema that is auto-detected from incoming files.",
                                    "type": "string",
                                },
                                "primary_key": {
                                    "title": "Primary Key",
                                    "description": "The column or columns (for a composite key) that serves as the unique identifier of a record. If empty, the primary key will default to the parser's default primary key.",
                                    "type": "string",
                                    "airbyte_hidden": True,
                                },
                                "days_to_sync_if_history_is_full": {
                                    "title": "Days To Sync If History Is Full",
                                    "description": "When the state history of the file store is full, syncs will only read files that were last modified in the provided day range.",
                                    "default": 3,
                                    "type": "integer",
                                },
                                "format": {
                                    "title": "Format",
                                    "description": "The configuration options that are used to alter how to read incoming files that deviate from the standard formatting.",
                                    "type": "object",
                                    "oneOf": [
                                        {
                                            "title": "Avro Format",
                                            "type": "object",
                                            "properties": {
                                                "filetype": {"title": "Filetype", "default": "avro", "const": "avro", "type": "string"},
                                                "double_as_string": {
                                                    "title": "Convert Double Fields to Strings",
                                                    "description": "Whether to convert double fields to strings. This is recommended if you have decimal numbers with a high degree of precision because there can be a loss precision when handling floating point numbers.",
                                                    "default": False,
                                                    "type": "boolean",
                                                },
                                            },
                                            "required": ["filetype"],
                                        },
                                        {
                                            "title": "CSV Format",
                                            "type": "object",
                                            "properties": {
                                                "filetype": {"title": "Filetype", "default": "csv", "const": "csv", "type": "string"},
                                                "delimiter": {
                                                    "title": "Delimiter",
                                                    "description": "The character delimiting individual cells in the CSV data. This may only be a 1-character string. For tab-delimited data enter '\\t'.",
                                                    "default": ",",
                                                    "type": "string",
                                                },
                                                "quote_char": {
                                                    "title": "Quote Character",
                                                    "description": "The character used for quoting CSV values. To disallow quoting, make this field blank.",
                                                    "default": '"',
                                                    "type": "string",
                                                },
                                                "escape_char": {
                                                    "title": "Escape Character",
                                                    "description": "The character used for escaping special characters. To disallow escaping, leave this field blank.",
                                                    "type": "string",
                                                },
                                                "encoding": {
                                                    "title": "Encoding",
                                                    "description": 'The character encoding of the CSV data. Leave blank to default to <strong>UTF8</strong>. See <a href="https://docs.python.org/3/library/codecs.html#standard-encodings" target="_blank">list of python encodings</a> for allowable options.',
                                                    "default": "utf8",
                                                    "type": "string",
                                                },
                                                "double_quote": {
                                                    "title": "Double Quote",
                                                    "description": "Whether two quotes in a quoted CSV value denote a single quote in the data.",
                                                    "default": True,
                                                    "type": "boolean",
                                                },
                                                "null_values": {
                                                    "title": "Null Values",
                                                    "description": "A set of case-sensitive strings that should be interpreted as null values. For example, if the value 'NA' should be interpreted as null, enter 'NA' in this field.",
                                                    "default": [],
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                    "uniqueItems": True,
                                                },
                                                "strings_can_be_null": {
                                                    "title": "Strings Can Be Null",
                                                    "description": "Whether strings can be interpreted as null values. If true, strings that match the null_values set will be interpreted as null. If false, strings that match the null_values set will be interpreted as the string itself.",
                                                    "default": True,
                                                    "type": "boolean",
                                                },
                                                "skip_rows_before_header": {
                                                    "title": "Skip Rows Before Header",
                                                    "description": "The number of rows to skip before the header row. For example, if the header row is on the 3rd row, enter 2 in this field.",
                                                    "default": 0,
                                                    "type": "integer",
                                                },
                                                "skip_rows_after_header": {
                                                    "title": "Skip Rows After Header",
                                                    "description": "The number of rows to skip after the header row.",
                                                    "default": 0,
                                                    "type": "integer",
                                                },
                                                "header_definition": {
                                                    "title": "CSV Header Definition",
                                                    "type": "object",
                                                    "description": "How headers will be defined. `User Provided` assumes the CSV does not have a header row and uses the headers provided and `Autogenerated` assumes the CSV does not have a header row and the CDK will generate headers using for `f{i}` where `i` is the index starting from 0. Else, the default behavior is to use the header from the CSV file. If a user wants to autogenerate or provide column names for a CSV having headers, they can skip rows.",
                                                    "default": {"header_definition_type": "From CSV"},
                                                    "oneOf": [
                                                        {
                                                            "title": "From CSV",
                                                            "type": "object",
                                                            "properties": {
                                                                "header_definition_type": {
                                                                    "title": "Header Definition Type",
                                                                    "default": "From CSV",
                                                                    "const": "From CSV",
                                                                    "type": "string",
                                                                },
                                                            },
                                                            "required": ["header_definition_type"],
                                                        },
                                                        {
                                                            "title": "Autogenerated",
                                                            "type": "object",
                                                            "properties": {
                                                                "header_definition_type": {
                                                                    "title": "Header Definition Type",
                                                                    "default": "Autogenerated",
                                                                    "const": "Autogenerated",
                                                                    "type": "string",
                                                                },
                                                            },
                                                            "required": ["header_definition_type"],
                                                        },
                                                        {
                                                            "title": "User Provided",
                                                            "type": "object",
                                                            "properties": {
                                                                "header_definition_type": {
                                                                    "title": "Header Definition Type",
                                                                    "default": "User Provided",
                                                                    "const": "User Provided",
                                                                    "type": "string",
                                                                },
                                                                "column_names": {
                                                                    "title": "Column Names",
                                                                    "description": "The column names that will be used while emitting the CSV records",
                                                                    "type": "array",
                                                                    "items": {"type": "string"},
                                                                },
                                                            },
                                                            "required": ["column_names", "header_definition_type"],
                                                        },
                                                    ],
                                                },
                                                "true_values": {
                                                    "title": "True Values",
                                                    "description": "A set of case-sensitive strings that should be interpreted as true values.",
                                                    "default": ["y", "yes", "t", "true", "on", "1"],
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                    "uniqueItems": True,
                                                },
                                                "false_values": {
                                                    "title": "False Values",
                                                    "description": "A set of case-sensitive strings that should be interpreted as false values.",
                                                    "default": ["n", "no", "f", "false", "off", "0"],
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                    "uniqueItems": True,
                                                },
                                                "inference_type": {
                                                    "title": "Inference Type",
                                                    "description": "How to infer the types of the columns. If none, inference default to strings.",
                                                    "default": "None",
                                                    "airbyte_hidden": True,
                                                    "enum": ["None", "Primitive Types Only"],
                                                },
                                                "ignore_errors_on_fields_mismatch": {
                                                    "type": "boolean",
                                                    "title": "Ignore errors on field mismatch",
                                                    "default": False,
                                                    "description": "Whether to ignore errors that occur when the number of fields in the CSV does not match the number of columns in the schema.",
                                                },
                                            },
                                            "required": ["filetype"],
                                        },
                                        {
                                            "title": "Jsonl Format",
                                            "type": "object",
                                            "properties": {
                                                "filetype": {"title": "Filetype", "default": "jsonl", "const": "jsonl", "type": "string"}
                                            },
                                            "required": ["filetype"],
                                        },
                                        {
                                            "title": "Parquet Format",
                                            "type": "object",
                                            "properties": {
                                                "filetype": {
                                                    "title": "Filetype",
                                                    "default": "parquet",
                                                    "const": "parquet",
                                                    "type": "string",
                                                },
                                                "decimal_as_float": {
                                                    "title": "Convert Decimal Fields to Floats",
                                                    "description": "Whether to convert decimal fields to floats. There is a loss of precision when converting decimals to floats, so this is not recommended.",
                                                    "default": False,
                                                    "type": "boolean",
                                                },
                                            },
                                            "required": ["filetype"],
                                        },
                                        {
                                            "title": "Unstructured Document Format",
                                            "type": "object",
                                            "properties": {
                                                "filetype": {
                                                    "title": "Filetype",
                                                    "default": "unstructured",
                                                    "const": "unstructured",
                                                    "type": "string",
                                                },
                                                "skip_unprocessable_files": {
                                                    "type": "boolean",
                                                    "default": True,
                                                    "title": "Skip Unprocessable Files",
                                                    "description": "If true, skip files that cannot be parsed and pass the error message along as the _ab_source_file_parse_error field. If false, fail the sync.",
                                                    "always_show": True,
                                                },
                                                "strategy": {
                                                    "type": "string",
                                                    "always_show": True,
                                                    "order": 0,
                                                    "default": "auto",
                                                    "title": "Parsing Strategy",
                                                    "enum": ["auto", "fast", "ocr_only", "hi_res"],
                                                    "description": "The strategy used to parse documents. `fast` extracts text directly from the document which doesn't work for all files. `ocr_only` is more reliable, but slower. `hi_res` is the most reliable, but requires an API key and a hosted instance of unstructured and can't be used with local mode. See the unstructured.io documentation for more details: https://unstructured-io.github.io/unstructured/core/partition.html#partition-pdf",
                                                },
                                                "processing": {
                                                    "title": "Processing",
                                                    "description": "Processing configuration",
                                                    "default": {"mode": "local"},
                                                    "type": "object",
                                                    "oneOf": [
                                                        {
                                                            "title": "Local",
                                                            "type": "object",
                                                            "properties": {
                                                                "mode": {
                                                                    "title": "Mode",
                                                                    "default": "local",
                                                                    "const": "local",
                                                                    "enum": ["local"],
                                                                    "type": "string",
                                                                }
                                                            },
                                                            "description": "Process files locally, supporting `fast` and `ocr` modes. This is the default option.",
                                                            "required": ["mode"],
                                                        },
                                                        {
                                                            "title": "via API",
                                                            "type": "object",
                                                            "properties": {
                                                                "mode": {
                                                                    "title": "Mode",
                                                                    "default": "api",
                                                                    "const": "api",
                                                                    "enum": ["api"],
                                                                    "type": "string",
                                                                },
                                                                "api_key": {
                                                                    "title": "API Key",
                                                                    "description": "The API key to use matching the environment",
                                                                    "default": "",
                                                                    "always_show": True,
                                                                    "airbyte_secret": True,
                                                                    "type": "string",
                                                                },
                                                                "api_url": {
                                                                    "title": "API URL",
                                                                    "description": "The URL of the unstructured API to use",
                                                                    "default": "https://api.unstructured.io",
                                                                    "always_show": True,
                                                                    "examples": ["https://api.unstructured.com"],
                                                                    "type": "string",
                                                                },
                                                                "parameters": {
                                                                    "title": "Additional URL Parameters",
                                                                    "description": "List of parameters send to the API",
                                                                    "default": [],
                                                                    "always_show": True,
                                                                    "type": "array",
                                                                    "items": {
                                                                        "title": "APIParameterConfigModel",
                                                                        "type": "object",
                                                                        "properties": {
                                                                            "name": {
                                                                                "title": "Parameter name",
                                                                                "description": "The name of the unstructured API parameter to use",
                                                                                "examples": ["combine_under_n_chars", "languages"],
                                                                                "type": "string",
                                                                            },
                                                                            "value": {
                                                                                "title": "Value",
                                                                                "description": "The value of the parameter",
                                                                                "examples": ["true", "hi_res"],
                                                                                "type": "string",
                                                                            },
                                                                        },
                                                                        "required": ["name", "value"],
                                                                    },
                                                                },
                                                            },
                                                            "description": "Process files via an API, using the `hi_res` mode. This option is useful for increased performance and accuracy, but requires an API key and a hosted instance of unstructured.",
                                                            "required": ["mode"],
                                                        },
                                                    ],
                                                },
                                            },
                                            "description": "Extract text from document formats (.pdf, .docx, .md, .pptx) and emit as one record per file.",
                                            "required": ["filetype"],
                                        },
                                    ],
                                },
                                "schemaless": {
                                    "title": "Schemaless",
                                    "description": "When enabled, syncs will not validate or structure records against the stream's schema.",
                                    "default": False,
                                    "type": "boolean",
                                },
                            },
                            "required": ["name", "format"],
                        },
                    },
                },
                "required": ["streams"],
            },
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
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val11",
                    "col2": "val12",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21",
                    "col2": "val22",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

csv_analytics_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_analytics")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["a.csv"],
                    "validation_policy": "Emit Record",
                },
                {
                    "name": "stream2",
                    "format": {"filetype": "csv"},
                    "globs": ["b.csv"],
                    "validation_policy": "Emit Record",
                }
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
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
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                },
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "col3": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream2",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records([
        {
            "data": {
                "col1": "val11a",
                "col2": "val12a",
                "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                "_ab_source_file_url": "a.csv",
            },
            "stream": "stream1",
        },
        {
            "data": {
                "col1": "val21a",
                "col2": "val22a",
                "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                "_ab_source_file_url": "a.csv",
            },
            "stream": "stream1",
        },
        {
            "data": {
                "col1": "val11b",
                "col2": "val12b",
                "col3": "val13b",
                "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                "_ab_source_file_url": "b.csv",
            },
            "stream": "stream2",
        },
        {
            "data": {
                "col1": "val21b",
                "col2": "val22b",
                "col3": "val23b",
                "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                "_ab_source_file_url": "b.csv",
            },
            "stream": "stream2",
        },
    ])
    .set_expected_analytics(
        [
            AirbyteAnalyticsTraceMessage(type="file-cdk-csv-stream-count", value="2"),
        ]
    )
).build()

multi_csv_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("multi_csv_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                }
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
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
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "col3": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val11a",
                    "col2": "val12a",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21a",
                    "col2": "val22a",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val11b",
                    "col2": "val12b",
                    "col3": "val13b",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21b",
                    "col2": "val22b",
                    "col3": "val23b",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

multi_csv_stream_n_file_exceeds_limit_for_inference = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("multi_csv_stream_n_file_exceeds_limit_for_inference")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                }
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
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
        .set_discovery_policy(LowInferenceLimitDiscoveryPolicy())
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val11a",
                    "col2": "val12a",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21a",
                    "col2": "val22a",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val11b",
                    "col2": "val12b",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21b",
                    "col2": "val22b",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

invalid_csv_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("invalid_csv_scenario")  # too many values for the number of headers
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                }
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
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
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records([])
    .set_expected_discover_error(AirbyteTracedException, FileBasedSourceError.SCHEMA_INFERENCE_ERROR.value)
    .set_expected_logs(
        {
            "read": [
                {
                    "level": "ERROR",
                    "message": f"{FileBasedSourceError.INVALID_SCHEMA_ERROR.value} stream=stream1 file=a.csv line_no=1 n_skipped=0",
                },
            ]
        }
    )
    .set_expected_read_error(
        AirbyteTracedException,
        "Please check the logged errors for more information.",
    )
).build()

invalid_csv_multi_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("invalid_csv_multi_scenario")  # too many values for the number of headers
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                },
                {
                    "name": "stream2",
                    "format": {"filetype": "csv"},
                    "globs": ["b.csv"],
                    "validation_policy": "Emit Record",
                },
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        ("col1",),
                        ("val11", "val12"),
                        ("val21", "val22"),
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                },
                "b.csv": {
                    "contents": [
                        ("col3",),
                        ("val13b", "val14b"),
                        ("val23b", "val24b"),
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                },
            }
        )
        .set_file_type("csv")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                },
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col3": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream2",
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                },
            ]
        }
    )
    .set_expected_records([])
    .set_expected_discover_error(AirbyteTracedException, FileBasedSourceError.SCHEMA_INFERENCE_ERROR.value)
    .set_expected_logs(
        {
            "read": [
                {
                    "level": "ERROR",
                    "message": f"{FileBasedSourceError.ERROR_PARSING_RECORD.value} stream=stream1 file=a.csv line_no=1 n_skipped=0",
                },
                {
                    "level": "ERROR",
                    "message": f"{FileBasedSourceError.ERROR_PARSING_RECORD.value} stream=stream2 file=b.csv line_no=1 n_skipped=0",
                },
            ]
        }
    )
    .set_expected_read_error(AirbyteTracedException, "Please check the logged errors for more information.")
).build()

csv_single_stream_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_single_stream_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*.csv"],
                    "validation_policy": "Emit Record",
                }
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
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
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val11a",
                    "col2": "val12a",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21a",
                    "col2": "val22a",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

csv_multi_stream_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_multi_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*.csv"],
                    "validation_policy": "Emit Record",
                },
                {
                    "name": "stream2",
                    "format": {"filetype": "csv"},
                    "globs": ["b.csv"],
                    "validation_policy": "Emit Record",
                },
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
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
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "col3": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                },
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col3": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream2",
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                },
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val11a",
                    "col2": "val12a",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21a",
                    "col2": "val22a",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {"col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "b.csv"},
                "stream": "stream1",
            },
            {
                "data": {"col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "b.csv"},
                "stream": "stream1",
            },
            {
                "data": {"col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "b.csv"},
                "stream": "stream2",
            },
            {
                "data": {"col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "b.csv"},
                "stream": "stream2",
            },
        ]
    )
).build()

csv_custom_format_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_custom_format")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "format": {
                        "filetype": "csv",
                        "delimiter": "#",
                        "quote_char": "|",
                        "escape_char": "!",
                        "double_quote": True,
                    },
                }
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
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
        .set_file_write_options(
            {
                "delimiter": "#",
                "quotechar": "|",
            }
        )
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": ["null", "string"],
                            },
                            "col2": {
                                "type": ["null", "string"],
                            },
                            "col3": {
                                "type": ["null", "string"],
                            },
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val11",
                    "col2": "val12",
                    "col3": "val |13|",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21",
                    "col2": "val22",
                    "col3": "val23",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val,31",
                    "col2": "val |,32|",
                    "col3": "val, !! 33",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

multi_stream_custom_format = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("multi_stream_custom_format_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*.csv"],
                    "validation_policy": "Emit Record",
                    "format": {"filetype": "csv", "delimiter": "#", "escape_char": "!", "double_quote": True, "newlines_in_values": False},
                },
                {
                    "name": "stream2",
                    "globs": ["b.csv"],
                    "validation_policy": "Emit Record",
                    "format": {
                        "filetype": "csv",
                        "delimiter": "#",
                        "escape_char": "@",
                        "double_quote": True,
                        "newlines_in_values": False,
                    },
                },
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
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
        .set_file_write_options(
            {
                "delimiter": "#",
            }
        )
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": ["null", "string"],
                            },
                            "col2": {
                                "type": ["null", "string"],
                            },
                            "col3": {
                                "type": ["null", "string"],
                            },
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                },
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col3": {
                                "type": ["null", "string"],
                            },
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream2",
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                },
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val11a",
                    "col2": "val ! 12a",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val ! 21a",
                    "col2": "val22a",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col3": "val @@@@ 13b",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {"col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "b.csv"},
                "stream": "stream1",
            },
            {
                "data": {
                    "col3": "val @@ 13b",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream2",
            },
            {
                "data": {"col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "b.csv"},
                "stream": "stream2",
            },
        ]
    )
).build()

empty_schema_inference_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("empty_schema_inference_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                }
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
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
        .set_parsers({CsvFormat: EmptySchemaParser()})
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_discover_error(AirbyteTracedException, FileBasedSourceError.SCHEMA_INFERENCE_ERROR.value)
).build()

schemaless_csv_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("schemaless_csv_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*"],
                    "validation_policy": "Skip Record",
                    "schemaless": True,
                }
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
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
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "object"},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "data": {"col1": "val11a", "col2": "val12a"},
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "data": {"col1": "val21a", "col2": "val22a"},
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "data": {"col1": "val11b", "col2": "val12b", "col3": "val13b"},
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "data": {"col1": "val21b", "col2": "val22b", "col3": "val23b"},
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

schemaless_csv_multi_stream_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("schemaless_csv_multi_stream_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["a.csv"],
                    "validation_policy": "Skip Record",
                    "schemaless": True,
                },
                {
                    "name": "stream2",
                    "format": {"filetype": "csv"},
                    "globs": ["b.csv"],
                    "validation_policy": "Skip Record",
                },
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
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
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "object"},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                },
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col3": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream2",
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                },
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "data": {"col1": "val11a", "col2": "val12a"},
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "data": {"col1": "val21a", "col2": "val22a"},
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {"col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "b.csv"},
                "stream": "stream2",
            },
            {
                "data": {"col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "b.csv"},
                "stream": "stream2",
            },
        ]
    )
).build()

schemaless_with_user_input_schema_fails_connection_check_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("schemaless_with_user_input_schema_fails_connection_check_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*"],
                    "validation_policy": "Skip Record",
                    "input_schema": '{"col1": "string", "col2": "string", "col3": "string"}',
                    "schemaless": True,
                }
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
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
    )
    .set_catalog(CatalogBuilder().with_stream("stream1", SyncMode.full_refresh).build())
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "object"},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_check_status("FAILED")
    .set_expected_check_error(AirbyteTracedException, FileBasedSourceError.CONFIG_VALIDATION_ERROR.value)
    .set_expected_discover_error(ConfigValidationError, FileBasedSourceError.CONFIG_VALIDATION_ERROR.value)
    .set_expected_read_error(ConfigValidationError, FileBasedSourceError.CONFIG_VALIDATION_ERROR.value)
).build()

schemaless_with_user_input_schema_fails_connection_check_multi_stream_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("schemaless_with_user_input_schema_fails_connection_check_multi_stream_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["a.csv"],
                    "validation_policy": "Skip Record",
                    "schemaless": True,
                    "input_schema": '{"col1": "string", "col2": "string", "col3": "string"}',
                },
                {
                    "name": "stream2",
                    "format": {"filetype": "csv"},
                    "globs": ["b.csv"],
                    "validation_policy": "Skip Record",
                },
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
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
    )
    .set_catalog(CatalogBuilder().with_stream("stream1", SyncMode.full_refresh).with_stream("stream2", SyncMode.full_refresh).build())
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "object"},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                },
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col3": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream2",
                    "source_defined_cursor": True,
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                },
            ]
        }
    )
    .set_expected_check_status("FAILED")
    .set_expected_check_error(AirbyteTracedException, FileBasedSourceError.CONFIG_VALIDATION_ERROR.value)
    .set_expected_discover_error(ConfigValidationError, FileBasedSourceError.CONFIG_VALIDATION_ERROR.value)
    .set_expected_read_error(ConfigValidationError, FileBasedSourceError.CONFIG_VALIDATION_ERROR.value)
).build()

csv_string_can_be_null_with_input_schemas_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_string_can_be_null_with_input_schema")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "input_schema": '{"col1": "string", "col2": "string"}',
                    "format": {
                        "filetype": "csv",
                        "null_values": ["null"],
                    },
                }
            ],
            "start_date": "2023-06-04T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        ("col1", "col2"),
                        ("2", "null"),
                    ],
                    "last_modified": "2023-06-05T03:54:07.000000Z",
                }
            }
        )
        .set_file_type("csv")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": "string"},
                            "col2": {"type": "string"},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "2",
                    "col2": None,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

csv_string_are_not_null_if_strings_can_be_null_is_false_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_string_are_not_null_if_strings_can_be_null_is_false")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "input_schema": '{"col1": "string", "col2": "string"}',
                    "format": {
                        "filetype": "csv",
                        "null_values": ["null"],
                        "strings_can_be_null": False,
                    },
                }
            ],
            "start_date": "2023-06-04T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        ("col1", "col2"),
                        ("2", "null"),
                    ],
                    "last_modified": "2023-06-05T03:54:07.000000Z",
                }
            }
        )
        .set_file_type("csv")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": "string"},
                            "col2": {"type": "string"},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "2",
                    "col2": "null",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

csv_string_not_null_if_no_null_values_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_string_not_null_if_no_null_values")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "format": {
                        "filetype": "csv",
                    },
                }
            ],
            "start_date": "2023-06-04T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        ("col1", "col2"),
                        ("2", "null"),
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                }
            }
        )
        .set_file_type("csv")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "2",
                    "col2": "null",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

csv_strings_can_be_null_not_quoted_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_strings_can_be_null_no_input_schema")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "format": {"filetype": "csv", "null_values": ["null"]},
                }
            ],
            "start_date": "2023-06-04T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        ("col1", "col2"),
                        ("2", "null"),
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                }
            }
        )
        .set_file_type("csv")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "2",
                    "col2": None,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

csv_newline_in_values_quoted_value_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_newline_in_values_quoted_value")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "format": {
                        "filetype": "csv",
                    },
                }
            ],
            "start_date": "2023-06-04T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        '''"col1","col2"''',
                        '''"2","val\n2"''',
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                }
            }
        )
        .set_file_type("csv")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "2",
                    "col2": "val\n2",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

csv_newline_in_values_not_quoted_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_newline_in_values_not_quoted")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "format": {
                        "filetype": "csv",
                    },
                }
            ],
            "start_date": "2023-06-04T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        """col1,col2""",
                        """2,val\n2""",
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                }
            }
        )
        .set_file_type("csv")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            # Note that the value for col2 is truncated to "val" because the newline is not escaped
            {
                "data": {
                    "col1": "2",
                    "col2": "val",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
    .set_expected_read_error(
        AirbyteTracedException,
        f"{FileBasedSourceError.ERROR_PARSING_RECORD.value} stream=stream1 file=a.csv line_no=2 n_skipped=0",
    )
    .set_expected_discover_error(AirbyteTracedException, FileBasedSourceError.SCHEMA_INFERENCE_ERROR.value)
    .set_expected_read_error(
        AirbyteTracedException,
        "Please check the logged errors for more information.",
    )
).build()

csv_escape_char_is_set_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_escape_char_is_set")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "format": {
                        "filetype": "csv",
                        "double_quotes": False,
                        "quote_char": '"',
                        "delimiter": ",",
                        "escape_char": "\\",
                    },
                }
            ],
            "start_date": "2023-06-04T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        """col1,col2""",
                        '''val11,"val\\"2"''',
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                }
            }
        )
        .set_file_type("csv")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val11",
                    "col2": 'val"2',
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

csv_double_quote_is_set_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_doublequote_is_set")
    # This scenario tests that quotes are properly escaped when double_quotes is True
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "format": {
                        "filetype": "csv",
                        "double_quotes": True,
                        "quote_char": '"',
                        "delimiter": ",",
                    },
                }
            ],
            "start_date": "2023-06-04T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        """col1,col2""",
                        '''val11,"val""2"''',
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                }
            }
        )
        .set_file_type("csv")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val11",
                    "col2": 'val"2',
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

csv_custom_delimiter_with_escape_char_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_custom_delimiter_with_escape_char")
    # This scenario tests that a value can contain the delimiter if it is wrapped in the quote_char
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "format": {"filetype": "csv", "double_quotes": True, "quote_char": "@", "delimiter": "|", "escape_char": "+"},
                }
            ],
            "start_date": "2023-06-04T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        """col1|col2""",
                        """val"1,1|val+|2""",
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                }
            }
        )
        .set_file_type("csv")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": 'val"1,1',
                    "col2": "val|2",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

csv_custom_delimiter_in_double_quotes_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_custom_delimiter_in_double_quotes")
    # This scenario tests that a value can contain the delimiter if it is wrapped in the quote_char
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "format": {
                        "filetype": "csv",
                        "double_quotes": True,
                        "quote_char": "@",
                        "delimiter": "|",
                    },
                }
            ],
            "start_date": "2023-06-04T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        """col1|col2""",
                        """val"1,1|@val|2@""",
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                }
            }
        )
        .set_file_type("csv")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": 'val"1,1',
                    "col2": "val|2",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

csv_skip_before_header_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_skip_before_header")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "format": {"filetype": "csv", "skip_rows_before_header": 2},
                }
            ],
            "start_date": "2023-06-04T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        ("skip_this", "skip_this"),
                        ("skip_this_too", "skip_this_too"),
                        ("col1", "col2"),
                        ("val11", "val12"),
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                }
            }
        )
        .set_file_type("csv")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val11",
                    "col2": "val12",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

csv_skip_after_header_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_skip_after_header")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "format": {"filetype": "csv", "skip_rows_after_header": 2},
                }
            ],
            "start_date": "2023-06-04T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        ("col1", "col2"),
                        ("skip_this", "skip_this"),
                        ("skip_this_too", "skip_this_too"),
                        ("val11", "val12"),
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                }
            }
        )
        .set_file_type("csv")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val11",
                    "col2": "val12",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

csv_skip_before_and_after_header_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_skip_before_after_header")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "format": {
                        "filetype": "csv",
                        "skip_rows_before_header": 1,
                        "skip_rows_after_header": 1,
                    },
                }
            ],
            "start_date": "2023-06-04T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        ("skip_this", "skip_this"),
                        ("col1", "col2"),
                        ("skip_this_too", "skip_this_too"),
                        ("val11", "val12"),
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                }
            }
        )
        .set_file_type("csv")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val11",
                    "col2": "val12",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

csv_autogenerate_column_names_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_autogenerate_column_names")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "format": {
                        "filetype": "csv",
                        "header_definition": {"header_definition_type": "Autogenerated"},
                    },
                }
            ],
            "start_date": "2023-06-04T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        ("val11", "val12"),
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                }
            }
        )
        .set_file_type("csv")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "f0": {"type": ["null", "string"]},
                            "f1": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "f0": "val11",
                    "f1": "val12",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

csv_custom_bool_values_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_custom_bool_values")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "input_schema": '{"col1": "boolean", "col2": "boolean"}',
                    "format": {
                        "filetype": "csv",
                        "true_values": ["this_is_true"],
                        "false_values": ["this_is_false"],
                    },
                }
            ],
            "start_date": "2023-06-04T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        ("col1", "col2"),
                        ("this_is_true", "this_is_false"),
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                }
            }
        )
        .set_file_type("csv")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": "boolean"},
                            "col2": {"type": "boolean"},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": True,
                    "col2": False,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

csv_custom_null_values_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_custom_null_values")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "input_schema": '{"col1": "boolean", "col2": "string"}',
                    "format": {
                        "filetype": "csv",
                        "null_values": ["null"],
                    },
                }
            ],
            "start_date": "2023-06-04T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        ("col1", "col2"),
                        ("null", "na"),
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                }
            }
        )
        .set_file_type("csv")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": "boolean"},
                            "col2": {"type": "string"},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": None,
                    "col2": "na",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
        ]
    )
).build()

earlier_csv_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("earlier_csv_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                }
            ],
            "start_date": "2023-06-10T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        ("col1", "col2"),
                        ("val11", "val12"),
                        ("val21", "val22"),
                    ],
                    "last_modified": "2023-06-05T03:54:07.000000Z",
                }
            }
        )
        .set_file_type("csv")
    )
    .set_expected_check_status("FAILED")
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                            "data": {"type": "object"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(None)
).build()

csv_no_records_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("csv_empty_no_records")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "input_schema": '{"col1": "boolean", "col2": "string"}',
                    "format": {
                        "filetype": "csv",
                        "null_values": ["null"],
                    },
                }
            ],
            "start_date": "2023-06-04T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [("col1", "col2")],  # column headers, but no data rows
                    "last_modified": "2023-06-05T03:54:07.000Z",
                }
            }
        )
        .set_file_type("csv")
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": "boolean"},
                            "col2": {"type": "string"},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records([])
).build()

csv_no_files_scenario: TestScenario[InMemoryFilesSource] = (
    TestScenarioBuilder[InMemoryFilesSource]()
    .set_name("no_files_csv_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                }
            ],
            "start_date": "2023-06-10T03:54:07.000000Z",
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files({})
        .set_file_type("csv")
    )
    .set_expected_check_status("FAILED")
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                            "data": {"type": "object"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
    .set_expected_records(None)
).build()
