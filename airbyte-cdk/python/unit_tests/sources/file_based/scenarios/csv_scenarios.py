#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unit_tests.sources.file_based.scenarios._base_scenario import BaseTestScenario


class SingleCsvTestScenario(BaseTestScenario):
    name = "single_csv_stream"
    config = {
        "streams": [
            {
                "name": name,
                "file_type": "csv",
                "globs": [["*.csv"]],
                "validation_policy": "emit_record_on_schema_mismatch",
            }
        ]
    }
    files = {
        "a.csv": {
            "contents": [
                ("col1", "col2"),
                ("val11", "val12"),
                ("val21", "val22"),
            ],
            "last_modified": "2023-06-05T03:54:07.000Z",
        }
    }
    expected_catalog = {
        "streams": [
            {
                "json_schema": {"col1": "string", "col2": "string"},
                "name": name,
                "supported_sync_modes": ["full_refresh"],
            }
        ]
    }
    expected_records = [
        {"col1": "val11", "col2": "val12"},
        {"col1": "val21", "col2": "val22"},
    ]


class MultiCsvTestScenario(BaseTestScenario):
    name = "multi_csv_stream"
    config = {
        "streams": [
            {
                "name": name,
                "file_type": "csv",
                "globs": [["*.csv"]],
                "validation_policy": "emit_record_on_schema_mismatch",
            }
        ]
    }
    files = {
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
    expected_catalog = {
        "streams": [
            {
                "json_schema": {"col1": "string", "col2": "string", "col3": "string"},
                "name": name,
                "supported_sync_modes": ["full_refresh"],
            }
        ]
    }
    expected_records = [
        {"col1": "val11a", "col2": "val12a"},
        {"col1": "val21a", "col2": "val22a"},
        {"col1": "val11b", "col2": "val12b", "col3": "val13b"},
        {"col1": "val21b", "col2": "val22b", "col3": "val23b"},
    ]


class MultiCsvNFilesExceedsLimitForSchemaInferenceTestScenario(MultiCsvTestScenario):
    name = "multi_csv_stream"
    schema_inference_limit = 1
    expected_catalog = {
        "streams": [
            {
                "json_schema": {"col1": "string", "col2": "string"},
                "name": name,
                "supported_sync_modes": ["full_refresh"],
            }
        ]
    }
