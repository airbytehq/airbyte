#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from source_intercom.components import IncrementalSingleSliceCursor, IncrementalSubstreamSlicerCursor, IntercomRateLimiter

from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.streams import Stream


def test_slicer():
    date_time_dict = {"updated_at": 1662459010}
    slicer = IncrementalSingleSliceCursor(config={}, parameters={}, cursor_field="updated_at")
    slicer.observe(date_time_dict, date_time_dict)
    slicer.close_slice(date_time_dict)
    assert slicer.get_stream_state() == date_time_dict
    assert slicer.get_request_headers() == {}
    assert slicer.get_request_body_data() == {}
    assert slicer.get_request_body_json() == {}


@pytest.mark.parametrize(
    "last_record, expected, records",
    [
        (
            {"first_stream_cursor": 1662459010},
            {
                "first_stream_cursor": 1662459010,
                "prior_state": {"first_stream_cursor": 1662459010, "parent_stream_name": {"parent_cursor_field": 1662459010}},
                "parent_stream_name": {"parent_cursor_field": 1662459010},
            },
            [{"first_stream_cursor": 1662459010}],
        )
    ],
)
def test_sub_slicer(last_record, expected, records):
    parent_stream = Mock(spec=Stream)
    parent_stream.name = "parent_stream_name"
    parent_stream.cursor_field = "parent_cursor_field"
    parent_stream.state = {"parent_stream_name": {"parent_cursor_field": 1662459010}}
    parent_stream.stream_slices.return_value = [{"a slice": "value"}]
    parent_stream.read_records = MagicMock(return_value=records)

    parent_config = ParentStreamConfig(
        stream=parent_stream,
        parent_key="first_stream_cursor",
        partition_field="first_stream_id",
        parameters={},
        config={},
    )

    slicer = IncrementalSubstreamSlicerCursor(
        config={}, parameters={}, cursor_field="first_stream_cursor", parent_stream_configs=[parent_config], parent_complete_fetch=True
    )
    slicer.set_initial_state(expected)
    stream_slice = next(slicer.stream_slices()) if records else {}
    slicer.observe(stream_slice, last_record)
    slicer.close_slice(stream_slice)
    assert slicer.get_stream_state() == expected


@pytest.mark.parametrize(
    "rate_limit_header, backoff_time",
    [
        ({"X-RateLimit-Limit": 167, "X-RateLimit-Remaining": 167}, 0.01),
        ({"X-RateLimit-Limit": 167, "X-RateLimit-Remaining": 100}, 0.01),
        ({"X-RateLimit-Limit": 167, "X-RateLimit-Remaining": 83}, 1.5),
        ({"X-RateLimit-Limit": 167, "X-RateLimit-Remaining": 16}, 8.0),
        ({}, 1.0),
    ],
)
def test_rate_limiter(rate_limit_header, backoff_time):
    def check_backoff_time(t):
        """A replacer for original `IntercomRateLimiter.backoff_time`"""
        assert backoff_time == t, f"Expected {backoff_time}, got {t}"

    class Requester:
        @IntercomRateLimiter.balance_rate_limit()
        def interpret_response_status(self, response: requests.Response):
            """A stub for the decorator function being tested"""

    with patch.object(IntercomRateLimiter, "backoff_time") as backoff_time_mock:
        # Call `check_backoff_time` instead of original `IntercomRateLimiter.backoff_time` method
        backoff_time_mock.side_effect = check_backoff_time

        requester = Requester()

        # Prepare requester object with headers
        response = requests.models.Response()
        response.headers = rate_limit_header

        # Call a decorated method
        requester.interpret_response_status(response)
