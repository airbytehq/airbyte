#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.file_based.stream.concurrent.cursor import FileBasedConcurrentCursor
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.sources.file_based.helpers import LowHistoryLimitConcurrentCursor
from unit_tests.sources.file_based.scenarios.file_based_source_builder import FileBasedSourceBuilder
from unit_tests.sources.file_based.scenarios.scenario_builder import IncrementalScenarioConfig, TestScenarioBuilder

single_csv_input_state_is_earlier_scenario_concurrent = (
    TestScenarioBuilder()
    .set_name("single_csv_input_state_is_earlier_concurrent")
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
                        ("val11", "val12"),
                        ("val21", "val22"),
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                }
            }
        )
        .set_file_type("csv")
        .set_cursor_cls(FileBasedConcurrentCursor)
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=StateBuilder()
            .with_stream_state(
                "stream1",
                {
                    "history": {"some_old_file.csv": "2023-06-01T03:54:07.000000Z"},
                    "_ab_source_file_last_modified": "2023-06-01T03:54:07.000000Z_some_old_file.csv",
                },
            )
            .build(),
        )
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
            {
                "history": {"some_old_file.csv": "2023-06-01T03:54:07.000000Z", "a.csv": "2023-06-05T03:54:07.000000Z"},
                "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z_a.csv",
            },
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
                                "type": ["null", "string"],
                            },
                            "col2": {
                                "type": ["null", "string"],
                            },
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                }
            ]
        }
    )
).build()

single_csv_file_is_skipped_if_same_modified_at_as_in_history_concurrent = (
    TestScenarioBuilder()
    .set_name("single_csv_file_is_skipped_if_same_modified_at_as_in_history_concurrent")
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
                        ("val11", "val12"),
                        ("val21", "val22"),
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                }
            }
        )
        .set_file_type("csv")
        .set_cursor_cls(FileBasedConcurrentCursor)
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=StateBuilder()
            .with_stream_state(
                "stream1",
                {
                    "history": {"a.csv": "2023-06-05T03:54:07.000000Z"},
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z_a.csv",
                },
            )
            .build(),
        )
    )
    .set_expected_records(
        [
            {
                "history": {"a.csv": "2023-06-05T03:54:07.000000Z"},
                "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z_a.csv",
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
                                "type": ["null", "string"],
                            },
                            "col2": {
                                "type": ["null", "string"],
                            },
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                }
            ]
        }
    )
).build()

single_csv_file_is_synced_if_modified_at_is_more_recent_than_in_history_concurrent = (
    TestScenarioBuilder()
    .set_name("single_csv_file_is_synced_if_modified_at_is_more_recent_than_in_history_concurrent")
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
                        ("val11", "val12"),
                        ("val21", "val22"),
                    ],
                    "last_modified": "2023-06-05T03:54:07.000Z",
                }
            }
        )
        .set_file_type("csv")
        .set_cursor_cls(FileBasedConcurrentCursor)
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=StateBuilder()
            .with_stream_state(
                "stream1",
                {
                    "history": {"a.csv": "2023-06-01T03:54:07.000000Z"},
                    "_ab_source_file_last_modified": "2023-06-01T03:54:07.000000Z_a.csv",
                },
            )
            .build(),
        )
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
            {
                "history": {"a.csv": "2023-06-05T03:54:07.000000Z"},
                "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z_a.csv",
            },
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
                                "type": ["null", "string"],
                            },
                            "col2": {
                                "type": ["null", "string"],
                            },
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                }
            ]
        }
    )
).build()

single_csv_no_input_state_scenario_concurrent = (
    TestScenarioBuilder()
    .set_name("single_csv_input_state_is_earlier_again_concurrent")
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
                        ("val11", "val12"),
                        ("val21", "val22"),
                    ],
                    "last_modified": "2023-06-05T03:54:07.000000Z",
                }
            }
        )
        .set_file_type("csv")
        .set_cursor_cls(FileBasedConcurrentCursor)
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
                                "type": ["null", "string"],
                            },
                            "col2": {
                                "type": ["null", "string"],
                            },
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
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
            {
                "history": {"a.csv": "2023-06-05T03:54:07.000000Z"},
                "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z_a.csv",
            },
        ]
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=[],
        )
    )
).build()

