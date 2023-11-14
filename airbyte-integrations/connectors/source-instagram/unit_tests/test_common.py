#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_instagram.common import fix_nested_timestamp, remove_params_from_url


def test_empty_url():
    url = ""
    parsed_url = remove_params_from_url(url=url, params=[])
    assert parsed_url == url


def test_does_not_raise_exception_for_invalid_url():
    url = "abcd"
    parsed_url = remove_params_from_url(url=url, params=["test"])
    assert parsed_url == url


def test_escaped_characters():
    url = "https://google.com?test=123%23%24%25%2A&test2=456"
    parsed_url = remove_params_from_url(url=url, params=["test3"])
    assert parsed_url == url


def test_no_params_url():
    url = "https://google.com"
    parsed_url = remove_params_from_url(url=url, params=["test"])
    assert parsed_url == url


def test_no_params_arg():
    url = "https://google.com?"
    parsed_url = remove_params_from_url(url=url, params=["test"])
    assert parsed_url == "https://google.com"


def test_partially_empty_params():
    url = "https://google.com?test=122&&"
    parsed_url = remove_params_from_url(url=url, params=[])
    assert parsed_url == "https://google.com?test=122"


def test_no_matching_params():
    url = "https://google.com?test=123"
    parsed_url = remove_params_from_url(url=url, params=["test2"])
    assert parsed_url == url


def test_removes_params():
    url = "https://google.com?test=123&test2=456"
    parsed_url = remove_params_from_url(url=url, params=["test2"])
    assert parsed_url == "https://google.com?test=123"

@pytest.mark.parametrize(
    "record, path, expected",
    [
        ({"timestamp": "2021-03-03T22:48:39+0000"}, ["timestamp"], {"timestamp": "2021-03-03T22:48:39+00:00"}),
        ({"parent": {"timestamp": "2021-03-03T22:48:39+0000"}}, ["parent", "timestamp"], {"parent": {"timestamp": "2021-03-03T22:48:39+00:00"}}),
        ({"parent": [{"timestamp": "2021-03-03T22:48:39+0000"}, {"timestamp": "2021-03-03T22:48:39+0000"}]}, ["parent", "timestamp"], {"parent": [{"timestamp": "2021-03-03T22:48:39+00:00"}, {"timestamp": "2021-03-03T22:48:39+00:00"}]}),
        ({"timestamp": "invalid-timestamp"}, ["timestamp"], (ValueError, "Error transforming timestamp for field 'timestamp': 'invalid-timestamp' is not a valid ISO 8601 timestamp. Ensure the timestamp is in the correct format and includes a timezone. This error occurred while processing the record: {'timestamp': 'invalid-timestamp'}")),
        ({"other_field": "2021-03-03T22:48:39+0000"}, ["timestamp"], {"other_field": "2021-03-03T22:48:39+0000"})
    ]
)
def test_fix_nested_timestamp(record, path, expected):
    if isinstance(expected, tuple) and issubclass(expected[0], Exception):
        with pytest.raises(expected[0], match=expected[1]):
            fix_nested_timestamp(record, path)
    else:
        fix_nested_timestamp(record, path)
        assert record == expected
