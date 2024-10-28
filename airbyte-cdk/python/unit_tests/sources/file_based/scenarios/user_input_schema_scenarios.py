#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.file_based.exceptions import ConfigValidationError, FileBasedSourceError
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from unit_tests.sources.file_based.scenarios.file_based_source_builder import FileBasedSourceBuilder
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenarioBuilder

"""
User input schema rules:
  - `check`: Successful if the schema conforms to a record, otherwise ConfigValidationError.
  - `discover`: User-input schema is output if the schema is valid, otherwise ConfigValidationError.
  - `read`: If the schema is valid, record values are cast to types in the schema; if this is successful
    the records are emitted. otherwise an error is logged. If the schema is not valid, ConfigValidationError.
"""


_base_user_input_schema_scenario = (
    TestScenarioBuilder()
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
)


valid_single_stream_user_input_schema_scenario = (
    _base_user_input_schema_scenario.copy()
    .set_name("valid_single_stream_user_input_schema_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "input_schema": '{"col1": "string", "col2": "string"}',
                }
            ]
        }
    )
    .set_expected_check_status("SUCCEEDED")
).build()


single_stream_user_input_schema_scenario_schema_is_invalid = (
    _base_user_input_schema_scenario.copy()
    .set_name("single_stream_user_input_schema_scenario_schema_is_invalid")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "input_schema": '{"col1": "x", "col2": "string"}',
                }
            ]
        }
    )
    .set_catalog(CatalogBuilder().with_stream("stream1", SyncMode.full_refresh).build())
    .set_expected_check_status("FAILED")
    .set_expected_check_error(None, FileBasedSourceError.ERROR_PARSING_USER_PROVIDED_SCHEMA.value)
    .set_expected_discover_error(ConfigValidationError, FileBasedSourceError.ERROR_PARSING_USER_PROVIDED_SCHEMA.value)
    .set_expected_read_error(ConfigValidationError, FileBasedSourceError.ERROR_PARSING_USER_PROVIDED_SCHEMA.value)
).build()


single_stream_user_input_schema_scenario_emit_nonconforming_records = (
    _base_user_input_schema_scenario.copy()
    .set_name("single_stream_user_input_schema_scenario_emit_nonconforming_records")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                    "input_schema": '{"col1": "integer", "col2": "string"}',
                }
            ]
        }
    )
    .set_expected_check_status("FAILED")
    .set_expected_check_error(None, FileBasedSourceError.SCHEMA_INFERENCE_ERROR.value)
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": "integer"},
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
).build()


single_stream_user_input_schema_scenario_skip_nonconforming_records = (
    _base_user_input_schema_scenario.copy()
    .set_name("single_stream_user_input_schema_scenario_skip_nonconforming_records")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*"],
                    "validation_policy": "Skip Record",
                    "input_schema": '{"col1": "integer", "col2": "string"}',
                }
            ]
        }
    )
    .set_expected_check_status("FAILED")
    .set_expected_check_error(None, FileBasedSourceError.SCHEMA_INFERENCE_ERROR.value)
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": "integer"},
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
    .set_expected_logs(
        {
            "read": [
                {
                    "level": "WARN",
                    "message": "Records in file did not pass validation policy. stream=stream1 file=a.csv n_skipped=2 validation_policy=skip_record",
                },
                {
                    "level": "WARN",
                    "message": "Could not cast the value to the expected type.: col1: value=val11,expected_type=integer",
                },
                {
                    "level": "WARN",
                    "message": "Could not cast the value to the expected type.: col1: value=val21,expected_type=integer",
                },
            ]
        }
    )
).build()


_base_multi_stream_user_input_schema_scenario = (
    TestScenarioBuilder()
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_files(
            {
                "a.csv": {
                    "contents": [
                        ("col1", "col2"),
                        ("val11a", 21),
                        ("val12a", 22),
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
                "c.csv": {
                    "contents": [
                        ("col1",),
                        ("val11c",),
                        ("val21c",),
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
                            "col1": {
                                "type": "string",
                            },
                            "col2": {
                                "type": "integer",
                            },
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
                            "col1": {
                                "type": "string",
                            },
                            "col2": {
                                "type": "string",
                            },
                            "col3": {
                                "type": "string",
                            },
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream2",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                },
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": ["null", "string"],
                            },
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream3",
                    "source_defined_cursor": True,
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
                    "col2": 21,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val12a",
                    "col2": 22,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            # The files in b.csv are emitted despite having an invalid schema
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
            {
                "data": {"col1": "val11c", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "c.csv"},
                "stream": "stream3",
            },
            {
                "data": {"col1": "val21c", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "c.csv"},
                "stream": "stream3",
            },
        ]
    )
)


valid_multi_stream_user_input_schema_scenario = (
    _base_multi_stream_user_input_schema_scenario.copy()
    .set_name("valid_multi_stream_user_input_schema_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["a.csv"],
                    "validation_policy": "Emit Record",
                    "input_schema": '{"col1": "string", "col2": "integer"}',
                },
                {
                    "name": "stream2",
                    "format": {"filetype": "csv"},
                    "globs": ["b.csv"],
                    "validation_policy": "Emit Record",
                    "input_schema": '{"col1": "string", "col2": "string", "col3": "string"}',
                },
                {
                    "name": "stream3",
                    "format": {"filetype": "csv"},
                    "globs": ["c.csv"],
                    "validation_policy": "Emit Record",
                },
            ]
        }
    )
    .set_expected_check_status("SUCCEEDED")
).build()