multi_csv_same_timestamp_scenario_concurrent = (
    TestScenarioBuilder()
    .set_name("multi_csv_same_timestamp_concurrent")
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
        .set_cursor_cls(FileBasedConcurrentCursor)
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
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
            {
                "history": {"a.csv": "2023-06-05T03:54:07.000000Z", "b.csv": "2023-06-05T03:54:07.000000Z"},
                "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z_b.csv",
            },
        ]
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=[],
        )
    )
).build()

single_csv_input_state_is_later_scenario_concurrent = (
    TestScenarioBuilder()
    .set_name("single_csv_input_state_is_later_concurrent")
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
                        ("val11", "val12"),
                        ("val21", "val22"),
                    ],
                    "last_modified": "2023-06-05T03:54:07.000000Z",
                }
            }
        )
        .set_file_type("csv")
        .set_cursor_cls(FileBasedConcurrentCursor)
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
                                "type": ["null", "string"],
                            },
                            "col2": {
                                "type": ["null", "string"],
                            },
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
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
            {
                "history": {
                    "recent_file.csv": "2023-07-15T23:59:59.000000Z",
                    "a.csv": "2023-06-05T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-07-15T23:59:59.000000Z_recent_file.csv",
            },
        ]
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=StateBuilder()
            .with_stream_state(
                "stream1",
                {
                    "history": {"recent_file.csv": "2023-07-15T23:59:59.000000Z"},
                    "_ab_source_file_last_modified": "2023-07-15T23:59:59.000000Z_recent_file.csv",
                },
            )
            .build(),
        )
    )
).build()

multi_csv_different_timestamps_scenario_concurrent = (
    TestScenarioBuilder()
    .set_name("multi_csv_stream_different_timestamps_concurrent")
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
        .set_cursor_cls(FileBasedConcurrentCursor)
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
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
                    "_ab_source_file_last_modified": "2023-06-04T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21a",
                    "col2": "val22a",
                    "_ab_source_file_last_modified": "2023-06-04T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "history": {
                    "a.csv": "2023-06-04T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-04T03:54:07.000000Z_a.csv",
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
            {
                "history": {"a.csv": "2023-06-04T03:54:07.000000Z", "b.csv": "2023-06-05T03:54:07.000000Z"},
                "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z_b.csv",
            },
        ]
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=[],
        )
    )
).build()

multi_csv_per_timestamp_scenario_concurrent = (
    TestScenarioBuilder()
    .set_name("multi_csv_per_timestamp_concurrent")
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
        .set_cursor_cls(FileBasedConcurrentCursor)
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
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
            {
                "history": {"a.csv": "2023-06-05T03:54:07.000000Z", "b.csv": "2023-06-05T03:54:07.000000Z"},
                "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z_b.csv",
            },
            {
                "data": {
                    "col1": "val11c",
                    "col2": "val12c",
                    "col3": "val13c",
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "c.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21c",
                    "col2": "val22c",
                    "col3": "val23c",
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "c.csv",
                },
                "stream": "stream1",
            },
            {
                "history": {
                    "a.csv": "2023-06-05T03:54:07.000000Z",
                    "b.csv": "2023-06-05T03:54:07.000000Z",
                    "c.csv": "2023-06-06T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z_c.csv",
            },
        ]
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=[],
        )
    )
).build()

multi_csv_skip_file_if_already_in_history_concurrent = (
    TestScenarioBuilder()
    .set_name("skip_files_already_in_history_concurrent")
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
        .set_cursor_cls(FileBasedConcurrentCursor)
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
    .set_expected_records(
        [
            # {"data": {"col1": "val11a", "col2": "val12a"}, "stream": "stream1"}, # this file is skipped
            # {"data": {"col1": "val21a", "col2": "val22a"}, "stream": "stream1"}, # this file is skipped
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
            {
                "history": {"a.csv": "2023-06-05T03:54:07.000000Z", "b.csv": "2023-06-05T03:54:07.000000Z"},
                "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z_b.csv",
            },
            {
                "data": {
                    "col1": "val11c",
                    "col2": "val12c",
                    "col3": "val13c",
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "c.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21c",
                    "col2": "val22c",
                    "col3": "val23c",
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "c.csv",
                },
                "stream": "stream1",
            },
            {
                "history": {
                    "a.csv": "2023-06-05T03:54:07.000000Z",
                    "b.csv": "2023-06-05T03:54:07.000000Z",
                    "c.csv": "2023-06-06T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z_c.csv",
            },
        ]
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=StateBuilder()
            .with_stream_state(
                "stream1",
                {"history": {"a.csv": "2023-06-05T03:54:07.000000Z"}, "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z_a.csv"},
            )
            .build(),
        )
    )
).build()

