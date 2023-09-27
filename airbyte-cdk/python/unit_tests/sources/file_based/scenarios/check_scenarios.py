#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError
from unit_tests.sources.file_based.helpers import (
    FailingSchemaValidationPolicy,
    TestErrorListMatchingFilesInMemoryFilesStreamReader,
    TestErrorOpenFileInMemoryFilesStreamReader,
)
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenarioBuilder

_base_success_scenario = (
    TestScenarioBuilder()
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
    .set_expected_check_status("SUCCEEDED")
)


success_csv_scenario = (
    _base_success_scenario.copy()
    .set_name("success_csv_scenario")
).build()


success_multi_stream_scenario = (
    _base_success_scenario.copy()
    .set_name("success_multi_stream_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*.csv", "*.gz"],
                    "validation_policy": "Emit Record",
                },
                {
                    "name": "stream2",
                    "format": {"filetype": "csv"},
                    "globs": ["*.csv", "*.gz"],
                    "validation_policy": "Emit Record",
                }
            ]
        }
    )
).build()


success_extensionless_scenario = (
    _base_success_scenario.copy()
    .set_name("success_extensionless_file_scenario")
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
    .set_files(
        {
            "a": {
                "contents": [
                    ("col1", "col2"),
                    ("val11", "val12"),
                    ("val21", "val22"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            }
        }
    )
).build()


success_user_provided_schema_scenario = (
    _base_success_scenario.copy()
    .set_name("success_user_provided_schema_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*.csv"],
                    "validation_policy": "Emit Record",
                    "input_schema": '{"col1": "string", "col2": "string"}',
                }
            ],
        }
    )
).build()


_base_failure_scenario = (
    _base_success_scenario.copy()
    .set_expected_check_status("FAILED")
)


error_empty_stream_scenario = (
    _base_failure_scenario.copy()
    .set_name("error_empty_stream_scenario")
    .set_files({})
    .set_expected_check_error(None, FileBasedSourceError.EMPTY_STREAM.value)
).build()


error_listing_files_scenario = (
    _base_failure_scenario.copy()
    .set_name("error_listing_files_scenario")
    .set_stream_reader(TestErrorListMatchingFilesInMemoryFilesStreamReader(files=_base_failure_scenario._files, file_type="csv"))
    .set_expected_check_error(None, FileBasedSourceError.ERROR_LISTING_FILES.value)
).build()


error_reading_file_scenario = (
    _base_failure_scenario.copy()
    .set_name("error_reading_file_scenario")
    .set_stream_reader(TestErrorOpenFileInMemoryFilesStreamReader(files=_base_failure_scenario._files, file_type="csv"))
    .set_expected_check_error(None, FileBasedSourceError.ERROR_READING_FILE.value)
).build()


error_record_validation_user_provided_schema_scenario = (
    _base_failure_scenario.copy()
    .set_name("error_record_validation_user_provided_schema_scenario")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "csv"},
                    "globs": ["*.csv"],
                    "validation_policy": "always_fail",
                    "input_schema": '{"col1": "number", "col2": "string"}',
                }
            ],
        }
    )
    .set_validation_policies({FailingSchemaValidationPolicy.ALWAYS_FAIL:  FailingSchemaValidationPolicy()})
    .set_expected_check_error(None, FileBasedSourceError.ERROR_VALIDATING_RECORD.value)
).build()


error_multi_stream_scenario = (
    _base_failure_scenario.copy()
    .set_name("error_multi_stream_scenario")
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
                    "format": {"filetype": "jsonl"},
                    "globs": ["*.csv"],
                    "validation_policy": "Emit Record",
                }
            ],
        }
    )
    .set_expected_check_error(None, FileBasedSourceError.ERROR_READING_FILE.value)
).build()
