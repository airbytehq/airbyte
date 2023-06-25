#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unit_tests.sources.file_based.scenarios._scenario_builder import IncrementalScenarioConfig, TestScenarioBuilder

single_csv_input_state_is_earlier_scenario = (
    TestScenarioBuilder()
    .set_name("single_csv_input_state_is_earlier")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*.csv"],
                    "validation_policy": "emit_record_on_schema_mismatch",
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
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[{
            "type": "STREAM",
            "stream": {
                "stream_state": {
                    "history": {
                        "some_old_file.csv": "2023-06-01T03:54:07.000000Z"
                    },
                },
                "stream_descriptor": {"name": "stream1"}
            }
        }
        ],
    ))
    .set_expected_records(
        [
            {"col1": "val11", "col2": "val12", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "a.csv"},
            {"col1": "val21", "col2": "val22", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "a.csv"},
            {
                "stream1": {
                    "history": {
                        "some_old_file.csv": "2023-06-01T03:54:07.000000Z",
                        "a.csv": "2023-06-05T03:54:07.000000Z"
                    },
                }
            }
        ]
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": ["null", "string"]
                            }, "col2": {
                                "type": ["null", "string"]
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
                }
            ]
        }
    )
).build()

single_csv_file_is_skipped_if_same_modified_at_as_in_history = (
    TestScenarioBuilder()
    .set_name("single_csv_file_is_skipped_if_same_modified_at_as_in_history")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*.csv"],
                    "validation_policy": "emit_record_on_schema_mismatch",
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
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[{
            "type": "STREAM",
            "stream": {
                "stream_state": {
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z"
                    },
                },
                "stream_descriptor": {"name": "stream1"}
            }
        }
        ],
    ))
    .set_expected_records(
        [
            {
                "stream1": {
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z"
                    },
                }
            }
        ]
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": ["null", "string"]
                            }, "col2": {
                                "type": ["null", "string"]
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
                }
            ]
        }
    )
).build()

single_csv_file_is_synced_if_modified_at_is_more_recent_than_in_history = (
    TestScenarioBuilder()
    .set_name("single_csv_file_is_synced_if_modified_at_is_more_recent_than_in_history")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*.csv"],
                    "validation_policy": "emit_record_on_schema_mismatch",
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
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[{
            "type": "STREAM",
            "stream": {
                "stream_state": {
                    "history": {
                        "a.csv": "2023-06-01T03:54:07.000000Z"
                    },
                },
                "stream_descriptor": {"name": "stream1"}
            }
        }
        ],
    ))
    .set_expected_records(
        [
            {"col1": "val11", "col2": "val12", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "a.csv"},
            {"col1": "val21", "col2": "val22", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "a.csv"},
            {
                "stream1": {
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z"
                    },
                }
            }
        ]
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": ["null", "string"]
                            }, "col2": {
                                "type": ["null", "string"]
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
                }
            ]
        }
    )
).build()

single_csv_no_input_state_scenario = (
    TestScenarioBuilder()
    .set_name("single_csv_input_state_is_earlier_again")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*.csv"],
                    "validation_policy": "emit_record_on_schema_mismatch",
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
                "last_modified": "2023-06-05T03:54:07.000000Z",
            }
        }
    )
    .set_file_type("csv")
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": ["null", "string"]
                            }, "col2": {
                                "type": ["null", "string"]
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
                }
            ]
        }
    )
    .set_expected_records(
        [
            {"col1": "val11", "col2": "val12", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "a.csv"},
            {"col1": "val21", "col2": "val22", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "a.csv"},
            {
                "stream1": {
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z"
                    },
                }
            }
        ]
    )
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[],
    ))).build()

