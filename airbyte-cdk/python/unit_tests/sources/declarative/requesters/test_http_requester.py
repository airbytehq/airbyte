#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import requests
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
from airbyte_cdk.sources.declarative.requesters.retriers.default_retrier import DefaultRetrier
from airbyte_cdk.sources.declarative.requesters.retriers.retrier import RetryResponseStatus
from airbyte_cdk.sources.streams.http.requests_native_auth.token import MultipleTokenAuthenticator


def test_http_requester():
    http_method = "GET"

    config = {"url": "https://airbyte.io"}

    request_params = {"param": "value"}
    request_body_data = "body_key_1=value_1&body_key_2=value2"
    request_headers = {"header": "value"}
    request_options_provider = InterpolatedRequestOptionsProvider(
        request_parameters=request_params, request_body_data=request_body_data, request_headers=request_headers, config=config
    )

    authenticator = MultipleTokenAuthenticator(tokens=["token"])

    max_retries = 10
    backoff_time = 1000
    retrier = DefaultRetrier()

    stream_slice = {"id": "1234"}

    name = "stream_name"

    requester = HttpRequester(
        stream_name=name,
        url_base="{{ config['url'] }}",
        path="v1/{{ stream_slice['id'] }}",
        http_method=http_method,
        request_options_provider=request_options_provider,
        authenticator=authenticator,
        retrier=retrier,
        config=config,
    )

    print(HttpRequester.schema())
    assert False

    assert isinstance(requester.url_base, InterpolatedString)
    assert isinstance(requester.path, InterpolatedString)

    assert requester.get_url_base() == "https://airbyte.io"
    assert requester.get_path(stream_state={}, stream_slice=stream_slice, next_page_token={}) == "v1/1234"
    assert requester.get_authenticator() == authenticator
    assert requester.get_method() == HttpMethod.GET
    assert requester.request_params(stream_state={}, stream_slice=None, next_page_token=None) == request_params
    assert requester.request_body_data(stream_state={}, stream_slice=None, next_page_token=None) == request_body_data
    assert requester.max_retries == max_retries
    should_retry = requester.should_retry(requests.Response())
    assert isinstance(should_retry, RetryResponseStatus)
    assert should_retry.retry_in == backoff_time