multi_csv_include_missing_files_within_history_range_concurrent_cursor_is_newer = (
    TestScenarioBuilder()
    .set_name("multi_csv_include_missing_files_within_history_range_concurrent_cursor_is_newer")
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
        .set_cursor_cls(FileBasedConcurrentCursor)
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
    .set_expected_records(
        [
            # {"data": {"col1": "val11a", "col2": "val12a"}, "stream": "stream1"}, # this file is skipped
            # {"data": {"col1": "val21a", "col2": "val22a"}, "stream": "stream1"}, # this file is skipped
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
            # {"data": {"col1": "val11c", "col2": "val12c", "col3": "val13c"}, "stream": "stream1"}, # this file is skipped
            # {"data": {"col1": "val21c", "col2": "val22c", "col3": "val23c"}, "stream": "stream1"}, # this file is skipped
            {
                "history": {
                    "a.csv": "2023-06-05T03:54:07.000000Z",
                    "b.csv": "2023-06-05T03:54:07.000000Z",
                    "c.csv": "2023-06-06T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z_c.csv",
            },
        ]
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=StateBuilder()
            .with_stream_state(
                "stream1",
                {
                    "history": {"a.csv": "2023-06-05T03:54:07.000000Z", "c.csv": "2023-06-06T03:54:07.000000Z"},
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z_c.csv",
                },
            )
            .build(),
        )
    )
).build()

multi_csv_include_missing_files_within_history_range_concurrent_cursor_is_older = (
    TestScenarioBuilder()
    .set_name("multi_csv_include_missing_files_within_history_range_concurrent_cursor_is_older")
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
        .set_cursor_cls(FileBasedConcurrentCursor)
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
    .set_expected_records(
        [
            # {"data": {"col1": "val11a", "col2": "val12a"}, "stream": "stream1"}, # this file is skipped
            # {"data": {"col1": "val21a", "col2": "val22a"}, "stream": "stream1"}, # this file is skipped
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
            # {"data": {"col1": "val11c", "col2": "val12c", "col3": "val13c"}, "stream": "stream1"}, # this file is skipped
            # {"data": {"col1": "val21c", "col2": "val22c", "col3": "val23c"}, "stream": "stream1"}, # this file is skipped
            {
                "history": {
                    "a.csv": "2023-06-05T03:54:07.000000Z",
                    "b.csv": "2023-06-05T03:54:07.000000Z",
                    "c.csv": "2023-06-06T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z_c.csv",
            },
        ]
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=StateBuilder()
            .with_stream_state(
                "stream1",
                {
                    "history": {"a.csv": "2023-06-05T03:54:07.000000Z", "c.csv": "2023-06-06T03:54:07.000000Z"},
                    "_ab_source_file_last_modified": "2023-06-03T03:54:07.000000Z_x.csv",
                },
            )
            .build()
        )
    )
).build()