multi_csv_same_timestamp_scenario = (
    TestScenarioBuilder()
    .set_name("multi_csv_same_timestamp")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*.csv"],
                    "validation_policy": "emit_record_on_schema_mismatch",
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
                "last_modified": "2023-06-05T03:54:07.000000Z",
            },
            "b.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11b", "val12b", "val13b"),
                    ("val21b", "val22b", "val23b"),
                ],
                "last_modified": "2023-06-05T03:54:07.000000Z",
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
                                "type": ["null", "string"]
                            },
                            "col2": {
                                "type": ["null", "string"]
                            },
                            "col3": {
                                "type": ["null", "string"]
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
            {"col1": "val11a", "col2": "val12a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "a.csv"},
            {"col1": "val21a", "col2": "val22a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "a.csv"},
            {"col1": "val11b", "col2": "val12b", "col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
             "_ab_source_file_url": "b.csv"},
            {"col1": "val21b", "col2": "val22b", "col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
             "_ab_source_file_url": "b.csv"},
            {
                "stream1": {
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z",
                        "b.csv": "2023-06-05T03:54:07.000000Z"
                    },
                }
            }
        ]
    )
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[],
    ))).build()

single_csv_input_state_is_later_scenario = (
    TestScenarioBuilder()
    .set_name("single_csv_input_state_is_later")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*.csv"],
                    "validation_policy": "emit_record_on_schema_mismatch",
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
                "last_modified": "2023-06-05T03:54:07.000000Z",
            }
        }
    )
    .set_file_type("csv")
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {
                                "type": ["null", "string"]
                            }, "col2": {
                                "type": ["null", "string"]
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
                }
            ]
        }
    )
    .set_expected_records(
        [
            {"col1": "val11", "col2": "val12", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "a.csv"},
            {"col1": "val21", "col2": "val22", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "a.csv"},
            {
                "stream1": {
                    "history": {
                        "recent_file.csv": "2023-07-15T23:59:59.000000Z",
                        "a.csv": "2023-06-05T03:54:07.000000Z",
                    },
                }
            }
        ]
    )
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[{
            "type": "STREAM",
            "stream": {
                "stream_state": {
                    "history": {
                        "recent_file.csv": "2023-07-15T23:59:59.000000Z"
                    }
                },
                "stream_descriptor": {"name": "stream1"}
            }
        }
        ],
    ))).build()

multi_csv_different_timestamps_scenario = (
    TestScenarioBuilder()
    .set_name("multi_csv_stream_different_timestamps")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*.csv"],
                    "validation_policy": "emit_record_on_schema_mismatch",
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
                "last_modified": "2023-06-04T03:54:07.000000Z",
            },
            "b.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11b", "val12b", "val13b"),
                    ("val21b", "val22b", "val23b"),
                ],
                "last_modified": "2023-06-05T03:54:07.000000Z",
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
                                "type": ["null", "string"]
                            },
                            "col2": {
                                "type": ["null", "string"]
                            },
                            "col3": {
                                "type": ["null", "string"]
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
            {"col1": "val11a", "col2": "val12a", "_ab_source_file_last_modified": "2023-06-04T03:54:07Z", "_ab_source_file_url": "a.csv"},
            {"col1": "val21a", "col2": "val22a", "_ab_source_file_last_modified": "2023-06-04T03:54:07Z", "_ab_source_file_url": "a.csv"},
            {
                "stream1": {
                    "history": {
                        "a.csv": "2023-06-04T03:54:07.000000Z",
                    },
                }
            },
            {"col1": "val11b", "col2": "val12b", "col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
             "_ab_source_file_url": "b.csv"},
            {"col1": "val21b", "col2": "val22b", "col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
             "_ab_source_file_url": "b.csv"},
            {
                "stream1": {
                    "history": {
                        "a.csv": "2023-06-04T03:54:07.000000Z",
                        "b.csv": "2023-06-05T03:54:07.000000Z"
                    },
                }
            }
        ]
    )
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[],
    ))).build()

