#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenarioBuilder

_base_single_stream_scenario = (
    TestScenarioBuilder()
    .set_files(
        {
            "a.csv": {
                "contents": [
                    ("col1", "col2"),
                    ("val_a_11", "1"),
                    ("val_a_12", "2"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b.csv": {  # The records in this file do not conform to the schema
                "contents": [
                    ("col1", "col2"),
                    ("val_b_11", "this is text that will trigger validation policy"),
                    ("val_b_12", "2"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "c.csv": {
                "contents": [
                    ("col1",),
                    ("val_c_11",),
                    ("val_c_12", "val_c_22"),  # This record is not parsable
                    ("val_c_13",),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "d.csv": {
                "contents": [
                    ("col1",),
                    ("val_d_11",),
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
                }
            ]
        }
    )
)


_base_multi_stream_scenario = (
    TestScenarioBuilder()
    .set_files(
        {
            "a/a1.csv": {
                "contents": [
                    ("col1", "col2"),
                    ("val_aa1_11", "1"),
                    ("val_aa1_12", "2"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "a/a2.csv": {
                "contents": [
                    ("col1", "col2"),
                    ("val_aa2_11", "this is text that will trigger validation policy"),
                    ("val_aa2_12", "2"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "a/a3.csv": {
                "contents": [
                    ("col1",),
                    ("val_aa3_11",),
                    ("val_aa3_12", "val_aa3_22"),  # This record is not parsable
                    ("val_aa3_13",),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "a/a4.csv": {
                "contents": [
                    ("col1",),
                    ("val_aa4_11",),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b/b1.csv": {  # The records in this file do not conform to the schema
                "contents": [
                    ("col1", "col2"),
                    ("val_bb1_11", "1"),
                    ("val_bb1_12", "2"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b/b2.csv": {
                "contents": [
                    ("col1", "col2"),
                    ("val_bb2_11", "this is text that will trigger validation policy"),
                    ("val_bb2_12", "2"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            },
            "b/b3.csv": {
                "contents": [
                    ("col1",),
                    ("val_bb3_11",),
                    ("val_bb3_12",),
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
                },
                {
                    "json_schema": {
                        "default_cursor_field": ["_ab_source_file_last_modified"],
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
                    "name": "stream2",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                },
            ]
        }
    )
)


skip_record_scenario_single_stream = (
    _base_single_stream_scenario.copy()
    .set_name("skip_record_scenario_single_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*.csv"],
                    "validation_policy": "Skip Record",
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val_a_11",
                    "col2": 1,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val_a_12",
                    "col2": 2,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            # {"data": {"col1": "val_b_11", "col2": "this is text that will trigger validation policy", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "b.csv"}, "stream": "stream1"},  # This record is skipped because it does not conform
            {
                "data": {
                    "col1": "val_b_12",
                    "col2": 2,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val_c_11",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "c.csv",
                },
                "stream": "stream1",
            },
            # {"data": {"col1": "val_c_12", None: "val_c_22", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "c.csv"}, "stream": "stream1"},  # This record is malformed so should not be emitted
            # {"data": {"col1": "val_c_13", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "c.csv"}, "stream": "stream1"},  # Skipped since previous record is malformed
            {
                "data": {
                    "col1": "val_d_11",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "d.csv",
                },
                "stream": "stream1",
            },
        ]
    )
    .set_expected_logs(
        {
            "read": [
                {
                    "level": "WARN",
                    "message": "Records in file did not pass validation policy. stream=stream1 file=b.csv n_skipped=1 validation_policy=skip_record",
                },
                {
                    "level": "ERROR",
                    "message": "Error parsing record. This could be due to a mismatch between the config's file type and the actual file type, or because the file or record is not parseable. stream=stream1 file=c.csv line_no=2 n_skipped=0",
                },
                {
                    "level": "WARN",
                    "message": "Could not cast the value to the expected type.: col2: value=this is text that will trigger validation policy,expected_type=integer",
                },
            ]
        }
    )
).build()


skip_record_scenario_multi_stream = (
    _base_multi_stream_scenario.copy()
    .set_name("skip_record_scenario_multi_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["a/*.csv"],
                    "validation_policy": "Skip Record",
                },
                {
                    "name": "stream2",
                    "format": {"filetype": "csv"},
                    "globs": ["b/*.csv"],
                    "validation_policy": "Skip Record",
                },
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val_aa1_11",
                    "col2": 1,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a/a1.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val_aa1_12",
                    "col2": 2,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a/a1.csv",
                },
                "stream": "stream1",
            },
            # {"data": {"col1": "val_aa2_11", "col2": "this is text that will trigger validation policy", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "a/a2.csv"}, "stream": "stream1"},  # This record is skipped because it does not conform
            {
                "data": {
                    "col1": "val_aa2_12",
                    "col2": 2,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a/a2.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val_aa3_11",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a/a3.csv",
                },
                "stream": "stream1",
            },
            # {"data": {"col1": "val_aa3_12", None: "val_aa3_22", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "a/a3.csv"}, "stream": "stream1"},  # This record is malformed so should not be emitted
            # {"data": {"col1": "val_aa3_13", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "a/a3.csv"}, "stream": "stream1"},  # Skipped since previous record is malformed
            {
                "data": {
                    "col1": "val_aa4_11",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a/a4.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val_bb1_11",
                    "col2": 1,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b/b1.csv",
                },
                "stream": "stream2",
            },
            {
                "data": {
                    "col1": "val_bb1_12",
                    "col2": 2,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b/b1.csv",
                },
                "stream": "stream2",
            },
            # {"data": {"col1": "val_bb2_11", "col2": "val_bb2_21", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "b/b2.csv"}, "stream": "stream2"},  # This record is skipped because it does not conform
            {
                "data": {
                    "col1": "val_bb2_12",
                    "col2": 2,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b/b2.csv",
                },
                "stream": "stream2",
            },
            {
                "data": {
                    "col1": "val_bb3_11",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b/b3.csv",
                },
                "stream": "stream2",
            },
            {
                "data": {
                    "col1": "val_bb3_12",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b/b3.csv",
                },
                "stream": "stream2",
            },
        ]
    )
    .set_expected_logs(
        {
            "read": [
                {
                    "level": "WARN",
                    "message": "Records in file did not pass validation policy. stream=stream1 file=a/a2.csv n_skipped=1 validation_policy=skip_record",
                },
                {
                    "level": "ERROR",
                    "message": "Error parsing record. This could be due to a mismatch between the config's file type and the actual file type, or because the file or record is not parseable. stream=stream1 file=a/a3.csv line_no=2 n_skipped=0",
                },
                {
                    "level": "WARN",
                    "message": "Records in file did not pass validation policy. stream=stream2 file=b/b2.csv n_skipped=1 validation_policy=skip_record",
                },
                {
                    "level": "WARN",
                    "message": "Could not cast the value to the expected type.: col2: value=this is text that will trigger validation policy,expected_type=integer",
                },
                {
                    "level": "WARN",
                    "message": "Could not cast the value to the expected type.: col2: value=this is text that will trigger validation policy,expected_type=integer",
                },
            ]
        }
    )
).build()


emit_record_scenario_single_stream = (
    _base_single_stream_scenario.copy()
    .set_name("emit_record_scenario_single_stream")
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
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val_a_11",
                    "col2": 1,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val_a_12",
                    "col2": 2,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val_b_11",
                    "col2": "this is text that will trigger validation policy",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },  # This record is skipped because it does not conform
            {
                "data": {
                    "col1": "val_b_12",
                    "col2": 2,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val_c_11",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "c.csv",
                },
                "stream": "stream1",
            },
            # {"data": {"col1": "val_c_12", None: "val_c_22", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "c.csv"}, "stream": "stream1"},  # This record is malformed so should not be emitted
            # {"data": {"col1": "val_c_13", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "c.csv"}, "stream": "stream1"},  # No more records from this stream are emitted after we hit a parse error
            {
                "data": {
                    "col1": "val_d_11",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "d.csv",
                },
                "stream": "stream1",
            },
        ]
    )
    .set_expected_logs(
        {
            "read": [
                {
                    "level": "ERROR",
                    "message": f"{FileBasedSourceError.ERROR_PARSING_RECORD.value} stream=stream1 file=c.csv line_no=2 n_skipped=0",
                },
                {
                    "level": "WARN",
                    "message": "Could not cast the value to the expected type.: col2: value=this is text that will trigger validation policy,expected_type=integer",
                },
            ]
        }
    )
).build()


emit_record_scenario_multi_stream = (
    _base_multi_stream_scenario.copy()
    .set_name("emit_record_scenario_multi_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["a/*.csv"],
                    "validation_policy": "Emit Record",
                },
                {
                    "name": "stream2",
                    "format": {"filetype": "csv"},
                    "globs": ["b/*.csv"],
                    "validation_policy": "Emit Record",
                },
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val_aa1_11",
                    "col2": 1,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a/a1.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val_aa1_12",
                    "col2": 2,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a/a1.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val_aa2_11",
                    "col2": "this is text that will trigger validation policy",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a/a2.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val_aa2_12",
                    "col2": 2,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a/a2.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val_aa3_11",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a/a3.csv",
                },
                "stream": "stream1",
            },
            # {"data": {"col1": "val_aa3_12", None: "val_aa3_22", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "a/a3.csv"}, "stream": "stream1"},  # This record is malformed so should not be emitted
            # {"data": {"col1": "val_aa3_13", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "a/a3.csv"}, "stream": "stream1"},  # Skipped since previous record is malformed
            {
                "data": {
                    "col1": "val_aa4_11",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a/a4.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val_bb1_11",
                    "col2": 1,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b/b1.csv",
                },
                "stream": "stream2",
            },
            {
                "data": {
                    "col1": "val_bb1_12",
                    "col2": 2,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b/b1.csv",
                },
                "stream": "stream2",
            },
            {
                "data": {
                    "col1": "val_bb2_11",
                    "col2": "this is text that will trigger validation policy",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b/b2.csv",
                },
                "stream": "stream2",
            },
            {
                "data": {
                    "col1": "val_bb2_12",
                    "col2": 2,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b/b2.csv",
                },
                "stream": "stream2",
            },
            {
                "data": {
                    "col1": "val_bb3_11",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b/b3.csv",
                },
                "stream": "stream2",
            },
            {
                "data": {
                    "col1": "val_bb3_12",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b/b3.csv",
                },
                "stream": "stream2",
            },
        ]
    )
    .set_expected_logs(
        {
            "read": [
                {
                    "level": "ERROR",
                    "message": f"{FileBasedSourceError.ERROR_PARSING_RECORD.value} stream=stream1 file=a/a3.csv line_no=2 n_skipped=0",
                },
                {
                    "level": "WARN",
                    "message": "Could not cast the value to the expected type.: col2: value=this is text that will trigger validation policy,expected_type=integer",
                },
                {
                    "level": "WARN",
                    "message": "Could not cast the value to the expected type.: col2: value=this is text that will trigger validation policy,expected_type=integer",
                },
            ]
        }
    )
).build()


wait_for_rediscovery_scenario_single_stream = (
    _base_single_stream_scenario.copy()
    .set_name("wait_for_rediscovery_scenario_single_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*.csv"],
                    "validation_policy": "Wait for Discover",
                }
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val_a_11",
                    "col2": 1,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val_a_12",
                    "col2": 2,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.csv",
                },
                "stream": "stream1",
            },
            # No records past that because the first record for the second file did not conform to the schema
        ]
    )
    .set_expected_logs(
        {
            "read": [
                {
                    "level": "WARN",
                    "message": "Stopping sync in accordance with the configured validation policy. Records in file did not conform to the schema. stream=stream1 file=b.csv validation_policy=Wait for Discover n_skipped=0",
                },
                {
                    "level": "WARN",
                    "message": "Could not cast the value to the expected type.: col2: value=this is text that will trigger validation policy,expected_type=integer",
                },
            ]
        }
    )
).build()


wait_for_rediscovery_scenario_multi_stream = (
    _base_multi_stream_scenario.copy()
    .set_name("wait_for_rediscovery_scenario_multi_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["a/*.csv"],
                    "validation_policy": "Wait for Discover",
                },
                {
                    "name": "stream2",
                    "format": {"filetype": "csv"},
                    "globs": ["b/*.csv"],
                    "validation_policy": "Wait for Discover",
                },
            ]
        }
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val_aa1_11",
                    "col2": 1,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a/a1.csv",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val_aa1_12",
                    "col2": 2,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a/a1.csv",
                },
                "stream": "stream1",
            },
            # {"data": {"col1": "val_aa2_11", "col2": "this is text that will trigger validation policy", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "a/a2.csv"}, "stream": "stream1"},
            # {"data": {"col1": "val_aa2_12", "col2": 2, "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "a/a2.csv"}, "stream": "stream1"},
            # {"data": {"col1": "val_aa3_11", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "a/a3.csv"}, "stream": "stream1"},
            # {"data": {"col1": "val_aa3_12", None: "val_aa3_22", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "a/a3.csv"}, "stream": "stream1"},
            # {"data": {"col1": "val_aa3_13", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "a/a3.csv"}, "stream": "stream1"},
            # {"data": {"col1": "val_aa4_11", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "a/a4.csv"}, "stream": "stream1"},
            {
                "data": {
                    "col1": "val_bb1_11",
                    "col2": 1,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b/b1.csv",
                },
                "stream": "stream2",
            },
            {
                "data": {
                    "col1": "val_bb1_12",
                    "col2": 2,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "b/b1.csv",
                },
                "stream": "stream2",
            },
            # {"data": {"col1": "val_bb2_11", "col2": "this is text that will trigger validation policy", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "b/b2.csv"}, "stream": "stream2"},
            # {"data": {"col1": "val_bb2_12", "col2": 2, "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "b/b2.csv"}, "stream": "stream2"},
            # {"data": {"col1": "val_bb3_11", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "b/b3.csv"}, "stream": "stream2"},
            # {"data": {"col1": "val_bb3_12", "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z", "_ab_source_file_url": "b/b3.csv"}, "stream": "stream2"},
        ]
    )
    .set_expected_logs(
        {
            "read": [
                {
                    "level": "WARN",
                    "message": "Stopping sync in accordance with the configured validation policy. Records in file did not conform to the schema. stream=stream1 file=a/a2.csv validation_policy=Wait for Discover n_skipped=0",
                },
                {
                    "level": "WARN",
                    "message": "Stopping sync in accordance with the configured validation policy. Records in file did not conform to the schema. stream=stream2 file=b/b2.csv validation_policy=Wait for Discover n_skipped=0",
                },
                {
                    "level": "WARN",
                    "message": "Could not cast the value to the expected type.: col2: value=this is text that will trigger validation policy,expected_type=integer",
                },
                {
                    "level": "WARN",
                    "message": "Could not cast the value to the expected type.: col2: value=this is text that will trigger validation policy,expected_type=integer",
                },
            ]
        }
    )
).build()
