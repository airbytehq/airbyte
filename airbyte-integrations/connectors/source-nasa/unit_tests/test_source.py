#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from source_nasa.source import NasaApod, SourceNasa

date_format = "%Y-%m-%d"
min_date = datetime.strptime("1995-06-16", date_format)
tomorrow = SourceNasa().max_date
after_tomorrow_str = (tomorrow + timedelta(days=1)).strftime(date_format)
valid_date_str = (min_date + timedelta(days=10)).strftime(date_format)


@pytest.mark.parametrize(
    ("config", "expected_return"),
    [
        ({"api_key": "foobar"}, (True, None)),
        ({"api_key": "foobar", "start_date": valid_date_str}, (True, None)),
        (
            {"api_key": "foobar", "start_date": valid_date_str, "count": 5},
            (False, "Invalid parameter combination. Cannot use start_date and count together."),
        ),
        (
            {"api_key": "foobar", "end_date": valid_date_str, "count": 5},
            (False, "Invalid parameter combination. Cannot use end_date and count together."),
        ),
        ({"api_key": "foobar", "end_date": valid_date_str}, (False, "Cannot use end_date without specifying start_date.")),
        (
            {"api_key": "foobar", "start_date": valid_date_str, "end_date": min_date.strftime(date_format)},
            (
                False,
                f"Invalid values. start_date ({datetime.strptime(valid_date_str, date_format)}) needs to be lower than or equal to end_date ({min_date}).",
            ),
        ),
        ({"api_key": "foobar", "start_date": min_date.strftime(date_format), "end_date": valid_date_str}, (True, None)),
        ({"api_key": "foobar", "count": 0}, (False, "Invalid count value: 0. The value should be in the range [1,101).")),
        ({"api_key": "foobar", "count": 101}, (False, "Invalid count value: 101. The value should be in the range [1,101).")),
        ({"api_key": "foobar", "count": 1}, (True, None)),
    ],
)
def test_check_connection(mocker, config, expected_return):
    with patch.object(NasaApod, "read_records") as mock_http_request:
        mock_http_request.return_value = iter([None])
        source = SourceNasa()
        logger_mock = MagicMock()
        assert source.check_connection(logger_mock, config) == expected_return


def test_streams(mocker):
    source = SourceNasa()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