multi_csv_per_timestamp_scenario = (
    TestScenarioBuilder()
    .set_name("multi_csv_per_timestamp")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*.csv"],
                    "validation_policy": "emit_record_on_schema_mismatch",
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
                "last_modified": "2023-06-05T03:54:07.000000Z",
            },
            "b.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11b", "val12b", "val13b"),
                    ("val21b", "val22b", "val23b"),
                ],
                "last_modified": "2023-06-05T03:54:07.000000Z",
            },
            "c.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11c", "val12c", "val13c"),
                    ("val21c", "val22c", "val23c"),
                ],
                "last_modified": "2023-06-06T03:54:07.000000Z",
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
                                "type": ["null", "string"]
                            },
                            "col2": {
                                "type": ["null", "string"]
                            },
                            "col3": {
                                "type": ["null", "string"]
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
            {"col1": "val11a", "col2": "val12a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "a.csv"},
            {"col1": "val21a", "col2": "val22a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "a.csv"},
            {"col1": "val11b", "col2": "val12b", "col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
             "_ab_source_file_url": "b.csv"},
            {"col1": "val21b", "col2": "val22b", "col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
             "_ab_source_file_url": "b.csv"},
            {
                "stream1": {
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z",
                        "b.csv": "2023-06-05T03:54:07.000000Z"
                    },
                }
            },
            {"col1": "val11c", "col2": "val12c", "col3": "val13c", "_ab_source_file_last_modified": "2023-06-06T03:54:07Z",
             "_ab_source_file_url": "c.csv"},
            {"col1": "val21c", "col2": "val22c", "col3": "val23c", "_ab_source_file_last_modified": "2023-06-06T03:54:07Z",
             "_ab_source_file_url": "c.csv"},
            {
                "stream1": {
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z",
                        "b.csv": "2023-06-05T03:54:07.000000Z",
                        "c.csv": "2023-06-06T03:54:07.000000Z"
                    },
                }
            },
        ]
    )
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[],
    ))).build()

multi_csv_skip_file_if_already_in_history = (
    TestScenarioBuilder()
    .set_name("skip_files_already_in_history")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*.csv"],
                    "validation_policy": "emit_record_on_schema_mismatch",
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
                "last_modified": "2023-06-05T03:54:07.000000Z",
            },
            "b.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11b", "val12b", "val13b"),
                    ("val21b", "val22b", "val23b"),
                ],
                "last_modified": "2023-06-05T03:54:07.000000Z",
            },
            "c.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11c", "val12c", "val13c"),
                    ("val21c", "val22c", "val23c"),
                ],
                "last_modified": "2023-06-06T03:54:07.000000Z",
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
                                "type": ["null", "string"]
                            },
                            "col2": {
                                "type": ["null", "string"]
                            },
                            "col3": {
                                "type": ["null", "string"]
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
            # {"col1": "val11a", "col2": "val12a"}, # this file is skipped
            # {"col1": "val21a", "col2": "val22a"}, # this file is skipped
            {"col1": "val11b", "col2": "val12b", "col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
             "_ab_source_file_url": "b.csv"},
            {"col1": "val21b", "col2": "val22b", "col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
             "_ab_source_file_url": "b.csv"},
            {
                "stream1": {
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z",
                        "b.csv": "2023-06-05T03:54:07.000000Z"
                    },
                }
            },
            {"col1": "val11c", "col2": "val12c", "col3": "val13c", "_ab_source_file_last_modified": "2023-06-06T03:54:07Z",
             "_ab_source_file_url": "c.csv"},
            {"col1": "val21c", "col2": "val22c", "col3": "val23c", "_ab_source_file_last_modified": "2023-06-06T03:54:07Z",
             "_ab_source_file_url": "c.csv"},
            {
                "stream1": {
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z",
                        "b.csv": "2023-06-05T03:54:07.000000Z",
                        "c.csv": "2023-06-06T03:54:07.000000Z"
                    },
                }
            },
        ]
    )
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[{
            "type": "STREAM",
            "stream": {
                "stream_state": {
                    "history": {"a.csv": "2023-06-05T03:54:07.000000Z"}
                },
                "stream_descriptor": {"name": "stream1"}
            }
        }
        ],
    ))).build()

