#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
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
    raise_on_http_errors = True
    requester.raise_on_http_errors = raise_on_http_errors
    max_retries = 10
    requester.max_retries = max_retries
    retry_factor = 2
    requester.retry_factor = retry_factor
    should_retry = True
    requester.should_retry.return_value = should_retry
    backoff_time = 60
    requester.backoff_time.return_value = backoff_time
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
    assert retriever.raise_on_http_errors == raise_on_http_errors
    assert retriever.max_retries == max_retries
    assert retriever.retry_factor == retry_factor
    assert retriever.should_retry(requests.Response()) == should_retry
    assert retriever.backoff_time(requests.Response()) == backoff_time
    assert retriever.request_body_data(None, None, None) == request_body_data
    assert retriever.request_body_json(None, None, None) == request_body_json
    assert retriever.request_kwargs(None, None, None) == request_kwargs
    assert retriever.cache_filename == cache_filename
    assert retriever.use_cache == use_cache
