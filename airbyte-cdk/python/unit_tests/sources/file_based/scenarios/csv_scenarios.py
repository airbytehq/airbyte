from unit_tests.sources.file_based.scenarios._base_scenario import BaseTestScenario


class SingleCsvTestScenario(BaseTestScenario):
    config = {
        "streams": [
            {
                "name": "single_csv_stream",
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
                "name": "single_csv_stream",
                "supported_sync_modes": ["full_refresh"],
            }
        ]
    }
    expected_records = [
        {"col1": "val11", "col2": "val12"},
        {"col1": "val21", "col2": "val22"},
    ]