multi_csv_include_missing_files_within_history_range = (
    TestScenarioBuilder()
    .set_name("include_missing_files_within_history_range")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*.csv"],
                    "validation_policy": "emit_record_on_schema_mismatch",
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
                "last_modified": "2023-06-05T03:54:07.000000Z",
            },
            "b.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11b", "val12b", "val13b"),
                    ("val21b", "val22b", "val23b"),
                ],
                "last_modified": "2023-06-05T03:54:07.000000Z",
            },
            "c.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11c", "val12c", "val13c"),
                    ("val21c", "val22c", "val23c"),
                ],
                "last_modified": "2023-06-06T03:54:07.000000Z",
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
                                "type": ["null", "string"]
                            },
                            "col2": {
                                "type": ["null", "string"]
                            },
                            "col3": {
                                "type": ["null", "string"]
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
            # {"col1": "val11a", "col2": "val12a"}, # this file is skipped
            # {"col1": "val21a", "col2": "val22a"}, # this file is skipped
            {"col1": "val11b", "col2": "val12b", "col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
             "_ab_source_file_url": "b.csv"},
            {"col1": "val21b", "col2": "val22b", "col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
             "_ab_source_file_url": "b.csv"},
            # {"col1": "val11c", "col2": "val12c", "col3": "val13c"}, # this file is skipped
            # {"col1": "val21c", "col2": "val22c", "col3": "val23c"}, # this file is skipped
            {
                "stream1": {
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z",
                        "b.csv": "2023-06-05T03:54:07.000000Z",
                        "c.csv": "2023-06-06T03:54:07.000000Z"
                    },
                }
            },
        ]
    )
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[{
            "type": "STREAM",
            "stream": {
                "stream_state": {
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z",
                        "c.csv": "2023-06-06T03:54:07.000000Z"
                    },
                },
                "stream_descriptor": {"name": "stream1"}
            }
        }
        ],
    ))).build()

