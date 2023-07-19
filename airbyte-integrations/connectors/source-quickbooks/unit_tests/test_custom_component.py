#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
from datetime import datetime, timezone

from source_quickbooks.components import CustomDatetimeBasedCursor, LastRecordDictProxy


def test_dict_proxy():
    record = {
        "Id": "1",
        "MetaData": {
            "CreateTime": "2023-02-10T14:42:07-08:00",
            "LastUpdatedTime": "2023-02-18T13:13:33-08:00"
        }
    }
    proxy = LastRecordDictProxy(record, {"airbyte_cursor": "MetaData/LastUpdatedTime"})

    assert proxy["MetaData/LastUpdatedTime"] == "2023-02-18T13:13:33-08:00"
    assert proxy["Id"] == "1"

    assert proxy.get("MetaData/LastUpdatedTime") == "2023-02-18T13:13:33-08:00"
    assert proxy.get("Id") == "1"

    assert "airbyte_cursor" not in record
    assert proxy["airbyte_cursor"] == record["MetaData"]["LastUpdatedTime"]

    proxy["MetaData/LastUpdatedTime"] = "0000-00-00T00:00:00+00:00"
    proxy["Id"] = "2"

    assert record["MetaData"]["LastUpdatedTime"] == "0000-00-00T00:00:00+00:00"
    assert record["Id"] == "2"

    del record["MetaData"]["CreateTime"]

    assert "CreateTime" not in record["MetaData"]

    assert record == {
        "Id": "2",
        "MetaData": {"LastUpdatedTime": "0000-00-00T00:00:00+00:00"}
    }


def test_custom_datetime_based_cursor__close_slice():
    cursor_field_name = "airbyte_cursor"
    record_cursor_value = "2023-02-10T14:42:05-08:00"

    date_time_based_cursor_component = CustomDatetimeBasedCursor(
        start_datetime="2023-02-01T00:00:00+00:00",
        end_datetime="2023-02-01T00:00:00+00:00",
        step="P30D",
        cursor_field=cursor_field_name,
        datetime_format="%Y-%m-%dT%H:%M:%S%z",
        cursor_granularity="PT0S",
        config={},
        parameters={}
    )

    slice_end_time = "2023-03-03T00:00:00+00:00"
    date_time_based_cursor_component.close_slice(
        {
            "start_time": "2023-02-01T00:00:00+00:00",
            "end_time": slice_end_time
        },
        {
            "Id": "1",
            "MetaData": {
                "CreateTime": "2023-02-10T14:42:07-08:00",
                "LastUpdatedTime": record_cursor_value
            }
        }
    )
    assert date_time_based_cursor_component.get_stream_state() == {cursor_field_name: slice_end_time}


def test_custom_datetime_based_cursor__format_datetime():
    date_time_based_cursor_component = CustomDatetimeBasedCursor(
        start_datetime="2023-02-01T00:00:00+00:00",
        end_datetime="2023-02-01T00:00:00+00:00",
        step="P30D",
        cursor_field="airbyte_cursor",
        datetime_format="%Y-%m-%dT%H:%M:%S%z",
        cursor_granularity="PT0S",
        config={},
        parameters={}
    )

    _format_datetime = getattr(date_time_based_cursor_component, "_format_datetime")
    pattern = re.compile("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[+-][0-9]{2}:[0-9]{2}")
    assert pattern.fullmatch(_format_datetime(datetime.now(timezone.utc)))


def test_custom_datetime_based_cursor__parse_datetime():
    date_time_based_cursor_component = CustomDatetimeBasedCursor(
        start_datetime="2023-02-01T00:00:00+00:00",
        end_datetime="2023-02-01T00:00:00+00:00",
        step="P30D",
        cursor_field="airbyte_cursor",
        datetime_format="%Y-%m-%dT%H:%M:%S%z",
        cursor_granularity="PT0S",
        config={},
        parameters={}
    )

    datetime_string_original_offset = "2023-02-10T14:42:05-08:00"
    datetime_string_in_utc = "2023-02-10T22:42:05+00:00"

    parse_date = getattr(date_time_based_cursor_component, "parse_date")
    dt_utc = parse_date(datetime_string_original_offset)

    _format_datetime = getattr(date_time_based_cursor_component, "_format_datetime")
    assert _format_datetime(dt_utc) == datetime_string_in_utc