multi_stream_user_input_schema_scenario_schema_is_invalid = (
    _base_multi_stream_user_input_schema_scenario.copy()
    .set_name("multi_stream_user_input_schema_scenario_schema_is_invalid")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["a.csv"],
                    "validation_policy": "Emit Record",
                    "input_schema": '{"col1": "string", "col2": "integer"}',
                },
                {
                    "name": "stream2",
                    "format": {"filetype": "csv"},
                    "globs": ["b.csv"],
                    "validation_policy": "Emit Record",
                    "input_schema": '{"col1": "x", "col2": "string", "col3": "string"}',  # this stream's schema is invalid
                },
                {
                    "name": "stream3",
                    "format": {"filetype": "csv"},
                    "globs": ["c.csv"],
                    "validation_policy": "Emit Record",
                },
            ]
        }
    )
    .set_catalog(
        CatalogBuilder()
        .with_stream("stream1", SyncMode.full_refresh)
        .with_stream("stream2", SyncMode.full_refresh)
        .with_stream("stream3", SyncMode.full_refresh)
        .build()
    )
    .set_expected_check_status("FAILED")
    .set_expected_check_error(None, FileBasedSourceError.ERROR_PARSING_USER_PROVIDED_SCHEMA.value)
    .set_expected_discover_error(ConfigValidationError, FileBasedSourceError.ERROR_PARSING_USER_PROVIDED_SCHEMA.value)
    .set_expected_read_error(ConfigValidationError, FileBasedSourceError.ERROR_PARSING_USER_PROVIDED_SCHEMA.value)
).build()


multi_stream_user_input_schema_scenario_emit_nonconforming_records = (
    _base_multi_stream_user_input_schema_scenario.copy()
    .set_name("multi_stream_user_input_schema_scenario_emit_nonconforming_records")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["a.csv"],
                    "validation_policy": "Emit Record",
                    "input_schema": '{"col1": "string", "col2": "integer"}',
                },
                {
                    "name": "stream2",
                    "format": {"filetype": "csv"},
                    "globs": ["b.csv"],
                    "validation_policy": "Emit Record",
                    "input_schema": '{"col1": "string", "col2": "integer", "col3": "string"}',  # this stream's records do not conform to the schema
                },
                {
                    "name": "stream3",
                    "format": {"filetype": "csv"},
                    "globs": ["c.csv"],
                    "validation_policy": "Emit Record",
                },
            ]
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
                            "col1": {"type": "string"},
                            "col2": {"type": "integer"},
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
                            "col1": {"type": "string"},
                            "col2": {"type": "integer"},
                            "col3": {"type": "string"},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream2",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                },
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": ["null", "string"],
                            },
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream3",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                },
            ]
        }
    )
    .set_expected_check_status("FAILED")
    .set_expected_check_error(None, FileBasedSourceError.ERROR_PARSING_USER_PROVIDED_SCHEMA.value)
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val11a",
                    "col2": 21,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val12a",
                    "col2": 22,
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
            {
                "data": {"col1": "val11c", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "c.csv"},
                "stream": "stream3",
            },
            {
                "data": {"col1": "val21c", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "c.csv"},
                "stream": "stream3",
            },
        ]
    )
    .set_expected_logs(
        {
            "read": [
                {
                    "level": "WARN",
                    "message": "Could not cast the value to the expected type.: col2: value=val12b,expected_type=integer",
                },
                {
                    "level": "WARN",
                    "message": "Could not cast the value to the expected type.: col2: value=val22b,expected_type=integer",
                },
            ]
        }
    )
).build()


multi_stream_user_input_schema_scenario_skip_nonconforming_records = (
    _base_multi_stream_user_input_schema_scenario.copy()
    .set_name("multi_stream_user_input_schema_scenario_skip_nonconforming_records")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["a.csv"],
                    "validation_policy": "Emit Record",
                    "input_schema": '{"col1": "string", "col2": "integer"}',
                },
                {
                    "name": "stream2",
                    "format": {"filetype": "csv"},
                    "globs": ["b.csv"],
                    "validation_policy": "Skip Record",
                    "input_schema": '{"col1": "string", "col2": "integer", "col3": "string"}',  # this stream's records do not conform to the schema
                },
                {
                    "name": "stream3",
                    "format": {"filetype": "csv"},
                    "globs": ["c.csv"],
                    "validation_policy": "Emit Record",
                },
            ]
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
                            "col1": {"type": "string"},
                            "col2": {"type": "integer"},
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
                            "col1": {"type": "string"},
                            "col2": {"type": "integer"},
                            "col3": {"type": "string"},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream2",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                },
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": ["null", "string"],
                            },
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream3",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                },
            ]
        }
    )
    .set_expected_check_status("FAILED")
    .set_expected_check_error(None, FileBasedSourceError.ERROR_PARSING_USER_PROVIDED_SCHEMA.value)
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val11a",
                    "col2": 21,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val12a",
                    "col2": 22,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            # {"data": {"col1": "val11b", "col2": "val12b", "col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
            #           "_ab_source_file_url": "b.csv"}, "stream": "stream2"},
            # {"data": {"col1": "val21b", "col2": "val22b", "col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
            #           "_ab_source_file_url": "b.csv"}, "stream": "stream2"},
            {
                "data": {"col1": "val11c", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "c.csv"},
                "stream": "stream3",
            },
            {
                "data": {"col1": "val21c", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "c.csv"},
                "stream": "stream3",
            },
        ]
    )
    .set_expected_logs(
        {
            "read": [
                {
                    "level": "WARN",
                    "message": "Records in file did not pass validation policy. stream=stream2 file=b.csv n_skipped=2 validation_policy=skip_record",
                },
                {
                    "level": "WARN",
                    "message": "Could not cast the value to the expected type.: col2: value=val12b,expected_type=integer",
                },
                {
                    "level": "WARN",
                    "message": "Could not cast the value to the expected type.: col2: value=val22b,expected_type=integer",
                },
            ]
        }
    )
).build()
