#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import decimal
import uuid

from unit_tests.sources.file_based.in_memory_files_source import TemporaryAvroFilesStreamReader
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenarioBuilder

_single_avro_file = {
    "a.avro": {
        "schema": {
            "type": "record",
            "name": "sampleAvro",
            "fields": [
                {"name": "col1", "type": "string"},
                {"name": "col2", "type": "int"},
            ],
        },
        "contents": [
            ("val11", 12),
            ("val21", 22),
        ],
        "last_modified": "2023-06-05T03:54:07.000Z",
    }
}

_multiple_avro_combine_schema_file = {
    "a.avro": {
        "schema": {
            "type": "record",
            "name": "sampleAvro",
            "fields": [
                {"name": "col_double", "type": "double"},
                {"name": "col_string", "type": "string"},
                {"name": "col_album", "type": {"type": "record", "name": "Album", "fields": [{"name": "album", "type": "string"}]}},
            ],
        },
        "contents": [
            (20.02, "Robbers", {"album": "The 1975"}),
            (20.23, "Somebody Else", {"album": "I Like It When You Sleep, for You Are So Beautiful yet So Unaware of It"}),
        ],
        "last_modified": "2023-06-05T03:54:07.000Z",
    },
    "b.avro": {
        "schema": {
            "type": "record",
            "name": "sampleAvro",
            "fields": [
                {"name": "col_double", "type": "double"},
                {"name": "col_string", "type": "string"},
                {"name": "col_song", "type": {"type": "record", "name": "Song", "fields": [{"name": "title", "type": "string"}]}},
            ],
        },
        "contents": [
            (1975.1975, "It's Not Living (If It's Not with You)", {"title": "Love It If We Made It"}),
            (5791.5791, "The 1975", {"title": "About You"}),
        ],
        "last_modified": "2023-06-06T03:54:07.000Z",
    },
}

_avro_all_types_file = {
    "a.avro": {
        "schema": {
            "type": "record",
            "name": "sampleAvro",
            "fields": [
                # Primitive Types
                {"name": "col_bool", "type": "boolean"},
                {"name": "col_int", "type": "int"},
                {"name": "col_long", "type": "long"},
                {"name": "col_float", "type": "float"},
                {"name": "col_double", "type": "double"},
                {"name": "col_bytes", "type": "bytes"},
                {"name": "col_string", "type": "string"},
                # Complex Types
                {
                    "name": "col_record",
                    "type": {
                        "type": "record",
                        "name": "SongRecord",
                        "fields": [
                            {"name": "artist", "type": "string"},
                            {"name": "song", "type": "string"},
                            {"name": "year", "type": "int"},
                        ],
                    },
                },
                {"name": "col_enum", "type": {"type": "enum", "name": "Genre", "symbols": ["POP_ROCK", "INDIE_ROCK", "ALTERNATIVE_ROCK"]}},
                {"name": "col_array", "type": {"type": "array", "items": "string"}},
                {"name": "col_map", "type": {"type": "map", "values": "string"}},
                {"name": "col_fixed", "type": {"type": "fixed", "name": "MyFixed", "size": 4}},
                # Logical Types
                {"name": "col_decimal", "type": {"type": "bytes", "logicalType": "decimal", "precision": 10, "scale": 5}},
                {"name": "col_uuid", "type": {"type": "bytes", "logicalType": "uuid"}},
                {"name": "col_date", "type": {"type": "int", "logicalType": "date"}},
                {"name": "col_time_millis", "type": {"type": "int", "logicalType": "time-millis"}},
                {"name": "col_time_micros", "type": {"type": "long", "logicalType": "time-micros"}},
                {"name": "col_timestamp_millis", "type": {"type": "long", "logicalType": "timestamp-millis"}},
                {"name": "col_timestamp_micros", "type": {"type": "long", "logicalType": "timestamp-micros"}},
            ],
        },
        "contents": [
            (
                True,
                27,
                1992,
                999.09723456,
                9123456.12394,
                b"\x00\x01\x02\x03",
                "Love It If We Made It",
                {"artist": "The 1975", "song": "About You", "year": 2022},
                "POP_ROCK",
                [
                    "The 1975",
                    "I Like It When You Sleep, for You Are So Beautiful yet So Unaware of It",
                    "The 1975 A Brief Inquiry into Online Relationships",
                    "Notes on a Conditional Form",
                    "Being Funny in a Foreign Language",
                ],
                {"lead_singer": "Matty Healy", "lead_guitar": "Adam Hann", "bass_guitar": "Ross MacDonald", "drummer": "George Daniel"},
                b"\x12\x34\x56\x78",
                decimal.Decimal("1234.56789"),
                uuid.UUID('123e4567-e89b-12d3-a456-426655440000').bytes,
                datetime.date(2022, 5, 29),
                datetime.time(6, 0, 0, 456000),
                datetime.time(12, 0, 0, 456789),
                datetime.datetime(2022, 5, 29, 0, 0, 0, 456000, tzinfo=datetime.timezone.utc),
                datetime.datetime(2022, 5, 30, 0, 0, 0, 456789, tzinfo=datetime.timezone.utc),
            ),
        ],
        "last_modified": "2023-06-05T03:54:07.000Z",
    }
}

