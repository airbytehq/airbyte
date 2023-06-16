from unit_tests.sources.file_based.scenarios._scenario_builder import TestScenarioBuilder, FileBasedStreamState, IncrementalScenarioConfig

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
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "json_schema": {"col1": "string", "col2": "string"},
                    "name": "stream1",
                }
            ]
        }
    )
    .set_expected_records(
        [
            {"col1": "val11", "col2": "val12"},
            {"col1": "val21", "col2": "val22"},
            {
                "stream1": {
                    "cursor_value": "2023-06-05T03:54:07.000000Z",
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z"
                    }
                }
            }
        ]
    )
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[FileBasedStreamState(mapping={
            "type": "STREAM",
            "stream": {
                "stream_state": {
                    "cursor_value": "2020-01-01T01:51:01.000000Z",
                    "history": {}
                },
                "stream_descriptor": {"name": "stream1"}
            }
        }
        )],
    ))).build()

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
                    "json_schema": {"col1": "string", "col2": "string"},
                    "name": "stream1",
                }
            ]
        }
    )
    .set_expected_records(
        [
            {"col1": "val11", "col2": "val12"},
            {"col1": "val21", "col2": "val22"},
            {
                "stream1": {
                    "cursor_value": "2023-06-05T03:54:07.000000Z",
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z"
                    }
                }
            }
        ]
    )
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[],
    ))).build()

multi_csv_same_timestamp_scenario = (
    TestScenarioBuilder()
    .set_name("multi_csv_stream_no_input_state")
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
                        "col1": "string",
                        "col2": "string",
                        "col3": "string",
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
            {"col1": "val11a", "col2": "val12a"},
            {"col1": "val21a", "col2": "val22a"},
            {"col1": "val11b", "col2": "val12b", "col3": "val13b"},
            {"col1": "val21b", "col2": "val22b", "col3": "val23b"},
            {
                "stream1": {
                    "cursor_value": "2023-06-05T03:54:07.000000Z",
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z",
                        "b.csv": "2023-06-05T03:54:07.000000Z"
                    }
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
                    "json_schema": {"col1": "string", "col2": "string"},
                    "name": "stream1",
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "stream1": {
                    "cursor_value": "2023-07-15T23:59:59.000000Z",
                    "history": {
                        "recent_file.csv": "2023-07-23:59:59.000000Z"
                    }
                }
            }
        ]
    )
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[FileBasedStreamState(mapping={
            "type": "STREAM",
            "stream": {
                "stream_state": {
                    "cursor_value": "2023-07-15T23:59:59.000000Z",
                    "history": {
                        "recent_file.csv": "2023-07-23:59:59.000000Z"
                    }
                },
                "stream_descriptor": {"name": "stream1"}
            }
        }
        )],
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
                        "col1": "string",
                        "col2": "string",
                        "col3": "string",
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
            {"col1": "val11a", "col2": "val12a"},
            {"col1": "val21a", "col2": "val22a"},
            {
                "stream1": {
                    "cursor_value": "2023-06-04T03:54:07.000000Z",
                    "history": {
                        "a.csv": "2023-06-04T03:54:07.000000Z",
                    }
                }
            },
            {"col1": "val11b", "col2": "val12b", "col3": "val13b"},
            {"col1": "val21b", "col2": "val22b", "col3": "val23b"},
            {
                "stream1": {
                    "cursor_value": "2023-06-05T03:54:07.000000Z",
                    "history": {
                        "a.csv": "2023-06-04T03:54:07.000000Z",
                        "b.csv": "2023-06-05T03:54:07.000000Z"
                    }
                }
            }
        ]
    )
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[],
    ))).build()

mulit_csv_per_timestamp_scenario = (
    TestScenarioBuilder()
    .set_name("mulit_csv_per_timestamp_scenario")
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
                        "col1": "string",
                        "col2": "string",
                        "col3": "string",
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
            {"col1": "val11a", "col2": "val12a"},
            {"col1": "val21a", "col2": "val22a"},
            {"col1": "val11b", "col2": "val12b", "col3": "val13b"},
            {"col1": "val21b", "col2": "val22b", "col3": "val23b"},
            {
                "stream1": {
                    "cursor_value": "2023-06-05T03:54:07.000000Z",
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z",
                        "b.csv": "2023-06-05T03:54:07.000000Z"
                    }
                }
            },
            {"col1": "val11c", "col2": "val12c", "col3": "val13c"},
            {"col1": "val21c", "col2": "val22c", "col3": "val23c"},
            {
                "stream1": {
                    "cursor_value": "2023-06-06T03:54:07.000000Z",
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z",
                        "b.csv": "2023-06-05T03:54:07.000000Z",
                        "c.csv": "2023-06-06T03:54:07.000000Z"
                    }
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
                        "col1": "string",
                        "col2": "string",
                        "col3": "string",
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
            {"col1": "val11b", "col2": "val12b", "col3": "val13b"},
            {"col1": "val21b", "col2": "val22b", "col3": "val23b"},
            {
                "stream1": {
                    "cursor_value": "2023-06-05T03:54:07.000000Z",
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z",
                        "b.csv": "2023-06-05T03:54:07.000000Z"
                    }
                }
            },
            {"col1": "val11c", "col2": "val12c", "col3": "val13c"},
            {"col1": "val21c", "col2": "val22c", "col3": "val23c"},
            {
                "stream1": {
                    "cursor_value": "2023-06-06T03:54:07.000000Z",
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000000Z",
                        "b.csv": "2023-06-05T03:54:07.000000Z",
                        "c.csv": "2023-06-06T03:54:07.000000Z"
                    }
                }
            },
        ]
    )
    .set_incremental_scenario_config(IncrementalScenarioConfig(
        input_state=[FileBasedStreamState(mapping={
            "type": "STREAM",
            "stream": {
                "stream_state": {
                    "cursor_value": "2023-06-05T03:54:07.000000Z",
                    "history": {"a.csv": "2023-06-05T03:54:07.000000Z"}
                },
                "stream_descriptor": {"name": "stream1"}
            }
        }
        )],
    ))).build()