multi_csv_remove_old_files_if_history_is_full_scenario_concurrent_cursor_is_newer = (
    TestScenarioBuilder()
    .set_name("multi_csv_remove_old_files_if_history_is_full_scenario_concurrent_cursor_is_newer")
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
        .set_cursor_cls(LowHistoryLimitConcurrentCursor)
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
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
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21a",
                    "col2": "val22a",
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "history": {
                    "very_old_file.csv": "2023-06-02T03:54:07.000000Z",
                    "old_file_same_timestamp_as_a.csv": "2023-06-06T03:54:07.000000Z",
                    "a.csv": "2023-06-06T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z_old_file_same_timestamp_as_a.csv",
            },
            {
                "data": {
                    "col1": "val11b",
                    "col2": "val12b",
                    "col3": "val13b",
                    "_ab_source_file_last_modified": "2023-06-07T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21b",
                    "col2": "val22b",
                    "col3": "val23b",
                    "_ab_source_file_last_modified": "2023-06-07T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
            {
                "history": {
                    "old_file_same_timestamp_as_a.csv": "2023-06-06T03:54:07.000000Z",
                    "a.csv": "2023-06-06T03:54:07.000000Z",
                    "b.csv": "2023-06-07T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-07T03:54:07.000000Z_b.csv",
            },
            {
                "data": {
                    "col1": "val11c",
                    "col2": "val12c",
                    "col3": "val13c",
                    "_ab_source_file_last_modified": "2023-06-10T03:54:07.000000Z",
                    "_ab_source_file_url": "c.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21c",
                    "col2": "val22c",
                    "col3": "val23c",
                    "_ab_source_file_last_modified": "2023-06-10T03:54:07.000000Z",
                    "_ab_source_file_url": "c.csv",
                },
                "stream": "stream1",
            },
            {
                "history": {
                    "old_file_same_timestamp_as_a.csv": "2023-06-06T03:54:07.000000Z",
                    "b.csv": "2023-06-07T03:54:07.000000Z",
                    "c.csv": "2023-06-10T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-10T03:54:07.000000Z_c.csv",
            },
        ]
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=StateBuilder()
            .with_stream_state(
                "stream1",
                {
                    "history": {
                        "very_very_old_file.csv": "2023-06-01T03:54:07.000000Z",
                        "very_old_file.csv": "2023-06-02T03:54:07.000000Z",
                        "old_file_same_timestamp_as_a.csv": "2023-06-06T03:54:07.000000Z",
                    },
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z_old_file_same_timestamp_as_a.csv",
                },
            )
            .build(),
        )
    )
).build()

multi_csv_remove_old_files_if_history_is_full_scenario_concurrent_cursor_is_older = (
    TestScenarioBuilder()
    .set_name("multi_csv_remove_old_files_if_history_is_full_scenario_concurrent_cursor_is_older")
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
        .set_cursor_cls(LowHistoryLimitConcurrentCursor)
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
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
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21a",
                    "col2": "val22a",
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "history": {
                    "very_old_file.csv": "2023-06-02T03:54:07.000000Z",
                    "old_file_same_timestamp_as_a.csv": "2023-06-06T03:54:07.000000Z",
                    "a.csv": "2023-06-06T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z_old_file_same_timestamp_as_a.csv",
            },
            {
                "data": {
                    "col1": "val11b",
                    "col2": "val12b",
                    "col3": "val13b",
                    "_ab_source_file_last_modified": "2023-06-07T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21b",
                    "col2": "val22b",
                    "col3": "val23b",
                    "_ab_source_file_last_modified": "2023-06-07T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
            {
                "history": {
                    "old_file_same_timestamp_as_a.csv": "2023-06-06T03:54:07.000000Z",
                    "a.csv": "2023-06-06T03:54:07.000000Z",
                    "b.csv": "2023-06-07T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-07T03:54:07.000000Z_b.csv",
            },
            {
                "data": {
                    "col1": "val11c",
                    "col2": "val12c",
                    "col3": "val13c",
                    "_ab_source_file_last_modified": "2023-06-10T03:54:07.000000Z",
                    "_ab_source_file_url": "c.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21c",
                    "col2": "val22c",
                    "col3": "val23c",
                    "_ab_source_file_last_modified": "2023-06-10T03:54:07.000000Z",
                    "_ab_source_file_url": "c.csv",
                },
                "stream": "stream1",
            },
            {
                "history": {
                    "old_file_same_timestamp_as_a.csv": "2023-06-06T03:54:07.000000Z",
                    "b.csv": "2023-06-07T03:54:07.000000Z",
                    "c.csv": "2023-06-10T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-10T03:54:07.000000Z_c.csv",
            },
        ]
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=StateBuilder()
            .with_stream_state(
                "stream1",
                {
                    "history": {
                        "very_very_old_file.csv": "2023-06-01T03:54:07.000000Z",
                        "very_old_file.csv": "2023-06-02T03:54:07.000000Z",
                        "old_file_same_timestamp_as_a.csv": "2023-06-06T03:54:07.000000Z",
                    },
                    "_ab_source_file_last_modified": "2023-05-01T03:54:07.000000Z_very_very_very_old_file.csv",
                },
            )
            .build(),
        )
    )
).build()

multi_csv_same_timestamp_more_files_than_history_size_scenario_concurrent_cursor_is_newer = (
    TestScenarioBuilder()
    .set_name("multi_csv_same_timestamp_more_files_than_history_size_scenario_concurrent_cursor_is_newer")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*.csv"],
                    "validation_policy": "Emit Record",
                    "days_to_sync_if_history_is_full": 3,
                }
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
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
        .set_cursor_cls(LowHistoryLimitConcurrentCursor)
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
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
            {
                "data": {
                    "col1": "val11c",
                    "col2": "val12c",
                    "col3": "val13c",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "c.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21c",
                    "col2": "val22c",
                    "col3": "val23c",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "c.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val11d",
                    "col2": "val12d",
                    "col3": "val13d",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "d.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21d",
                    "col2": "val22d",
                    "col3": "val23d",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "d.csv",
                },
                "stream": "stream1",
            },
            {
                "history": {
                    "b.csv": "2023-06-05T03:54:07.000000Z",
                    "c.csv": "2023-06-05T03:54:07.000000Z",
                    "d.csv": "2023-06-05T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z_d.csv",
            },
        ]
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=[],
        )
    )
).build()

