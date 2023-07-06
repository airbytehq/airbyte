from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenarioBuilder
from unit_tests.sources.file_based.temporary_files_source import TemporaryFilesStreamReader
_single_parquet_file = {
    "a.parquet": {
        "contents": [
            ("col1", "col2"),
            ("val11", "val12"),
            ("val21", "val22"),
        ],
        "last_modified": "2023-06-05T03:54:07.000Z",
    }
}

_multiple_parquet_file = {
    "a.parquet": {
        "contents": [
            ("col1", "col2"),
            ("val11a", "val12a"),
            ("val21a", "val22a"),
        ],
        "last_modified": "2023-06-05T03:54:07.000Z",
    },
    "b.parquet": {
        "contents": [
            ("col1", "col2", "col3"),
            ("val11b", "val12b", "val13b"),
            ("val21b", "val22b", "val23b"),
        ],
        "last_modified": "2023-06-05T03:54:07.000Z",
    },
}

single_parquet_scenario = (
    TestScenarioBuilder()
    .set_name("single_parquet_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "parquet",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_stream_reader(TemporaryFilesStreamReader(files=_single_parquet_file, file_type="parquet"))
    .set_file_type("parquet")
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
                      "_ab_source_file_url": "a.parquet"}, "stream": "stream1"},
            {"data": {"col1": "val21", "col2": "val22", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.parquet"}, "stream": "stream1"},
        ]
    )
).build()

multi_parquet_scenario = (
    TestScenarioBuilder()
    .set_name("multi_parquet_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "parquet",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_file_type("parquet")
    .set_stream_reader(TemporaryFilesStreamReader(files=_multiple_parquet_file, file_type="parquet"))
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
                      "_ab_source_file_url": "a.parquet"}, "stream": "stream1"},
            {"data": {"col1": "val21a", "col2": "val22a", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "a.parquet"}, "stream": "stream1"},
            {"data": {"col1": "val11b", "col2": "val12b", "col3": "val13b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "b.parquet"}, "stream": "stream1"},
            {"data": {"col1": "val21b", "col2": "val22b", "col3": "val23b", "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                      "_ab_source_file_url": "b.parquet"}, "stream": "stream1"},
        ]
    )
).build()
