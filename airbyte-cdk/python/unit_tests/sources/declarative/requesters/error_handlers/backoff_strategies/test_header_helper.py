#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.header_helper import get_numeric_value_from_header


@pytest.mark.parametrize(
    "test_name, headers, requested_header, regex, expected_value",
    [
        ("test_get_numeric_value_from_header", {"header": 1}, "header", None, 1),
        ("test_get_numeric_value_float_from_header", {"header": 1.2}, "header", None, 1.2),
        ("test_get_numeric_value_from_string_value", {"header": "10.9"}, "header", None, 10.9),
        ("test_get_numeric_value_from_non_numeric", {"header": "60,120"}, "header", None, None),
        ("test_get_numeric_value_from_missing_header", {"header": 1}, "notheader", None, None),
        ("test_get_numeric_value_with_regex", {"header": "61,60"}, "header", re.compile("([-+]?\d+)"), 61),  # noqa
        ("test_get_numeric_value_with_regex_no_header", {"header": "61,60"}, "notheader", re.compile("([-+]?\d+)"), None),  # noqa
        ("test_get_numeric_value_with_regex_not_matching", {"header": "abc61,60"}, "header", re.compile("([-+]?\d+)"), None),  # noqa
    ],
)
def test_get_numeric_value_from_header(test_name, headers, requested_header, regex, expected_value):
    response_mock = create_response(headers=headers)
    numeric_value = get_numeric_value_from_header(response_mock, requested_header, regex)
    assert numeric_value == expected_value


def create_response(headers=None, json_body=None):
    url = "https://airbyte.io"

    response_mock = MagicMock()
    response_mock.url = url
    response_mock.headers = headers or {}
    response_mock.json.return_value = json_body or {}
    return response_mock