multi_csv_same_timestamp_more_files_than_history_size_scenario_concurrent_cursor_is_older = (
    TestScenarioBuilder()
    .set_name("multi_csv_same_timestamp_more_files_than_history_size_scenario_concurrent_cursor_is_older")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*.csv"],
                    "validation_policy": "Emit Record",
                    "days_to_sync_if_history_is_full": 3,
                }
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
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
        .set_cursor_cls(LowHistoryLimitConcurrentCursor)
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
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
            {
                "data": {
                    "col1": "val11c",
                    "col2": "val12c",
                    "col3": "val13c",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "c.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21c",
                    "col2": "val22c",
                    "col3": "val23c",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "c.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val11d",
                    "col2": "val12d",
                    "col3": "val13d",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "d.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21d",
                    "col2": "val22d",
                    "col3": "val23d",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "d.csv",
                },
                "stream": "stream1",
            },
            {
                "history": {
                    "b.csv": "2023-06-05T03:54:07.000000Z",
                    "c.csv": "2023-06-05T03:54:07.000000Z",
                    "d.csv": "2023-06-05T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z_d.csv",
            },
        ]
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=[],
        )
    )
).build()

multi_csv_sync_recent_files_if_history_is_incomplete_scenario_concurrent_cursor_is_older = (
    TestScenarioBuilder()
    .set_name("multi_csv_sync_recent_files_if_history_is_incomplete_scenario_concurrent_cursor_is_older")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*.csv"],
                    "validation_policy": "Emit Record",
                    "days_to_sync_if_history_is_full": 3,
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
        .set_cursor_cls(LowHistoryLimitConcurrentCursor)
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "history": {
                    "b.csv": "2023-06-05T03:54:07.000000Z",
                    "c.csv": "2023-06-05T03:54:07.000000Z",
                    "d.csv": "2023-06-05T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z_d.csv",
            }
        ]
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=StateBuilder()
            .with_stream_state(
                "stream1",
                {
                    "history": {
                        "b.csv": "2023-06-05T03:54:07.000000Z",
                        "c.csv": "2023-06-05T03:54:07.000000Z",
                        "d.csv": "2023-06-05T03:54:07.000000Z",
                    },
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z_b.csv",
                },
            )
            .build(),
        )
    )
).build()