multi_csv_remove_old_files_if_history_is_full_scenario = (
    TestScenarioBuilder()
    .set_name("multi_csv_remove_old_files_if_history_is_full")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*.csv"],
                    "validation_policy": "emit_record_on_schema_mismatch",
                    "max_history_size": 3,
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
                "last_modified": "2023-06-06T03:54:07.000000Z",
            },
            "b.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11b", "val12b", "val13b"),
                    ("val21b", "val22b", "val23b"),
                ],
                "last_modified": "2023-06-07T03:54:07.000000Z",
            },
            "c.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11c", "val12c", "val13c"),
                    ("val21c", "val22c", "val23c"),
                ],
                "last_modified": "2023-06-10T03:54:07.000000Z",
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
                                "type": ["null", "string"]
                            },
                            "col2": {
                                "type": ["null", "string"]
                            },
                            "col3": {
                                "type": ["null", "string"]
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
            {"col1": "val11a", "col2": "val12a", "_ab_source_file_last_modified": "2023-06-06T03:54:07Z", "_ab_source_file_url": "a.csv"},
            {"col1": "val21a", "col2": "val22a", "_ab_source_file_last_modified": "2023-06-06T03:54:07Z", "_ab_source_file_url": "a.csv"},
            {
                "stream1": {
                    "history": {
                        "very_old_file.csv": "2023-06-02T03:54:07.000000Z",
                        "old_file_same_timestamp_as_a.csv": "2023-06-06T03:54:07.000000Z",
                        "a.csv": "2023-06-06T03:54:07.000000Z",
                    },
                }
            },
            {"col1": "val11b", "col2": "val12b", "col3": "val13b", "_ab_source_file_last_modified": "2023-06-07T03:54:07Z",
             "_ab_source_file_url": "b.csv"},
            {"col1": "val21b", "col2": "val22b", "col3": "val23b", "_ab_source_file_last_modified": "2023-06-07T03:54:07Z",
             "_ab_source_file_url": "b.csv"},
            {
                "stream1": {
                    "history": {
                        "old_file_same_timestamp_as_a.csv": "2023-06-06T03:54:07.000000Z",
                        "a.csv": "2023-06-06T03:54:07.000000Z",
                        "b.csv": "2023-06-07T03:54:07.000000Z",
                    },
                }
            },
            {"col1": "val11c", "col2": "val12c", "col3": "val13c", "_ab_source_file_last_modified": "2023-06-10T03:54:07Z",
             "_ab_source_file_url": "c.csv"},
            {"col1": "val21c", "col2": "val22c", "col3": "val23c", "_ab_source_file_last_modified": "2023-06-10T03:54:07Z",
             "_ab_source_file_url": "c.csv"},
            {
                "stream1": {
                    "history": {
                        "old_file_same_timestamp_as_a.csv": "2023-06-06T03:54:07.000000Z",
                        "b.csv": "2023-06-07T03:54:07.000000Z",
                        "c.csv": "2023-06-10T03:54:07.000000Z"
                    },
                }
            },
        ]
    )
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[{
            "type": "STREAM",
            "stream": {
                "stream_state": {
                    "history": {
                        "very_very_old_file.csv": "2023-06-01T03:54:07.000000Z",
                        "very_old_file.csv": "2023-06-02T03:54:07.000000Z",
                        "old_file_same_timestamp_as_a.csv": "2023-06-06T03:54:07.000000Z",
                    },
                },
                "stream_descriptor": {"name": "stream1"}
            }
        }
        ],
    ))).build()

multi_csv_same_timestamp_more_files_than_history_size_scenario = (
    TestScenarioBuilder()
    .set_name("multi_csv_same_timestamp_more_files_than_history_size")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*.csv"],
                    "validation_policy": "emit_record_on_schema_mismatch",
                    "max_history_size": 3,
                    "days_to_sync_if_history_is_full": 3,
                }
            ]
        }
    )
    .set_files(
        {
            "b.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11b", "val12b", "val13b"),
                    ("val21b", "val22b", "val23b"),
                ],
                "last_modified": "2023-06-05T03:54:07.000000Z",
            },
            "a.csv": {
                "contents": [
                    ("col1", "col2"),
                    ("val11a", "val12a"),
                    ("val21a", "val22a"),
                ],
                "last_modified": "2023-06-05T03:54:07.000000Z",
            },
            "c.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11c", "val12c", "val13c"),
                    ("val21c", "val22c", "val23c"),
                ],
                "last_modified": "2023-06-05T03:54:07.000000Z",
            },
            "d.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11d", "val12d", "val13d"),
                    ("val21d", "val22d", "val23d"),
                ],
                "last_modified": "2023-06-05T03:54:07.000000Z",
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
                                "type": ["null", "string"]
                            },
                            "col2": {
                                "type": ["null", "string"]
                            },
                            "col3": {
                                "type": ["null", "string"]
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
            {"col1": "val11a", "col2": "val12a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "a.csv"},
            {"col1": "val21a", "col2": "val22a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z", "_ab_source_file_url": "a.csv"},
            {"col1": "val11b", "col2": "val12b", "col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
             "_ab_source_file_url": "b.csv"},
            {"col1": "val21b", "col2": "val22b", "col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
             "_ab_source_file_url": "b.csv"},
            {"col1": "val11c", "col2": "val12c", "col3": "val13c", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
             "_ab_source_file_url": "c.csv"},
            {"col1": "val21c", "col2": "val22c", "col3": "val23c", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
             "_ab_source_file_url": "c.csv"},
            {"col1": "val11d", "col2": "val12d", "col3": "val13d", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
             "_ab_source_file_url": "d.csv"},
            {"col1": "val21d", "col2": "val22d", "col3": "val23d", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
             "_ab_source_file_url": "d.csv"},
            {
                "stream1": {
                    "history": {
                        "b.csv": "2023-06-05T03:54:07.000000Z",
                        "c.csv": "2023-06-05T03:54:07.000000Z",
                        "d.csv": "2023-06-05T03:54:07.000000Z",
                    },
                }
            }
        ]
    )
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[],
    ))).build()