_multiple_avro_stream_file = {
    "odesza_songs.avro": {
        "schema": {
            "type": "record",
            "name": "sampleAvro",
            "fields": [
                {"name": "col_title", "type": "string"},
                {
                    "name": "col_album",
                    "type": {
                        "type": "enum",
                        "name": "Album",
                        "symbols": ["SUMMERS_GONE", "IN_RETURN", "A_MOMENT_APART", "THE_LAST_GOODBYE"],
                    },
                },
                {"name": "col_year", "type": "int"},
                {"name": "col_vocals", "type": "boolean"},
            ],
        },
        "contents": [
            ("Late Night", "A_MOMENT_APART", 2017, False),
            ("White Lies", "IN_RETURN", 2014, True),
            ("Wide Awake", "THE_LAST_GOODBYE", 2022, True),
            ("Sun Models", "SUMMERS_GONE", 2012, True),
            ("All We Need", "IN_RETURN", 2014, True),
        ],
        "last_modified": "2023-06-05T03:54:07.000Z",
    },
    "california_festivals.avro": {
        "schema": {
            "type": "record",
            "name": "sampleAvro",
            "fields": [
                {"name": "col_name", "type": "string"},
                {
                    "name": "col_location",
                    "type": {
                        "type": "record",
                        "name": "LocationRecord",
                        "fields": [
                            {"name": "country", "type": "string"},
                            {"name": "state", "type": "string"},
                            {"name": "city", "type": "string"},
                        ],
                    },
                },
                {"name": "col_attendance", "type": "long"},
            ],
        },
        "contents": [
            ("Coachella", {"country": "USA", "state": "California", "city": "Indio"}, 250000),
            ("CRSSD", {"country": "USA", "state": "California", "city": "San Diego"}, 30000),
            ("Lightning in a Bottle", {"country": "USA", "state": "California", "city": "Buena Vista Lake"}, 18000),
            ("Outside Lands", {"country": "USA", "state": "California", "city": "San Francisco"}, 220000),
        ],
        "last_modified": "2023-06-06T03:54:07.000Z",
    },
}

