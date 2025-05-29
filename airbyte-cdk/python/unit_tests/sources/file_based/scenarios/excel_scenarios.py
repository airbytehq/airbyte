#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import datetime

from unit_tests.sources.file_based.in_memory_files_source import TemporaryExcelFilesStreamReader
from unit_tests.sources.file_based.scenarios.file_based_source_builder import FileBasedSourceBuilder
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenarioBuilder

_single_excel_file = {
    "a.xlsx": {
        "contents": [
            {"col1": "val11", "col2": "val12"},
            {"col1": "val21", "col2": "val22"},
        ],
        "last_modified": "2023-06-05T03:54:07.000Z",
    }
}

_multiple_excel_combine_schema_file = {
    "a.xlsx": {
        "contents": [
            {"col_double": 20.02, "col_string": "Robbers", "col_album": "The 1975"},
            {
                "col_double": 20.23,
                "col_string": "Somebody Else",
                "col_album": "I Like It When You Sleep, for You Are So Beautiful yet So Unaware of It",
            },
        ],
        "last_modified": "2023-06-05T03:54:07.000Z",
    },
    "b.xlsx": {
        "contents": [
            {"col_double": 1975.1975, "col_string": "It's Not Living (If It's Not with You)", "col_song": "Love It If We Made It"},
            {"col_double": 5791.5791, "col_string": "The 1975", "col_song": "About You"},
        ],
        "last_modified": "2023-06-06T03:54:07.000Z",
    },
}

_excel_all_types_file = {
    "a.xlsx": {
        "contents": [
            {
                "col_bool": True,
                "col_int": 27,
                "col_long": 1992,
                "col_float": 999.09723456,
                "col_string": "Love It If We Made It",
                "col_date": datetime.date(2022, 5, 29),
                "col_time_millis": datetime.time(6, 0, 0, 456000),
                "col_time_micros": datetime.time(12, 0, 0, 456789),
            }
        ],
        "last_modified": "2023-06-05T03:54:07.000Z",
    }
}

_multiple_excel_stream_file = {
    "odesza_songs.xlsx": {
        "contents": [
            {"col_title": "Late Night", "col_album": "A_MOMENT_APART", "col_year": 2017, "col_vocals": False},
            {"col_title": "White Lies", "col_album": "IN_RETURN", "col_year": 2014, "col_vocals": True},
            {"col_title": "Wide Awake", "col_album": "THE_LAST_GOODBYE", "col_year": 2022, "col_vocals": True},
        ],
        "last_modified": "2023-06-05T03:54:07.000Z",
    },
    "california_festivals.xlsx": {
        "contents": [
            {
                "col_name": "Lightning in a Bottle",
                "col_location": {"country": "USA", "state": "California", "city": "Buena Vista Lake"},
                "col_attendance": 18000,
            },
            {
                "col_name": "Outside Lands",
                "col_location": {"country": "USA", "state": "California", "city": "San Francisco"},
                "col_attendance": 220000,
            },
        ],
        "last_modified": "2023-06-06T03:54:07.000Z",
    },
}

single_excel_scenario = (
    TestScenarioBuilder()
    .set_name("single_excel_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "excel"},
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                }
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_stream_reader(TemporaryExcelFilesStreamReader(files=_single_excel_file, file_type="excel"))
        .set_file_type("excel")
    )
    .set_expected_check_status("SUCCEEDED")
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val11",
                    "col2": "val12",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.xlsx",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21",
                    "col2": "val22",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.xlsx",
                },
                "stream": "stream1",
            },
        ]
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col1": {"type": ["null", "string"]},
                            "col2": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
).build()

multiple_excel_combine_schema_scenario = (
    TestScenarioBuilder()
    .set_name("multiple_excel_combine_schema_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "excel"},
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                }
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_stream_reader(TemporaryExcelFilesStreamReader(files=_multiple_excel_combine_schema_file, file_type="excel"))
        .set_file_type("excel")
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col_double": 20.02,
                    "col_string": "Robbers",
                    "col_album": "The 1975",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.xlsx",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col_double": 20.23,
                    "col_string": "Somebody Else",
                    "col_album": "I Like It When You Sleep, for You Are So Beautiful yet So Unaware of It",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.xlsx",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col_double": 1975.1975,
                    "col_string": "It's Not Living (If It's Not with You)",
                    "col_song": "Love It If We Made It",
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "b.xlsx",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col_double": 5791.5791,
                    "col_string": "The 1975",
                    "col_song": "About You",
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "b.xlsx",
                },
                "stream": "stream1",
            },
        ]
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col_double": {"type": ["null", "number"]},
                            "col_string": {"type": ["null", "string"]},
                            "col_album": {"type": ["null", "string"]},
                            "col_song": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
).build()