multi_csv_sync_recent_files_if_history_is_incomplete_scenario = (
    TestScenarioBuilder()
    .set_name("multi_csv_sync_recent_files_if_history_is_incomplete")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*.csv"],
                    "validation_policy": "emit_record_on_schema_mismatch",
                    "max_history_size": 3,
                    "days_to_sync_if_history_is_full": 3,
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
                "last_modified": "2023-06-05T03:54:07.000000Z",
            },
            "b.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11b", "val12b", "val13b"),
                    ("val21b", "val22b", "val23b"),
                ],
                "last_modified": "2023-06-05T03:54:07.000000Z",
            },
            "c.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11c", "val12c", "val13c"),
                    ("val21c", "val22c", "val23c"),
                ],
                "last_modified": "2023-06-05T03:54:07.000000Z",
            },
            "d.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11d", "val12d", "val13d"),
                    ("val21d", "val22d", "val23d"),
                ],
                "last_modified": "2023-06-05T03:54:07.000000Z",
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
                                "type": ["null", "string"]
                            },
                            "col2": {
                                "type": ["null", "string"]
                            },
                            "col3": {
                                "type": ["null", "string"]
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
            {
                "stream1": {
                    "history": {
                        "b.csv": "2023-06-05T03:54:07.000000Z",
                        "c.csv": "2023-06-05T03:54:07.000000Z",
                        "d.csv": "2023-06-05T03:54:07.000000Z",
                    },
                }
            }
        ]
    )
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[{
            "type": "STREAM",
            "stream": {
                "stream_state": {
                    "history": {
                        "b.csv": "2023-06-05T03:54:07.000000Z",
                        "c.csv": "2023-06-05T03:54:07.000000Z",
                        "d.csv": "2023-06-05T03:54:07.000000Z",
                    },
                },
                "stream_descriptor": {"name": "stream1"}
            }
        }
        ],
    ))).build()

multi_csv_sync_files_within_time_window_if_history_is_incomplete__different_timestamps_scenario = (
    TestScenarioBuilder()
    .set_name("multi_csv_sync_recent_files_if_history_is_incomplete__different_timestamps")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*.csv"],
                    "validation_policy": "emit_record_on_schema_mismatch",
                    "max_history_size": 3,
                    "days_to_sync_if_history_is_full": 3,
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
                "last_modified": "2023-06-05T03:54:07.000000Z",
            },
            "b.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11b", "val12b", "val13b"),
                    ("val21b", "val22b", "val23b"),
                ],
                "last_modified": "2023-06-06T03:54:07.000000Z",
            },
            "c.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11c", "val12c", "val13c"),
                    ("val21c", "val22c", "val23c"),
                ],
                "last_modified": "2023-06-07T03:54:07.000000Z",
            },
            "d.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11d", "val12d", "val13d"),
                    ("val21d", "val22d", "val23d"),
                ],
                "last_modified": "2023-06-08T03:54:07.000000Z",
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
                                "type": ["null", "string"]
                            },
                            "col2": {
                                "type": ["null", "string"]
                            },
                            "col3": {
                                "type": ["null", "string"]
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
            # {"col1": "val11a", "col2": "val12a"}, # This file is skipped because it is older than the time_window
            # {"col1": "val21a", "col2": "val22a"},
            {"col1": "val11b", "col2": "val12b", "col3": "val13b", "_ab_source_file_last_modified": "2023-06-06T03:54:07Z",
             "_ab_source_file_url": "b.csv"},
            {"col1": "val21b", "col2": "val22b", "col3": "val23b", "_ab_source_file_last_modified": "2023-06-06T03:54:07Z",
             "_ab_source_file_url": "b.csv"},
            {
                "stream1": {
                    "history": {
                        "c.csv": "2023-06-07T03:54:07.000000Z",
                        "d.csv": "2023-06-08T03:54:07.000000Z",
                        "e.csv": "2023-06-08T03:54:07.000000Z",
                    },
                }
            },
        ]
    )
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[{
            "type": "STREAM",
            "stream": {
                "stream_state": {
                    "history": {
                        "c.csv": "2023-06-07T03:54:07.000000Z",
                        "d.csv": "2023-06-08T03:54:07.000000Z",
                        "e.csv": "2023-06-08T03:54:07.000000Z",
                    },
                },
                "stream_descriptor": {"name": "stream1"}
            }
        }
        ],
    ))).build()