single_avro_scenario = (
    TestScenarioBuilder()
    .set_name("single_avro_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "avro",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_stream_reader(TemporaryAvroFilesStreamReader(files=_single_avro_file, file_type="avro"))
    .set_file_type("avro")
    .set_expected_check_status("SUCCEEDED")
    .set_expected_records(
        [
            {
                "data": {
                    "col1": "val11",
                    "col2": 12,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                    "_ab_source_file_url": "a.avro",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col1": "val21",
                    "col2": 22,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                    "_ab_source_file_url": "a.avro",
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
                            "col1": {"type": "string"},
                            "col2": {"type": "integer"},
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
).build()

multiple_avro_combine_schema_scenario = (
    TestScenarioBuilder()
    .set_name("multiple_avro_combine_schema_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "avro",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_stream_reader(TemporaryAvroFilesStreamReader(files=_multiple_avro_combine_schema_file, file_type="avro"))
    .set_file_type("avro")
    .set_expected_records(
        [
            {
                "data": {
                    "col_double": "20.02",
                    "col_string": "Robbers",
                    "col_album": {"album": "The 1975"},
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                    "_ab_source_file_url": "a.avro",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col_double": "20.23",
                    "col_string": "Somebody Else",
                    "col_album": {"album": "I Like It When You Sleep, for You Are So Beautiful yet So Unaware of It"},
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                    "_ab_source_file_url": "a.avro",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col_double": "1975.1975",
                    "col_string": "It's Not Living (If It's Not with You)",
                    "col_song": {"title": "Love It If We Made It"},
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07Z",
                    "_ab_source_file_url": "b.avro",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col_double": "5791.5791",
                    "col_string": "The 1975",
                    "col_song": {"title": "About You"},
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07Z",
                    "_ab_source_file_url": "b.avro",
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
                            "col_double": {"type": "string"},
                            "col_string": {"type": "string"},
                            "col_album": {
                                "properties": {
                                    "album": {"type": "string"},
                                },
                                "type": "object",
                            },
                            "col_song": {
                                "properties": {
                                    "title": {"type": "string"},
                                },
                                "type": "object",
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
).build()

avro_all_types_scenario = (
    TestScenarioBuilder()
    .set_name("avro_all_types_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "avro",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                }
            ]
        }
    )
    .set_stream_reader(TemporaryAvroFilesStreamReader(files=_avro_all_types_file, file_type="avro"))
    .set_file_type("avro")
    .set_expected_records(
        [
            {
                "data": {
                    "col_bool": True,
                    "col_int": 27,
                    "col_long": 1992,
                    "col_float": 999.09723456,
                    "col_double": "9123456.12394",
                    "col_bytes": "\x00\x01\x02\x03",
                    "col_string": "Love It If We Made It",
                    "col_record": {"artist": "The 1975", "song": "About You", "year": 2022},
                    "col_enum": "POP_ROCK",
                    "col_array": [
                        "The 1975",
                        "I Like It When You Sleep, for You Are So Beautiful yet So Unaware of It",
                        "The 1975 A Brief Inquiry into Online Relationships",
                        "Notes on a Conditional Form",
                        "Being Funny in a Foreign Language",
                    ],
                    "col_map": {
                        "lead_singer": "Matty Healy",
                        "lead_guitar": "Adam Hann",
                        "bass_guitar": "Ross MacDonald",
                        "drummer": "George Daniel",
                    },
                    "col_fixed": "\x12\x34\x56\x78",
                    "col_decimal": 1234.56789,
                    "col_uuid": "123e4567-e89b-12d3-a456-426655440000",
                    "col_date": "2022-05-29",
                    "col_time_millis": "06:00:00.456000",
                    "col_time_micros": "12:00:00.456789",
                    "col_timestamp_millis": "2022-05-29T00:00:00.456000+00:00",
                    "col_timestamp_micros": "2022-05-30T00:00:00.456789+00:00",
                    "col_local_timestamp_millis": "2022-05-29T00:00:00.456000",
                    "col_local_timestamp_micros": "2022-05-30T00:00:00.456789",
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                    "_ab_source_file_url": "a.avro",
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
                            "col_array": {"items": {"type": "string"}, "type": "array"},
                            "col_bool": {"type": "boolean"},
                            "col_bytes": {"type": "string"},
                            "col_double": {"type": "string"},
                            "col_enum": {"enum": ["POP_ROCK", "INDIE_ROCK", "ALTERNATIVE_ROCK"], "type": "string"},
                            "col_fixed": {"pattern": "^[0-9A-Fa-f]{8}$", "type": "string"},
                            "col_float": {"type": "number"},
                            "col_int": {"type": "integer"},
                            "col_long": {"type": "integer"},
                            "col_map": {"additionalProperties": {"type": "string"}, "type": "object"},
                            "col_record": {
                                "properties": {"artist": {"type": "string"}, "song": {"type": "string"}, "year": {"type": "integer"}},
                                "type": "object",
                            },
                            "col_string": {"type": "string"},
                            "col_decimal": {"pattern": "^-?\\d{(1, 5)}(?:\\.\\d(1, 5))?$", "type": "string"},
                            "col_uuid": {"type": "string"},
                            "col_date": {"format": "date", "type": "string"},
                            "col_time_millis": {"type": "integer"},
                            "col_time_micros": {"type": "integer"},
                            "col_timestamp_millis": {"format": "date-time", "type": "string"},
                            "col_timestamp_micros": {"type": "string"},
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
).build()

multiple_streams_avro_scenario = (
    TestScenarioBuilder()
    .set_name("multiple_streams_avro_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "songs_stream",
                    "file_type": "avro",
                    "globs": ["*_songs.avro"],
                    "validation_policy": "emit_record",
                },
                {
                    "name": "festivals_stream",
                    "file_type": "avro",
                    "globs": ["*_festivals.avro"],
                    "validation_policy": "emit_record",
                },
            ]
        }
    )
    .set_stream_reader(TemporaryAvroFilesStreamReader(files=_multiple_avro_stream_file, file_type="avro"))
    .set_file_type("avro")
    .set_expected_records(
        [
            {
                "data": {
                    "col_title": "Late Night",
                    "col_album": "A_MOMENT_APART",
                    "col_year": 2017,
                    "col_vocals": False,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                    "_ab_source_file_url": "odesza_songs.avro",
                },
                "stream": "songs_stream",
            },
            {
                "data": {
                    "col_title": "White Lies",
                    "col_album": "IN_RETURN",
                    "col_year": 2014,
                    "col_vocals": True,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                    "_ab_source_file_url": "odesza_songs.avro",
                },
                "stream": "songs_stream",
            },
            {
                "data": {
                    "col_title": "Wide Awake",
                    "col_album": "THE_LAST_GOODBYE",
                    "col_year": 2022,
                    "col_vocals": True,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                    "_ab_source_file_url": "odesza_songs.avro",
                },
                "stream": "songs_stream",
            },
            {
                "data": {
                    "col_title": "Sun Models",
                    "col_album": "SUMMERS_GONE",
                    "col_year": 2012,
                    "col_vocals": True,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                    "_ab_source_file_url": "odesza_songs.avro",
                },
                "stream": "songs_stream",
            },
            {
                "data": {
                    "col_title": "All We Need",
                    "col_album": "IN_RETURN",
                    "col_year": 2014,
                    "col_vocals": True,
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                    "_ab_source_file_url": "odesza_songs.avro",
                },
                "stream": "songs_stream",
            },
            {
                "data": {
                    "col_name": "Coachella",
                    "col_location": {"country": "USA", "state": "California", "city": "Indio"},
                    "col_attendance": 250000,
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07Z",
                    "_ab_source_file_url": "california_festivals.avro",
                },
                "stream": "festivals_stream",
            },
            {
                "data": {
                    "col_name": "CRSSD",
                    "col_location": {"country": "USA", "state": "California", "city": "San Diego"},
                    "col_attendance": 30000,
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07Z",
                    "_ab_source_file_url": "california_festivals.avro",
                },
                "stream": "festivals_stream",
            },
            {
                "data": {
                    "col_name": "Lightning in a Bottle",
                    "col_location": {"country": "USA", "state": "California", "city": "Buena Vista Lake"},
                    "col_attendance": 18000,
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07Z",
                    "_ab_source_file_url": "california_festivals.avro",
                },
                "stream": "festivals_stream",
            },
            {
                "data": {
                    "col_name": "Outside Lands",
                    "col_location": {"country": "USA", "state": "California", "city": "San Francisco"},
                    "col_attendance": 220000,
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07Z",
                    "_ab_source_file_url": "california_festivals.avro",
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
                            "col_title": {"type": "string"},
                            "col_album": {"type": "string", "enum": ["SUMMERS_GONE", "IN_RETURN", "A_MOMENT_APART", "THE_LAST_GOODBYE"]},
                            "col_year": {"type": "integer"},
                            "col_vocals": {"type": "boolean"},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "songs_stream",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                },
                {
                    "default_cursor_field": ["_ab_source_file_last_modified"],
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "col_name": {"type": "string"},
                            "col_location": {
                                "properties": {"country": {"type": "string"}, "state": {"type": "string"}, "city": {"type": "string"}},
                                "type": "object",
                            },
                            "col_attendance": {"type": "integer"},
                            "_ab_source_file_last_modified": {"type": "string"},
                            "_ab_source_file_url": {"type": "string"},
                        },
                    },
                    "name": "festivals_stream",
                    "source_defined_cursor": True,
                    "supported_sync_modes": ["full_refresh", "incremental"],
                },
            ]
        }
    )
).build()

avro_file_with_decimal_as_float_scenario = (
    TestScenarioBuilder()
    .set_name("avro_file_with_decimal_as_float_stream")
    .set_config(
        {
            "streams": [
                {
                    "name": "stream1",
                    "file_type": "avro",
                    "globs": ["*"],
                    "validation_policy": "emit_record",
                    "format": {
                        "avro": {
                            "filetype": "avro",
                            "decimal_as_float": True
                        }
                    }
                }
            ]
        }
    )
    .set_stream_reader(TemporaryAvroFilesStreamReader(files=_multiple_avro_combine_schema_file, file_type="avro"))
    .set_file_type("avro")
    .set_expected_records(
        [
            {
                "data": {
                    "col_double": 20.02,
                    "col_string": "Robbers",
                    "col_album": {"album": "The 1975"},
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                    "_ab_source_file_url": "a.avro",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col_double": 20.23,
                    "col_string": "Somebody Else",
                    "col_album": {"album": "I Like It When You Sleep, for You Are So Beautiful yet So Unaware of It"},
                    "_ab_source_file_last_modified": "2023-06-05T03:54:07Z",
                    "_ab_source_file_url": "a.avro",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col_double": 1975.1975,
                    "col_string": "It's Not Living (If It's Not with You)",
                    "col_song": {"title": "Love It If We Made It"},
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07Z",
                    "_ab_source_file_url": "b.avro",
                },
                "stream": "stream1",
            },
            {
                "data": {
                    "col_double": 5791.5791,
                    "col_string": "The 1975",
                    "col_song": {"title": "About You"},
                    "_ab_source_file_last_modified": "2023-06-06T03:54:07Z",
                    "_ab_source_file_url": "b.avro",
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
                            "col_double": {"type": "number"},
                            "col_string": {"type": "string"},
                            "col_album": {
                                "properties": {
                                    "album": {"type": "string"},
                                },
                                "type": "object",
                            },
                            "col_song": {
                                "properties": {
                                    "title": {"type": "string"},
                                },
                                "type": "object",
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
).build()