multi_csv_sync_recent_files_if_history_is_incomplete_scenario_concurrent_cursor_is_newer = (
    TestScenarioBuilder()
    .set_name("multi_csv_sync_recent_files_if_history_is_incomplete_scenario_concurrent_cursor_is_newer")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*.csv"],
                    "validation_policy": "Emit Record",
                    "days_to_sync_if_history_is_full": 3,
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
        .set_cursor_cls(LowHistoryLimitConcurrentCursor)
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                    "history": {
                        "b.csv": "2023-06-05T03:54:07.000000Z",
                        "c.csv": "2023-06-05T03:54:07.000000Z",
                        "d.csv": "2023-06-05T03:54:07.000000Z",
                    },
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z_d.csv",
            }
        ]
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=StateBuilder()
            .with_stream_state(
                "stream1",
                {
                    "history": {
                        "b.csv": "2023-06-05T03:54:07.000000Z",
                        "c.csv": "2023-06-05T03:54:07.000000Z",
                        "d.csv": "2023-06-05T03:54:07.000000Z",
                    },
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z_d.csv",
                },
            )
            .build(),
        )
    )
).build()


multi_csv_sync_files_within_time_window_if_history_is_incomplete__different_timestamps_scenario_concurrent_cursor_is_older = (
    TestScenarioBuilder()
    .set_name("multi_csv_sync_files_within_time_window_if_history_is_incomplete__different_timestamps_scenario_concurrent_cursor_is_older")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*.csv"],
                    "validation_policy": "Emit Record",
                    "days_to_sync_if_history_is_full": 3,
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
        .set_cursor_cls(LowHistoryLimitConcurrentCursor)
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
    .set_expected_records(
        [
            # {"data": {"col1": "val11a", "col2": "val12a"}, "stream": "stream1"}, # This file is skipped because it is older than the time_window
            # {"data": {"col1": "val21a", "col2": "val22a"}, "stream": "stream1"},
            {
                "data": {
                    "col1": "val11b",
                    "col2": "val12b",
                    "col3": "val13b",
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21b",
                    "col2": "val22b",
                    "col3": "val23b",
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
            {
                "history": {
                    "c.csv": "2023-06-07T03:54:07.000000Z",
                    "d.csv": "2023-06-08T03:54:07.000000Z",
                    "e.csv": "2023-06-08T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-08T03:54:07.000000Z_e.csv",
            },
        ]
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=StateBuilder()
            .with_stream_state(
                "stream1",
                {
                    "history": {
                        "c.csv": "2023-06-07T03:54:07.000000Z",
                        "d.csv": "2023-06-08T03:54:07.000000Z",
                        "e.csv": "2023-06-08T03:54:07.000000Z",
                    },
                    "_ab_source_file_last_modified": "2023-06-08T03:54:07.000000Z_e.csv",
                },
            )
            .build(),
        )
    )
).build()

multi_csv_sync_files_within_time_window_if_history_is_incomplete__different_timestamps_scenario_concurrent_cursor_is_newer = (
    TestScenarioBuilder()
    .set_name("multi_csv_sync_files_within_time_window_if_history_is_incomplete__different_timestamps_scenario_concurrent_cursor_is_newer")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*.csv"],
                    "validation_policy": "Emit Record",
                    "days_to_sync_if_history_is_full": 3,
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
        .set_cursor_cls(LowHistoryLimitConcurrentCursor)
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
                }
            ]
        }
    )
    .set_expected_records(
        [
            # {"data": {"col1": "val11a", "col2": "val12a"}, "stream": "stream1"}, # This file is skipped because it is older than the time_window
            # {"data": {"col1": "val21a", "col2": "val22a"}, "stream": "stream1"},
            {
                "data": {
                    "col1": "val11b",
                    "col2": "val12b",
                    "col3": "val13b",
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21b",
                    "col2": "val22b",
                    "col3": "val23b",
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
            {
                "history": {
                    "c.csv": "2023-06-07T03:54:07.000000Z",
                    "d.csv": "2023-06-08T03:54:07.000000Z",
                    "e.csv": "2023-06-08T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-08T03:54:07.000000Z_e.csv",
            },
        ]
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=StateBuilder()
            .with_stream_state(
                "stream1",
                {
                    "history": {
                        "c.csv": "2023-06-07T03:54:07.000000Z",
                        "d.csv": "2023-06-08T03:54:07.000000Z",
                        "e.csv": "2023-06-08T03:54:07.000000Z",
                    },
                    "_ab_source_file_last_modified": "2023-06-08T03:54:07.000000Z_e.csv",
                },
            )
            .build(),
        )
    )
).build()

multi_csv_sync_files_within_history_time_window_if_history_is_incomplete_different_timestamps_scenario_concurrent_cursor_is_newer = (
    TestScenarioBuilder()
    .set_name(
        "multi_csv_sync_files_within_history_time_window_if_history_is_incomplete_different_timestamps_scenario_concurrent_cursor_is_newer"
    )
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*.csv"],
                    "validation_policy": "Emit Record",
                    "days_to_sync_if_history_is_full": 3,
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
        .set_cursor_cls(LowHistoryLimitConcurrentCursor)
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
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
                "history": {
                    "a.csv": "2023-06-05T03:54:07.000000Z",
                    "c.csv": "2023-06-07T03:54:07.000000Z",
                    "d.csv": "2023-06-08T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-08T03:54:07.000000Z_d.csv",
            },
            {
                "data": {
                    "col1": "val11b",
                    "col2": "val12b",
                    "col3": "val13b",
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21b",
                    "col2": "val22b",
                    "col3": "val23b",
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
            {
                "history": {
                    "b.csv": "2023-06-06T03:54:07.000000Z",
                    "c.csv": "2023-06-07T03:54:07.000000Z",
                    "d.csv": "2023-06-08T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-08T03:54:07.000000Z_d.csv",
            },
        ]
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=StateBuilder()
            .with_stream_state(
                "stream1",
                {
                    "history": {
                        "old_file.csv": "2023-06-05T00:00:00.000000Z",
                        "c.csv": "2023-06-07T03:54:07.000000Z",
                        "d.csv": "2023-06-08T03:54:07.000000Z",
                    },
                    "_ab_source_file_last_modified": "2023-06-08T03:54:07.000000Z_d.csv",
                },
            )
            .build(),
        )
    )
).build()

multi_csv_sync_files_within_history_time_window_if_history_is_incomplete_different_timestamps_scenario_concurrent_cursor_is_older = (
    TestScenarioBuilder()
    .set_name(
        "multi_csv_sync_files_within_history_time_window_if_history_is_incomplete_different_timestamps_scenario_concurrent_cursor_is_older"
    )
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*.csv"],
                    "validation_policy": "Emit Record",
                    "days_to_sync_if_history_is_full": 3,
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
        .set_cursor_cls(LowHistoryLimitConcurrentCursor)
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
                    "supported_sync_modes": ["full_refresh", "incremental"],
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
                "history": {
                    "a.csv": "2023-06-05T03:54:07.000000Z",
                    "c.csv": "2023-06-07T03:54:07.000000Z",
                    "d.csv": "2023-06-08T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-08T03:54:07.000000Z_d.csv",
            },
            {
                "data": {
                    "col1": "val11b",
                    "col2": "val12b",
                    "col3": "val13b",
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21b",
                    "col2": "val22b",
                    "col3": "val23b",
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
            {
                "history": {
                    "b.csv": "2023-06-06T03:54:07.000000Z",
                    "c.csv": "2023-06-07T03:54:07.000000Z",
                    "d.csv": "2023-06-08T03:54:07.000000Z",
                },
                "_ab_source_file_last_modified": "2023-06-08T03:54:07.000000Z_d.csv",
            },
        ]
    )
    .set_incremental_scenario_config(
        IncrementalScenarioConfig(
            input_state=StateBuilder()
            .with_stream_state(
                "stream1",
                {
                    "history": {
                        "old_file.csv": "2023-06-05T00:00:00.000000Z",
                        "c.csv": "2023-06-07T03:54:07.000000Z",
                        "d.csv": "2023-06-08T03:54:07.000000Z",
                    },
                    "_ab_source_file_last_modified": "2023-06-04T00:00:00.000000Z_very_old_file.csv",
                },
            )
            .build(),
        )
    )
).build()
