#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import requests
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpMethod, HttpRequester


def test():
    http_method = "GET"

    request_options_provider = MagicMock()
    request_params = {"param": "value"}
    request_body_data = "body_key_1=value_1&body_key_2=value2"
    request_body_json = {"body_field": "body_value"}
    request_options_provider.request_params.return_value = request_params
    request_options_provider.request_body_data.return_value = request_body_data
    request_options_provider.request_body_json.return_value = request_body_json

    request_headers_provider = MagicMock()
    request_headers = {"header": "value"}
    request_headers_provider.request_headers.return_value = request_headers

    authenticator = MagicMock()

    retrier = MagicMock()
    max_retries = 10
    should_retry = True
    backoff_time = 1000
    retrier.max_retries = max_retries
    retrier.should_retry.return_value = should_retry
    retrier.backoff_time.return_value = backoff_time

    config = {"url": "https://airbyte.io"}
    stream_slice = {"id": "1234"}

    name = "stream_name"

    requester = HttpRequester(
        name=name,
        url_base="{{ config['url'] }}",
        path="v1/{{ stream_slice['id'] }}",
        http_method=http_method,
        request_options_provider=request_options_provider,
        authenticator=authenticator,
        retrier=retrier,
        config=config,
    )

    assert requester.get_url_base() == "https://airbyte.io"
    assert requester.get_path(stream_state={}, stream_slice=stream_slice, next_page_token={}) == "v1/1234"
    assert requester.get_authenticator() == authenticator
    assert requester.get_method() == HttpMethod.GET
    assert requester.request_params(stream_state={}, stream_slice=None, next_page_token=None) == request_params
    assert requester.request_body_data(stream_state={}, stream_slice=None, next_page_token=None) == request_body_data
    assert requester.request_body_json(stream_state={}, stream_slice=None, next_page_token=None) == request_body_json
    assert requester.max_retries == max_retries
    assert requester.should_retry(requests.Response()) == should_retry
    assert requester.backoff_time(requests.Response()) == backoff_time