excel_all_types_scenario = (
    TestScenarioBuilder()
    .set_name("excel_all_types_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "format": {"filetype": "excel"},
                    "globs": ["*"],
                    "validation_policy": "Emit Record",
                }
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_stream_reader(TemporaryExcelFilesStreamReader(files=_excel_all_types_file, file_type="excel"))
        .set_file_type("excel")
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col_bool": True,
                    "col_int": 27,
                    "col_long": 1992,
                    "col_float": 999.09723456,
                    "col_string": "Love It If We Made It",
                    "col_date": "2022-05-29T00:00:00.000000",
                    "col_time_millis": "06:00:00.456000",
                    "col_time_micros": "12:00:00.456789",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "a.xlsx",
                },
                "stream": "stream1",
            },
        ]
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col_bool": {"type": ["null", "boolean"]},
                            "col_int": {"type": ["null", "number"]},
                            "col_long": {"type": ["null", "number"]},
                            "col_float": {"type": ["null", "number"]},
                            "col_string": {"type": ["null", "string"]},
                            "col_date": {"format": "date-time", "type": ["null", "string"]},
                            "col_time_millis": {"type": ["null", "string"]},
                            "col_time_micros": {"type": ["null", "string"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "stream1",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                }
            ]
        }
    )
).build()

multiple_streams_excel_scenario = (
    TestScenarioBuilder()
    .set_name("multiple_streams_excel_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "songs_stream",
                    "format": {"filetype": "excel"},
                    "globs": ["*_songs.xlsx"],
                    "validation_policy": "Emit Record",
                },
                {
                    "name": "festivals_stream",
                    "format": {"filetype": "excel"},
                    "globs": ["*_festivals.xlsx"],
                    "validation_policy": "Emit Record",
                },
            ]
        }
    )
    .set_source_builder(
        FileBasedSourceBuilder()
        .set_stream_reader(TemporaryExcelFilesStreamReader(files=_multiple_excel_stream_file, file_type="excel"))
        .set_file_type("excel")
    )
    .set_expected_records(
        [
            {
                "data": {
                    "col_title": "Late Night",
                    "col_album": "A_MOMENT_APART",
                    "col_year": 2017,
                    "col_vocals": False,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "odesza_songs.xlsx",
                },
                "stream": "songs_stream",
            },
            {
                "data": {
                    "col_title": "White Lies",
                    "col_album": "IN_RETURN",
                    "col_year": 2014,
                    "col_vocals": True,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "odesza_songs.xlsx",
                },
                "stream": "songs_stream",
            },
            {
                "data": {
                    "col_title": "Wide Awake",
                    "col_album": "THE_LAST_GOODBYE",
                    "col_year": 2022,
                    "col_vocals": True,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07.000000Z",
                    "_ab_source_file_url": "odesza_songs.xlsx",
                },
                "stream": "songs_stream",
            },
            {
                "data": {
                    "col_name": "Lightning in a Bottle",
                    "col_location": "{'country': 'USA', 'state': 'California', 'city': 'Buena Vista Lake'}",
                    "col_attendance": 18000,
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "california_festivals.xlsx",
                },
                "stream": "festivals_stream",
            },
            {
                "data": {
                    "col_name": "Outside Lands",
                    "col_location": "{'country': 'USA', 'state': 'California', 'city': 'San Francisco'}",
                    "col_attendance": 220000,
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07.000000Z",
                    "_ab_source_file_url": "california_festivals.xlsx",
                },
                "stream": "festivals_stream",
            },
        ]
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col_title": {"type": ["null", "string"]},
                            "col_album": {"type": ["null", "string"]},
                            "col_year": {"type": ["null", "number"]},
                            "col_vocals": {"type": ["null", "boolean"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "songs_stream",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                },
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col_name": {"type": ["null", "string"]},
                            "col_location": {"type": ["null", "string"]},
                            "col_attendance": {"type": ["null", "number"]},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "festivals_stream",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "is_resumable": True,
                },
            ]
        }
    )
).build()
