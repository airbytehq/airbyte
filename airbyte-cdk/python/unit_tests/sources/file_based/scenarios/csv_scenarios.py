#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.file_based.discovery_policy import DefaultDiscoveryPolicy
from airbyte_cdk.sources.file_based.remote_file import FileType
from unit_tests.sources.file_based.scenarios._scenario_builder import TestScenarioBuilder

single_csv_scenario = (
    TestScenarioBuilder()
    .set_name("single_csv_stream")
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
                    "json_schema": {"col1": "string", "col2": "string"},
                    "name": "stream1",
                    "supported_sync_modes": ["full_refresh"],
                }
            ]
        }
    )
    .set_expected_records(
        [
            {"col1": "val11", "col2": "val12"},
            {"col1": "val21", "col2": "val22"},
        ]
    )
    .set_discovery_policy(DefaultDiscoveryPolicy())
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
    .set_file_type(FileType.Csv)
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "col1": "string",
                        "col2": "string",
                        "col3": "string",
                    },
                    "name": "stream1",
                    "supported_sync_modes": ["full_refresh"],
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
        ]
    )
    .set_discovery_policy(DefaultDiscoveryPolicy())
).build()


class LowInferenceLimitDiscoveryPolicy(DefaultDiscoveryPolicy):
    @property
    def max_n_files_for_schema_inference(self):
        return 1


multi_csv_stream_n_file_exceeds_limit_for_inference = (
    TestScenarioBuilder()
    .set_name("multi_csv_stream_n_file_exceeds_limit")
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
    .set_file_type(FileType.Csv)
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {"col1": "string", "col2": "string"},
                    "name": "stream1",
                    "supported_sync_modes": ["full_refresh"],
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
        ]
    )
    .set_discovery_policy(LowInferenceLimitDiscoveryPolicy())
).build()