multi_csv_sync_files_within_history_time_window_if_history_is_incomplete_different_timestamps_scenario = (
    TestScenarioBuilder()
    .set_name("multi_csv_sync_files_within_history_time_window_if_history_is_incomplete_different_timestamps")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "csv",
                    "globs": ["*.csv"],
                    "validation_policy": "emit_record_on_schema_mismatch",
                    "max_history_size": 3,
                    "days_to_sync_if_history_is_full": 3,
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
                "last_modified": "2023-06-05T03:54:07.000000Z",
            },
            "b.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11b", "val12b", "val13b"),
                    ("val21b", "val22b", "val23b"),
                ],
                "last_modified": "2023-06-06T03:54:07.000000Z",
            },
            "c.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11c", "val12c", "val13c"),
                    ("val21c", "val22c", "val23c"),
                ],
                "last_modified": "2023-06-07T03:54:07.000000Z",
            },
            "d.csv": {
                "contents": [
                    ("col1", "col2", "col3"),
                    ("val11d", "val12d", "val13d"),
                    ("val21d", "val22d", "val23d"),
                ],
                "last_modified": "2023-06-08T03:54:07.000000Z",
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
                                "type": ["null", "string"]
                            },
                            "col2": {
                                "type": ["null", "string"]
                            },
                            "col3": {
                                "type": ["null", "string"]
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
            {"col1": "val11a", "col2": "val12a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
             "_ab_source_file_url": "a.csv"},
            {"col1": "val21a", "col2": "val22a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
             "_ab_source_file_url": "a.csv"},
            {
                "stream1": {
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z",
                        "c.csv": "2023-06-07T03:54:07.000000Z",
                        "d.csv": "2023-06-08T03:54:07.000000Z",
                    },
                }
            },
            {"col1": "val11b", "col2": "val12b", "col3": "val13b", "_ab_source_file_last_modified": "2023-06-06T03:54:07Z",
             "_ab_source_file_url": "b.csv"},
            {"col1": "val21b", "col2": "val22b", "col3": "val23b", "_ab_source_file_last_modified": "2023-06-06T03:54:07Z",
             "_ab_source_file_url": "b.csv"},
            {
                "stream1": {
                    "history": {
                        "b.csv": "2023-06-06T03:54:07.000000Z",
                        "c.csv": "2023-06-07T03:54:07.000000Z",
                        "d.csv": "2023-06-08T03:54:07.000000Z",
                    },
                }
            },
        ]
    )
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[{
            "type": "STREAM",
            "stream": {
                "stream_state": {
                    "history": {
                        "old_file.csv": "2023-06-05T00:00:00.000000Z",
                        "c.csv": "2023-06-07T03:54:07.000000Z",
                        "d.csv": "2023-06-08T03:54:07.000000Z",
                    },
                },
                "stream_descriptor": {"name": "stream1"}
            }
        }
        ],
    ))).build()
