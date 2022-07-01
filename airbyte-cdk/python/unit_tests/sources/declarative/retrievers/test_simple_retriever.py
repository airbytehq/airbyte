#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
from airbyte_cdk.sources.declarative.requesters.retriers.retrier import NonRetriableResponseStatus, RetryResponseStatus
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever

primary_key = "pk"
records = [{"id": 1}, {"id": 2}]


def test_simple_retriever():
    requester = MagicMock()
    request_params = {"param": "value"}
    requester.request_params.return_value = request_params

    paginator = MagicMock()
    next_page_token = {"cursor": "cursor_value"}
    paginator.next_page_token.return_value = next_page_token

    record_selector = MagicMock()
    record_selector.select_records.return_value = records

    iterator = MagicMock()
    stream_slices = [{"date": "2022-01-01"}, {"date": "2022-01-02"}]
    iterator.stream_slices.return_value = stream_slices

    response = requests.Response()

    state = MagicMock()
    underlying_state = {"date": "2021-01-01"}
    state.get_stream_state.return_value = underlying_state

    url_base = "https://airbyte.io"
    requester.get_url_base.return_value = url_base
    path = "/v1"
    requester.get_path.return_value = path
    http_method = HttpMethod.GET
    requester.get_method.return_value = http_method
    max_retries = 10
    requester.max_retries = max_retries
    retry_factor = 2
    requester.retry_factor = retry_factor
    backoff_time = 60
    should_retry = RetryResponseStatus(backoff_time)
    requester.should_retry.return_value = should_retry
    request_body_data = {"body": "data"}
    requester.request_body_data.return_value = request_body_data
    request_body_json = {"body": "json"}
    requester.request_body_json.return_value = request_body_json
    request_kwargs = {"kwarg": "value"}
    requester.request_kwargs.return_value = request_kwargs
    cache_filename = "cache"
    requester.cache_filename = cache_filename
    use_cache = True
    requester.use_cache = use_cache

    retriever = SimpleRetriever(
        "stream_name",
        primary_key,
        requester=requester,
        paginator=paginator,
        record_selector=record_selector,
        stream_slicer=iterator,
        state=state,
    )

    # hack because we clone the state...
    retriever._state = state

    assert retriever.primary_key == primary_key
    assert retriever.url_base == url_base
    assert retriever.path() == path
    assert retriever.state == underlying_state
    assert retriever.next_page_token(response) == next_page_token
    assert retriever.request_params(None, None, None) == request_params
    assert retriever.stream_slices(sync_mode=SyncMode.incremental) == stream_slices

    assert retriever._last_response is None
    assert retriever._last_records is None
    assert retriever.parse_response(response, stream_state=None) == records
    assert retriever._last_response == response
    assert retriever._last_records == records

    assert retriever.http_method == "GET"
    assert not retriever.raise_on_http_errors
    assert retriever.max_retries == max_retries
    assert retriever.retry_factor == retry_factor
    assert retriever.should_retry(requests.Response())
    assert retriever.backoff_time(requests.Response()) == backoff_time
    assert retriever.request_body_data(None, None, None) == request_body_data
    assert retriever.request_body_json(None, None, None) == request_body_json
    assert retriever.request_kwargs(None, None, None) == request_kwargs
    assert retriever.cache_filename == cache_filename
    assert retriever.use_cache == use_cache


@pytest.mark.parametrize(
    "test_name, requester_response, expected_should_retry, expected_backoff_time",
    [
        ("test_should_retry_fail", NonRetriableResponseStatus.FAIL, False, None),
        ("test_should_retry_none_backoff", RetryResponseStatus(None), True, None),
        ("test_should_retry_custom_backoff", RetryResponseStatus(60), True, 60),
    ],
)
def test_should_retry(test_name, requester_response, expected_should_retry, expected_backoff_time):
    requester = MagicMock()
    retriever = SimpleRetriever("stream_name", primary_key, requester=requester, record_selector=MagicMock())
    requester.should_retry.return_value = requester_response
    assert retriever.should_retry(requests.Response()) == expected_should_retry
    if isinstance(requester_response, RetryResponseStatus):
        assert retriever.backoff_time(requests.Response()) == expected_backoff_time


@pytest.mark.parametrize(
    "test_name, status_code, response_status, len_expected_records",
    [
        ("test_parse_response_fails_if_should_retry_is_fail", 404, NonRetriableResponseStatus.FAIL, None),
        ("test_parse_response_succeeds_if_should_retry_is_ok", 200, NonRetriableResponseStatus.Ok, 1),
        ("test_parse_response_succeeds_if_should_retry_is_ignore", 404, NonRetriableResponseStatus.IGNORE, 0),
    ],
)
def test_parse_response(test_name, status_code, response_status, len_expected_records):
    requester = MagicMock()
    record_selector = MagicMock()
    record_selector.select_records.return_value = [{"id": 100}]
    retriever = SimpleRetriever("stream_name", primary_key, requester=requester, record_selector=record_selector)
    response = requests.Response()
    response.status_code = status_code
    requester.should_retry.return_value = response_status
    if len_expected_records is None:
        try:
            retriever.parse_response(response, stream_state={})
            assert False
        except requests.exceptions.HTTPError:
            pass
    else:
        records = retriever.parse_response(response, stream_state={})
        assert len(records) == len_expected_records
