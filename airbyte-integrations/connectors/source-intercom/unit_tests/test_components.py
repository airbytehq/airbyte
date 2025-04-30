# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from components import CustomScrollRetriever
from requests.exceptions import HTTPError

from airbyte_cdk.sources.declarative.partition_routers.single_partition_router import SinglePartitionRouter
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.streams import Stream


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
def test_rate_limiter(components_module, rate_limit_header, backoff_time):
    IntercomRateLimiter = components_module.IntercomRateLimiter

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


def test_restart_on_500_error():
    # Mock the requester, paginator, record_selector, config, and parameters
    requester = MagicMock()
    paginator = MagicMock()
    record_selector = MagicMock()
    stream_slicer = SinglePartitionRouter(parameters={})
    config = {}  # Mock config as an empty dictionary
    parameters = {}  # Mock parameters as an empty dictionary

    # Mock responses for the companies stream
    first_response = requests.Response()
    first_response.status_code = 200
    first_response._content = json.dumps({"data": [{"id": "comp1"}, {"id": "comp2"}], "scroll_param": "next_page_token_1"}).encode("utf-8")

    second_response = requests.Response()
    second_response.status_code = 200
    second_response._content = json.dumps({"data": [{"id": "comp3"}, {"id": "comp4"}], "scroll_param": "next_page_token_2"}).encode("utf-8")

    error_response = requests.Response()
    error_response.status_code = 500
    error_response._content = b"Internal Server Error"

    empty_response = requests.Response()
    empty_response.status_code = 200
    empty_response._content = json.dumps({"data": [], "scroll_param": ""}).encode("utf-8")

    # Simulate the sequence: first page, second page, error, restart first page, empty page
    requester.send_request.side_effect = [
        first_response,  # First page
        second_response,  # Second page
        HTTPError(response=error_response),  # Simulate HTTP 500 error
        first_response,  # Restart first page
        empty_response,  # Empty page to stop
    ]

    # Mock the record selector to return records for successful responses
    record_selector.select_records.side_effect = [
        [{"id": "comp1"}, {"id": "comp2"}],  # First page
        [{"id": "comp3"}, {"id": "comp4"}],  # Second page
        [{"id": "comp1"}, {"id": "comp2"}],  # Restart first page
        [],  # Empty page
    ]

    # Set up the paginator mock to handle __name__ attribute
    paginator.get_request_headers = MagicMock(__name__="get_request_headers")
    paginator.get_request_params = MagicMock(__name__="get_request_params")
    paginator.get_request_body_data = MagicMock(__name__="get_request_body_data")
    paginator.get_request_body_json = MagicMock(__name__="get_request_body_json")

    # Initialize the CustomScrollRetriever with config and parameters
    retriever = CustomScrollRetriever(
        requester=requester,
        paginator=paginator,
        record_selector=record_selector,
        stream_slicer=stream_slicer,
        config=config,  # Pass mocked config
        parameters=parameters,  # Pass mocked parameters
    )

    # Mock the stream state and slice
    stream_state = {}
    stream_slice = StreamSlice(partition={}, cursor_slice={})

    # Collect records from the retriever
    records = list(retriever.read_records(stream_state, stream_slice))

    # Verify the records fetched
    expected_records = [
        {"id": "comp1"},
        {"id": "comp2"},  # Initial first page
        {"id": "comp3"},
        {"id": "comp4"},  # Second page
        {"id": "comp1"},
        {"id": "comp2"},  # Restarted first page
    ]
    assert records == expected_records, f"Expected {expected_records}, but got {records}"

    # Verify that the requester was called with the correct parameters
    assert requester.send_request.call_args_list[0][1]["request_params"] == {}  # First call: no scroll_param
    assert requester.send_request.call_args_list[1][1]["request_params"] == {"scroll_param": "next_page_token_1"}  # Second call
    assert requester.send_request.call_args_list[2][1]["request_params"] == {"scroll_param": "next_page_token_2"}  # Third call (error)
    assert requester.send_request.call_args_list[3][1]["request_params"] == {}  # Fourth call: restarted, no scroll_param
    assert requester.send_request.call_args_list[4][1]["request_params"] == {"scroll_param": "next_page_token_1"}  # Fifth call
