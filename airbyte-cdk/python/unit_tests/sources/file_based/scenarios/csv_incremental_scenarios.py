from typing import Any, Mapping, List

from airbyte_cdk.sources.file_based.exceptions import RecordParseError, SchemaInferenceError
from airbyte_cdk.sources.file_based.remote_file import FileType
from unit_tests.sources.file_based.helpers import LowInferenceLimitDiscoveryPolicy
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
    .set_file_type(FileType.Csv)
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
                    "history": {
                        "a.csv": "2023-06-05T03:54:07.000Z"
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
                    "history": {}
                },
                "stream_descriptor": {"name": "stream1"}
            }
        }
        )],
    ))).build()
