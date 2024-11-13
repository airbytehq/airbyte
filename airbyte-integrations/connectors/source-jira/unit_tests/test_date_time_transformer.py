#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from conftest import find_stream


@pytest.mark.parametrize(
    "origin_item,sub_schema,expected",
    [
        ("2023-05-08T03:04:45.139-0700", {"type": "string", "format": "date-time"}, "2023-05-08T03:04:45.139000-07:00"),
        ("2022-10-31T09:00:00.594Z", {"type": "string", "format": "date-time"}, "2022-10-31T09:00:00.594000+00:00"),
        ("2023-09-11t17:51:41.666-0700", {"type": "string", "format": "date-time"}, "2023-09-11T17:51:41.666000-07:00"),
        ("some string", {"type": "string"}, "some string"),
        (1234, {"type": "integer"}, 1234),
    ],
)
def test_converting_date_to_date_time(origin_item, sub_schema, expected, config):
    stream = find_stream("pull_requests", config)
    actual = stream.transformer.default_convert(origin_item, sub_schema)
    assert actual == expected


def test_converting_date_with_incorrect_format_returning_original_value(config, caplog):
    sub_schema = {"type": "string", "format": "date-time"}
    incorrectly_formatted_date = "incorrectly_formatted_date"
    stream = find_stream("pull_requests", config)
    actual = stream.transformer.default_convert(incorrectly_formatted_date, sub_schema)
    assert actual == incorrectly_formatted_date
    assert f"{incorrectly_formatted_date}: doesn't match expected format." in caplog.text
