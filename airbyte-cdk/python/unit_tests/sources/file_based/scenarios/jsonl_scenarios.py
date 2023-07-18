#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError, SchemaInferenceError
from unit_tests.sources.file_based.helpers import LowInferenceBytesJsonlParser, LowInferenceLimitDiscoveryPolicy
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenarioBuilder

single_jsonl_scenario = (
    TestScenarioBuilder()
    .set_name("single_jsonl_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "jsonl",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_files(
        {
            "a.jsonl": {
                "contents": [
                    {"col1": "val11", "col2": "val12"},
                    {"col1": "val21", "col2": "val22"},
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            }
        }
    )
    .set_file_type("jsonl")
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
                      "_ab_source_file_url": "a.jsonl"}, "stream": "stream1"},
            {"data": {"col1": "val21", "col2": "val22", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.jsonl"}, "stream": "stream1"},
        ]
    )
).build()


multi_jsonl_with_different_keys_scenario = (
    TestScenarioBuilder()
    .set_name("multi_jsonl_with_different_keys_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "jsonl",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_files(
        {
            "a.jsonl": {
                "contents": [
                    {"col1": "val11a", "col2": "val12a"},
                    {"col1": "val21a", "col2": "val22a"},
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b.jsonl": {
                "contents": [
                    {"col1": "val11b", "col2": "val12b", "col3": "val13b"},
                    {"col1": "val21b", "col3": "val23b"},
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
        }
    )
    .set_file_type("jsonl")
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
                      "_ab_source_file_url": "a.jsonl"}, "stream": "stream1"},
            {"data": {"col1": "val21a", "col2": "val22a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.jsonl"}, "stream": "stream1"},
            {"data": {"col1": "val11b", "col2": "val12b", "col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "b.jsonl"}, "stream": "stream1"},
            {"data": {"col1": "val21b", "col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "b.jsonl"}, "stream": "stream1"},
        ]
    )
).build()


multi_jsonl_stream_n_file_exceeds_limit_for_inference = (
    TestScenarioBuilder()
    .set_name("multi_jsonl_stream_n_file_exceeds_limit_for_inference")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "jsonl",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_files(
        {
            "a.jsonl": {
                "contents": [
                    {"col1": "val11a", "col2": "val12a"},
                    {"col1": "val21a", "col2": "val22a"},
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b.jsonl": {
                "contents": [
                    {"col1": "val11b", "col2": "val12b", "col3": "val13b"},
                    {"col1": "val21b", "col3": "val23b"},
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
        }
    )
    .set_file_type("jsonl")
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
                      "_ab_source_file_url": "a.jsonl"}, "stream": "stream1"},
            {"data": {"col1": "val21a", "col2": "val22a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.jsonl"}, "stream": "stream1"},
            {"data": {"col1": "val11b", "col2": "val12b", "col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "b.jsonl"}, "stream": "stream1"},
            {"data": {"col1": "val21b", "col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "b.jsonl"}, "stream": "stream1"},
        ]
    )
    .set_discovery_policy(LowInferenceLimitDiscoveryPolicy())
).build()


multi_jsonl_stream_n_bytes_exceeds_limit_for_inference = (
    TestScenarioBuilder()
    .set_name("multi_jsonl_stream_n_bytes_exceeds_limit_for_inference")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "jsonl",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_files(
        {
            "a.jsonl": {
                "contents": [
                    {"col1": "val11a", "col2": "val12a"},
                    {"col1": "val21a", "col2": "val22a"},
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b.jsonl": {
                "contents": [
                    {"col1": "val11b", "col2": "val12b"},
                    {"col1": "val21b", "col2": "val22b", "col3": "val23b"},
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
        }
    )
    .set_file_type("jsonl")
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
                      "_ab_source_file_url": "a.jsonl"}, "stream": "stream1"},
            {"data": {"col1": "val21a", "col2": "val22a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.jsonl"}, "stream": "stream1"},
            {"data": {"col1": "val11b", "col2": "val12b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "b.jsonl"}, "stream": "stream1"},
            {"data": {"col1": "val21b", "col2": "val22b", "col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "b.jsonl"}, "stream": "stream1"},
        ]
    )
    .set_parsers({"jsonl": LowInferenceBytesJsonlParser()})
).build()


invalid_jsonl_scenario = (
    TestScenarioBuilder()
    .set_name("invalid_jsonl_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "jsonl",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_files(
        {
            "a.jsonl": {
                "contents": [
                    {"col1": "val1"},
                    "invalid",
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            }
        }
    )
    .set_file_type("jsonl")
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
    .set_expected_records([
        {"data": {"col1": "val1", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                  "_ab_source_file_url": "a.jsonl"}, "stream": "stream1"},
    ])
    .set_expected_discover_error(SchemaInferenceError, FileBasedSourceError.SCHEMA_INFERENCE_ERROR.value)
    .set_expected_logs(
        {
            "read": [
                {
                    "level": "ERROR",
                    "message": f"{FileBasedSourceError.ERROR_PARSING_RECORD.value} stream=stream1 file=a.jsonl line_no=2 n_skipped=0",
                },
            ]
        }
    )
).build()


jsonl_multi_stream_scenario = (
    TestScenarioBuilder()
    .set_name("jsonl_multi_stream_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "jsonl",
                    "globs": ["*.jsonl"],
                    "validation_policy": "emit_record",
                },
                {
                    "name": "stream2",
                    "file_type": "jsonl",
                    "globs": ["b.jsonl"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_files(
        {
            "a.jsonl": {
                "contents": [
                    {"col1": 1, "col2": "record1"},
                    {"col1": 2, "col2": "record2"},
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b.jsonl": {
                "contents": [
                    {"col3": 1.1},
                    {"col3": 2.2},
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
        }
    )
    .set_file_type("jsonl")
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": "integer"
                            },
                            "col2": {
                                "type": "string"
                            },
                            "col3": {
                                "type": "number"
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
                                "type": "number"
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
            {"data": {"col1": 1, "col2": "record1", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.jsonl"}, "stream": "stream1"},
            {"data": {"col1": 2, "col2": "record2", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.jsonl"}, "stream": "stream1"},
            {"data": {"col3": 1.1, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "b.jsonl"},
             "stream": "stream1"},
            {"data": {"col3": 2.2, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "b.jsonl"},
             "stream": "stream1"},
            {"data": {"col3": 1.1, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "b.jsonl"},
             "stream": "stream2"},
            {"data": {"col3": 2.2, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "b.jsonl"},
             "stream": "stream2"},
        ]
    )
).build()


schemaless_jsonl_scenario = (
    TestScenarioBuilder()
    .set_name("schemaless_jsonl_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "jsonl",
                    "globs": ["*"],
                    "validation_policy": "skip_record",
                    "schemaless": True,
                }
            ]
        }
    )
    .set_files(
        {
            "a.jsonl": {
                "contents": [
                    {"col1": 1, "col2": "record1"},
                    {"col1": 2, "col2": "record2"},
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b.jsonl": {
                "contents": [
                    {"col1": 3, "col2": "record3", "col3": 1.1},
                    {"col1": 4, "col2": "record4", "col3": 1.1},
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
        }
    )
    .set_file_type("jsonl")
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
            {"data": {"data": {"col1": 1, "col2": "record1"}, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.jsonl"}, "stream": "stream1"},
            {"data": {"data": {"col1": 2, "col2": "record2"}, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.jsonl"}, "stream": "stream1"},
            {"data": {"data": {"col1": 3, "col2": "record3", "col3": 1.1}, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "b.jsonl"}, "stream": "stream1"},
            {"data": {"data": {"col1": 4, "col2": "record4", "col3": 1.1}, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "b.jsonl"}, "stream": "stream1"},
        ]
    )
).build()


schemaless_jsonl_multi_stream_scenario = (
    TestScenarioBuilder()
    .set_name("schemaless_jsonl_multi_stream_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "jsonl",
                    "globs": ["a.jsonl"],
                    "validation_policy": "skip_record",
                    "schemaless": True,
                },
                {
                    "name": "stream2",
                    "file_type": "jsonl",
                    "globs": ["b.jsonl"],
                    "validation_policy": "skip_record",
                }
            ]
        }
    )
    .set_files(
        {
            "a.jsonl": {
                "contents": [
                    {"col1": 1, "col2": "record1"},
                    {"col1": 2, "col2": "record2"},
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b.jsonl": {
                "contents": [
                    {"col3": 1.1},
                    {"col3": 2.2},
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
        }
    )
    .set_file_type("jsonl")
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
                                "type": "number"
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
            {"data": {"data": {"col1": 1, "col2": "record1"}, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.jsonl"}, "stream": "stream1"},
            {"data": {"data": {"col1": 2, "col2": "record2"}, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.jsonl"}, "stream": "stream1"},
            {"data": {"col3": 1.1, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "b.jsonl"},
             "stream": "stream2"},
            {"data": {"col3": 2.2, "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "b.jsonl"},
             "stream": "stream2"},
        ]
    )
).build()

jsonl_user_input_schema_scenario = (
    TestScenarioBuilder()
    .set_name("jsonl_user_input_schema_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "jsonl",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                    "input_schema": '{"col1": "integer", "col2": "string"}'
                }
            ]
        }
    )
    .set_files(
        {
            "a.jsonl": {
                "contents": [
                    {"col1": 1, "col2": "val12"},
                    {"col1": 2, "col2": "val22"},
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            }
        }
    )
    .set_file_type("jsonl")
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": "integer"
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
            {"data": {"col1": 1, "col2": "val12", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.jsonl"}, "stream": "stream1"},
            {"data": {"col1": 2, "col2": "val22", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.jsonl"}, "stream": "stream1"},
        ]
    )
).build()
